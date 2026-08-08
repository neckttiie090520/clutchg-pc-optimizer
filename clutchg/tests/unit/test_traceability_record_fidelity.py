"""Static contract that the ISO 29110 traceability record cites real evidence.

The traceability record is submitted as a work product, so a row naming a test
file that does not exist is an audit defect even though no code is broken. This
test reads Markdown and never executes anything.
"""

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RECORD = REPO_ROOT / "docs" / "iso29110-clutchg" / "06-Traceability-Record.md"
TESTS_ROOT = REPO_ROOT / "clutchg" / "tests"

_TABLE_ROW = re.compile(r"^\|\s*(test_\w+\.py)\s*\|\s*(\d+)\s*\|")


def _cited_rows():
    """Yield (test_file, claimed_count) for each traceability table row."""
    rows = []
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        match = _TABLE_ROW.match(line.strip())
        if match:
            rows.append((match.group(1), int(match.group(2))))
    return rows


CITED_ROWS = _cited_rows()


@pytest.mark.unit
class TestTraceabilityRecordFidelity:
    def test_record_exists_and_cites_tests(self):
        assert RECORD.is_file()
        assert len(CITED_ROWS) >= 15

    @pytest.mark.parametrize(
        "test_file", [pytest.param(name, id=name) for name, _ in CITED_ROWS]
    )
    def test_every_cited_test_file_exists(self, test_file):
        matches = list(TESTS_ROOT.rglob(test_file))
        assert matches, f"Traceability record cites a missing test file: {test_file}"

    @pytest.mark.parametrize(
        "test_file,claimed",
        [pytest.param(name, count, id=name) for name, count in CITED_ROWS],
    )
    def test_claimed_test_count_is_supported_by_the_file(self, test_file, claimed):
        """The record must not claim tests a file cannot produce.

        Parametrised cases make one ``def`` yield several collected tests, so the
        defined-function count is a lower bound, not the collected total. The
        defensible contract is therefore: the file must define at least one test,
        and a file with no parametrisation must not be credited with more tests
        than it defines.
        """
        matches = list(TESTS_ROOT.rglob(test_file))
        if not matches:
            pytest.skip("Missing file is reported by the existence test")
        source = matches[0].read_text(encoding="utf-8", errors="ignore")
        defined = len(re.findall(r"^\s*def (test_\w+)", source, re.MULTILINE))
        assert defined > 0, f"{test_file} defines no test functions"

        if "parametrize" not in source:
            assert claimed <= defined, (
                f"{test_file} defines {defined} test functions and is not "
                f"parametrised, but the record claims {claimed}"
            )
