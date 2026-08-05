"""Static contract that ISO work products do not carry stale measured metrics.

Hand-maintained counts drift silently as the suite grows, and a defense panel
reads those numbers as measurements. These tests recompute the ground truth from
the repository and assert the documents agree. Markdown only; nothing executes.
"""

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
ISO_DIR = REPO_ROOT / "docs" / "iso29110-clutchg"
UNIT_DIR = REPO_ROOT / "clutchg" / "tests" / "unit"
INTEGRATION_DIR = REPO_ROOT / "clutchg" / "tests" / "integration"

# Superseded figures that must not reappear as current-state claims. Revision
# history legitimately records them, so history lines are excluded below.
STALE_TOKENS = ("400+", "496+", "516+", "~65% core", "432+")

# Parametrisation makes the collected count exceed the number of ``def``s. The
# headroom factor bounds that ratio. It is deliberately not documented as a
# point-in-time measurement, because such a figure drifts as tests are added —
# ``test_the_ceiling_is_tight_enough_to_actually_fail`` asserts the bound stays
# meaningful algebraically instead.
COLLECTED_PER_DEFINED_HEADROOM = 1.5

DOCUMENTS = (
    "04-Test-Plan.md",
    "05-Test-Record.md",
    "06-Traceability-Record.md",
    "08-Progress-Status-Record.md",
    "09-Configuration-Plan.md",
)


def _is_history_line(line: str) -> bool:
    """Whether a line records history rather than asserting the current state.

    Revision-history rows and milestone rows legitimately cite superseded figures.
    A progression (``285→372→496+``) is exempted only for the numbers that are
    part of the progression itself — see ``_stale_tokens_in``, which strips the
    arrow-joined run rather than exempting the whole line. Exempting the entire
    line would let a stale current-state claim ride along beside a progression.
    """
    stripped = line.strip()
    if re.match(r"^\|\s*v?\d+\.\d+\s*\|\s*20\d\d-\d\d(-\d\d)?\s*\|", stripped):
        return True
    return bool(re.match(r"^\|\s*M\d+\b", stripped))


# A run of values joined by arrows is a progression, e.g. "285→372→496+".
_PROGRESSION = re.compile(r"[\w.+%]+(?:\s*→\s*[\w.+%]+)+")


def _stale_tokens_in(line: str) -> list:
    """Superseded metrics asserted as current on this line.

    Arrow-joined progressions are removed before matching, so "285→400+" is
    ignored while a bare "400+" elsewhere on the same line is still caught.
    """
    scannable = _PROGRESSION.sub(" ", line)
    return [token for token in STALE_TOKENS if token in scannable]


def _count_test_functions(directory: Path) -> int:
    total = 0
    for path in sorted(directory.glob("test_*.py")):
        source = path.read_text(encoding="utf-8", errors="ignore")
        total += len(re.findall(r"^\s*def (test_\w+)", source, re.MULTILINE))
    return total


@pytest.mark.unit
class TestIsoMetricCurrency:
    @pytest.mark.parametrize("document", DOCUMENTS)
    def test_no_superseded_metric_is_stated_as_current(self, document):
        path = ISO_DIR / document
        assert path.is_file(), f"Missing ISO work product: {document}"

        offenders = []
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if _is_history_line(line):
                continue
            for token in _stale_tokens_in(line):
                offenders.append(f"{document}:{number}: {token}")
        assert not offenders, "Superseded metrics stated as current:\n" + "\n".join(
            offenders
        )

    def test_test_suite_is_large_enough_to_justify_the_recorded_scale(self):
        """Guard against a document claiming a suite far larger than the code."""
        unit_defined = _count_test_functions(UNIT_DIR)
        integration_defined = _count_test_functions(INTEGRATION_DIR)
        assert unit_defined >= 300, unit_defined
        assert integration_defined >= 10, integration_defined

    @pytest.mark.parametrize("document", DOCUMENTS)
    def test_no_recorded_total_exceeds_the_collectable_suite(self, document):
        """A recorded pass count must be achievable by the tests that exist.

        Parametrisation means one ``def`` can yield several collected tests, so the
        defined-function count is a lower bound and an exact match cannot be
        asserted. The bound must still be tight enough to fail, which
        ``test_the_ceiling_is_tight_enough_to_actually_fail`` enforces. A large
        multiplier here would make the assertion decorative.
        """
        collectable_ceiling = int(
            COLLECTED_PER_DEFINED_HEADROOM
            * (_count_test_functions(UNIT_DIR) + _count_test_functions(INTEGRATION_DIR))
        )
        path = ISO_DIR / document
        offenders = []
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if _is_history_line(line):
                continue
            for match in re.finditer(
                r"\b(\d{3,5})\s*(?:tests?|passed|pass\b|collected)", line, re.IGNORECASE
            ):
                if int(match.group(1)) > collectable_ceiling:
                    offenders.append(f"{document}:{number}: {match.group(1)}")
        assert not offenders, (
            f"Recorded totals exceed the collectable ceiling "
            f"({collectable_ceiling}):\n" + "\n".join(offenders)
        )

    def test_the_ceiling_is_tight_enough_to_actually_fail(self):
        """A bound with unlimited headroom is decoration, not a guard.

        This asserts the guard above has teeth: the ceiling must sit within a
        small factor of the real collected count, so a plausible overstatement is
        rejected rather than sailing under an enormous limit.
        """
        defined = _count_test_functions(UNIT_DIR) + _count_test_functions(
            INTEGRATION_DIR
        )
        ceiling = int(COLLECTED_PER_DEFINED_HEADROOM * defined)
        # An overstatement of roughly double the suite must be caught.
        assert ceiling < 2 * defined, (
            f"Ceiling {ceiling} is too loose against {defined} defined tests"
        )


@pytest.mark.unit
class TestGuardDiscriminates:
    """A guard that cannot fail is decoration. These assert it has teeth."""

    _ARROW = "→"

    def test_progression_is_exempt_but_a_stale_claim_beside_it_is_not(self):
        legitimate = f"| Coverage | 39% {self._ARROW} 80% core | current |"
        smuggled = (
            f"| Tests | grew 285 {self._ARROW} 400+ and we now run 400+ | CURRENT |"
        )

        assert _stale_tokens_in(legitimate) == []
        assert _stale_tokens_in(smuggled) == ["400+"], (
            "A stale current-state claim must not be exempted just because a "
            "progression appears on the same line"
        )

    def test_revision_history_rows_are_exempt(self):
        assert _is_history_line("| v2.1 | 2026-04-10 | nextzus | 400+ tests |") is True
        assert _is_history_line("| Current | 400+ tests | |") is False

    def test_bare_stale_token_is_caught(self):
        assert _stale_tokens_in("| Current | 400+ tests | |") == ["400+"]
