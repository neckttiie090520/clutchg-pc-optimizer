"""
Inline Help Box Component
Info/warning box displayed within views
"""

import customtkinter as ctk
from gui.theme import COLORS, SIZES
from gui.style import font


class InlineHelpBox(ctk.CTkFrame):
    """Inline help box with icon, title, and content"""

    def __init__(self, parent, title: str, content: str, help_type: str = "info"):
        super().__init__(
            parent,
            fg_color=self._get_bg_color(help_type),
            corner_radius=SIZES["card_radius"],
            border_width=1,
            border_color=self._get_border_color(help_type)
        )

        self.help_type = help_type
        self.grid_columnconfigure(1, weight=1)

        # Icon
        icon = self._get_icon(help_type)
        ctk.CTkLabel(
            self,
            text=icon,
            font=font("section", size=18)
        ).grid(row=0, column=0, padx=(15, 10), pady=12)

        # Content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=10)

        ctk.CTkLabel(
            content_frame,
            text=title,
            font=font("body_bold", size=12, weight="bold"),
            text_color=self._get_text_color(help_type)
        ).pack(anchor="w")

        ctk.CTkLabel(
            content_frame,
            text=content,
            font=font("caption", size=11),
            text_color=self._get_text_color(help_type),
            wraplength=600
        ).pack(anchor="w", pady=(5, 0))

    def _get_bg_color(self, help_type: str) -> str:
        colors = {
            "info": COLORS["bg_card"],
            "warning": COLORS["bg_card"],
            "danger": COLORS["bg_card"],
            "critical": COLORS["bg_card"],
            "success": COLORS["bg_card"]
        }
        return colors.get(help_type, colors["info"])

    def _get_border_color(self, help_type: str) -> str:
        colors = {
            "info": COLORS["accent"],
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "critical": "#EF4444",  # Same as danger
            "success": "#22C55E"
        }
        return colors.get(help_type, colors["info"])

    def _get_text_color(self, help_type: str) -> str:
        colors = {
            "info": COLORS["text_primary"],
            "warning": COLORS["text_primary"],
            "danger": COLORS["text_primary"],
            "critical": COLORS["text_primary"],
            "success": COLORS["text_primary"]
        }
        return colors.get(help_type, colors["info"])

    def _get_icon(self, help_type: str) -> str:
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "danger": "❌",
            "critical": "🚨",  # Distinct icon for critical
            "success": "✅"
        }
        return icons.get(help_type, icons["info"])
