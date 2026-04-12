"""
ClutchG - Main Entry Point
Windows PC Optimizer Launcher

Main entry point for the ClutchG application.
Handles initialization, admin check, and application startup.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path (PyInstaller already sets sys._MEIPASS)
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).parent))

from app_minimal import ClutchGApp
from utils.admin import AdminChecker
from utils.logger import setup_logging


def main():
    """Main entry point for ClutchG"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="ClutchG - Windows PC Optimizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Disable welcome overlay and popups for automated testing",
    )
    parser.add_argument(
        "--config-path",
        type=str,
        default=None,
        help="Path to custom config directory for testing",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Check for admin privileges
    admin_checker = AdminChecker()
    if not args.test_mode and not admin_checker.is_admin():
        print("ClutchG requires administrator privileges.")
        print("Please run as administrator.")

        # Attempt to elevate
        if admin_checker.request_elevation():
            # Will restart with admin privileges
            return 0
        else:
            print("\nFailed to obtain administrator privileges.")
            print("Exiting...")
            return 1

    # Create and run application
    app = ClutchGApp(test_mode=args.test_mode, config_path=args.config_path)
    app.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
