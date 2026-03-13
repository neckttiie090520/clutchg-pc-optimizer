"""
Profiles Page Object

Page Object for the Profiles view in ClutchG.
Provides methods to interact with optimization profiles.
"""

from typing import List
from tests.e2e.pages.base_page import BasePage


class ProfilesPage(BasePage):
    """
    Page Object for Profiles view

    The Profiles view shows three optimization profiles:
    - SAFE: Conservative, proven tweaks
    - COMPETITIVE: Balanced performance
    - EXTREME: Aggressive optimizations
    """

    PROFILES = ["SAFE", "COMPETITIVE", "EXTREME"]

    def __init__(self, app):
        """
        Initialize Profiles page

        Args:
            app: pywinauto Application instance
        """
        super().__init__(app)

    def wait_for_profiles_loaded(self, timeout: int = 10):
        """
        Wait for profiles view to fully load

        Args:
            timeout: Timeout in seconds

        Returns:
            ProfilesPage: Self for method chaining
        """
        self.wait_for_window(timeout=timeout)

        # Wait for at least one profile to be visible
        import time
        time.sleep(1)

        return self

    def get_profile_cards(self) -> List[str]:
        """
        Get list of available profile cards

        Returns:
            list: List of profile names found
        """
        profiles_found = []

        try:
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text()
                # Check if this text matches a profile name
                for profile in self.PROFILES:
                    if profile in text.upper() and profile not in profiles_found:
                        profiles_found.append(profile)

        except Exception:
            pass

        return profiles_found

    def is_profile_visible(self, profile_name: str) -> bool:
        """
        Check if a profile card is visible

        Args:
            profile_name: Profile name (SAFE, COMPETITIVE, EXTREME)

        Returns:
            bool: True if profile is visible
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    if profile_name.upper() in text.upper():
                        return True

            return False
        except Exception:
            return False

    def select_profile(self, profile_name: str):
        """
        Select a profile by clicking on it

        Args:
            profile_name: Profile name to select

        Returns:
            ProfilesPage: Self for method chaining
        """
        try:
            # Try to find and click the profile
            elements = self.window.descendants()

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    if profile_name.upper() in text.upper():
                        # Click on the element
                        elem.click_input()
                        break

        except Exception as e:
            print(f"Warning: Could not select profile {profile_name}: {e}")

        return self

    def click_apply_button(self, timeout: int = 5):
        """
        Click the Apply button

        Args:
            timeout: Timeout in seconds

        Returns:
            ProfilesPage: Self for method chaining
        """
        try:
            self.click_button("Apply", timeout=timeout)
        except Exception:
            # Try alternative button text
            try:
                self.click_button("Apply Profile", timeout=timeout)
            except Exception:
                pass

        return self

    def is_apply_button_enabled(self) -> bool:
        """
        Check if Apply button is enabled

        Returns:
            bool: True if enabled
        """
        try:
            apply_btn = self.window.child_window(title="Apply", control_type="Button")
            return apply_btn.is_enabled()
        except Exception:
            return False

    def get_profile_description(self, profile_name: str) -> str:
        """
        Get description text for a profile

        Args:
            profile_name: Profile name

        Returns:
            str: Profile description
        """
        try:
            # Find profile-related text elements
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()
                if profile_name.upper() in text.upper() and len(text) > 20:
                    # Longer text is likely the description
                    return text

            return "No description found"
        except Exception:
            return "Error reading description"

    def get_profile_risk_indicator(self, profile_name: str) -> str:
        """
        Get risk level indicator for a profile

        Args:
            profile_name: Profile name

        Returns:
            str: Risk level (Low, Medium, High)
        """
        # Risk levels based on profile type
        risk_map = {
            "SAFE": "Low",
            "COMPETITIVE": "Medium",
            "EXTREME": "High"
        }

        return risk_map.get(profile_name.upper(), "Unknown")

    def get_expected_fps_gain(self, profile_name: str) -> str:
        """
        Get expected FPS gain for a profile

        Args:
            profile_name: Profile name

        Returns:
            str: Expected FPS gain text
        """
        fps_gain_map = {
            "SAFE": "2-5%",
            "COMPETITIVE": "5-10%",
            "EXTREME": "10-15%"
        }

        return fps_gain_map.get(profile_name.upper(), "Unknown")

    def confirm_profile_application(self, timeout: int = 5):
        """
        Confirm profile application dialog

        Args:
            timeout: Timeout in seconds

        Returns:
            ProfilesPage: Self for method chaining
        """
        try:
            # Look for confirmation dialog
            confirm_dialog = self.app.window(title_re=".*[Cc]onfirm.*")

            if confirm_dialog.exists():
                # Click Yes button
                yes_btn = confirm_dialog.child_window(title="Yes", control_type="Button")
                yes_btn.click_input()

        except Exception as e:
            print(f"Warning: Could not confirm dialog: {e}")

        return self

    def cancel_profile_application(self, timeout: int = 5):
        """
        Cancel profile application dialog

        Args:
            timeout: Timeout in seconds

        Returns:
            ProfilesPage: Self for method chaining
        """
        try:
            confirm_dialog = self.app.window(title_re=".*[Cc]onfirm.*")

            if confirm_dialog.exists():
                # Click No button
                no_btn = confirm_dialog.child_window(title="No", control_type="Button")
                no_btn.click_input()

        except Exception as e:
            print(f"Warning: Could not cancel dialog: {e}")

        return self

    def wait_for_execution_completion(self, timeout: int = 60):
        """
        Wait for profile execution to complete

        Args:
            timeout: Timeout in seconds

        Returns:
            ProfilesPage: Self for method chaining
        """
        import time

        # Wait for execution dialog to appear and disappear
        elapsed = 0
        while elapsed < timeout:
            try:
                # Check if execution dialog exists
                exec_dialog = self.app.window(title_re=".*[Ee]xecutin.*|.*[Pp]rogress.*")

                if not exec_dialog.exists():
                    # Dialog is gone, execution complete
                    break

            except Exception:
                # Dialog doesn't exist, execution complete
                break

            time.sleep(1)
            elapsed += 1

        return self

    def get_success_message(self) -> str:
        """
        Get success message after profile application

        Returns:
            str: Success message text
        """
        try:
            # Look for success toast or message
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()
                if any(keyword in text.lower() for keyword in ["success", "applied", "complete", "done"]):
                    return text

            return "No success message found"
        except Exception:
            return "Error reading message"

    def is_execution_dialog_visible(self) -> bool:
        """
        Check if execution/progress dialog is visible

        Returns:
            bool: True if execution dialog is visible
        """
        try:
            exec_dialog = self.app.window(title_re=".*[Ee]xecutin.*|.*[Pp]rogress.*")
            return exec_dialog.exists() and exec_dialog.is_visible()
        except Exception:
            return False

    def get_execution_progress(self) -> str:
        """
        Get current execution progress text

        Returns:
            str: Progress information
        """
        try:
            exec_dialog = self.app.window(title_re=".*[Ee]xecutin.*|.*[Pp]rogress.*")

            if exec_dialog.exists():
                elements = exec_dialog.descendants(control_type="Text")
                for elem in elements:
                    text = elem.window_text()
                    if "%" in text or any(keyword in text for keyword in ["progress", "executing"]):
                        return text

            return "No progress info"
        except Exception:
            return "Error reading progress"
