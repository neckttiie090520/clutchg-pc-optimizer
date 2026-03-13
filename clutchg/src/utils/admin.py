"""
Admin Privileges Checker
Handles checking and requesting administrator privileges on Windows
"""

import sys
import os
import ctypes
import subprocess

from utils.logger import get_logger

logger = get_logger(__name__)


class AdminChecker:
    """Check and request administrator privileges"""

    def is_admin(self) -> bool:
        """
        Check if running with administrator privileges.

        Returns:
            True if running as admin, False otherwise
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def request_elevation(self) -> bool:
        """
        Request administrator privileges (UAC prompt).
        Will restart the application with elevated rights if the user approves.

        Returns:
            True if elevation was granted (current process will exit),
            False if the user denied the UAC prompt or an error occurred.
        """
        if self.is_admin():
            return True

        try:
            # Build a properly-quoted parameter string so that paths containing
            # spaces are passed correctly to the elevated process.
            script = os.path.abspath(sys.argv[0])
            params = subprocess.list2cmdline([script] + sys.argv[1:])

            # Request elevation via ShellExecuteW with the "runas" verb.
            ret = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1,  # SW_SHOWNORMAL
            )

            # ret > 32 means ShellExecuteW succeeded (UAC accepted).
            if ret > 32:
                # Exit the non-elevated instance; the elevated one will start.
                sys.exit(0)
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to request elevation: {e}")
            return False
