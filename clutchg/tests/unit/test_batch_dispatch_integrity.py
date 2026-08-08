"""Static dispatch-integrity contracts for the batch engine and tweak registry.

Every test here reads batch files and registry metadata as text or data. None of
them starts CMD and none of them mutates Windows.

They exist because four defects reached the repository undetected:

* ``validation/benchmark-runner.bat`` shipped a malformed guard
  (``if "%~1":"compare_results"`` instead of ``if "%~1"=="compare_results"``).
  CMD aborts the whole dispatch block on that line, so every route declared at
  or after it answers ``goto was unexpected at this time`` instead of running.
* ``optimizer.bat`` invoked that module with a colon-prefixed route
  (``":run_benchmark"``) the module never accepted, so the benchmark would fall
  through to ``:usage`` even once the malformed guard was repaired.
* ``core/gpu-optimizer-enhanced.bat`` and ``core/power-manager-enhanced.bat``
  carried security-reducing registry writes that no route and no ``call`` could
  reach, and that no rollback path could undo.
* ``core/tweak_registry.py`` advertised ``bat_function`` entry points that do
  not exist in the script each entry names.

The reachability model matches how CMD actually resolves work: a label counts as
reachable when a dispatch route names it, or when a reachable label ``call``s or
``goto``s it. That deliberately accepts labels invoked only through an aggregate
route such as ``:apply_all_enhanced``.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.tweak_registry import get_tweak_registry  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[3]
BATCH_ROOT = REPO_ROOT / "src"

# ``call "%CORE_DIR%\\module.bat" ":route"`` is the only way optimizer.bat reaches
# a module, so caller/callee agreement can only be checked once these resolve.
DIR_VARS = {
    "SCRIPT_DIR": BATCH_ROOT,
    "CORE_DIR": BATCH_ROOT / "core",
    "PROFILES_DIR": BATCH_ROOT / "profiles",
    "SAFETY_DIR": BATCH_ROOT / "safety",
    "BACKUP_DIR": BATCH_ROOT / "backup",
    "LOGGING_DIR": BATCH_ROOT / "logging",
    "VALIDATION_DIR": BATCH_ROOT / "validation",
}

# Scratch names that must never ship inside the engine: BatchParser discovers
# scripts with rglob("*.bat") and has no exclude list, so any stray file becomes
# a user-visible script in the GUI.
SCRATCH_NAME_RE = re.compile(r"(?i)^(?:test|tmp|temp|scratch|debug|copy of|new )")

# Security-reducing writes that must not exist anywhere in the engine. Each one
# weakens a hardware or kernel mitigation and has no rollback counterpart, so a
# reachable version would violate the reversibility constraint outright.
FORBIDDEN_MUTATIONS = {
    "VBS / Device Guard": re.compile(r"(?i)EnableVirtualizationBasedSecurity"),
    "HVCI": re.compile(r"(?i)HypervisorEnforcedCodeIntegrity"),
    "System Guard launch": re.compile(r"(?i)ConfigureSystemGuardLaunch"),
    "Spectre/Meltdown mitigations": re.compile(r"(?i)FeatureSettingsOverride"),
}

MUTATION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"^\s*reg\s+(?:add|delete|import)\b",
        r"^\s*powercfg\s+/(?:setacvalueindex|setdcvalueindex|setactive|hibernate"
        r"|change|import|restoredefaultschemes|duplicatescheme|delete)\b",
        r"^\s*bcdedit\s+/(?:set|deletevalue|import)\b",
        r"^\s*netsh\b.*\bset\b",
        r"^\s*fsutil\s+behavior\s+set\b",
        r"^\s*sc\s+(?:config|stop|start)\b",
        r"^\s*net\s+(?:start|stop)\b",
        r"^\s*(?:powershell|dism)\b.*"
        r"(?:Set-|Enable-|Disable-|Remove-|/enable-feature|/disable-feature)",
        r"^\s*(?:takeown|icacls)\b",
    )
)

LABEL_RE = re.compile(r"(?m)^[ \t]*:([A-Za-z_][A-Za-z0-9_]*)[ \t]*$")

# A dispatch attempt is any ``if`` that jumps. Detecting the attempt separately
# from validating its shape is what makes the malformed-guard defect visible:
# ``if "%~1":"compare_results" goto :compare_results`` reads as a dispatch line
# but satisfies no legal CMD comparison.
DISPATCH_ATTEMPT_RE = re.compile(r"(?i)^[ \t]*if\b.*\bgoto\b")

# One legal condition. CMD allows these to be chained (``if A if B goto :x``),
# so the guard check requires a legal condition immediately after every ``if``
# rather than a single condition before the ``goto``.
CONDITION = r"""
    (?:/i[ \t]+)?
    (?:not[ \t]+)?
    (?:
        "[^"]*"[ \t]*==[ \t]*"[^"]*"
      | defined[ \t]+\w+
      | errorlevel[ \t]+\d+
      | exist[ \t]+\S+
      | [^"\s]+[ \t]*==[ \t]*[^"\s]+
    )
"""

WELLFORMED_GUARD_RE = re.compile(
    rf"""(?ix)
    ^[ \t]*if[ \t]+ {CONDITION}
    (?:[ \t]+if[ \t]+ {CONDITION} )*
    [ \t]+\(?[ \t]*goto[ \t]*:\w+
    """
)

# Both operand orders appear in the engine, so routes are collected from either.
ROUTE_RES = (
    re.compile(
        r'(?i)^[ \t]*if[ \t]+(?:/i[ \t]+)?"(?:%~1|%COMMAND%|!COMMAND!)"[ \t]*=='
        r'[ \t]*"([^"]*)"[ \t]+\(?[ \t]*goto[ \t]*:(\w+)'
    ),
    re.compile(
        r'(?i)^[ \t]*if[ \t]+(?:/i[ \t]+)?"([^"]*)"[ \t]*=='
        r'[ \t]*"(?:%~1|%COMMAND%|!COMMAND!)"[ \t]+\(?[ \t]*goto[ \t]*:(\w+)'
    ),
)

EDGE_RE = re.compile(r"(?i)\b(?:call|goto)[ \t]+:([A-Za-z_][A-Za-z0-9_]*)")

CALL_MODULE_RE = re.compile(
    r'(?i)\bcall[ \t]+"([^"]*\.bat)"(?:[ \t]+"([^"]*)"|[ \t]+([^\s"&|)]+))?'
)


def _batch_files():
    return sorted(BATCH_ROOT.rglob("*.bat"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _is_comment(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("::") or stripped[:4].lower() == "rem "


def _code_lines(content: str):
    """Yield ``(line_number, line)`` for executable lines only."""
    for number, line in enumerate(content.split("\n"), start=1):
        if not _is_comment(line):
            yield number, line


def _labels(content: str) -> dict:
    """Map lowercase label name to its match position."""
    return {m.group(1).lower(): m.start() for m in LABEL_RE.finditer(content)}


def _label_blocks(content: str) -> dict:
    """Map lowercase label name to the text between it and the next label."""
    matches = list(LABEL_RE.finditer(content))
    blocks = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        blocks[match.group(1).lower()] = content[match.end():end]
    return blocks


def _preamble(content: str) -> str:
    """Text before the first label: the implicit entry path of a module."""
    first = LABEL_RE.search(content)
    return content[: first.start()] if first else content


def _routes(content: str) -> dict:
    """Map the accepted argument literal to the label it jumps to."""
    routes = {}
    for _, line in _code_lines(content):
        for pattern in ROUTE_RES:
            match = pattern.match(line)
            if match:
                routes[match.group(1)] = match.group(2).lower()
                break
    return routes


def _edges(text: str) -> set:
    """Labels reached by ``call``/``goto`` from executable lines of *text*."""
    found = set()
    for _, line in _code_lines(text):
        for match in EDGE_RE.finditer(line):
            target = match.group(1).lower()
            if target != "eof":
                found.add(target)
    return found


def _reachable_labels(content: str) -> set:
    """Transitive closure of labels CMD can actually enter."""
    blocks = _label_blocks(content)
    frontier = set(_routes(content).values()) | _edges(_preamble(content))
    reachable = set()
    while frontier:
        label = frontier.pop()
        if label in reachable or label not in blocks:
            continue
        reachable.add(label)
        frontier |= _edges(blocks[label])
    return reachable


def _mutates(block: str) -> bool:
    return any(
        pattern.search(line)
        for _, line in _code_lines(block)
        for pattern in MUTATION_PATTERNS
    )


def _resolve_module_path(raw: str, caller: Path):
    """Resolve a quoted ``call`` target into a path, or None if undecidable.

    ``%~dp0`` expands to the directory of the script performing the call, so it
    must be resolved against *caller* rather than the engine root.
    """
    resolved = raw
    for name, path in DIR_VARS.items():
        resolved = resolved.replace(f"%{name}%", str(path))
    resolved = resolved.replace("%~dp0", str(caller.parent) + "\\")
    if "%" in resolved or "!" in resolved:
        return None
    candidate = Path(resolved.replace("\\", "/"))
    if not candidate.is_absolute():
        candidate = caller.parent / candidate
    try:
        return candidate.resolve()
    except OSError:
        return None


@pytest.fixture(scope="module")
def batch_sources():
    return {path: _read(path) for path in _batch_files()}


@pytest.mark.unit
class TestDispatchGuardSyntax:
    """A malformed guard silently disables every route below it."""

    def test_every_dispatch_guard_is_a_legal_cmd_comparison(self, batch_sources):
        violations = []
        for path, content in batch_sources.items():
            for number, line in _code_lines(content):
                if DISPATCH_ATTEMPT_RE.match(line) and not WELLFORMED_GUARD_RE.match(
                    line
                ):
                    violations.append(f"{_rel(path)}:{number}: {line.strip()}")
        assert violations == [], "Malformed dispatch guards:\n" + "\n".join(violations)

    def test_every_dispatch_route_targets_an_existing_label(self, batch_sources):
        violations = []
        for path, content in batch_sources.items():
            labels = _labels(content)
            for argument, target in _routes(content).items():
                if target not in labels:
                    violations.append(
                        f"{_rel(path)}: route {argument!r} -> missing :{target}"
                    )
        assert violations == [], "Dangling dispatch routes:\n" + "\n".join(violations)


@pytest.mark.unit
class TestModuleInvocationAgreement:
    """The engine mixes bare and colon-prefixed routes, so callers must match."""

    def test_every_module_call_passes_an_accepted_route(self, batch_sources):
        violations = []
        for path, content in batch_sources.items():
            for number, line in _code_lines(content):
                for match in CALL_MODULE_RE.finditer(line):
                    argument = match.group(2) or match.group(3)
                    if not argument or argument.startswith("-"):
                        continue
                    target = _resolve_module_path(match.group(1), path)
                    if target is None or not target.is_file():
                        continue
                    routes = _routes(batch_sources.get(target, _read(target)))
                    if not routes:
                        continue
                    accepted = {route.lower() for route in routes}
                    if argument.lower() not in accepted:
                        violations.append(
                            f"{_rel(path)}:{number}: {target.name} rejects "
                            f"{argument!r}; accepts {sorted(routes)}"
                        )
        assert violations == [], "Unroutable module calls:\n" + "\n".join(violations)

    def test_every_module_call_targets_an_existing_script(self, batch_sources):
        violations = []
        for path, content in batch_sources.items():
            for number, line in _code_lines(content):
                for match in CALL_MODULE_RE.finditer(line):
                    target = _resolve_module_path(match.group(1), path)
                    if target is not None and not target.is_file():
                        violations.append(
                            f"{_rel(path)}:{number}: missing {match.group(1)}"
                        )
        assert violations == [], "Calls to absent scripts:\n" + "\n".join(violations)


@pytest.mark.unit
class TestNoUnreachableMutations:
    """Unreachable mutating code is either a dead claim or a latent hazard."""

    def test_no_mutating_label_is_unreachable(self, batch_sources):
        violations = []
        for path, content in batch_sources.items():
            reachable = _reachable_labels(content)
            for label, block in _label_blocks(content).items():
                if label not in reachable and _mutates(block):
                    violations.append(f"{_rel(path)}: :{label}")
        assert violations == [], (
            "Unreachable mutating labels (delete them or route them with a "
            "rollback path):\n" + "\n".join(violations)
        )

    @pytest.mark.parametrize("description", sorted(FORBIDDEN_MUTATIONS))
    def test_security_reducing_mutation_is_absent(self, description, batch_sources):
        pattern = FORBIDDEN_MUTATIONS[description]
        hits = [
            f"{_rel(path)}:{number}: {line.strip()}"
            for path, content in batch_sources.items()
            for number, line in _code_lines(content)
            if pattern.search(line)
        ]
        assert hits == [], (
            f"{description} must not be weakened by the engine:\n" + "\n".join(hits)
        )


@pytest.mark.unit
class TestEngineHygiene:
    def test_no_scratch_batch_files_ship_in_the_engine(self):
        strays = [
            _rel(path) for path in _batch_files() if SCRATCH_NAME_RE.match(path.stem)
        ]
        assert strays == [], (
            "BatchParser discovers every .bat under src/, so scratch files "
            "surface in the GUI:\n" + "\n".join(strays)
        )


@pytest.mark.unit
class TestTweakRegistryTraceability:
    """Registry metadata is the thesis traceability claim; it must resolve."""

    @pytest.fixture(scope="class")
    def routed_tweaks(self):
        return [
            tweak
            for tweak in get_tweak_registry().get_all_tweaks()
            if tweak.bat_script and tweak.bat_function
        ]

    def test_every_declared_script_exists(self, routed_tweaks):
        violations = [
            f"{tweak.id}: {tweak.bat_script}"
            for tweak in routed_tweaks
            if not (BATCH_ROOT / tweak.bat_script).is_file()
        ]
        assert violations == [], "Registry names absent scripts:\n" + "\n".join(
            violations
        )

    def test_every_declared_entry_point_exists(self, routed_tweaks, batch_sources):
        violations = []
        for tweak in routed_tweaks:
            script = BATCH_ROOT / tweak.bat_script
            if not script.is_file():
                continue
            content = batch_sources.get(script, _read(script))
            label = tweak.bat_function.lstrip(":").lower()
            if label not in _labels(content):
                violations.append(
                    f"{tweak.id}: {tweak.bat_script} has no {tweak.bat_function}"
                )
        assert violations == [], "Registry names absent labels:\n" + "\n".join(
            violations
        )

    def test_every_declared_entry_point_is_reachable(self, routed_tweaks, batch_sources):
        violations = []
        for tweak in routed_tweaks:
            script = BATCH_ROOT / tweak.bat_script
            if not script.is_file():
                continue
            content = batch_sources.get(script, _read(script))
            label = tweak.bat_function.lstrip(":").lower()
            if label in _labels(content) and label not in _reachable_labels(content):
                violations.append(
                    f"{tweak.id}: {tweak.bat_script} cannot reach "
                    f"{tweak.bat_function}"
                )
        assert violations == [], "Registry names unreachable labels:\n" + "\n".join(
            violations
        )
