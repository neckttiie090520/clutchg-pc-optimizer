"""
Base Page Object Model Class

Provides common functionality for all page objects in the E2E test suite.
"""

from typing import Optional
from pywinauto import Application


class BasePage:
    """
    Base page class with common methods for all page objects

    This class provides shared functionality for interacting with
    the ClutchG application UI, including waiting for elements,
    clicking buttons, and reading text.

    Attributes:
        app: pywinauto Application instance
        window: Main ClutchG window
    """

    # Default timeout for waiting (in seconds)
    DEFAULT_TIMEOUT = 10

    def __init__(self, app: Application):
        """
        Initialize base page

        Args:
            app: pywinauto Application instance
        """
        self.app = app
        self.window = app.window(title_re=".*ClutchG.*")

    def wait_for_window(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Wait for main window to be ready

        Args:
            timeout: Timeout in seconds

        Returns:
            BasePage: Self for method chaining
        """
        self.window.wait('ready', timeout=timeout * 1000)
        return self

    def wait_for_element(
        self,
        title: Optional[str] = None,
        control_type: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Wait for an element to be visible and ready

        Args:
            title: Element title/text
            control_type: Element control type (Button, Text, etc.)
            timeout: Timeout in seconds

        Returns:
            Element: pywinauto element wrapper

        Raises:
            Exception: If element not found within timeout
        """
        kwargs = {}
        if title:
            kwargs['title'] = title
        if control_type:
            kwargs['control_type'] = control_type

        element = self.window.child_window(**kwargs)
        element.wait('visible', timeout=timeout * 1000)

        return element

    def click_button(self, button_text: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Click a button by its text

        Args:
            button_text: Button text/title
            timeout: Timeout in seconds

        Returns:
            BasePage: Self for method chaining
        """
        button = self.wait_for_element(title=button_text, control_type="Button", timeout=timeout)
        button.click_input()
        return self

    def click_text(self, text: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Click on a text element (useful for navigation links)

        Args:
            text: Text to click
            timeout: Timeout in seconds

        Returns:
            BasePage: Self for method chaining
        """
        text_element = self.wait_for_element(title=text, control_type="Text", timeout=timeout)
        text_element.click_input()
        return self

    def read_text(self, element_title: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        """
        Read text from an element

        Args:
            element_title: Title of the element
            timeout: Timeout in seconds

        Returns:
            str: Element text content
        """
        element = self.wait_for_element(title=element_title, timeout=timeout)
        return element.window_text()

    def is_element_visible(
        self,
        title: Optional[str] = None,
        control_type: Optional[str] = None
    ) -> bool:
        """
        Check if an element is visible

        Args:
            title: Element title/text
            control_type: Element control type

        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            kwargs = {}
            if title:
                kwargs['title'] = title
            if control_type:
                kwargs['control_type'] = control_type

            element = self.window.child_window(**kwargs)
            return element.is_visible()
        except Exception:
            return False

    def get_window_title(self) -> str:
        """
        Get the main window title

        Returns:
            str: Window title
        """
        return self.window.window_text()

    def take_screenshot(self, filename: str):
        """
        Capture screenshot of current window

        Args:
            filename: Path to save screenshot
        """
        from PIL import Image

        # Capture screenshot using pywinauto
        img = self.window.capture_as_image()
        img.save(filename)

    def print_ui_tree(self):
        """
        Print the UI tree for debugging

        Useful during test development to see the available
        elements and their properties.
        """
        self.window.print_control_identifiers()

    def get_all_children(self, control_type: Optional[str] = None):
        """
        Get all child elements of the window

        Args:
            control_type: Filter by control type (optional)

        Returns:
            list: List of child elements
        """
        if control_type:
            return self.window.children(control_type=control_type)
        return self.window.children()

    def wait_for_dialog(self, dialog_title: str, timeout: int = 5):
        """
        Wait for a dialog window to appear

        Args:
            dialog_title: Title of the dialog
            timeout: Timeout in seconds

        Returns:
            Window: Dialog window wrapper
        """
        dialog = self.app.window(title=dialog_title)
        dialog.wait('ready', timeout=timeout * 1000)
        return dialog

    def close_dialog(self, dialog_title: str, button_text: str = "OK"):
        """
        Close a dialog by clicking a button

        Args:
            dialog_title: Title of the dialog
            button_text: Button text to click (default: "OK")

        Returns:
            BasePage: Self for method chaining
        """
        dialog = self.wait_for_dialog(dialog_title)
        dialog.child_window(title=button_text, control_type="Button").click_input()
        return self
