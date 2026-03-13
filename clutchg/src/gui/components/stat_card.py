"""
StatCard Component - Compact Hardware Stat Display (Sparkle Beta Style)
Purpose: Display hardware metrics in a compact grid layout
"""

import customtkinter as ctk
from gui.theme import theme_manager, SPACING, RADIUS


class StatCard(ctk.CTkFrame):
    """
    Compact stat card for displaying hardware metrics
    Layout: Icon + Value + Label (horizontal layout)
    Height: 60px (compact)
    """

    def __init__(
        self,
        master,
        icon: str,
        value: str,
        label: str,
        icon_color: str = None,
        **kwargs
    ):
        """
        Create a compact stat card

        Args:
            master: Parent widget
            icon: Icon character (emoji or Material Symbol)
            value: Value to display (e.g., "8", "16GB", "NVIDIA")
            label: Label text (e.g., "CPU", "RAM", "GPU")
            icon_color: Optional custom icon color
        """
        colors = theme_manager.get_colors()

        # Set icon color if not provided
        if icon_color is None:
            icon_color = colors["accent"]

        # Glassmorphism background
        super().__init__(
            master,
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=colors.get("border_subtle", colors["border"]),
            fg_color=colors.get("bg_card", colors["bg_secondary"]),
            **kwargs
        )

        # Configure grid for horizontal layout
        self.grid_columnconfigure(1, weight=1)  # Value/label section expands

        # Icon (left side)
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=24),
            text_color=icon_color
        )
        self.icon_label.grid(row=0, column=0, padx=SPACING["md"], pady=SPACING["sm"])

        # Value and Label container (right side)
        value_label_container = ctk.CTkFrame(self, fg_color="transparent")
        value_label_container.grid(row=0, column=1, sticky="ew", padx=(0, SPACING["md"]), pady=SPACING["sm"])
        value_label_container.grid_columnconfigure(0, weight=1)

        # Value (top text, larger, bold)
        self.value_label = ctk.CTkLabel(
            value_label_container,
            text=value,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=colors["text_primary"],
            anchor="w"
        )
        self.value_label.grid(row=0, column=0, sticky="w")

        # Label (bottom text, smaller, muted)
        self.label_label = ctk.CTkLabel(
            value_label_container,
            text=label,
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=colors["text_secondary"],
            anchor="w"
        )
        self.label_label.grid(row=1, column=0, sticky="w")

    def update_value(self, new_value: str):
        """
        Update the value displayed

        Args:
            new_value: New value string to display
        """
        self.value_label.configure(text=new_value)

    def update_label(self, new_label: str):
        """
        Update the label text

        Args:
            new_label: New label text
        """
        self.label_label.configure(text=new_label)

    def update_icon_color(self, new_color: str):
        """
        Update the icon color

        Args:
            new_color: New color for icon
        """
        self.icon_label.configure(text_color=new_color)

    def set_hover_effect(self, enabled: bool = True):
        """
        Enable or disable hover effect

        Args:
            enabled: Whether to enable hover effect
        """
        colors = theme_manager.get_colors()

        if enabled:
            def on_enter(event):
                self.configure(border_color=colors["accent"], border_width=2)

            def on_leave(event):
                self.configure(
                    border_color=colors.get("border_subtle", colors["border"]),
                    border_width=1
                )

            self.bind("<Enter>", on_enter)
            self.bind("<Leave>", on_leave)
        else:
            # Unbind any existing hover events
            self.unbind("<Enter>")
            self.unbind("<Leave>")
