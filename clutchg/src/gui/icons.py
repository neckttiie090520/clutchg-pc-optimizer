"""
Tabler Icons constants for ClutchG
All codepoints use the bundled Tabler Icons font (tabler-icons.ttf, v3.41.1)
"""

import customtkinter as ctk


# ============================================================================
# TABLER ICON CONSTANTS
# ============================================================================
# All codepoints are Tabler Icons (ea00+)

MATERIAL_ICONS = {
    # Navigation & Layout
    "dashboard": "\ueac1",  # home
    "grid_view": "\ueb0b",  # layout-grid
    "view_module": "\ueb0b",  # layout-grid
    # Profiles & Optimization
    "speed": "\ueab1",  # gauge
    "tune": "\uec38",  # adjustments-horizontal
    "bolt": "\uea38",  # bolt
    "shield": "\ueb24",  # shield
    "balance": "\uf1f4",  # arrows-exchange
    # Scripts & Code
    "code": "\uea86",  # code
    "terminal": "\ueb55",  # terminal-2
    "play_arrow": "\ued46",  # player-play
    "list": "\uea97",  # list
    "folder": "\uea83",  # folder
    # Backup & Storage
    "backup": "\uf235",  # stack-push
    "cloud_upload": "\uea75",  # cloud-upload
    "restore": "\ufafd",  # restore
    "cloud_download": "\uea76",  # cloud-download
    "schedule": "\ueb65",  # calendar-time
    "history": "\uebea",  # history
    "inventory_2": "\uea45",  # box
    # Help & Info
    "help": "\ufa0b",  # progress-help
    "help_outline": "\ufa0b",  # progress-help
    "info": "\ueac5",  # info-circle
    "info_outline": "\ueac5",  # info-circle
    "question_mark": "\ueac5",  # info-circle
    "lightbulb": "\uea51",  # bulb
    "menu_book": "\uea39",  # book
    # Settings & Configuration
    "settings": "\ueb20",  # settings-2
    "settings_applications": "\ueb20",  # settings-2
    "palette": "\uea2d",  # color-swatch
    # System & Status
    "check_circle": "\uea67",  # circle-check
    "error": "\uea87",  # circle-x
    "warning": "\uea35",  # alert-triangle
    "cancel": "\uea87",  # circle-x
    "close": "\ueb55",  # x
    "delete": "\ueb55",  # trash
    # Actions
    "add": "\uea9e",  # plus
    "remove": "\uec8e",  # minus
    "edit": "\uec9b",  # pencil
    "save": "\ueb62",  # device-floppy
    "refresh": "\ueb13",  # refresh
    # Search & Filter
    "search": "\ueb1c",  # search
    "filter_list": "\uea5a",  # filter
    "sort": "\ueb73",  # arrows-sort
    # System Hardware
    "memory": "\uefce",  # memory
    "storage": "\ueb2b",  # server
    "cpu": "\ueb87",  # cpu
    "developer_board": "\ueb87",  # cpu
    "videogame_asset": "\uf50d",  # device-desktop-analytics
    "monitor": "\ueb2a",  # device-desktop
    # Arrows & Navigation
    "arrow_back": "\uea19",  # arrow-left
    "arrow_forward": "\uea1f",  # arrow-right
    "home": "\ueac1",  # home
    "exit_to_app": "\uea0a",  # door-exit
    # Misc
    "star": "\ueb2e",  # star
    "favorite": "\ueb2e",  # star
    "visibility": "\uea9a",  # eye
    "visibility_off": "\ueba3",  # eye-off
    "expand_more": "\uea5f",  # chevron-down
    "expand_less": "\uea61",  # chevron-up
    "more_vert": "\uea37",  # dots-vertical
    # Help topic & Phase 2 icons
    "rocket_launch": "\uec45",  # rocket
    "bar_chart": "\uea59",  # chart-bar
    "extension": "\ueb10",  # puzzle
    "description": "\uf028",  # file-description
    "target": "\ueb35",  # target
    "lan": "\uf09f",  # network
    "build": "\ueb40",  # tool
    "download": "\uea96",  # download
    "upload": "\ueb47",  # upload
    "open_in_new": "\uea99",  # external-link
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
    Get Tabler Icons font for use in CustomTkinter widgets

    Args:
        size: Font size

    Returns:
        CTkFont configured for Tabler Icons
    """
    return ctk.CTkFont(family="Tabler Icons", size=size)


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
    Create a CTkLabel with a Tabler Icon

    Args:
        parent: Parent widget
        icon_name: Name of the icon from MATERIAL_ICONS
        size: Icon size
        color: Text color (optional)
        **kwargs: Additional CTkLabel arguments

    Returns:
        CTkLabel configured with Tabler Icon
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
    Create a CTkButton with a Tabler Icon

    Args:
        parent: Parent widget
        icon_name: Name of the icon from MATERIAL_ICONS
        size: Button size
        command: Button command
        **kwargs: Additional CTkButton arguments

    Returns:
        CTkButton configured with Tabler Icon
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
