"""
Shared UI styling helpers.
Keeps typography and control styles consistent across views.
"""

import customtkinter as ctk
from gui.theme import COLORS, FONTS, SIZES


def font(key: str, size: int | None = None, weight: str | None = None, family: str | None = None) -> ctk.CTkFont:
    """Return a CTkFont with optional overrides."""
    base_family, base_size, base_weight = FONTS[key]
    return ctk.CTkFont(
        family=family or base_family,
        size=base_size if size is None else size,
        weight=base_weight if weight is None else weight,
    )


def style_primary_button(button: ctk.CTkButton, small: bool = False) -> None:
    height = SIZES["button_height_sm"] if small else SIZES["button_height"]
    button.configure(
        fg_color=COLORS["accent"],
        hover_color=COLORS["accent_hover"],
        text_color=COLORS["bg_primary"],
        corner_radius=SIZES["button_radius"],
        height=height,
    )


def style_outline_button(button: ctk.CTkButton, small: bool = False, color: str | None = None) -> None:
    height = SIZES["button_height_sm"] if small else SIZES["button_height"]
    accent = color or COLORS["accent"]
    button.configure(
        fg_color="transparent",
        border_width=1,
        border_color=accent,
        text_color=COLORS["text_primary"],
        hover_color=COLORS["bg_hover"],
        corner_radius=SIZES["button_radius"],
        height=height,
    )


def style_ghost_button(button: ctk.CTkButton, small: bool = False) -> None:
    height = SIZES["button_height_sm"] if small else SIZES["button_height"]
    button.configure(
        fg_color="transparent",
        text_color=COLORS["text_secondary"],
        hover_color=COLORS["bg_hover"],
        corner_radius=SIZES["button_radius"],
        height=height,
    )


def style_entry(entry: ctk.CTkEntry) -> None:
    entry.configure(
        fg_color=COLORS["bg_elevated"],
        text_color=COLORS["text_primary"],
        border_color=COLORS["border"],
        height=SIZES["input_height"],
    )
