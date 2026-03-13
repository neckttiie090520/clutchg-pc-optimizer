"""
Scripts Page Object

Page Object for the Scripts view in ClutchG.
Provides methods to interact with batch script execution.
"""

from typing import List
from tests.e2e.pages.base_page import BasePage


class ScriptsPage(BasePage):
    """
    Page Object for Scripts view

    The Scripts view shows available batch optimization scripts
    organized by category, with search and filter capabilities.
    """

    CATEGORIES = ["core", "power", "services", "network", "registry"]

    def __init__(self, app):
        """
        Initialize Scripts page

        Args:
            app: pywinauto Application instance
        """
        super().__init__(app)

    def wait_for_scripts_loaded(self, timeout: int = 10):
        """
        Wait for scripts view to fully load

        Args:
            timeout: Timeout in seconds

        Returns:
            ScriptsPage: Self for method chaining
        """
        self.wait_for_window(timeout=timeout)
        return self

    def get_script_list(self) -> List[str]:
        """
        Get list of visible scripts

        Returns:
            list: List of script names
        """
        scripts = []

        try:
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    # Filter out common non-script text
                    if text and not any(skip in text.lower() for skip in ["search", "filter", "category", "scripts"]):
                        # Scripts usually have .bat or meaningful names
                        if len(text) < 50 and text not in scripts:
                            scripts.append(text)

        except Exception:
            pass

        return scripts

    def search_scripts(self, search_term: str):
        """
        Search for scripts by name

        Args:
            search_term: Search term to filter scripts

        Returns:
            ScriptsPage: Self for method chaining
        """
        try:
            # Find search box
            # Search box is usually a text input or editable control
            from pywinauto.keyboard import send_keys

            # Try to find and click search box
            search_box = self.window.child_window(auto_id="search", control_type="Edit")

            if not search_box.exists():
                # Try alternative search box locators
                descendants = self.window.descendants(control_type="Edit")
                for elem in descendants:
                    text = elem.window_text().lower()
                    if "search" in text or elem.is_visible():
                        search_box = elem
                        break

            if search_box.exists():
                search_box.click_input()
                search_box.set_text("")
                send_keys(search_term)
                send_keys("{ENTER}")

        except Exception as e:
            print(f"Warning: Could not search scripts: {e}")

        return self

    def clear_search(self):
        """
        Clear search filter

        Returns:
            ScriptsPage: Self for method chaining
        """
        try:
            search_box = self.window.child_window(auto_id="search", control_type="Edit")

            if search_box.exists():
                search_box.click_input()
                search_box.set_text("")

        except Exception:
            pass

        return self

    def filter_by_category(self, category: str):
        """
        Filter scripts by category

        Args:
            category: Category name (core, power, services, network, registry)

        Returns:
            ScriptsPage: Self for method chaining
        """
        try:
            # Look for category filter buttons or dropdown
            category_btn = self.window.child_window(title=category, control_type="Button")

            if category_btn.exists():
                category_btn.click_input()

        except Exception:
            # Try alternative approach - look for text with category name
            try:
                self.click_text(category)
            except Exception:
                pass

        return self

    def get_active_filter(self) -> str:
        """
        Get the currently active filter

        Returns:
            str: Active filter name or "All" if no filter
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text()
                if any(cat in text.lower() for cat in self.CATEGORIES):
                    # This might be the active filter
                    return text

            return "All"
        except Exception:
            return "Unknown"

    def select_script(self, script_name: str):
        """
        Select a script from the list

        Args:
            script_name: Name of the script to select

        Returns:
            ScriptsPage: Self for method chaining
        """
        try:
            # Find and click on the script
            elements = self.window.descendants()

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    if script_name.lower() in text.lower():
                        elem.click_input()
                        break

        except Exception as e:
            print(f"Warning: Could not select script {script_name}: {e}")

        return self

    def execute_selected_script(self, timeout: int = 5):
        """
        Execute the currently selected script

        Args:
            timeout: Timeout in seconds

        Returns:
            ScriptsPage: Self for method chaining
        """
        try:
            self.click_button("Execute", timeout=timeout)
        except Exception:
            try:
                self.click_button("Run", timeout=timeout)
            except Exception:
                pass

        return self

    def execute_script(self, script_name: str):
        """
        Execute a specific script

        Args:
            script_name: Name of script to execute

        Returns:
            ScriptsPage: Self for method chaining
        """
        self.select_script(script_name)
        self.execute_selected_script()
        return self

    def confirm_execution(self, timeout: int = 5):
        """
        Confirm script execution dialog

        Args:
            timeout: Timeout in seconds

        Returns:
            ScriptsPage: Self for method chaining
        """
        try:
            confirm_dialog = self.app.window(title_re=".*[Cc]onfirm.*|.*[Ee]xecute.*")

            if confirm_dialog.exists():
                yes_btn = confirm_dialog.child_window(title="Yes", control_type="Button")
                yes_btn.click_input()

        except Exception as e:
            print(f"Warning: Could not confirm execution: {e}")

        return self

    def wait_for_execution_completion(self, timeout: int = 60):
        """
        Wait for script execution to complete

        Args:
            timeout: Timeout in seconds

        Returns:
            ScriptsPage: Self for method chaining
        """
        import time

        elapsed = 0
        while elapsed < timeout:
            try:
                exec_dialog = self.app.window(title_re=".*[Ee]xecutin.*|.*[Pp]rogress.*")

                if not exec_dialog.exists():
                    break

            except Exception:
                break

            time.sleep(1)
            elapsed += 1

        return self

    def get_execution_result(self) -> str:
        """
        Get the execution result message

        Returns:
            str: Result message
        """
        try:
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()
                if any(keyword in text.lower() for keyword in ["success", "failed", "error", "complete"]):
                    return text

            return "No result message"
        except Exception:
            return "Error reading result"

    def get_script_description(self, script_name: str) -> str:
        """
        Get description of a script

        Args:
            script_name: Name of the script

        Returns:
            str: Script description
        """
        try:
            # Find script-related text
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text()
                if script_name.lower() in text.lower() and len(text) > 30:
                    # Longer text is likely description
                    return text

            return "No description available"
        except Exception:
            return "Error reading description"

    def get_script_count(self) -> int:
        """
        Get number of visible scripts

        Returns:
            int: Number of scripts
        """
        scripts = self.get_script_list()
        return len(scripts)

    def is_script_visible(self, script_name: str) -> bool:
        """
        Check if a script is visible in the list

        Args:
            script_name: Name of the script

        Returns:
            bool: True if visible
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    if script_name.lower() in text.lower():
                        return True

            return False
        except Exception:
            return False

    def is_execute_button_enabled(self) -> bool:
        """
        Check if execute button is enabled

        Returns:
            bool: True if enabled
        """
        try:
            execute_btn = self.window.child_window(title="Execute", control_type="Button")
            return execute_btn.is_enabled()
        except Exception:
            try:
                run_btn = self.window.child_window(title="Run", control_type="Button")
                return run_btn.is_enabled()
            except Exception:
                return False
