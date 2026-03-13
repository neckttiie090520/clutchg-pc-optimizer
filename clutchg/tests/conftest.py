"""
Pytest Configuration and Fixtures for ClutchG Testing

This module contains shared pytest fixtures and configuration
for automated testing of the ClutchG application.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Generator


def pytest_addoption(parser):
    """Add custom command line options for pytest"""
    parser.addoption(
        "--skip-e2e",
        action="store_true",
        default=False,
        help="Skip end-to-end tests"
    )
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to ClutchG executable or main.py"
    )
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="Skip slow tests (>10 seconds)"
    )


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (business logic workflows)")
    config.addinivalue_line("markers", "e2e: End-to-end UI tests (full application)")
    config.addinivalue_line("markers", "slow: Tests that take >10 seconds")
    config.addinivalue_line("markers", "admin: Tests requiring admin privileges")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on command line options"""
    # Skip E2E tests if --skip-e2e is provided
    if config.getoption("--skip-e2e"):
        skip_e2e = pytest.mark.skip(reason="E2E tests skipped via --skip-e2e")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)

    # Skip slow tests if --skip-slow is provided
    if config.getoption("--skip-slow"):
        skip_slow = pytest.mark.skip(reason="Slow tests skipped via --skip-slow")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def src_dir(project_root) -> Path:
    """Get the source directory"""
    return project_root / "src"


@pytest.fixture(scope="session")
def test_config_dir(tmp_path_factory) -> Path:
    """
    Create isolated test config directory

    This fixture creates a temporary directory for test configurations
    to avoid interfering with the user's actual configuration.

    Yields:
        Path: Temporary config directory
    """
    config_dir = tmp_path_factory.mktemp("test_config")

    # Copy default config if it exists
    source_config_dir = Path(__file__).parent.parent / "config"
    if source_config_dir.exists():
        default_config = source_config_dir / "default_config.json"
        if default_config.exists():
            shutil.copy(default_config, config_dir / "default_config.json")

    yield config_dir

    # Cleanup is handled by tmp_path_factory


@pytest.fixture(scope="session")
def app_path(src_dir) -> Path:
    """
    Get path to ClutchG application entry point

    Returns:
        Path: Path to main.py
    """
    return src_dir / "main.py"


@pytest.fixture(scope="function")
def temp_output_dir(tmp_path) -> Path:
    """
    Create temporary directory for test outputs

    Yields:
        Path: Temporary output directory
    """
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    yield output_dir


@pytest.fixture(scope="function")
def screenshot_dir(temp_output_dir) -> Path:
    """
    Create directory for test screenshots

    Yields:
        Path: Screenshot directory
    """
    screenshot_dir = temp_output_dir / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    yield screenshot_dir


@pytest.fixture(scope="function")
def log_dir(temp_output_dir) -> Path:
    """
    Create directory for test logs

    Yields:
        Path: Log directory
    """
    log_dir = temp_output_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    yield log_dir


@pytest.fixture(scope="function")
def test_timestamp() -> str:
    """
    Get timestamp for test execution

    Returns:
        str: Timestamp in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# Admin check fixture for tests requiring admin privileges
@pytest.fixture(scope="function")
def require_admin():
    """
    Fixture that skips test if not running with admin privileges

    Use this fixture in tests that require administrator rights:
    ```python
    def test_admin_feature(require_admin):
        # Test code here
    ```
    """
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()

    if not is_admin:
        pytest.skip("Test requires administrator privileges")

    yield is_admin


# Config fixture for tests that need custom configuration
@pytest.fixture(scope="function")
def test_config(test_config_dir) -> dict:
    """
    Create test configuration dictionary

    Yields:
        dict: Test configuration
    """
    config = {
        "version": "1.0.0",
        "language": "en",
        "theme": "dark",
        "auto_backup": True,
        "confirm_actions": False,  # Disable for faster testing
        "log_level": "DEBUG",
        "batch_scripts_dir": "../src",
        "backup_dir": "./data/backups",
        "max_backups": 5,  # Lower for faster tests
        "default_profile": "SAFE",
        "window_size": {
            "width": 1000,
            "height": 700
        },
        "startup_checks": {
            "check_admin": True,
            "detect_system": False,  # Skip for faster tests
            "verify_scripts": False  # Skip for faster tests
        },
        "welcome_shown": True  # Skip welcome overlay in tests
    }

    yield config


# Hook for capturing screenshots on test failure
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, screenshot_dir, test_timestamp):
    """
    Automatically capture screenshot on test failure

    This fixture runs automatically for every test and captures
    a screenshot if the test fails. Works with E2E tests that
    use the app_instance fixture.
    """
    yield

    # Check if test failed
    if hasattr(request.node, 'rep_call') and request.node.rep_call is not None:
        # Check if the call phase failed
        if request.node.rep_call.excinfo is not None:
            # Only capture if we have an app_instance with UI
            if "app_instance" in request.fixturenames:
                try:
                    # Try to get the app instance from the test
                    app_instance = request.getfixturevalue("app_instance")

                    # Capture screenshot
                    screenshot_path = screenshot_dir / f"failure_{request.node.name}_{test_timestamp}.png"

                    # Use pywinauto to capture screenshot
                    try:
                        from pywinauto.application import Application
                        # If app_instance is a pywinauto Application
                        if hasattr(app_instance, 'window'):
                            window = app_instance.window()
                            if hasattr(window, 'capture_as_image'):
                                img = window.capture_as_image()
                                img.save(str(screenshot_path))
                                print(f"\n[Screenshot saved: {screenshot_path}]")
                    except Exception as e:
                        print(f"\n[Failed to capture screenshot: {e}]")

                except Exception:
                    # Silently fail if screenshot capture fails
                    pass


# Hook for storing test results (not a fixture!)
def pytest_runtest_makereport(item, call):
    """
    Store test result for screenshot_on_failure fixture

    This is a pytest hook, not a fixture. It stores the test result
    on the item so the screenshot_on_failure fixture can access it.
    """
    if call.when == "call":
        # Store the result on the item for later access
        item.rep_call = call
