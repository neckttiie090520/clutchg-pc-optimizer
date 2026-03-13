# ClutchG UI Automation Testing

This directory contains the automated testing infrastructure for ClutchG using **pytest** and **pywinauto**.

## Quick Start

### 1. Install Test Dependencies

```bash
# From the clutchg directory
pip install -r requirements-test.txt
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/ -v

# Run only E2E tests
pytest tests/e2e/ -v -m e2e

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/e2e/tests/test_navigation.py -v

# Skip E2E tests (faster)
pytest --skip-e2e -v
```

### 3. Run as Administrator

**Important:** E2E tests require administrator privileges because ClutchG requires admin to run.

On Windows, right-click on Command Prompt or PowerShell and select "Run as administrator", then run the tests.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── pytest.ini               # Pytest settings (in parent directory)
│
├── unit/                    # Unit tests (business logic)
│   ├── test_config.py       # Config manager tests
│   ├── test_system_info.py  # System detection tests
│   └── ...
│
├── integration/             # Integration tests
│   ├── test_profile_workflow.py
│   └── ...
│
└── e2e/                     # End-to-end UI tests
    ├── fixtures/            # Reusable fixtures
    │   └── app_fixture.py   # Application launch/quit
    │
    ├── pages/               # Page Object Model
    │   ├── base_page.py     # Base page class
    │   ├── dashboard_page.py
    │   └── ...
    │
    ├── tests/               # E2E test scenarios
    │   ├── test_navigation.py
    │   ├── test_profiles.py
    │   └── ...
    │
    └── utils/               # Test utilities
        └── ui_helpers.py
```

## Test Categories

### Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (business logic workflows)
- `@pytest.mark.e2e` - End-to-end UI tests (full application)
- `@pytest.mark.slow` - Tests that take >10 seconds
- `@pytest.mark.admin` - Tests requiring admin privileges

### Running by Marker

```bash
# Run only unit tests
pytest -m unit -v

# Run only tests requiring admin
pytest -m admin -v

# Skip slow tests
pytest -m "not slow" -v
```

## Fixtures

### Available Fixtures

- `app_path` - Path to ClutchG main.py
- `test_config_dir` - Isolated test config directory
- `app_instance` - Launched ClutchG application (E2E)
- `app_window` - Main ClutchG window (E2E)
- `app_with_admin` - App instance with admin check (E2E)
- `require_admin` - Skips test if not running as admin
- `screenshot_dir` - Directory for test screenshots
- `temp_output_dir` - Temporary output directory

### Using Fixtures in Tests

```python
import pytest

@pytest.mark.e2e
def test_example(app_window):
    """Test using app_window fixture"""
    # app_window is the main ClutchG window
    assert app_window.is_visible()

@pytest.mark.e2e
@pytest.mark.admin
def test_admin_feature(app_with_admin):
    """Test requiring admin privileges"""
    # Test will be skipped if not running as admin
    pass
```

## Page Object Model

The Page Object Model (POM) pattern is used for E2E tests to make them more maintainable.

### Base Page

```python
from tests.e2e.pages.base_page import BasePage

@pytest.mark.e2e
def test_with_pom(app_instance):
    """Test using Page Object Model"""
    page = BasePage(app_instance)
    page.wait_for_window()
    title = page.get_window_title()
    assert "ClutchG" in title
```

### Creating Page Objects

```python
# tests/e2e/pages/profiles_page.py
from tests.e2e.pages.base_page import BasePage

class ProfilesPage(BasePage):
    """Page Object for Profiles view"""

    def navigate_to_profiles(self):
        """Navigate to Profiles view"""
        self.click_text("Profiles")
        return self

    def select_profile(self, profile_name: str):
        """Select a profile"""
        # Implementation...
        return self
```

## CLI Options

### Custom Pytest Options

```bash
# Skip E2E tests
pytest --skip-e2e

# Skip slow tests
pytest --skip-slow

# Specify custom app path
pytest --app-path "C:\path\to\main.py"
```

## Debugging

### Print UI Tree

To see the available UI elements for test development:

```python
@pytest.mark.e2e
def test_debug_ui_tree(app_instance):
    """Print UI tree for debugging"""
    from tests.e2e.pages.base_page import BasePage

    page = BasePage(app_instance)
    page.print_ui_tree()  # Prints all available elements
```

### Screenshot on Failure

Tests automatically capture screenshots on failure (saved to `test_outputs/screenshots/`).

### Inspect.exe

Use **Inspect.exe** (from Windows SDK) to view the UI Automation tree:
1. Open Inspect.exe
2. Hover over ClutchG window
3. See automation IDs, control types, and element hierarchy

## Best Practices

1. **Use Page Objects** - Don't interact with pywinauto directly in tests
2. **One Assertion Per Test** - Keep tests focused
3. **Wait, Don't Sleep** - Use `wait_for_element()` instead of `time.sleep()`
4. **Descriptive Names** - `test_apply_safe_profile_successfully()` not `test_profile_1()`
5. **Test Behavior, Not Implementation** - Test what users see, not internal methods
6. **Isolate Test Data** - Each test uses its own config directory

## Current Test Coverage

### Implemented (Phase 1)
- ✅ Test infrastructure (pytest, fixtures, configuration)
- ✅ Base Page Object Model class
- ✅ Application launch/quit fixture
- ✅ Basic navigation test (app launches, window visible)

### TODO (Phase 2+)
- ⏳ Profile application tests
- ⏳ Settings tests (theme, language)
- ⏳ Script execution tests
- ⏳ Backup management tests
- ⏳ Complete Page Object classes

## Troubleshooting

### "Test requires administrator privileges"

Run terminal as Administrator:
- Right-click Command Prompt/PowerShell
- Select "Run as administrator"

### "Element not found"

1. Use `page.print_ui_tree()` to see available elements
2. Check if element title/text matches
3. Verify element is visible (not hidden/covered)
4. Increase timeout: `page.wait_for_element(title="Text", timeout=20)`

### Tests timing out

1. Increase timeout in fixture or test
2. Skip slow tests: `pytest --skip-slow`
3. Run fewer tests in parallel: `pytest -n 2`

### pywinauto can't find CustomTkinter widgets

CustomTkinter widgets wrap standard Tkinter widgets. Use:
- Window title/text for locating
- Control type (Button, Text, Group)
- Automation ID (if added to widgets)

## CI/CD

Tests are configured to run on GitHub Actions (see `.github/workflows/ci.yml`).

### CI Configuration

- **Runner:** `windows-latest`
- **Workflow trigger:** Push to `main`/`develop`, PRs to `main`
- **Jobs:** Unit tests (`pytest -m unit`), Integration tests (`pytest -m integration`)
- **Skipped on CI:** E2E tests (require desktop session + GUI display), Admin tests (require elevated privileges)
- **Artifacts:** HTML coverage report, JUnit XML test results (retained 14 days)
- **Coverage:** Generated via `pytest-cov` targeting `src/`

## Contributing

When adding new tests:

1. Use existing fixtures and Page Objects
2. Add appropriate markers (`@pytest.mark.e2e`, `@pytest.mark.admin`)
3. Follow naming convention: `test_<action>_<expected_result>()`
4. Keep tests independent (no shared state between tests)
5. Update this README if adding new patterns

## Resources

- **pytest Documentation:** https://docs.pytest.org/
- **pywinauto Documentation:** https://pywinauto.readthedocs.io/
- **Page Object Model:** https://www.selenium.dev/documentation/test_practices/encouraged_page_object_models/
- **Project Plan:** See plan file for full implementation roadmap
