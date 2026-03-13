"""
Application Fixture for E2E Testing

Provides pywinauto application instance management for E2E tests.
"""

import pytest
import time
from pathlib import Path
from pywinauto import Application
from pywinauto.timings import Timings


@pytest.fixture(scope="function")
def app_instance(app_path, test_config_dir):
    """
    Launch ClutchG application for testing

    This fixture launches the ClutchG application with test configuration
    and automatically cleans up (quits) after the test.

    Args:
        app_path: Path to main.py (from conftest fixture)
        test_config_dir: Test config directory (from conftest fixture)

    Yields:
        Application: pywinauto Application instance

    Example:
        def test_something(app_instance):
            window = app_instance.window(title="ClutchG")
            # Interact with UI...
    """
    # Configure pywinauto timings for faster tests
    Timings.fast()

    # Build command with test flags
    cmd = f'python "{app_path}" --test-mode --config-path "{test_config_dir}"'

    # Launch application
    app = Application(backend="uia").start(cmd, timeout=15)

    # Give the app time to start
    time.sleep(2)

    yield app

    # Cleanup: Quit application
    try:
        app.kill(timeout=5)
    except Exception:
        # Force kill if graceful shutdown fails
        try:
            app.kill(soft=False)
        except Exception:
            pass


@pytest.fixture(scope="function")
def app_window(app_instance):
    """
    Get the main ClutchG window

    This is a convenience fixture that returns the main window
    directly, saving test code from having to call .window()

    Args:
        app_instance: pywinauto Application instance

    Yields:
        Window: pywinauto WindowWrapper for main ClutchG window

    Example:
        def test_something(app_window):
            app_window.child_window(title="Profiles").click()
    """
    # Wait for window to be ready
    window = app_instance.window(title_re=".*ClutchG.*")
    window.wait('ready', timeout=10)

    yield window


@pytest.fixture(scope="function")
def app_with_admin(app_instance, require_admin):
    """
    Fixture that ensures app runs with admin privileges

    This fixture combines app_instance with admin privilege checking.
    Tests using this fixture will be skipped if not running as admin.

    Args:
        app_instance: pywinauto Application instance
        require_admin: Admin check fixture (skips if not admin)

    Yields:
        Application: pywinauto Application instance (guaranteed admin)

    Example:
        @pytest.mark.admin
        def test_admin_feature(app_with_admin):
            # Test code that requires admin...
    """
    yield app_instance


@pytest.fixture(scope="function")
def restart_app(app_instance, app_path, test_config_dir):
    """
    Fixture that provides a function to restart the application

    Useful for tests that need to restart the app to verify
    configuration persistence.

    Args:
        app_instance: Initial app instance
        app_path: Path to main.py
        test_config_dir: Test config directory

    Yields:
        function: Function that restarts the app and returns new instance

    Example:
        def test_persistence(restart_app):
            # Make changes...
            new_app = restart_app()
            # Verify changes persisted...
    """
    def _restart():
        # Kill existing app
        try:
            app_instance.kill()
        except Exception:
            pass

        # Wait for cleanup
        time.sleep(1)

        # Start new instance
        cmd = f'python "{app_path}" --test-mode --config-path "{test_config_dir}"'
        new_app = Application(backend="uia").start(cmd, timeout=15)
        time.sleep(2)

        return new_app

    yield _restart

    # Final cleanup
    try:
        app_instance.kill()
    except Exception:
        pass
