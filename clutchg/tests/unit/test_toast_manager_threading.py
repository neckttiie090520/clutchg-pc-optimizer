"""Unit tests for ToastManager main-thread marshalling."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gui.components.toast import ToastManager


class QueuedParent:
    """Minimal Tk parent that records after callbacks without running them."""

    def __init__(self):
        self.callbacks = []

    def after(self, delay, callback, *args):
        self.callbacks.append((delay, callback, args))

    def run_next(self):
        delay, callback, args = self.callbacks.pop(0)
        assert delay == 0
        callback(*args)


class FakeToast:
    """Toast double that records construction and repositioning."""

    def __init__(
        self,
        parent,
        message,
        toast_type,
        duration,
        y_offset,
        on_close,
    ):
        self.parent = parent
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.y_offset = y_offset
        self.on_close = on_close
        self.positions = []

    def get_height(self):
        return 54

    def position_toast(self, y_offset):
        self.positions.append(y_offset)


@pytest.mark.unit
class TestToastManagerThreadMarshalling:
    def test_show_waits_for_parent_after_before_state_or_widget_access(self):
        parent = QueuedParent()
        manager = ToastManager(parent)

        with patch("gui.components.toast.ToastNotification", FakeToast):
            manager.info("Queued message", duration=1234)

            assert manager._active == []
            assert len(parent.callbacks) == 1

            parent.run_next()

        assert len(manager._active) == 1
        toast = manager._active[0]
        assert toast.message == "Queued message"
        assert toast.toast_type == "info"
        assert toast.duration == 1234
        assert toast.y_offset == 0

    def test_remove_waits_for_parent_after_before_mutating_or_repositioning(self):
        parent = QueuedParent()
        manager = ToastManager(parent)

        with patch("gui.components.toast.ToastNotification", FakeToast):
            manager.success("First")
            manager.warning("Second")
            parent.run_next()
            parent.run_next()

        first, second = manager._active
        assert second.y_offset == 64

        manager._remove(first)

        assert manager._active == [first, second]
        assert second.positions == []

        parent.run_next()

        assert manager._active == [second]
        assert second.positions == [0]
