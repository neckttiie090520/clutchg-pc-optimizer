"""CTk-aware widget tree walker — fixes for CustomTkinter navigation.

The key insight: CustomTkinter widgets are composed of internal tkinter widgets
(Canvas + Label children inside Frames). The tkinter-mcp agent sees these raw
internal widgets but the click bindings live on the CTk parent, not the children.

This module walks the raw widget tree and maps inner labels/frames to their
logical CTk parent containers that have click bindings.
"""

from __future__ import annotations

import tkinter as tk
from typing import Any


def _get_text(widget: tk.Widget) -> str | None:
    try:
        return widget.cget("text")
    except Exception:
        pass
    try:
        if hasattr(widget, "get"):
            return widget.get()
    except Exception:
        pass
    return None


def _widget_class(widget: tk.Widget) -> str:
    return widget.winfo_class()


def walk_ctk_parent(widget: tk.Widget, max_levels: int = 6) -> tk.Widget | None:
    """Walk up from an inner Label/Canvas to find a Frame parent that could be a CTk nav item.

    CTk nav buttons are structured like:
        Frame (nav item — has <Button-1> binding)
          Frame (indicator strip)
          Frame (icon container)
            Canvas
            Label (icon glyph)
          Frame (label container)
            Canvas
            Label ("Home" / "Tweaks" / etc.)

    We start from the Label with text like "Home" and walk up 2-3 levels
    to find the outermost Frame that has geometry typical of a nav item (~264x45).
    """
    current = widget
    best = None
    for _ in range(max_levels):
        parent = current.nametowidget(current.winfo_parent())
        if parent is None:
            break
        cls = _widget_class(parent)
        geo_w = parent.winfo_width()
        geo_h = parent.winfo_height()

        # Nav items are Frames roughly 200-300px wide and 35-260px tall
        if cls == "Frame" and 200 <= geo_w <= 400 and 30 <= geo_h <= 300:
            best = parent

        # Don't go above the sidebar container
        if geo_w > 400:
            break

        current = parent

    return best


def find_widget_by_id(root: tk.Widget, widget_id: int) -> tk.Widget | None:
    if root.winfo_id() == widget_id:
        return root
    for child in root.winfo_children():
        result = find_widget_by_id(child, widget_id)
        if result is not None:
            return result
    return None


def find_widget_by_text(root: tk.Widget, text: str) -> tk.Widget | None:
    """Find first widget whose text contains `text`."""
    widget_text = _get_text(root)
    if isinstance(widget_text, str) and text in widget_text:
        return root
    for child in root.winfo_children():
        result = find_widget_by_text(child, text)
        if result is not None:
            return result
    return None


def find_ctk_frame_for_label(root: tk.Widget, label_text: str) -> dict[str, Any] | None:
    """Find a sidebar nav item by its label text, returning the clickable parent frame.

    Returns dict with:
        - frame_id: winfo_id() of the clickable CTk nav frame
        - label_id: winfo_id() of the Label widget
        - frame_widget: the actual widget (for event generation)
    """
    label_widget = find_widget_by_text(root, label_text)
    if label_widget is None:
        return None

    parent_frame = walk_ctk_parent(label_widget)
    if parent_frame is None:
        parent_frame = label_widget.master

    return {
        "frame_id": parent_frame.winfo_id(),
        "label_id": label_widget.winfo_id(),
        "frame_widget": parent_frame,
        "label_widget": label_widget,
    }


def serialize_widget_tree(root: tk.Tk) -> dict[str, Any]:
    """Serialize widget tree into a flat dict format."""
    root.update_idletasks()

    def _ser(widget: tk.Widget) -> dict[str, Any]:
        widget.update_idletasks()
        return {
            "class": _widget_class(widget),
            "id": widget.winfo_id(),
            "name": widget.winfo_name(),
            "text": _get_text(widget),
            "geometry": {
                "x": widget.winfo_x(),
                "y": widget.winfo_y(),
                "width": widget.winfo_width(),
                "height": widget.winfo_height(),
            },
            "state": str(widget.cget("state")) if _has_state(widget) else "normal",
            "is_mapped": widget.winfo_ismapped() == 1,
            "children": [_ser(c) for c in widget.winfo_children()],
        }

    return {
        "window_title": root.title(),
        "root": _ser(root),
    }


def _has_state(widget: tk.Widget) -> bool:
    try:
        widget.cget("state")
        return True
    except Exception:
        return False
