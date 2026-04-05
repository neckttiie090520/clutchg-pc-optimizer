"""
Shared UI styling helpers.
Keeps typography and control styles consistent across views.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union

import customtkinter as ctk
from gui.theme import COLORS, FONTS, SIZES


def font(
    key: str,
    size: int | None = None,
    weight: str | None = None,
    family: str | None = None,
) -> ctk.CTkFont:
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


def style_outline_button(
    button: ctk.CTkButton, small: bool = False, color: str | None = None
) -> None:
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


def bind_dynamic_wraplength(
    container: Any,
    labels: Union[ctk.CTkLabel, Sequence[ctk.CTkLabel]],
    padding: int = 8,
    min_width: int = 60,
) -> None:
    """Bind a ``<Configure>`` handler so *labels* reflow when *container* resizes.

    CTkLabel internally multiplies ``wraplength`` by the DPI scaling factor,
    while ``winfo_width()`` returns screen pixels.  This helper converts
    screen px -> logical px before passing to ``configure(wraplength=...)``,
    preventing text from being clipped on scaled displays.

    Parameters
    ----------
    container:
        The widget whose width drives the wrap calculation.
    labels:
        One label or a sequence of labels to keep in sync.
    padding:
        Logical-px safety margin subtracted from the usable width.
    min_width:
        Ignore resize events that would produce a wraplength below this.
    """
    if isinstance(labels, ctk.CTkLabel):
        label_list: List[ctk.CTkLabel] = [labels]
    else:
        label_list = list(labels)

    def _on_configure(event=None):
        w = container.winfo_width()
        if w <= 20:
            return
        try:
            scaling = ctk.ScalingTracker.get_widget_scaling(container)
        except Exception:
            scaling = 1.0
        if scaling <= 0:
            scaling = 1.0
        usable = int(w / scaling) - padding
        if usable < min_width:
            return
        for lbl in label_list:
            try:
                lbl.configure(wraplength=usable)
            except Exception:
                pass

    container.bind("<Configure>", _on_configure, add="+")
    # Catch late layout passes
    for delay in (50, 150):
        container.after(delay, _on_configure)
