"""
ClutchG - Context Help Button Component
Help button with "?" icon for contextual assistance
"""

import customtkinter as ctk
from gui.theme import COLORS, SIZES
from gui.style import font


class ContextHelpButton(ctk.CTkButton):
    """
    A help button with "?" icon that opens contextual help.

    Features:
    - Circular "?" button
    - Clickable to open help topic
    - Optional tooltip on hover
    - Integrates with HelpManager for topic lookup
    """

    def __init__(
        self,
        parent,
        app,
        topic_id: str,
        size: str = "medium",
        tooltip_text: str = None
    ):
        """
        Initialize context help button.

        Args:
            parent: Parent widget
            app: ClutchGApp instance (for HelpManager access)
            topic_id: Help topic ID (e.g., "risk_levels", "profiles")
            size: "small", "medium", or "large"
            tooltip_text: Optional tooltip text for hover
        """
        self.app = app
        self.topic_id = topic_id

        # Size configurations
        sizes = {
            "small": {"width": 28, "height": 28, "font_size": 14},
            "medium": {"width": 32, "height": 32, "font_size": 16},
            "large": {"width": 36, "height": 36, "font_size": 18}
        }
        size_config = sizes.get(size, sizes["medium"])

        super().__init__(
            parent,
            width=size_config["width"],
            height=size_config["height"],
            text="?",
            font=font("body_bold", size=size_config["font_size"], weight="bold"),
            fg_color=COLORS["bg_secondary"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_secondary"],
            corner_radius=int(size_config["width"] / 2),
            border_width=1,
            border_color=COLORS["border"]
        )

        # Add tooltip if provided
        if tooltip_text:
            from gui.components.tooltip import ToolTip
            ToolTip(self, tooltip_text)

        # Bind click event
        self.configure(command=self._open_help)

    def _open_help(self):
        """Open help topic in HelpView."""
        # Switch to help view with specific topic
        if hasattr(self.app, 'switch_view'):
            self.app.switch_view("help")
            # Navigate to specific topic (if HelpView supports it)
            if hasattr(self.app, 'help_manager'):
                # Could add topic highlighting here
                pass


# InlineHelpBox has been consolidated into gui.components.inline_help.
# Import from there: from gui.components.inline_help import InlineHelpBox


def add_contextual_help(widget, app, topic_id: str, tooltip_text: str = None):
    """
    Convenience function to add contextual help button to a widget.

    Usage:
        button = ctk.CTkButton(parent, text="Apply")
        add_contextual_help(button, app, "risk_levels", "Learn about risk levels")
    """
    help_button = ContextHelpButton(
        widget,
        app,
        topic_id,
        size="small",
        tooltip_text=tooltip_text
    )
    help_button.pack(side="left", padx=(8, 0))

    return help_button
