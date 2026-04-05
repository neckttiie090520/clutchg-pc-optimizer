"""
Toast Notification - Flat Design
Simple popup notifications
Updated: 2026-03-06 (stacking support, dynamic sizing)
"""

import customtkinter as ctk
from gui.theme import COLORS, SIZES
from gui.style import font

_TOAST_MIN_HEIGHT = 54  # minimum px per toast slot
_TOAST_WIDTH = 320
_TOAST_MARGIN = 10  # px from screen edge and between toasts


class ToastNotification(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        message,
        title="",
        toast_type="info",
        duration=3000,
        y_offset=0,
        on_close=None,
    ):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_card"])
        self._on_close = on_close
        self._y_offset = y_offset
        self._actual_height = _TOAST_MIN_HEIGHT

        # Simple border
        self.frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.frame.pack(fill="both", expand=True)

        # Color strip
        color = COLORS.get(toast_type, COLORS["info"])
        ctk.CTkFrame(self.frame, width=4, fg_color=color).pack(side="left", fill="y")

        # Content
        ctk.CTkLabel(
            self.frame,
            text=message,
            font=font("caption", size=12),
            text_color=COLORS["text_primary"],
            padx=15,
            pady=15,
            wraplength=_TOAST_WIDTH - 40,
            justify="left",
            anchor="w",
        ).pack(side="left", fill="both", expand=True)

        # Initial position — will be adjusted after layout
        self.position_toast(y_offset)
        self.after(50, self._adjust_height)
        self.after(duration, self._close)
        self.bind("<Button-1>", lambda e: self._close())

    def _adjust_height(self):
        """Recalculate toast height after widget layout is resolved."""
        self.update_idletasks()
        needed = self.frame.winfo_reqheight()
        self._actual_height = max(_TOAST_MIN_HEIGHT, needed)
        self.position_toast(self._y_offset)

    def get_height(self) -> int:
        """Return the actual rendered height of this toast."""
        return self._actual_height

    def position_toast(self, y_offset: int = 0):
        self._y_offset = y_offset
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = screen_w - _TOAST_WIDTH - _TOAST_MARGIN
        y = screen_h - self._actual_height - _TOAST_MARGIN - y_offset
        self.geometry(f"{_TOAST_WIDTH}x{self._actual_height}+{x}+{y}")

    def _close(self):
        if self._on_close:
            self._on_close(self)
        try:
            self.destroy()
        except Exception:
            pass


class ToastManager:
    """
    Manages a stack of toast notifications so they do not overlap.
    Each new toast is offset upward from the previous one.
    """

    def __init__(self, parent):
        self.parent = parent
        self._active: list = []  # list of ToastNotification instances

    def _show(self, msg: str, toast_type: str, duration: int = 3000):
        y_offset = sum((t.get_height() + _TOAST_MARGIN) for t in self._active)
        toast = ToastNotification(
            self.parent,
            msg,
            toast_type=toast_type,
            duration=duration,
            y_offset=y_offset,
            on_close=self._remove,
        )
        self._active.append(toast)

    def _remove(self, toast: "ToastNotification"):
        if toast in self._active:
            self._active.remove(toast)
            # Reposition remaining toasts to close gaps
            running_offset = 0
            for remaining in self._active:
                try:
                    remaining.position_toast(running_offset)
                    running_offset += remaining.get_height() + _TOAST_MARGIN
                except Exception:
                    pass

    def success(self, msg: str, duration: int = 3000):
        self._show(msg, "success", duration)

    def error(self, msg: str, duration: int = 4000):
        self._show(msg, "danger", duration)

    def info(self, msg: str, duration: int = 3000):
        self._show(msg, "info", duration)

    def warning(self, msg: str, duration: int = 3500):
        self._show(msg, "warning", duration)
