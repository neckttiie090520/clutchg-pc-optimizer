"""No-window lifecycle tests for the update install handoff."""

from pathlib import Path
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gui.components.update_dialog import UpdateDialog


@pytest.mark.unit
class TestUpdateInstallHandoff:
    @staticmethod
    def _dialog(install_result: bool):
        dialog = UpdateDialog.__new__(UpdateDialog)
        dialog._installer_path = Path("ClutchG-Setup-1.0.4.exe")
        dialog._install_handoff_complete = False
        dialog._build_error_state = MagicMock()
        dialog.app = MagicMock()
        dialog.app._async_updater.install.return_value = install_result
        return dialog

    def test_failed_handoff_keeps_application_running(self):
        dialog = self._dialog(False)

        dialog._perform_install_handoff()

        dialog.app.window.destroy.assert_not_called()
        dialog._build_error_state.assert_called_once()
        assert dialog._install_handoff_complete is False

    def test_successful_handoff_closes_application(self):
        dialog = self._dialog(True)

        dialog._perform_install_handoff()

        dialog.app._async_updater.install.assert_called_once_with(
            dialog._installer_path, silent=False
        )
        dialog.app.window.destroy.assert_called_once_with()
        dialog._build_error_state.assert_not_called()
        assert dialog._install_handoff_complete is True

    def test_successful_handoff_is_one_shot(self):
        dialog = self._dialog(True)

        dialog._perform_install_handoff()
        dialog._perform_install_handoff()

        dialog.app._async_updater.install.assert_called_once()
        dialog.app.window.destroy.assert_called_once()


@pytest.mark.unit
class TestShutdownFailureDiagnostics:
    """A failure during shutdown must be logged, not replaced by a NameError."""

    def test_shutdown_failure_is_logged_rather_than_raising(self, caplog):
        dialog = UpdateDialog.__new__(UpdateDialog)
        dialog._installer_path = Path("ClutchG-Setup-1.0.4.exe")
        dialog._install_handoff_complete = False
        dialog._build_error_state = MagicMock()
        dialog.app = MagicMock()
        dialog.app._async_updater.install.return_value = True
        dialog.app.window.destroy.side_effect = RuntimeError("window already gone")

        with caplog.at_level("ERROR"):
            dialog._perform_install_handoff()

        assert dialog._install_handoff_complete is True
        assert "window already gone" in caplog.text
