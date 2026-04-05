"""Local tkinter capture module — CTk-aware fork of tkinter-mcp internals.

Fixes for CustomTkinter apps:
1. find_widget_by_text returns the clickable CTk parent frame, not just the inner Label
2. click_widget generates events with proper coordinates targeting the center of the frame
3. walk_ctk_parents() to find the logical CTk container for any child widget
"""

from tkinter_capture._walker import (
    find_ctk_frame_for_label,
    find_widget_by_id,
    find_widget_by_text,
    serialize_widget_tree,
    walk_ctk_parent,
)
from tkinter_capture._client import CaptureClient
from tkinter_capture._screenshot import save_screenshot

__all__ = [
    "CaptureClient",
    "save_screenshot",
    "find_widget_by_id",
    "find_widget_by_text",
    "find_ctk_frame_for_label",
    "walk_ctk_parent",
    "serialize_widget_tree",
]
