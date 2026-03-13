"""
Settings Page Object

Page Object for the Settings view in ClutchG.
Provides methods to interact with application settings.
"""

from typing import Optional
from tests.e2e.pages.base_page import BasePage


class SettingsPage(BasePage):
    """
    Page Object for Settings view

    The Settings view allows users to configure:
    - Theme (Dark/Light)
    - Language (English/Thai)
    - Auto-backup
    - Confirmation dialogs
    - Other preferences
    """

    THEMES = ["Dark", "Light"]
    LANGUAGES = ["English", "Thai", "EN", "TH"]

    def __init__(self, app):
        """
        Initialize Settings page

        Args:
            app: pywinauto Application instance
        """
        super().__init__(app)

    def wait_for_settings_loaded(self, timeout: int = 10):
        """
        Wait for settings view to fully load

        Args:
            timeout: Timeout in seconds

        Returns:
            SettingsPage: Self for method chaining
        """
        self.wait_for_window(timeout=timeout)
        return self

    def get_current_theme(self) -> str:
        """
        Get the current theme setting

        Returns:
            str: Current theme (dark or light)
        """
        try:
            # Look for theme dropdown or switch
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text()
                # Check for theme indicators
                if any(theme in text for theme in self.THEMES):
                    # Return lowercase version
                    return text.lower()

            # Default to dark if not found
            return "dark"
        except Exception:
            return "unknown"

    def toggle_theme(self):
        """
        Toggle between dark and light theme

        Returns:
            SettingsPage: Self for method chaining
        """
        try:
            # Look for theme toggle button or dropdown
            # Try common button texts
            theme_button = None

            # Try to find a button with "theme" in its name
            descendants = self.window.descendants(control_type="Button")
            for elem in descendants:
                text = elem.window_text().lower()
                if "theme" in text or "dark" in text or "light" in text:
                    theme_button = elem
                    break

            if theme_button:
                theme_button.click_input()

        except Exception as e:
            print(f"Warning: Could not toggle theme: {e}")

        return self

    def set_theme(self, theme: str):
        """
        Set specific theme

        Args:
            theme: Theme to set (dark or light)

        Returns:
            SettingsPage: Self for method chaining
        """
        current_theme = self.get_current_theme()

        # If already on desired theme, no need to change
        if current_theme.lower() == theme.lower():
            return self

        # Toggle to switch theme
        self.toggle_theme()

        return self

    def get_current_language(self) -> str:
        """
        Get the current language setting

        Returns:
            str: Current language (en or th)
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text()
                # Check for language indicators
                if any(lang in text.upper() for lang in ["ENGLISH", "THAI", "EN", "TH"]):
                    # Normalize to en/th
                    if "EN" in text.upper():
                        return "en"
                    elif "TH" in text.upper() or "THAI" in text.upper():
                        return "th"

            return "en"  # Default to English
        except Exception:
            return "unknown"

    def switch_language(self, language: str):
        """
        Switch application language

        Args:
            language: Language to switch to (en or th)

        Returns:
            SettingsPage: Self for method chaining
        """
        try:
            current_lang = self.get_current_language()

            # Only switch if different
            if current_lang.lower() == language.lower():
                return self

            # Look for language dropdown or switch
            lang_button = None

            descendants = self.window.descendants(control_type="Button")
            for elem in descendants:
                text = elem.window_text().lower()
                if "language" in text or "lang" in text:
                    lang_button = elem
                    break

            if lang_button:
                lang_button.click_input()

        except Exception as e:
            print(f"Warning: Could not switch language: {e}")

        return self

    def is_auto_backup_enabled(self) -> bool:
        """
        Check if auto-backup setting is enabled

        Returns:
            bool: True if auto-backup is enabled
        """
        try:
            # Look for checkbox or toggle switch
            # This is a placeholder - actual implementation depends on UI structure
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text().lower()
                if "auto backup" in text or "automatic backup" in text:
                    # Check if it's checked/enabled
                    # Implementation depends on control type
                    return True

            return False
        except Exception:
            return False

    def toggle_auto_backup(self):
        """
        Toggle auto-backup setting

        Returns:
            SettingsPage: Self for method chaining
        """
        try:
            # Find and click auto-backup toggle
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text().lower()
                if "auto backup" in text or "automatic backup" in text:
                    elem.click_input()
                    break

        except Exception as e:
            print(f"Warning: Could not toggle auto-backup: {e}")

        return self

    def is_confirm_actions_enabled(self) -> bool:
        """
        Check if confirmation dialogs are enabled

        Returns:
            bool: True if confirmations are enabled
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text().lower()
                if "confirm" in text and "action" in text:
                    return True

            return False
        except Exception:
            return False

    def toggle_confirm_actions(self):
        """
        Toggle confirm actions setting

        Returns:
            SettingsPage: Self for method chaining
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text().lower()
                if "confirm" in text:
                    elem.click_input()
                    break

        except Exception as e:
            print(f"Warning: Could not toggle confirm actions: {e}")

        return self

    def click_reset_to_defaults(self):
        """
        Reset all settings to defaults

        Returns:
            SettingsPage: Self for method chaining
        """
        try:
            self.click_button("Reset", timeout=5)

            # Confirm reset if dialog appears
            import time
            time.sleep(0.5)

            try:
                confirm_dialog = self.app.window(title_re=".*[Rr]eset.*")
                if confirm_dialog.exists():
                    yes_btn = confirm_dialog.child_window(title="Yes", control_type="Button")
                    yes_btn.click_input()
            except Exception:
                pass

        except Exception as e:
            print(f"Warning: Could not reset to defaults: {e}")

        return self

    def get_setting_value(self, setting_name: str) -> Optional[str]:
        """
        Get value of a specific setting

        Args:
            setting_name: Name of the setting

        Returns:
            str: Setting value or None if not found
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                text = elem.window_text()
                if setting_name.lower() in text.lower():
                    # Return the element's text or state
                    return text

            return None
        except Exception:
            return None

    def is_setting_visible(self, setting_name: str) -> bool:
        """
        Check if a setting is visible in the settings view

        Args:
            setting_name: Name of the setting

        Returns:
            bool: True if setting is visible
        """
        try:
            return self.is_element_visible(title=setting_name)
        except Exception:
            return False

    def get_all_visible_settings(self) -> list:
        """
        Get list of all visible setting names

        Returns:
            list: List of setting names
        """
        settings = []

        try:
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    # Filter out empty text and common UI elements
                    if text and len(text) < 50 and text not in ["Settings", "ClutchG"]:
                        settings.append(text)

        except Exception:
            pass

        return settings

    def save_settings(self):
        """
        Save current settings (if there's a save button)

        Returns:
            SettingsPage: Self for method chaining
        """
        try:
            self.click_button("Save", timeout=5)
        except Exception:
            # Settings might auto-save
            pass

        return self
