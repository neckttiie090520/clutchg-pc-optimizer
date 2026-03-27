"""
Google Material Symbols Integration for ClutchG
Provides Material Design icons using Google Material Symbols font
"""

import customtkinter as ctk


# ============================================================================
# MATERIAL SYMBOLS ICON CONSTANTS
# ============================================================================
# Using Google Material Symbols Outlined (unicode values)
# Reference: https://fonts.google.com/icons

MATERIAL_ICONS = {
    # Navigation & Layout
    "dashboard": "\ue8b0",  # Dashboard icon
    "grid_view": "\ue8d4",  # Grid view
    "view_module": "\ue8d5",  # Module view
    # Profiles & Optimization
    "speed": "\ue3de",  # Speed/Performance
    "tune": "\ue429",  # Tune/Settings
    "bolt": "\ue929",  # Lightning bolt (Extreme)
    "shield": "\ue914",  # Shield (Safe)
    "balance": "\uec0e",  # Balance (Competitive)
    # Scripts & Code
    "code": "\ue86f",  # Code
    "terminal": "\ue8c9",  # Terminal
    "play_arrow": "\ue037",  # Play/Run
    "list": "\ue896",  # List
    "folder": "\ue92c",  # Folder
    # Backup & Storage
    "backup": "\ue860",  # Backup (cloud_upload alternative)
    "cloud_upload": "\ue8c5",  # Cloud upload
    "restore": "\ue855",  # Restore (cloud_download)
    "cloud_download": "\ue8c4",  # Cloud download
    "schedule": "\ue8b5",  # Schedule/Timeline
    "history": "\ue8b1",  # History
    "inventory_2": "\ue1d7",  # Stack/Layers (for backup)
    # Help & Info
    "help": "\ue88a",  # Help
    "help_outline": "\ue88b",  # Help outline
    "info": "\ue88e",  # Info
    "info_outline": "\ue88f",  # Info outline
    "question_mark": "\ue8b6",  # Question mark
    "lightbulb": "\ue0a3",  # Lightbulb/Tips
    "menu_book": "\ue8ca",  # Book/Documentation
    # Settings & Configuration
    "settings": "\ue8b8",  # Settings
    "settings_applications": "\ue8c3",  # App settings
    "palette": "\ue40a",  # Palette/Theme
    # System & Status
    "check_circle": "\ue86c",  # Check circle (success)
    "error": "\ue000",  # Error
    "warning": "\ue002",  # Warning
    "cancel": "\ue5c9",  # Cancel/Close
    "close": "\ue5cd",  # Close
    "delete": "\ue872",  # Delete
    # Actions
    "add": "\ue145",  # Add
    "remove": "\ue15b",  # Remove
    "edit": "\ue3c9",  # Edit
    "save": "\ue161",  # Save
    "refresh": "\ue5d5",  # Refresh
    # Search & Filter
    "search": "\ue8b6",  # Search
    "filter_list": "\ue152",  # Filter
    "sort": "\ue164",  # Sort
    # System Hardware
    "memory": "\ue326",  # RAM/Memory
    "storage": "\ue1db",  # Storage
    "cpu": "\ue331",  # CPU (developer_board)
    "developer_board": "\ue331",  # Developer board (CPU)
    "videogame_asset": "\ue338",  # Game/GPU
    "monitor": "\ue314",  # Monitor
    # Arrows & Navigation
    "arrow_back": "\ue5c4",  # Arrow back
    "arrow_forward": "\ue5c8",  # Arrow forward
    "home": "\ue88a",  # Home
    "exit_to_app": "\ue905",  # Exit
    # Misc
    "star": "\ue838",  # Star
    "favorite": "\ue87d",  # Favorite
    "visibility": "\ue8f4",  # Visibility
    "visibility_off": "\ue8f5",  # Visibility off
    "expand_more": "\ue5ce",  # Expand more (chevron down)
    "expand_less": "\ue5cf",  # Expand less (chevron up)
    "more_vert": "\ue5d4",  # More vertical (kebab menu)
    # Help topic & Phase 2 icons
    "rocket_launch": "\ue559",  # Getting Started
    "bar_chart": "\ue26b",  # Dashboard topic
    "extension": "\ue87b",  # Optimization topic
    "description": "\ue873",  # Scripts/description
    "target": "\uf2c4",  # Profile recommendations
    "lan": "\ue639",  # Network category
    "build": "\ue869",  # Troubleshooting / Custom tab
    "download": "\ue2c4",  # Import/Download
    "upload": "\ue2c6",  # Export/Upload
    "open_in_new": "\ue89e",  # External link
}


# ============================================================================
# LEGACY NAV ICONS (Fallback for old code)
# ============================================================================
NAV_ICONS_LEGACY = {
    "dashboard": MATERIAL_ICONS["dashboard"],
    "profiles": MATERIAL_ICONS["tune"],
    "scripts": MATERIAL_ICONS["code"],
    "backup": MATERIAL_ICONS["inventory_2"],
    "help": MATERIAL_ICONS["help_outline"],
    "settings": MATERIAL_ICONS["settings"],
}


# ============================================================================
# FONT LOADER
# ============================================================================
def get_material_font(size: int = 24) -> ctk.CTkFont:
    """
    Get Material Symbols font for use in CustomTkinter widgets

    Args:
        size: Font size

    Returns:
        CTkFont configured for Material Symbols
    """
    return ctk.CTkFont(family="Material Symbols Outlined", size=size)


def get_icon_text(icon_name: str, fallback: str = None) -> str:
    """
    Get the unicode character for an icon

    Args:
        icon_name: Name of the icon from MATERIAL_ICONS
        fallback: Fallback character if icon not found

    Returns:
        Unicode character for the icon
    """
    return MATERIAL_ICONS.get(icon_name, fallback or "?")


def create_icon_label(
    parent, icon_name: str, size: int = 24, color: str = None, **kwargs
) -> ctk.CTkLabel:
    """
    Create a CTkLabel with a Material Symbol icon

    Args:
        parent: Parent widget
        icon_name: Name of the icon from MATERIAL_ICONS
        size: Icon size
        color: Text color (optional)
        **kwargs: Additional CTkLabel arguments

    Returns:
        CTkLabel configured with Material Symbol icon
    """
    from gui.theme import COLORS

    icon_text = get_icon_text(icon_name)
    text_color = color or COLORS.get("text_primary", "#E9EDF2")

    return ctk.CTkLabel(
        parent,
        text=icon_text,
        font=get_material_font(size),
        text_color=text_color,
        **kwargs,
    )


def create_icon_button(
    parent, icon_name: str, size: int = 40, command=None, **kwargs
) -> ctk.CTkButton:
    """
    Create a CTkButton with a Material Symbol icon

    Args:
        parent: Parent widget
        icon_name: Name of the icon from MATERIAL_ICONS
        size: Button size
        command: Button command
        **kwargs: Additional CTkButton arguments

    Returns:
        CTkButton configured with Material Symbol icon
    """
    from gui.theme import COLORS

    icon_text = get_icon_text(icon_name)

    # Set defaults
    defaults = {
        "width": size,
        "height": size,
        "fg_color": "transparent",
        "text_color": COLORS.get("text_secondary", "#A6B0BB"),
        "hover_color": COLORS.get("bg_hover", "#1A2028"),
    }

    # Merge with user kwargs (user kwargs override defaults)
    defaults.update(kwargs)

    return ctk.CTkButton(
        parent,
        text=icon_text,
        font=get_material_font(int(size * 0.6)),
        command=command,
        **defaults,
    )


# ============================================================================
# ICON PAIRS FOR PROFILES
# ============================================================================
PROFILE_ICONS = {
    "SAFE": {
        "icon": "shield",
        "color": "#22C55E",
    },
    "COMPETITIVE": {
        "icon": "balance",
        "color": "#F59E0B",
    },
    "EXTREME": {
        "icon": "bolt",
        "color": "#EF4444",
    },
}


def get_profile_icon(profile_name: str) -> dict:
    """
    Get icon info for a profile

    Args:
        profile_name: Profile name (SAFE, COMPETITIVE, EXTREME)

    Returns:
        Dict with 'icon' and 'color' keys
    """
    return PROFILE_ICONS.get(profile_name.upper(), {"icon": "tune", "color": "#00C6FF"})
