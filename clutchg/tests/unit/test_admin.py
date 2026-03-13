"""
Unit Tests for AdminChecker (utils/admin.py)

Tests is_admin() and request_elevation() without touching real UAC or
launching real processes. All OS/ctypes calls are mocked.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.admin import AdminChecker


# ---------------------------------------------------------------------------
# is_admin
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsAdmin:

    def test_returns_true_when_admin(self):
        checker = AdminChecker()
        with patch("ctypes.windll") as mock_windll:
            mock_windll.shell32.IsUserAnAdmin.return_value = 1
            assert checker.is_admin() is True

    def test_returns_false_when_not_admin(self):
        checker = AdminChecker()
        with patch("ctypes.windll") as mock_windll:
            mock_windll.shell32.IsUserAnAdmin.return_value = 0
            assert checker.is_admin() is False

    def test_returns_false_on_exception(self):
        checker = AdminChecker()
        with patch("ctypes.windll") as mock_windll:
            mock_windll.shell32.IsUserAnAdmin.side_effect = OSError("no windll")
            assert checker.is_admin() is False

    def test_non_zero_values_are_truthy(self):
        """Any non-zero value from IsUserAnAdmin should count as admin."""
        checker = AdminChecker()
        with patch("ctypes.windll") as mock_windll:
            mock_windll.shell32.IsUserAnAdmin.return_value = 42
            assert checker.is_admin() is True


# ---------------------------------------------------------------------------
# request_elevation — already admin
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRequestElevationAlreadyAdmin:

    def test_returns_true_if_already_admin(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=True):
            assert checker.request_elevation() is True

    def test_does_not_call_shellexecute_if_admin(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=True), \
             patch("ctypes.windll") as mock_windll:
            checker.request_elevation()
            mock_windll.shell32.ShellExecuteW.assert_not_called()


# ---------------------------------------------------------------------------
# request_elevation — UAC accepted (ret > 32)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRequestElevationUACAccepted:

    def test_calls_shellexecute_with_runas(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("sys.exit") as mock_exit, \
             patch("subprocess.list2cmdline", return_value="script.py"):
            mock_windll.shell32.ShellExecuteW.return_value = 33  # > 32 = success
            checker.request_elevation()
            mock_windll.shell32.ShellExecuteW.assert_called_once()
            call_args = mock_windll.shell32.ShellExecuteW.call_args[0]
            assert "runas" in call_args

    def test_exits_current_process_on_uac_success(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("sys.exit") as mock_exit, \
             patch("subprocess.list2cmdline", return_value="script.py"):
            mock_windll.shell32.ShellExecuteW.return_value = 33
            checker.request_elevation()
            mock_exit.assert_called_once_with(0)


# ---------------------------------------------------------------------------
# request_elevation — UAC denied (ret <= 32)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRequestElevationUACDenied:

    def test_returns_false_when_uac_denied(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("subprocess.list2cmdline", return_value="script.py"):
            mock_windll.shell32.ShellExecuteW.return_value = 2  # <= 32 = denied
            result = checker.request_elevation()
            assert result is False

    def test_does_not_exit_when_uac_denied(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("sys.exit") as mock_exit, \
             patch("subprocess.list2cmdline", return_value="script.py"):
            mock_windll.shell32.ShellExecuteW.return_value = 5
            checker.request_elevation()
            mock_exit.assert_not_called()

    def test_boundary_ret_32_is_denied(self):
        """ShellExecuteW ret == 32 is still a failure (must be > 32)."""
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("subprocess.list2cmdline", return_value="script.py"):
            mock_windll.shell32.ShellExecuteW.return_value = 32
            result = checker.request_elevation()
            assert result is False

    def test_boundary_ret_33_is_success(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("sys.exit"), \
             patch("subprocess.list2cmdline", return_value="script.py"):
            mock_windll.shell32.ShellExecuteW.return_value = 33
            # Should call sys.exit(0) — no return value check since it exits
            # Just verify it doesn't raise
            checker.request_elevation()


# ---------------------------------------------------------------------------
# request_elevation — exception path
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRequestElevationException:

    def test_returns_false_on_exception(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll:
            mock_windll.shell32.ShellExecuteW.side_effect = OSError("ctypes failure")
            result = checker.request_elevation()
            assert result is False

    def test_logs_error_on_exception(self):
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("utils.admin.logger") as mock_logger:
            mock_windll.shell32.ShellExecuteW.side_effect = RuntimeError("fail")
            checker.request_elevation()
            mock_logger.error.assert_called_once()


# ---------------------------------------------------------------------------
# list2cmdline integration (params quoting)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestParamsQuoting:

    def test_list2cmdline_used_for_params(self):
        """Verify subprocess.list2cmdline is called to build the params string."""
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("sys.exit"), \
             patch("subprocess.list2cmdline", return_value="fake params") as mock_l2c:
            mock_windll.shell32.ShellExecuteW.return_value = 33
            checker.request_elevation()
            mock_l2c.assert_called_once()

    def test_params_passed_to_shellexecute(self):
        """The quoted params string must appear as the 4th ShellExecuteW arg."""
        checker = AdminChecker()
        with patch.object(checker, "is_admin", return_value=False), \
             patch("ctypes.windll") as mock_windll, \
             patch("sys.exit"), \
             patch("subprocess.list2cmdline", return_value="--arg value"):
            mock_windll.shell32.ShellExecuteW.return_value = 33
            checker.request_elevation()
            args = mock_windll.shell32.ShellExecuteW.call_args[0]
            # args[3] should be the params string
            assert args[3] == "--arg value"
