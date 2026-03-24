"""
E2E Test Configuration and Fixtures

Exposes pywinauto-based fixtures for E2E tests.
Skips all E2E tests when:
  - pywinauto is not installed, OR
  - --app-path is not provided on the CLI (no live app to test against)
"""

import pytest


def _e2e_available(config) -> bool:
    """Return True only when both pywinauto and --app-path are present."""
    try:
        import pywinauto  # noqa: F401
    except ImportError:
        return False
    app_path = config.getoption("--app-path", default=None)
    return bool(app_path)


def pytest_collection_modifyitems(config, items):
    """Skip all e2e-marked tests unless the environment is fully ready."""
    if not _e2e_available(config):
        reason = "E2E tests require --app-path and pywinauto (run with: pytest --app-path src/main.py)"
        skip_marker = pytest.mark.skip(reason=reason)
        for item in items:
            if "e2e" in item.keywords or "e2e" in item.nodeid:
                item.add_marker(skip_marker)


# Always define stub fixtures — they skip immediately when called without a live app.
# When --app-path IS supplied, the real fixtures from app_fixture.py override these
# via the session-scoped import below (only attempted when e2e is actually ready).

@pytest.fixture
def app_instance(request):
    if not _e2e_available(request.config):
        pytest.skip("E2E tests require --app-path and pywinauto")
    from tests.e2e.fixtures.app_fixture import app_instance as _real  # noqa: F401
    yield from _real.__wrapped__(request)


@pytest.fixture
def app_window(request, app_instance):
    if not _e2e_available(request.config):
        pytest.skip("E2E tests require --app-path and pywinauto")
    from pywinauto import Application  # noqa: F401
    window = app_instance.window(title_re=".*ClutchG.*")
    window.wait("ready", timeout=10)
    yield window


@pytest.fixture
def app_with_admin(app_instance, require_admin):
    yield app_instance


@pytest.fixture
def restart_app(app_instance, request, test_config_dir):
    import time
    from pywinauto import Application

    def _restart():
        try:
            app_instance.kill()
        except Exception:
            pass
        time.sleep(1)
        app_path = request.config.getoption("--app-path")
        cmd = f'python "{app_path}" --test-mode --config-path "{test_config_dir}"'
        new_app = Application(backend="uia").start(cmd, timeout=15)
        time.sleep(2)
        return new_app

    yield _restart
    try:
        app_instance.kill()
    except Exception:
        pass
