"""
Navigation Tests for ClutchG E2E Testing

Tests user navigation between different views in the ClutchG application.
"""

import pytest
from tests.e2e.pages.base_page import BasePage


@pytest.mark.e2e
def test_app_launches(app_window):
    """
    Test that ClutchG application launches successfully

    This is the most basic E2E test - it verifies that the app
    can start up and the main window is visible.

    Args:
        app_window: Main ClutchG window fixture
    """
    # Assert window is visible
    assert app_window.is_visible()

    # Assert window title contains "ClutchG"
    window_title = app_window.window_text()
    assert "ClutchG" in window_title


@pytest.mark.e2e
def test_window_has_sidebar(app_window):
    """
    Test that main window has navigation sidebar

    Args:
        app_window: Main ClutchG window fixture
    """
    # Look for sidebar elements (navigation buttons/labels)
    # The sidebar should have labels for different views

    # Check for common navigation items
    nav_items = ["Dashboard", "Profiles", "Scripts", "Backup", "Settings"]

    for item in nav_items:
        # Try to find each navigation item
        # We use a helper function to check visibility
        found = False
        try:
            from pywinauto import findwindows
            # Search for element with this text
            elements = app_window.descendants(control_type="Text")
            for elem in elements:
                if item in elem.window_text():
                    found = True
                    break
        except Exception:
            pass

        # At minimum, Dashboard and Profiles should exist
        if item in ["Dashboard", "Profiles"]:
            assert found, f"Navigation item '{item}' not found in sidebar"


@pytest.mark.e2e
def test_dashboard_view_is_default(app_window):
    """
    Test that Dashboard is shown by default when app launches

    Args:
        app_window: Main ClutchG window fixture
    """
    # Look for Dashboard-specific elements
    # Dashboard should show system information or score

    # Try to find dashboard-related text
    dashboard_elements_found = False

    try:
        elements = app_window.descendants()
        for elem in elements:
            text = elem.window_text()
            # Dashboard might show "System", "Score", "CPU", "GPU", etc.
            if any(keyword in text for keyword in ["System", "Score", "CPU", "Tier", "Performance"]):
                dashboard_elements_found = True
                break
    except Exception:
        pass

    # We should at least see some dashboard content
    assert dashboard_elements_found, "Dashboard content not found"


@pytest.mark.e2e
@pytest.mark.skip(reason="Navigation test - needs navigation button implementation")
def test_navigate_to_profiles(app_window):
    """
    Test navigation to Profiles view

    NOTE: This test is skipped until we implement proper navigation
    button finding. It serves as a template for future navigation tests.

    Args:
        app_window: Main ClutchG window fixture
    """
    # This is a template for navigation tests
    # Once we know the exact control structure, we can implement this

    # Click Profiles navigation button
    # profiles_btn = app_window.child_window(title="Profiles", control_type="Button")
    # profiles_btn.click_input()

    # Verify Profiles view is shown
    # assert app_window.child_window(title="SAFE", control_type="Text").exists()

    pass  # Placeholder until implemented


@pytest.mark.e2e
class TestPageObjectModel:
    """
    Tests using the Page Object Model pattern

    These tests demonstrate the use of BasePage for cleaner,
    more maintainable test code.
    """

    def test_base_page_initialization(self, app_instance):
        """
        Test that BasePage can be initialized

        Args:
            app_instance: pywinauto Application fixture
        """
        page = BasePage(app_instance)

        # Verify window is accessible
        assert page.window is not None
        assert page.window.is_visible()

    def test_base_page_wait_for_window(self, app_instance):
        """
        Test BasePage wait_for_window method

        Args:
            app_instance: pywinauto Application fixture
        """
        page = BasePage(app_instance)
        page.wait_for_window(timeout=5)

        # Should not raise exception if window is ready
        assert True

    def test_base_page_get_window_title(self, app_instance):
        """
        Test BasePage get_window_title method

        Args:
            app_instance: pywinauto Application fixture
        """
        page = BasePage(app_instance)
        title = page.get_window_title()

        assert "ClutchG" in title
