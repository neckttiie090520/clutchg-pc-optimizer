"""
ClutchG - Risk Badge Component
Reusable risk indicator with icon and color coding
"""

import customtkinter as ctk
from gui.theme import COLORS
from gui.style import font


class RiskBadge(ctk.CTkFrame):
    """
    A reusable risk indicator badge component.

    Displays risk level with:
    - Colored left border strip (4px)
    - Icon (triangle/circle indicator)
    - Label text
    - Optional tooltip
    """

    def __init__(self, parent, risk_level: str, label: str, show_border: bool = True, size: str = "medium"):
        """
        Initialize risk badge.

        Args:
            parent: Parent widget
            risk_level: One of "LOW", "MEDIUM", "HIGH"
            label: Text label to display (e.g., "LOW RISK", "MEDIUM RISK")
            show_border: Whether to show colored left border strip
            size: "small", "medium", or "large"
        """
        super().__init__(parent, fg_color="transparent")

        # Get risk color from theme
        self.risk_color = self._get_risk_color(risk_level)
        self.risk_level = risk_level

        # Size configurations
        sizes = {
            "small": {"height": 24, "font_size": 11, "border_width": 3},
            "medium": {"height": 28, "font_size": 12, "border_width": 4},
            "large": {"height": 32, "font_size": 13, "border_width": 5}
        }
        size_config = sizes.get(size, sizes["medium"])

        # Configure frame
        self.configure(height=size_config["height"], fg_color="transparent")

        # Colored border strip (left side)
        if show_border:
            border = ctk.CTkFrame(
                self,
                width=size_config["border_width"],
                fg_color=self.risk_color,
                corner_radius=0
            )
            border.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        # Icon based on risk level
        icon = self._get_risk_icon(risk_level)

        # Risk label
        label_widget = ctk.CTkLabel(
            self,
            text=f"{icon}  {label}",
            font=font("caption", size=size_config["font_size"], weight="bold"),
            text_color=self.risk_color
        )
        label_widget.grid(row=0, column=1, sticky="w")

        self.grid_columnconfigure(1, weight=1)

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level from theme"""
        risk_colors = {
            "LOW": COLORS["risk_low"],      # Green
            "MEDIUM": COLORS["risk_medium"],  # Orange
            "HIGH": COLORS["risk_high"],     # Red
            "SAFE": COLORS["risk_low"],      # Alias for LOW
            "CAUTION": COLORS["risk_medium"], # Alias for MEDIUM
            "ADVANCED": COLORS["risk_high"],  # Alias for HIGH
        }
        return risk_colors.get(risk_level.upper(), COLORS["risk_medium"])

    def _get_risk_icon(self, risk_level: str) -> str:
        """Get icon for risk level"""
        risk_icons = {
            "LOW": "🛡️",      # Shield
            "MEDIUM": "⚠️",   # Warning
            "HIGH": "🔥",     # Fire
            "SAFE": "🛡️",
            "CAUTION": "⚠️",
            "ADVANCED": "🔥"
        }
        return risk_icons.get(risk_level.upper(), "⚠️")


class RiskIndicator(ctk.CTkLabel):
    """
    Simplified risk indicator for inline use (smaller, just icon).

    Usage:
        risk_indicator = RiskIndicator(parent, risk_level="LOW")
        risk_indicator.pack()
    """

    def __init__(self, parent, risk_level: str, size: int = 16):
        """
        Initialize simplified risk indicator.

        Args:
            parent: Parent widget
            risk_level: One of "LOW", "MEDIUM", "HIGH"
            size: Icon size in pixels
        """
        # Get icon and color
        icon = self._get_risk_icon(risk_level)
        color = self._get_risk_color(risk_level)

        super().__init__(
            parent,
            text=icon,
            font=font("body", size=size),
            text_color=color
        )

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level from theme"""
        risk_colors = {
            "LOW": COLORS["risk_low"],
            "MEDIUM": COLORS["risk_medium"],
            "HIGH": COLORS["risk_high"],
        }
        return risk_colors.get(risk_level.upper(), COLORS["risk_medium"])

    def _get_risk_icon(self, risk_level: str) -> str:
        """Get icon for risk level"""
        risk_icons = {
            "LOW": "🛡️",
            "MEDIUM": "⚠️",
            "HIGH": "🔥",
        }
        return risk_icons.get(risk_level.upper(), "⚠️")


def add_risk_tooltip(widget, risk_level: str, explanation_key: str = None):
    """
    Add risk-aware tooltip to a widget.

    Args:
        widget: Widget to attach tooltip to
        risk_level: Risk level ("LOW", "MEDIUM", "HIGH")
        explanation_key: Optional key for detailed explanation (e.g., "risk_low_profile")

    Usage:
        button = ctk.CTkButton(parent, text="Apply")
        add_risk_tooltip(button, "MEDIUM", "risk_competitive_profile")
    """
    from gui.components.tooltip import ToolTip

    # Default explanations by risk level
    explanations = {
        "LOW": "✓ Safe for daily use - No system impact expected",
        "MEDIUM": "⚠ Use with caution - May affect some features",
        "HIGH": "🔥 Advanced users only - Can cause system changes",
    }

    tooltip_text = explanations.get(risk_level.upper(), explanations["MEDIUM"])

    # Add tooltip (will integrate with tooltip.py later for clickable links)
    tooltip = ToolTip(widget, tooltip_text)

    return tooltip
