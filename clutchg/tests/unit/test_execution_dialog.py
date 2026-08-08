"""
Unit tests for execution dialog generic job title resolution.
"""

import pytest
import sys
import threading
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gui.components.execution_dialog import ExecutionDialog


@pytest.mark.unit
class TestExecutionDialog:

    def test_resolve_job_title_from_profile_like_object(self):
        class ProfileLike:
            display_name = "Safe Mode"

        assert ExecutionDialog.resolve_job_title(ProfileLike()) == "Safe Mode"

    def test_resolve_job_title_from_name_object(self):
        class NamedJob:
            name = "Quick Action"

        assert ExecutionDialog.resolve_job_title(NamedJob()) == "Quick Action"

    def test_resolve_job_title_from_string(self):
        assert ExecutionDialog.resolve_job_title("Custom (4 tweaks)") == "Custom (4 tweaks)"

    def test_cancel_sets_early_event_before_active_job_callback(self):
        dialog = ExecutionDialog.__new__(ExecutionDialog)
        dialog.is_complete = False
        dialog._cancel_event = threading.Event()
        dialog.add_output = MagicMock()
        dialog.cancel_btn = MagicMock()
        observed = []
        dialog._cancel_handler = lambda: observed.append(dialog.cancellation_event.is_set())

        dialog.on_cancel()

        assert dialog.cancellation_event.is_set()
        assert observed == [True]
        dialog.cancel_btn.configure.assert_called_once_with(
            state="disabled", text="Cancelling..."
        )

    def test_all_execution_views_forward_the_early_cancel_event(self):
        repo_root = Path(__file__).resolve().parents[3]
        profiles_view = (repo_root / "clutchg/src/gui/views/profiles_minimal.py").read_text(
            encoding="utf-8"
        )
        scripts_view = (repo_root / "clutchg/src/gui/views/scripts_minimal.py").read_text(
            encoding="utf-8"
        )

        marker = "cancellation_event=dialog.cancellation_event"
        assert profiles_view.count(marker) == 1
        assert scripts_view.count(marker) == 3


@pytest.mark.unit
class TestThreadMarshallingInvariant:
    """Every worker-facing callback must marshal onto Tk's main thread.

    Tkinter is single-threaded: only the main thread may touch widgets. Profile
    and tweak application run on ``threading.Thread(daemon=True)`` workers that
    call these methods directly, so each one must re-post itself via ``after()``
    when invoked off-thread. A future callback added without the guard would
    corrupt or crash the UI intermittently, which is exactly the failure mode
    that is hardest to reproduce — so the invariant is pinned statically here.
    """

    WORKER_FACING = (
        "add_output",
        "set_progress",
        "add_tweak_status",
        "show_result",
        "show_diff",
    )

    @staticmethod
    def _source() -> str:
        path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "gui"
            / "components"
            / "execution_dialog.py"
        )
        return path.read_text(encoding="utf-8")

    @pytest.mark.parametrize("method", WORKER_FACING)
    def test_callback_reposts_itself_when_called_off_the_main_thread(self, method):
        source = self._source()
        marker = f"    def {method}("
        assert marker in source, f"{method} is missing from ExecutionDialog"

        body = source.split(marker, 1)[1].split("\n    def ", 1)[0]
        assert "threading.current_thread() is not threading.main_thread()" in body, (
            f"{method} does not check whether it is on the main thread"
        )
        assert f"self.after(0, lambda: self.{method}(" in body, (
            f"{method} does not re-post itself onto the main thread"
        )
        guard_index = body.index("threading.current_thread()")
        assert "return" in body[guard_index:guard_index + 200], (
            f"{method} must return after re-posting, not fall through to widget work"
        )

    def test_toast_manager_marshals_rather_than_touching_widgets_directly(self):
        """Workers call ``app.toast.*`` directly, so ToastManager must marshal."""
        path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "gui"
            / "components"
            / "toast.py"
        )
        source = path.read_text(encoding="utf-8")

        assert "def _run_on_main_thread(self, callback, *args):" in source
        assert "self.parent.after(0, callback, *args)" in source
        show_body = source.split("    def _show(", 1)[1].split("\n    def ", 1)[0]
        assert "_run_on_main_thread(" in show_body, (
            "ToastManager._show must marshal; workers call it off-thread"
        )
