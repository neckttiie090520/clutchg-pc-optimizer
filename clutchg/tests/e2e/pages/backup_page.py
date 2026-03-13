"""
Backup Page Object

Page Object for the Backup view in ClutchG.
Provides methods to manage system backups and restore points.
"""

from typing import List, Dict
from tests.e2e.pages.base_page import BasePage


class BackupPage(BasePage):
    """
    Page Object for Backup view

    The Backup view allows users to:
    - Create new backups
    - View existing backups
    - Restore from backups
    - Delete backups
    """

    def __init__(self, app):
        """
        Initialize Backup page

        Args:
            app: pywinauto Application instance
        """
        super().__init__(app)

    def wait_for_backup_loaded(self, timeout: int = 10):
        """
        Wait for backup view to fully load

        Args:
            timeout: Timeout in seconds

        Returns:
            BackupPage: Self for method chaining
        """
        self.wait_for_window(timeout=timeout)
        return self

    def get_backup_list(self) -> List[Dict[str, str]]:
        """
        Get list of existing backups

        Returns:
            list: List of backup dictionaries with keys: name, date, size
        """
        backups = []

        try:
            elements = self.window.descendants(control_type="Text")

            # Parse backup information from text elements
            # This is a simplified implementation
            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    # Look for date patterns (YYYY-MM-DD or similar)
                    if any(char.isdigit() for char in text) and len(text) < 30:
                        if "backup" in text.lower() or "/" in text or "-" in text:
                            backups.append({
                                "name": text,
                                "date": text,
                                "size": "Unknown"
                            })

        except Exception:
            pass

        return backups

    def get_backup_count(self) -> int:
        """
        Get number of existing backups

        Returns:
            int: Number of backups
        """
        backups = self.get_backup_list()
        return len(backups)

    def click_create_backup(self):
        """
        Click create backup button

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            self.click_button("Create Backup", timeout=5)
        except Exception:
            try:
                self.click_button("New Backup", timeout=5)
            except Exception:
                try:
                    self.click_button("Create", timeout=5)
                except Exception:
                    pass

        return self

    def confirm_create_backup(self, timeout: int = 5):
        """
        Confirm backup creation dialog

        Args:
            timeout: Timeout in seconds

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            confirm_dialog = self.app.window(title_re=".*[Cc]onfirm.*|.*[Cc]reate.*")

            if confirm_dialog.exists():
                yes_btn = confirm_dialog.child_window(title="Yes", control_type="Button")
                yes_btn.click_input()

        except Exception as e:
            print(f"Warning: Could not confirm create backup: {e}")

        return self

    def wait_for_backup_completion(self, timeout: int = 30):
        """
        Wait for backup creation to complete

        Args:
            timeout: Timeout in seconds

        Returns:
            BackupPage: Self for method chaining
        """
        import time

        elapsed = 0
        while elapsed < timeout:
            try:
                progress_dialog = self.app.window(title_re=".*[Bb]ackup.*|.*[Pp]rogress.*")

                if not progress_dialog.exists():
                    break

            except Exception:
                break

            time.sleep(1)
            elapsed += 1

        return self

    def select_backup(self, backup_name: str):
        """
        Select a backup from the list

        Args:
            backup_name: Name or date of backup to select

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            elements = self.window.descendants()

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    if backup_name.lower() in text.lower():
                        elem.click_input()
                        break

        except Exception as e:
            print(f"Warning: Could not select backup {backup_name}: {e}")

        return self

    def click_restore_backup(self):
        """
        Click restore backup button

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            self.click_button("Restore", timeout=5)
        except Exception as e:
            print(f"Warning: Could not click restore: {e}")

        return self

    def confirm_restore(self, timeout: int = 5):
        """
        Confirm restore dialog

        Args:
            timeout: Timeout in seconds

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            confirm_dialog = self.app.window(title_re=".*[Rr]estore.*|.*[Cc]onfirm.*")

            if confirm_dialog.exists():
                yes_btn = confirm_dialog.child_window(title="Yes", control_type="Button")
                yes_btn.click_input()

        except Exception as e:
            print(f"Warning: Could not confirm restore: {e}")

        return self

    def wait_for_restore_completion(self, timeout: int = 60):
        """
        Wait for restore operation to complete

        Args:
            timeout: Timeout in seconds

        Returns:
            BackupPage: Self for method chaining
        """
        import time

        elapsed = 0
        while elapsed < timeout:
            try:
                restore_dialog = self.app.window(title_re=".*[Rr]estorin.*|.*[Pp]rogress.*")

                if not restore_dialog.exists():
                    break

            except Exception:
                break

            time.sleep(1)
            elapsed += 1

        return self

    def click_delete_backup(self):
        """
        Click delete backup button

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            self.click_button("Delete", timeout=5)
        except Exception as e:
            print(f"Warning: Could not click delete: {e}")

        return self

    def confirm_delete(self, timeout: int = 5):
        """
        Confirm delete dialog

        Args:
            timeout: Timeout in seconds

        Returns:
            BackupPage: Self for method chaining
        """
        try:
            confirm_dialog = self.app.window(title_re=".*[Dd]elete.*|.*[Cc]onfirm.*")

            if confirm_dialog.exists():
                yes_btn = confirm_dialog.child_window(title="Yes", control_type="Button")
                yes_btn.click_input()

        except Exception as e:
            print(f"Warning: Could not confirm delete: {e}")

        return self

    def get_backup_details(self, backup_name: str) -> Dict[str, str]:
        """
        Get details for a specific backup

        Args:
            backup_name: Name of backup

        Returns:
            dict: Backup details with keys: name, date, size, description
        """
        details = {
            "name": backup_name,
            "date": "Unknown",
            "size": "Unknown",
            "description": "No description"
        }

        try:
            # Select the backup first
            self.select_backup(backup_name)

            # Look for details in the UI
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                if elem.is_visible():
                    text = elem.window_text()
                    # Look for date patterns
                    if "/" in text or "-" in text:
                        details["date"] = text
                    # Look for size info (MB, GB)
                    elif "MB" in text or "GB" in text:
                        details["size"] = text

        except Exception:
            pass

        return details

    def is_backup_button_enabled(self) -> bool:
        """
        Check if create backup button is enabled

        Returns:
            bool: True if enabled
        """
        try:
            create_btn = self.window.child_window(title="Create Backup", control_type="Button")
            return create_btn.is_enabled()
        except Exception:
            try:
                create_btn = self.window.child_window(title="Create", control_type="Button")
                return create_btn.is_enabled()
            except Exception:
                return False

    def is_restore_button_enabled(self) -> bool:
        """
        Check if restore button is enabled (requires selected backup)

        Returns:
            bool: True if enabled
        """
        try:
            restore_btn = self.window.child_window(title="Restore", control_type="Button")
            return restore_btn.is_enabled()
        except Exception:
            return False

    def is_delete_button_enabled(self) -> bool:
        """
        Check if delete button is enabled (requires selected backup)

        Returns:
            bool: True if enabled
        """
        try:
            delete_btn = self.window.child_window(title="Delete", control_type="Button")
            return delete_btn.is_enabled()
        except Exception:
            return False

    def get_backup_status_message(self) -> str:
        """
        Get status message from backup operation

        Returns:
            str: Status message
        """
        try:
            elements = self.window.descendants(control_type="Text")

            for elem in elements:
                text = elem.window_text()
                if any(keyword in text.lower() for keyword in ["success", "complete", "failed", "error"]):
                    return text

            return "No status message"
        except Exception:
            return "Error reading status"

    def has_backups(self) -> bool:
        """
        Check if any backups exist

        Returns:
            bool: True if backups exist
        """
        return self.get_backup_count() > 0

    def is_backup_list_empty(self) -> bool:
        """
        Check if backup list is empty

        Returns:
            bool: True if no backups
        """
        return not self.has_backups()

    def get_max_backups_limit(self) -> int:
        """
        Get maximum number of backups allowed

        Returns:
            int: Max backups (default from config: 10)
        """
        # This would normally come from config
        # For now, return the default
        return 10

    def is_max_backups_reached(self) -> bool:
        """
        Check if maximum number of backups has been reached

        Returns:
            bool: True if at max
        """
        return self.get_backup_count() >= self.get_max_backups_limit()
