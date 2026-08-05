"""Static fidelity contracts between tweak knowledge records and batch scripts.

Every user-facing claim in ``tweak_registry.py`` is read by the GUI and by the
thesis documentation, so a claim that the batch engine does not implement is a
truthfulness defect even when nothing crashes. These tests read batch files as
text; they never execute CMD and never mutate Windows.
"""

from pathlib import Path
import re
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.tweak_registry import get_tweak_registry

REPO_ROOT = Path(__file__).resolve().parents[3]
BATCH_ROOT = REPO_ROOT / "src"

_HIVES = ("HKLM", "HKCU", "HKU", "HKCR", "HKCC")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")


def _label_body(content: str, label: str) -> str:
    """Return the text of one label block, up to the next label definition."""
    marker = f"\n{label}\n"
    if marker not in content:
        return ""
    tail = content.split(marker, 1)[1]
    return re.split(r"\n:(?!:)", tail, maxsplit=1)[0]


def _written_keys(body: str) -> set:
    r"""Collect registry keys the block writes, normalised to HIVE\path.

    Three forms occur in this engine: a direct ``reg add``/``reg delete``; a
    helper call such as ``call :reg_set "HKCU\..." "Value" "REG_DWORD" "0"``; and
    a service reconfiguration (``sc config <name> start= disabled``), which the
    Service Control Manager persists under that service's own key. Missing any
    form would let the fidelity check pass by seeing nothing rather than by
    agreeing with the record.
    """
    keys = set()
    for match in re.finditer(
        r'reg(?:\.exe)?\s+(?:add|delete)\s+"([^"]+)"', body, re.IGNORECASE
    ):
        keys.add(match.group(1).strip().upper())
    for match in re.finditer(
        r'call\s+:\w+\s+"((?:HKLM|HKCU|HKU|HKCR|HKCC)[\\][^"]*)"', body, re.IGNORECASE
    ):
        keys.add(match.group(1).strip().upper())
    keys |= _service_keys(body)
    return keys


_SERVICE_KEY_PREFIX = "HKLM\\SYSTEM\\CURRENTCONTROLSET\\SERVICES\\"


def _service_keys(body: str) -> set:
    """Service keys the block reconfigures via the Service Control Manager.

    ``sc config <name> start= disabled`` persists to
    ``HKLM\\SYSTEM\\CurrentControlSet\\Services\\<name>``, so a record naming
    that key is accurate even though no ``reg add`` appears.
    """
    names = set(re.findall(r"\bsc\s+config\s+\"?([\w.-]+)\"?", body, re.IGNORECASE))
    # Helper wrappers take the service name as their first quoted argument.
    for match in re.finditer(
        r"\bcall\s+:\w*(?:service|svc)\w*\s+\"([\w.-]+)\"", body, re.IGNORECASE
    ):
        names.add(match.group(1))
    resolved = {name for name in names if not name.startswith("%")}
    return {f"{_SERVICE_KEY_PREFIX}{name.upper()}" for name in resolved}


def _registry_tweaks():
    """Tweaks that declare registry keys and route to a resolvable batch label.

    A tweak whose label writes no keys at all is NOT dropped here. Dropping it
    was the original defect: a record could declare a key, route to a label that
    writes nothing, and be reported as passing because it was never compared.
    Such a tweak is emitted with an empty ``written_keys`` so the comparison
    fails loudly.
    """
    selected = []
    for tweak in get_tweak_registry().get_all_tweaks():
        if not tweak.registry_keys or not tweak.bat_script or not tweak.bat_function:
            continue
        script = BATCH_ROOT / tweak.bat_script
        if not script.is_file():
            continue
        body = _label_body(_read(script), tweak.bat_function)
        if not body:
            continue
        selected.append(pytest.param(tweak, _written_keys(body), id=tweak.id))
    return selected


REGISTRY_TWEAKS = _registry_tweaks()


@pytest.mark.unit
class TestRegistryClaimFidelity:
    def test_registry_tweaks_were_discovered(self):
        """Guard the harness itself: a parser regression must not silently pass."""
        assert len(REGISTRY_TWEAKS) >= 10

    def test_every_registry_declaring_tweak_is_actually_compared(self):
        """A parser that sees nothing passes vacuously — hold it to its subjects.

        An earlier version of ``_written_keys`` carried a broken escape in the
        helper-call pattern, so it matched nothing and silently compared only 13
        of the 28 records that declare registry keys. Every record it skipped was
        reported as passing. A later version still dropped a tweak whose label
        wrote no keys at all. The floor is therefore exact: every record that
        declares a key and routes to a real label must be compared.
        """
        declaring = [
            tweak
            for tweak in get_tweak_registry().get_all_tweaks()
            if tweak.registry_keys
        ]
        compared = {param.values[0].id for param in REGISTRY_TWEAKS}
        skipped = sorted(t.id for t in declaring if t.id not in compared)
        assert not skipped, (
            f"{len(compared)} of {len(declaring)} registry-declaring tweaks are "
            f"compared; silently skipped: {skipped}"
        )

    @pytest.mark.parametrize("tweak,written_keys", REGISTRY_TWEAKS)
    def test_declared_hive_matches_the_hive_the_script_writes(
        self, tweak, written_keys
    ):
        """A record must not claim a machine-wide scope for a per-user write."""
        written_hives = {
            key.split("\\", 1)[0] for key in written_keys if key.startswith(_HIVES)
        }
        declared_hives = {
            key.upper().split("\\", 1)[0]
            for key in tweak.registry_keys
            if key.upper().startswith(_HIVES)
        }
        if not declared_hives or not written_hives:
            pytest.skip("No comparable hive declaration for this tweak")
        assert declared_hives <= written_hives, (
            f"{tweak.id} declares {sorted(declared_hives)} but "
            f"{tweak.bat_function} writes {sorted(written_hives)}"
        )

    @pytest.mark.parametrize("tweak,written_keys", REGISTRY_TWEAKS)
    def test_declared_keys_are_actually_written(self, tweak, written_keys):
        """Each declared key must appear as a key the routed block writes."""
        for declared in tweak.registry_keys:
            normalised = declared.upper().replace("/", "\\")
            if not normalised.startswith(_HIVES):
                continue
            assert any(
                written == normalised or written.startswith(normalised + "\\")
                for written in written_keys
            ), (
                f"{tweak.id} declares '{declared}' but {tweak.bat_function} "
                f"writes {sorted(written_keys)}"
            )
