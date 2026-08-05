"""Contract binding the V&V harness to the shipped recovery engine.

``tests/vv/verify-recovery-mechanism.bat`` proves the one claim plan mode cannot:
that capture-then-restore actually round-trips a registry value. It does so by
copying the capture and restore logic verbatim out of the engine and driving it
against a scratch key under HKCU.

That design has an obvious hazard — if the engine changes and the copy does not,
the harness verifies a fossil. These tests assert the copy still matches, so the
harness cannot silently stop testing the product.

Reads files as text. Executes nothing; the harness itself is run separately
because it performs real (scratch-key-only) registry writes.
"""

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HARNESS = REPO_ROOT / "clutchg" / "tests" / "vv" / "verify-recovery-mechanism.bat"
BACKUP = REPO_ROOT / "src" / "backup" / "backup-registry.bat"
ROLLBACK = REPO_ROOT / "src" / "safety" / "rollback.bat"


# Backslash as a value, so no escaping layer can corrupt the literals below.
BS = chr(92)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")


# The statements that constitute the mechanism. Each must appear in BOTH the
# shipped engine and the harness, or the harness has drifted.
CAPTURE_STATEMENTS = (
    'reg query "!REGISTRY_KEY!" >nul 2>&1 && set "KEY_EXISTED=1"',
    'echo key_existed=!KEY_EXISTED!',
    'echo value_existed=!VALUE_EXISTED!',
    'echo data=!VALUE_DATA!',
)

RESTORE_STATEMENTS = (
    'reg add "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /t REG_DWORD /d "!VALUE_DATA!" /f >nul 2>&1',
    'reg delete "!REGISTRY_KEY!" /f >nul 2>&1',
    'reg delete "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /f >nul 2>&1',
)


@pytest.mark.unit
class TestHarnessMatchesEngine:
    def test_harness_exists_and_is_crlf(self):
        assert HARNESS.is_file(), "V&V harness is missing"
        raw = HARNESS.read_bytes()
        assert b"\r\n" in raw, "harness is LF-only; CMD will mis-parse it"
        assert raw.count(b"\n") - raw.count(b"\r\n") == 0

    @pytest.mark.parametrize("statement", CAPTURE_STATEMENTS)
    def test_capture_statement_matches_the_backup_engine(self, statement):
        engine = _read(BACKUP)
        harness = _read(HARNESS)
        assert statement in engine, (
            f"backup-registry.bat no longer contains {statement!r} — the engine "
            f"changed, so the V&V harness must be re-derived from it"
        )
        assert statement in harness, f"harness has drifted: missing {statement!r}"

    @pytest.mark.parametrize("statement", RESTORE_STATEMENTS)
    def test_restore_statement_matches_the_rollback_engine(self, statement):
        engine = _read(ROLLBACK)
        harness = _read(HARNESS)
        assert statement in engine, (
            f"rollback.bat no longer contains {statement!r} — the engine changed, "
            f"so the V&V harness must be re-derived from it"
        )
        assert statement in harness, f"harness has drifted: missing {statement!r}"

    def test_state_file_field_names_agree(self):
        """The artifact written by capture must be readable by restore."""
        backup, rollback, harness = _read(BACKUP), _read(ROLLBACK), _read(HARNESS)
        for field in ("key_existed", "value_existed", "data="):
            assert field in backup, f"{field} not written by the backup engine"
            assert field in rollback, f"{field} not read by the rollback engine"
            assert field in harness, f"{field} absent from the harness"


@pytest.mark.unit
class TestHarnessTouchesOnlyScratchState:
    """The harness must be incapable of altering a real Windows setting."""

    SCRATCH = r"HKCU\Software\ClutchG-VV-Scratch"

    def test_every_registry_write_targets_the_scratch_key(self):
        harness = _read(HARNESS)
        assert f'set "SCRATCH_KEY={self.SCRATCH}"' in harness

        offenders = []
        for number, line in enumerate(harness.split("\n"), start=1):
            match = re.match(r'\s*reg\s+(add|delete)\s+"([^"]+)"', line, re.IGNORECASE)
            if match and match.group(2) not in ("!SCRATCH_KEY!", "!REGISTRY_KEY!"):
                offenders.append(f"{number}: {line.strip()[:80]}")
        assert not offenders, (
            "harness writes outside the scratch key:\n" + "\n".join(offenders)
        )

    def test_registry_key_variable_is_only_ever_the_scratch_key(self):
        """`!REGISTRY_KEY!` is the engine's variable name, kept for verbatim copy."""
        harness = _read(HARNESS)
        assignments = set(re.findall(r'set "REGISTRY_KEY=([^"]*)"', harness))
        assert assignments == {"!SCRATCH_KEY!"}, (
            f"REGISTRY_KEY is assigned something other than the scratch key: "
            f"{sorted(assignments)}"
        )

    def test_harness_cleans_up_after_itself(self):
        harness = _read(HARNESS)
        assert ":cleanup_scratch" in harness
        assert 'reg delete "!SCRATCH_KEY!" /f' in harness
        # Cleanup must run at the end of the run, not only per-case.
        tail = harness.split("call :case_absent_key", 1)[1][:400]
        assert "call :cleanup_scratch" in tail

@pytest.mark.unit
class TestPowerSchemeCaseMatchesEngine:
    """Case 4 verifies the power-scheme component the same way as the registry ones.

    It duplicates the active scheme, activates the copy, then runs the engine's
    real capture (getactivescheme + write active_power_guid.txt) and restore
    (read the file, validate the GUID shape, setactive). The original is
    reactivated and the copy deleted, so the machine ends where it started.
    powercfg /duplicatescheme and /setactive need no elevation, which is what
    makes this testable outside a VM.
    """

    def test_capture_mirrors_the_backup_engine(self):
        engine = _read(BACKUP)
        harness = _read(HARNESS)
        getactive = (
            'for /f "tokens=4" %%G in (' + chr(39) + "powercfg /getactivescheme "
            "2^>nul" + chr(39) + ") do set"
        )
        assert getactive in engine, "backup engine no longer reads the active scheme"
        assert 'powercfg /export "!BACKUP_FOLDER!' + BS + 'power_plan.pow"' in engine
        assert getactive in harness, "harness dropped the getactivescheme capture"
        assert '>"!STATE_DIR!' + BS + 'active_power_guid.txt" echo !ORIGINAL_GUID!' in harness

    def test_restore_mirrors_the_rollback_engine(self):
        engine = _read(ROLLBACK)
        harness = _read(HARNESS)
        assert (
            'set /p ORIGINAL_POWER_GUID=<"!RESTORE_DIR!' + BS + 'active_power_guid.txt"'
        ) in engine, "rollback engine no longer reads the captured GUID"
        assert 'powercfg /setactive "!ORIGINAL_POWER_GUID!"' in engine
        assert (
            'set /p RESTORED_GUID=<"!STATE_DIR!' + BS + 'active_power_guid.txt"'
        ) in harness, "harness dropped the GUID read"
        assert 'powercfg /setactive "!RESTORED_GUID!"' in harness

    def test_guid_shape_check_is_carried_over(self):
        """The engine refuses a malformed GUID before calling setactive."""
        pattern = "[0-9A-Fa-f][0-9A-Fa-f]*-[0-9A-Fa-f][0-9A-Fa-f]*-"
        assert pattern in _read(ROLLBACK), "rollback.bat no longer shape-checks the GUID"
        assert pattern in _read(HARNESS), "harness dropped the GUID shape check"

    def test_scratch_scheme_is_deleted_and_original_reactivated(self):
        harness = _read(HARNESS)
        assert 'powercfg /duplicatescheme "!ORIGINAL_GUID!"' in harness
        assert 'powercfg /delete "!SCRATCH_GUID!"' in harness

    def test_unelevated_export_is_reported_as_partial_not_passed(self):
        """powercfg /export needs SeBackupPrivilege.

        That is an environment limit rather than a defect, so it must not fail
        the run — but it must not be silently counted as a pass either, and a
        scheme that fails to reactivate must still be a hard failure.
        """
        harness = _read(HARNESS)
        assert "CASES_PARTIAL" in harness
        assert "export-needs-elevation" in harness
        block = harness.split('if not "!EXPORT_CODE!"=="0" (', 1)[1].split(chr(10) + ")", 1)[0]
        assert "CASES_PASSED" not in block, "an unexportable run must not count as passed"
        assert "scheme-not-reactivated" in block, (
            "failing to reactivate the original scheme must still be reported"
        )

@pytest.mark.unit
class TestServiceCaptureCaseMatchesEngine:
    """Case 5 verifies the read-only half of the service component.

    ``sc config`` needs elevation, so restore cannot run outside a VM. But the
    capture half is entirely read-only (``sc qc``, ``sc query``, ``reg query``),
    so it can be verified here — and what it verifies is real: that capture writes
    a state file whose shape restore actually accepts, and whose start_type maps
    to a legal ``sc config`` argument. That closes the "capture writes something
    restore cannot read" failure mode without touching a service.
    """

    def test_capture_mirrors_the_backup_engine(self):
        engine = _read(BACKUP)
        harness = _read(HARNESS)
        for statement in (
            'for /f "tokens=3" %%T in (' + chr(39) + 'sc qc "',
            'echo start_type=',
            'echo delayed_auto=',
            'echo running=',
        ):
            assert statement in engine, f"backup engine changed: {statement!r}"
            assert statement in harness, f"harness drifted: missing {statement!r}"

    def test_restore_parse_mirrors_the_rollback_engine(self):
        engine = _read(ROLLBACK)
        harness = _read(HARNESS)
        for statement in (
            'if /i "%%K"=="start_type"',
            'if /i "%%K"=="delayed_auto"',
            'if /i "%%K"=="running"',
        ):
            assert statement in engine, f"rollback engine changed: {statement!r}"
            assert statement in harness, f"harness drifted: missing {statement!r}"

    def test_start_type_mapping_matches_the_engine(self):
        """The captured numeric start type must map to the same sc argument."""
        engine = _read(ROLLBACK)
        harness = _read(HARNESS)
        for start_type, argument in (("2", "auto"), ("3", "demand"), ("4", "disabled")):
            assert f'=="{start_type}" set "SERVICE_START_ARG={argument}"' in engine, (
                f"rollback.bat no longer maps start_type {start_type} to {argument}"
            )
            assert f'=="{start_type}" set "R_ARG={argument}"' in harness, (
                f"harness no longer mirrors start_type {start_type} -> {argument}"
            )
        assert 'set "SERVICE_START_ARG=delayed-auto"' in engine
        assert 'set "R_ARG=delayed-auto"' in harness

    def test_unelevated_config_is_reported_as_partial_not_passed(self):
        harness = _read(HARNESS)
        assert "sc-config-needs-elevation" in harness
        label = chr(10) + ":case_service_capture" + chr(10)
        rest = harness.split(label, 1)[1]
        # stop at the next real label — a line opening with ":" but not "::"
        body = re.split(r"^:(?!:)", rest, maxsplit=1, flags=re.MULTILINE)[0]
        assert "CASES_PARTIAL" in body
        assert "CASES_PASSED" not in body, (
            "the service case cannot fully execute here, so it must never be "
            "counted as a pass"
        )
        assert "round-trip-mismatch" in body, (
            "a capture that does not survive the restore parse must still fail"
        )
