"""
Dashboard Page Object

Page Object for the Dashboard view in ClutchG.
Provides methods to interact with dashboard elements.
"""

from typing import Dict, Any
from tests.e2e.pages.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object for Dashboard view

    The Dashboard shows system information, performance score,
    and quick navigation to profiles.
    """

    def __init__(self, app):
        """
        Initialize Dashboard page

        Args:
            app: pywinauto Application instance
        """
        super().__init__(app)

    def wait_for_dashboard_loaded(self, timeout: int = 10):
        """
        Wait for dashboard to fully load

        Args:
            timeout: Timeout in seconds

        Returns:
            DashboardPage: Self for method chaining
        """
        # Dashboard should show system information
        # Wait for any dashboard-related element to be visible
        self.wait_for_window(timeout=timeout)

        # Give extra time for system detection to complete
        import time
        time.sleep(1)

        return self

    def get_system_score(self) -> str:
        """
        Get the system performance score

        Returns:
            str: System score text (e.g., "85", "Good")
        """
        try:
            # Try to find score element
            # Score might be in a Text element with "score" in its name
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()
                # Score is usually a number or rating
                if text.isdigit() or any(keyword in text.lower() for keyword in ["score", "rating", "tier"]):
                    return text

            return "Unknown"
        except Exception:
            return "Unknown"

    def get_system_tier(self) -> str:
        """
        Get the system tier classification

        Returns:
            str: System tier (e.g., "High", "Medium", "Low")
        """
        try:
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()
                # Look for tier information
                if any(tier in text.upper() for tier in ["HIGH", "MEDIUM", "LOW", "TIER"]):
                    return text

            return "Unknown"
        except Exception:
            return "Unknown"

    def get_hardware_info(self) -> Dict[str, str]:
        """
        Get hardware information displayed on dashboard

        Returns:
            dict: Hardware info with keys: cpu, gpu, ram, storage
        """
        hardware = {
            "cpu": "Unknown",
            "gpu": "Unknown",
            "ram": "Unknown",
            "storage": "Unknown"
        }

        try:
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()

                # Detect CPU info (usually contains "Intel", "AMD", "Core", "Ryzen")
                if any(cpu_keyword in text for cpu_keyword in ["Intel", "AMD", "Core", "Ryzen", "CPU"]):
                    hardware["cpu"] = text

                # Detect GPU info (usually contains "NVIDIA", "AMD", "RTX", "GTX", "RX")
                elif any(gpu_keyword in text for gpu_keyword in ["NVIDIA", "RTX", "GTX", "AMD", "RX", "GPU"]):
                    hardware["gpu"] = text

                # Detect RAM info (usually contains "GB" or "MB" with number)
                elif "GB" in text or "MB" in text:
                    if any(mem_keyword in text.lower() for mem_keyword in ["ram", "memory", "ddr"]):
                        hardware["ram"] = text

                # Detect Storage info (usually contains "TB", "GB", "SSD", "HDD")
                elif any(storage_keyword in text for storage_keyword in ["SSD", "HDD", "TB", "GB"]):
                    if "drive" not in text.lower():
                        hardware["storage"] = text

        except Exception:
            pass

        return hardware

    def is_quick_profile_button_visible(self, profile_name: str) -> bool:
        """
        Check if quick profile button is visible

        Args:
            profile_name: Profile name (SAFE, COMPETITIVE, EXTREME)

        Returns:
            bool: True if button is visible
        """
        return self.is_element_visible(title=profile_name, control_type="Button")

    def click_quick_profile_button(self, profile_name: str):
        """
        Click quick profile button on dashboard

        Args:
            profile_name: Profile name to click

        Returns:
            DashboardPage: Self for method chaining
        """
        try:
            self.click_button(profile_name, timeout=5)
        except Exception:
            # Button might not exist or use different text
            pass

        return self

    def navigate_to_profiles(self):
        """
        Navigate to Profiles view

        Returns:
            DashboardPage: Self for method chaining
        """
        self.click_text("Profiles")
        return self

    def navigate_to_scripts(self):
        """
        Navigate to Scripts view

        Returns:
            DashboardPage: Self for method chaining
        """
        self.click_text("Scripts")
        return self

    def navigate_to_backup(self):
        """
        Navigate to Backup view

        Returns:
            DashboardPage: Self for method chaining
        """
        self.click_text("Backup")
        return self

    def navigate_to_settings(self):
        """
        Navigate to Settings view

        Returns:
            DashboardPage: Self for method chaining
        """
        self.click_text("Settings")
        return self

    def navigate_to_help(self):
        """
        Navigate to Help view

        Returns:
            DashboardPage: Self for method chaining
        """
        self.click_text("Help")
        return self
