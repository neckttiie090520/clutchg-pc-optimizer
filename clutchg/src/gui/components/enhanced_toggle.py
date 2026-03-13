"""
EnhancedToggle Component - Modern Toggle Switches (QuickBoost Style)
Purpose: Replace CTkSwitch and CTkCheckBox with modern, color-coded toggles
"""

import customtkinter as ctk
from gui.theme import theme_manager, SPACING, RADIUS
from typing import Callable, Optional


class EnhancedToggle(ctk.CTkFrame):
    """
    Modern toggle switch with color-coded states
    - ON: Green accent color
    - OFF: Gray muted color
    - Size: 44x24px (compact)
    - Static transitions (no animation per user preference)
    """

    def __init__(
        self,
        master,
        text: str = "",
        state: bool = False,
        command: Optional[Callable[[bool], None]] = None,
        width: int = 44,
        height: int = 24,
        **kwargs
    ):
        """
        Create a modern toggle switch

        Args:
            master: Parent widget
            text: Label text displayed next to toggle
            state: Initial state (True=on, False=off)
            command: Callback function when toggle state changes
            width: Toggle width (default: 44px)
            height: Toggle height (default: 24px)
        """
        colors = theme_manager.get_colors()

        # Transparent container
        super().__init__(master, fg_color="transparent", **kwargs)

        self.state = state
        self.command = command
        self.width = width
        self.height = height

        # Configure grid layout
        self.grid_columnconfigure(1, weight=0)  # Toggle track doesn't expand

        # Text label (if provided)
        if text:
            self.text_label = ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color=colors["text_secondary"],
                anchor="w"
            )
            self.text_label.grid(row=0, column=0, padx=(0, SPACING["sm"]), pady=SPACING["xs"])
            self.text_label.bind("<Button-1>", self._on_click)

        # Toggle track (background)
        self.track = ctk.CTkFrame(
            self,
            width=width,
            height=height,
            corner_radius=RADIUS["full"],
            cursor="hand2"
        )
        self.track.grid(row=0, column=1, pady=SPACING["xs"])
        self.track.bind("<Button-1>", self._on_click)

        # Toggle thumb (circle)
        self.thumb_size = height - 6  # 6px smaller than track height
        self.thumb = ctk.CTkFrame(
            self.track,
            width=self.thumb_size,
            height=self.thumb_size,
            corner_radius=RADIUS["full"],
            cursor="hand2"
        )
        self.thumb.place(x=3, rely=0.5, y=0, anchor="w")
        self.thumb.bind("<Button-1>", self._on_click)

        # Set initial visual state
        self._update_visuals()

    def _on_click(self, event=None):
        """Handle toggle click"""
        self.state = not self.state
        self._update_visuals()

        # Call command if provided
        if self.command:
            self.command(self.state)

    def _update_visuals(self):
        """Update visual appearance based on state"""
        colors = theme_manager.get_colors()

        if self.state:
            # ON state: Green accent
            self.track.configure(
                fg_color=colors.get("success", "#22C55E"),
                border_width=0
            )
            self.thumb.configure(fg_color=colors["text_primary"])
            # Move thumb to right
            self.thumb.place(
                x=self.width - self.thumb_size - 3,
                rely=0.5,
                y=0,
                anchor="w"
            )
        else:
            # OFF state: Gray
            self.track.configure(
                fg_color=colors.get("bg_active", colors["bg_tertiary"]),
                border_width=1,
                border_color=colors.get("border", colors["bg_tertiary"])
            )
            self.thumb.configure(fg_color=colors["text_muted"])
            # Move thumb to left
            self.thumb.place(x=3, rely=0.5, y=0, anchor="w")

    def set(self, value: bool):
        """
        Set toggle state programmatically

        Args:
            value: New state (True=on, False=off)
        """
        if self.state != value:
            self.state = value
            self._update_visuals()

    def get(self) -> bool:
        """
        Get current toggle state

        Returns:
            Current state (True=on, False=off)
        """
        return self.state

    def configure(self, **kwargs):
        """
        Override configure to handle text updates

        Args:
            **kwargs: Configuration options
        """
        if "text" in kwargs and hasattr(self, "text_label"):
            self.text_label.configure(text=kwargs.pop("text"))

        super().configure(**kwargs)

    def set_hover_effect(self, enabled: bool = True):
        """
        Enable or disable hover effect

        Args:
            enabled: Whether to enable hover effect
        """
        colors = theme_manager.get_colors()

        if enabled:
            def on_enter(event):
                if not self.state:
                    # Lighten track on hover when OFF
                    self.track.configure(
                        fg_color=colors.get("bg_hover", colors["bg_active"])
                    )

            def on_leave(event):
                if not self.state:
                    # Return to normal when OFF
                    self.track.configure(
                        fg_color=colors.get("bg_active", colors["bg_tertiary"])
                    )

            self.track.bind("<Enter>", on_enter)
            self.track.bind("<Leave>", on_leave)
            self.thumb.bind("<Enter>", on_enter)
            self.thumb.bind("<Leave>", on_leave)
        else:
            # Unbind any existing hover events
            self.track.unbind("<Enter>")
            self.track.unbind("<Leave>")
            self.thumb.unbind("<Enter>")
            self.thumb.unbind("<Leave>")

    def enable(self):
        """Enable the toggle (interactive)"""
        self.track.configure(state="normal")
        self.thumb.configure(state="normal")
        if hasattr(self, "text_label"):
            self.text_label.configure(state="normal")

    def disable(self):
        """Disable the toggle (non-interactive)"""
        self.track.configure(state="disabled")
        self.thumb.configure(state="disabled")
        if hasattr(self, "text_label"):
            self.text_label.configure(state="disabled")
