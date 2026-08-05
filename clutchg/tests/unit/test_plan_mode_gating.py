"""Static proof that plan mode cannot mutate the host.

The Sandbox/VM verification gate needs a way to exercise the batch engine's real
code paths without touching Windows. ``CLUTCHG_DRY_RUN=1`` / ``--plan`` is that
mechanism, but it is only trustworthy if EVERY mutating command sits behind the
plan guard. A single unguarded ``reg add`` would turn a "dry run" into a real
system change — so the guarantee is asserted here rather than assumed.

Reads batch files as text. Executes nothing.
"""

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLAN_AWARE_SCRIPTS = (
    REPO_ROOT / "src" / "backup" / "backup-registry.bat",
    REPO_ROOT / "src" / "safety" / "rollback.bat",
    REPO_ROOT / "src" / "safety" / "flight-recorder.bat",
)

# Commands that change host state. Redirections are excluded: plan mode still
# writes its own plan output, and artifact files live under the backup root.
MUTATING_COMMAND = re.compile(
    r"^\s*("
    r"reg(?:\.exe)?\s+(?:add|delete|import)\b"
    r"|sc\s+config\b"
    r"|sc\s+(?:start|stop)\b"
    r"|bcdedit\s+/(?:import|set|deletevalue)\b"
    r"|powercfg\s+/(?:setactive|setacvalueindex|setdcvalueindex|import)\b"
    r"|net\s+(?:start|stop)\b"
    r")",
    re.IGNORECASE,
)


def _reachable_mutations_in_plan_mode(path: Path) -> list:
    """Mutating lines reachable when PLAN_MODE==1.

    Walks each label block. A ``if "!PLAN_MODE!"=="1" ( ... exit /b )`` block
    makes everything after it in that block unreachable under plan mode, as does
    wrapping a mutation in ``if "!PLAN_MODE!"=="0" (``. Paren depth is tracked so
    a nested if/else inside the plan branch does not end it early.
    """
    lines = path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n").split("\n")
    findings = []
    plan_exited = False
    plan_depth = None
    depth = 0

    for number, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        if re.match(r"^:[A-Za-z_]", stripped):
            plan_exited, plan_depth, depth = False, None, 0
            continue

        if plan_depth is None and re.match(r'if\s+"!PLAN_MODE!"=="1"\s*\($', stripped):
            plan_depth = depth
            depth += 1
            continue

        if plan_depth is not None:
            if re.match(r"exit /b|goto :eof", stripped):
                plan_exited = True
            depth += stripped.count("(") - stripped.count(")")
            if depth <= plan_depth:
                plan_depth = None
            continue

        depth += stripped.count("(") - stripped.count(")")

        if re.match(
            r'if\s+"!PLAN_MODE!"=="1".*(exit /b|goto :eof)', stripped
        ) or re.match(r'if\s+"!PLAN_MODE!"=="0"\s*\(', stripped):
            plan_exited = True
            continue

        if MUTATING_COMMAND.match(raw) and not plan_exited:
            findings.append(f"{path.name}:{number}: {stripped[:90]}")

    return findings


@pytest.mark.unit
class TestPlanModeGating:
    @pytest.mark.parametrize(
        "script", PLAN_AWARE_SCRIPTS, ids=lambda p: p.name
    )
    def test_no_mutation_is_reachable_in_plan_mode(self, script):
        assert script.is_file(), f"missing plan-aware script: {script}"
        leaks = _reachable_mutations_in_plan_mode(script)
        assert not leaks, (
            "these commands could run during a --plan dry run:\n" + "\n".join(leaks)
        )

    @pytest.mark.parametrize(
        "script", PLAN_AWARE_SCRIPTS, ids=lambda p: p.name
    )
    def test_script_honours_both_plan_switches(self, script):
        """A caller may set the env var or pass the flag; both must work."""
        content = script.read_text(encoding="utf-8", errors="ignore")
        assert 'if /i "%CLUTCHG_DRY_RUN%"=="1" set "PLAN_MODE=1"' in content
        assert '--plan' in content

    def test_the_detector_would_catch_an_unguarded_mutation(self, tmp_path):
        """A guard that cannot fail is decoration — prove this one can."""
        hostile = tmp_path / "hostile.bat"
        hostile.write_text(
            "@echo off\r\n"
            ':restore_thing\r\n'
            'if "!PLAN_MODE!"=="1" (\r\n'
            "    echo PLAN|RESTORE|thing\r\n"
            ")\r\n"
            'reg add "HKCU\\Software\\Test" /v X /t REG_DWORD /d 1 /f\r\n',
            encoding="utf-8",
        )
        leaks = _reachable_mutations_in_plan_mode(hostile)
        assert leaks, "detector missed a reg add that plan mode does not guard"
        assert "reg add" in leaks[0]

    def test_the_detector_accepts_a_correctly_guarded_mutation(self, tmp_path):
        safe = tmp_path / "safe.bat"
        safe.write_text(
            "@echo off\r\n"
            ':restore_thing\r\n'
            'if "!PLAN_MODE!"=="1" (\r\n'
            "    echo PLAN|RESTORE|thing\r\n"
            "    exit /b 0\r\n"
            ")\r\n"
            'reg add "HKCU\\Software\\Test" /v X /t REG_DWORD /d 1 /f\r\n',
            encoding="utf-8",
        )
        assert _reachable_mutations_in_plan_mode(safe) == []
