"""
Icon Provider - Centralized Icon Management
Provides consistent icons across the application with fallback support
Uses Material Symbols Outlined as primary, with fallbacks
"""

import platform
from typing import Dict, Optional


class IconProvider:
    """
    Centralized icon management with automatic fallback support.

    Priority:
    1. Material Symbols Outlined (primary) - Modern, consistent
    2. Segoe MDL2 Assets (Windows fallback) - Native Windows icons
    3. Text labels (final fallback) - Accessible to everyone
    """

    # Material Symbols Outlined icon mappings
    ICONS = {
        # Navigation
        "dashboard": "\ue871",  # grid_view
        "profiles": "\ue8d8",  # tune
        "scripts": "\uf069",  # terminal
        "backup": "\uf1c9",  # backup / save
        "restore": "\ue855",  # restore / history
        "help": "\ue8b8",  # settings / help
        "settings": "\ue8b8",  # settings
        # Actions
        "create": "\ue145",  # add_circle
        "add": "\ue145",  # add
        "delete": "\ue872",  # delete
        "edit": "\ue3c9",  # edit
        "save": "\ue161",  # save
        "cancel": "\ue5c9",  # close
        "confirm": "\ue876",  # check_circle
        "apply": "\ue157",  # done
        # Status
        "success": "\ue876",  # check_circle
        "error": "\uf5ad",  # error / cancel
        "warning": "\ue002",  # warning
        "info": "\ue88e",  # info
        "loading": "\ue863",  # refresh
        # States
        "check": "\ue876",  # check
        "close": "\ue5c9",  # close
        "expand": "\ue5c5",  # expand_more
        "collapse": "\ue5c6",  # expand_less
        "arrow_right": "\ue5c8",  # arrow_forward
        "arrow_left": "\ue5c4",  # arrow_back
        "arrow_down": "\ue5c5",  # arrow_downward
        "arrow_up": "\ue5c7",  # arrow_upward
        # System
        "cpu": "\ue635",  # memory
        "gpu": "\ue334",  # display_settings
        "ram": "\ue322",  # memory
        "storage": "\ue1db",  # storage
        "network": "\ue639",  # wifi
        # UI Elements
        "search": "\ue8b6",  # search
        "filter": "\ue152",  # filter_list
        "sort": "\ue164",  # sort
        "more": "\ue5d3",  # more_vert
        "menu": "\ue5d2",  # menu
        "home": "\ue88a",  # home
        # Backup/Restore specific
        "history": "\ue81c",  # history (Segoe MDL2)
        "backup_restore": "\ue855",  # restore_from_trash
        "system_snapshot": "\ue8b8",  # settings_backup_restore
        # Files/Folders
        "folder": "\ue2c7",  # folder
        "file": "\ue873",  # insert_drive_file
        "document": "\ue873",  # description
        # Help topic icons
        "rocket_launch": "\ue559",  # Getting Started
        "bar_chart": "\ue26b",  # Dashboard topic
        "tune": "\ue429",  # Profiles / tune
        "extension": "\ue87b",  # Optimization topic
        "bolt": "\ue929",  # Quick Actions / Power
        "description": "\ue873",  # Scripts topic
        "shield": "\ue914",  # Safety topic
        "target": "\uf2c4",  # Profile recommendations
        "lightbulb": "\ue0a3",  # Tips
        "lan": "\ue639",  # Network category
        "build": "\ue869",  # Troubleshooting / Custom tab
        "menu_book": "\ue8ca",  # Glossary tab
        "download": "\ue2c4",  # Import
        "upload": "\ue2c6",  # Export
        "play_arrow": "\ue037",  # Run button
        "open_in_new": "\ue89e",  # External link
        "expand_more": "\ue5cf",  # Expand arrow
        "check_circle": "\ue86c",  # Backup with restore point
        "inventory_2": "\ue1d7",  # Registry-only backup
        "refresh": "\ue5d5",  # Restart indicator
    }

    def __init__(self):
        """Initialize icon provider and detect available fonts"""
        self.system = platform.system()
        self._material_symbols_available = self._check_material_symbols()
        self._segmdl2_available = self._check_segmdl2()

    def _check_material_symbols(self) -> bool:
        """
        Check if Material Symbols Outlined font is available.

        Returns:
            True if font is available, False otherwise
        """
        return self._is_font_available("Material Symbols Outlined")

    def _check_segmdl2(self) -> bool:
        """
        Check if Segoe MDL2 Assets font is available (Windows only).

        Returns:
            True if on Windows and font is available, False otherwise
        """
        if self.system != "Windows":
            return False
        return self._is_font_available("Segoe MDL2 Assets")

    @staticmethod
    def _is_font_available(family_name: str) -> bool:
        """
        Check if a font family is installed by querying tkinter font families.

        Args:
            family_name: Font family name to check

        Returns:
            True if font is available, False otherwise
        """
        try:
            import tkinter.font as tkfont

            available = tkfont.families()
            return family_name in available
        except Exception:
            return False

    def get_icon(self, icon_name: str) -> str:
        """
        Get icon character with fallback logic.

        Args:
            icon_name: Name of the icon (from ICONS dict)

        Returns:
            Icon character as string
        """
        # Try to get from Material Symbols
        icon = self.ICONS.get(icon_name, "")
        if icon:
            return icon

        # Fallback to empty string (caller should handle display)
        return ""

    def get_icon_font(self, icon_name: Optional[str] = None) -> tuple:
        """
        Get font family for icons with fallback chain.

        Args:
            icon_name: Optional icon name for specific font selection

        Returns:
            Tuple of (primary_font, fallback_fonts)
        """
        # Primary: Segoe MDL2 Assets (Windows Native) - Request for professional look
        if self._segmdl2_available:
            return ("Segoe MDL2 Assets",)

        # Secondary: Material Symbols Outlined
        if self._material_symbols_available:
            return ("Material Symbols Outlined",)

        # Tertiary: System default with emoji support
        if self.system == "Windows":
            return ("Segoe UI Emoji", "Segoe UI Symbol")
        elif self.system == "Darwin":  # macOS
            return ("Apple Color Emoji", "Arial Unicode MS")
        else:  # Linux
            return ("Noto Color Emoji", "DejaVu Sans")

    def get_icon_with_fallback(self, icon_name: str, fallback_text: str = "") -> tuple:
        """
        Get icon character and font with fallback support.

        Args:
            icon_name: Name of the icon
            fallback_text: Text to use if icon unavailable

        Returns:
            Tuple of (icon_char, font_family)
        """
        icon_char = self.get_icon(icon_name)

        if not icon_char and fallback_text:
            # Use fallback text
            return (fallback_text, "Segoe UI")

        font_family = self.get_icon_font(icon_name)[0]
        return (icon_char, font_family)

    def is_icon_available(self, icon_name: str) -> bool:
        """
        Check if an icon is available.

        Args:
            icon_name: Name of the icon to check

        Returns:
            True if icon exists in ICONS dict
        """
        return icon_name in self.ICONS

    def get_all_icons(self) -> Dict[str, str]:
        """
        Get all available icons.

        Returns:
            Dictionary of icon_name -> icon_character
        """
        return self.ICONS.copy()


# Singleton instance for easy access
_icon_provider_instance = None


def get_icon_provider() -> IconProvider:
    """
    Get singleton instance of IconProvider.

    Returns:
        IconProvider instance
    """
    global _icon_provider_instance
    if _icon_provider_instance is None:
        _icon_provider_instance = IconProvider()
    return _icon_provider_instance


# Convenience functions for quick access
def get_icon(icon_name: str) -> str:
    """Quick access to get icon character"""
    return get_icon_provider().get_icon(icon_name)


def get_icon_font(icon_name: Optional[str] = None) -> tuple:
    """Quick access to get icon font"""
    return get_icon_provider().get_icon_font(icon_name)
