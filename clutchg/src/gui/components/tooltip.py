"""
Tooltip Component
Shows helpful information on hover
"""

import customtkinter as ctk
from gui.theme import COLORS
from gui.style import font


class ToolTip(ctk.CTkToplevel):
    """Tooltip window that appears on hover"""

    def __init__(self, parent, text: str, width: int = 250):
        super().__init__(parent)

        self.text = text
        self.width = width

        # Configure window
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLORS["bg_card"])

        # Create content
        label = ctk.CTkLabel(
            self,
            text=text,
            font=font("micro", size=11),
            text_color=COLORS["text_primary"],
            wraplength=self.width - 20,
            justify="left",
            padx=10,
            pady=8
        )
        label.pack()

        # Hide initially
        self.withdraw()

    def show(self, x: int, y: int):
        """Show tooltip at position"""
        self.update_idletasks()
        self.geometry(f"+{x}+{y}")
        self.deiconify()

    def hide(self):
        """Hide tooltip"""
        self.withdraw()


class ToolTipBinder:
    """Binds tooltip to a widget"""

    def __init__(self, widget, text: str, width: int = 250):
        self.widget = widget
        self.tooltip = None
        self.text = text
        self.width = width

        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        """Show tooltip on mouse enter"""
        if not self.tooltip:
            self.tooltip = ToolTip(self.widget.winfo_toplevel(), self.text, self.width)

        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tooltip.show(x, y)

    def on_leave(self, event):
        """Hide tooltip on mouse leave"""
        if self.tooltip:
            self.tooltip.hide()
