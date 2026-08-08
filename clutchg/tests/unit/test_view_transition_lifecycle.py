"""Lifecycle contract for ViewTransition's widget-existence check.

``winfo_exists()`` returns 0 for a destroyed widget rather than raising, so its
result must be inspected. An earlier version called it and discarded the value,
returning True unconditionally — a destroyed view was reported as present and the
caller then called ``destroy()`` on it a second time.

These tests use a stub rather than a real Tk window so they run headless in CI.
"""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gui.components.view_transition import ViewTransition


class _Widget:
    """Minimal stand-in for a Tk widget's existence protocol."""

    def __init__(self, exists: int = 1):
        self._exists = exists

    def winfo_exists(self) -> int:
        return self._exists


class _DeadInterpreter:
    """A widget whose interpreter has gone away, as during app shutdown."""

    def winfo_exists(self):
        raise RuntimeError("main thread is not in main loop")


def _transition(widget) -> ViewTransition:
    transition = ViewTransition.__new__(ViewTransition)
    transition.current_widget = widget
    return transition


@pytest.mark.unit
class TestCurrentViewExists:
    def test_no_widget_reports_absent(self):
        assert _transition(None).current_view_exists() is False

    def test_live_widget_reports_present(self):
        assert _transition(_Widget(exists=1)).current_view_exists() is True

    def test_destroyed_widget_reports_absent(self):
        """The regression: winfo_exists() returns 0 without raising."""
        assert _transition(_Widget(exists=0)).current_view_exists() is False

    def test_dead_interpreter_reports_absent(self):
        assert _transition(_DeadInterpreter()).current_view_exists() is False

    def test_result_is_a_bool_not_a_tk_int(self):
        """Callers branch on this, so it must not leak Tcl's 0/1 ints."""
        assert _transition(_Widget(exists=1)).current_view_exists() is True
        assert _transition(_Widget(exists=0)).current_view_exists() is False
