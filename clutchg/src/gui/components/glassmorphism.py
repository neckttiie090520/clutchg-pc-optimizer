"""
Glassmorphism Components for ClutchG
Simulated glass/acrylic effects for CustomTkinter
"""

import customtkinter as ctk
from typing import Optional
from gui.theme import theme_manager, SIZES


class GlassmorphismCard(ctk.CTkFrame):
    """
    Card with glassmorphism effect

    Simulates glass using:
    - Semi-transparent background (simulated via color)
    - Subtle borders with highlights
    - Inner glow effect

    Args:
        parent: Parent widget
        intensity: "low", "medium", or "high" glass effect
        **kwargs: Additional CTkFrame arguments
    """

    def __init__(self, parent, intensity: str = "medium", **kwargs):
        # Get current theme colors
        colors = theme_manager.get_colors()

        # Determine glass colors based on theme and intensity
        self.glass_colors = self._get_glass_colors(colors, intensity)

        # Remove fg_color from kwargs if present, we'll set it ourselves
        kwargs.pop('fg_color', None)

        # Configure frame with glass effect colors
        super().__init__(
            parent,
            fg_color=self.glass_colors["bg"],
            border_color=self.glass_colors["border"],
            border_width=1,
            corner_radius=SIZES["card_radius"],
            **kwargs
        )

        # Create inner highlight (top border simulation for depth)
        self._create_highlight()

    def _get_glass_colors(self, theme_colors: dict, intensity: str) -> dict:
        """Calculate glass effect colors based on theme and intensity"""
        theme = theme_manager.current_theme

        # Base colors from theme
        if theme == "dark":
            base_bg = theme_colors["bg_card"]
            base_border = theme_colors["border"]
        else:
            base_bg = theme_colors["bg_card"]
            base_border = theme_colors["border"]

        # Intensity adjustments (simulated transparency)
        # Higher intensity = more "glassy" appearance
        intensity_map = {
            "low": {"bg_offset": 0, "border_lighten": 5},
            "medium": {"bg_offset": 0, "border_lighten": 15},
            "high": {"bg_offset": 0, "border_lighten": 25},
        }

        adjustments = intensity_map.get(intensity, intensity_map["medium"])

        return {
            "bg": base_bg,
            "border": base_border,
            "highlight": self._lighten_color(base_border, adjustments["border_lighten"]),
            "theme": theme,
        }

    def _lighten_color(self, hex_color: str, amount: int) -> str:
        """Lighten a hex color by specified amount"""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Lighten
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _darken_color(self, hex_color: str, amount: int) -> str:
        """Darken a hex color by specified amount"""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Darken
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _create_highlight(self):
        """Create subtle top border highlight for depth"""
        # Store reference for redraw on resize
        self._highlight_widget = None

        # Create highlight frame
        self._draw_highlight()

        # Bind configure event to redraw highlight on resize
        self.bind("<Configure>", self._on_resize)

    def _draw_highlight(self):
        """Draw the highlight line at the top"""
        if self._highlight_widget:
            self._highlight_widget.destroy()

        # Calculate width (account for padding)
        width = self.winfo_width()
        if width <= 1:  # Not yet mapped
            return

        # Create highlight frame (thin top border)
        highlight = ctk.CTkFrame(
            self,
            height=1,
            fg_color=self.glass_colors["highlight"],
            corner_radius=0
        )
        # Position at top with padding
        highlight.place(x=8, y=0, width=max(1, width - 16), anchor="nw")
        self._highlight_widget = highlight

    def _on_resize(self, event=None):
        """Handle resize event to redraw highlight"""
        # Schedule redraw to avoid issues during initialization
        self.after(10, self._draw_highlight)


def create_blur_background(image_path: str, blur_radius: int = 20) -> Optional[ctk.CTkImage]:
    """
    Create a blurred background image from a file

    Useful for creating backdrop effects behind glass cards.
    Requires PIL (Pillow).

    Args:
        image_path: Path to image file
        blur_radius: Blur radius (higher = more blur)

    Returns:
        CTkImage object or None if failed
    """
    try:
        from PIL import Image as PILImage, ImageFilter

        # Open and blur image
        img = PILImage.open(image_path)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Convert to CTkImage
        return ctk.CTkImage(blurred, size=blurred.size)
    except Exception as e:
        print(f"Warning: Failed to create blur background: {e}")
        return None


def blend_colors(color1: str, color2: str, ratio: float) -> str:
    """
    Blend two hex colors together

    Args:
        color1: First hex color (e.g., "#00C6FF")
        color2: Second hex color
        ratio: Blend ratio (0.0 = all color1, 1.0 = all color2)

    Returns:
        Blended hex color
    """
    # Parse hex to RGB
    c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
    c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))

    # Interpolate
    result = tuple(int(c1[i] + (c2[i] - c1[i]) * ratio) for i in range(3))

    # Return hex
    return f"#{result[0]:02x}{result[1]:02x}{result[2]:02x}"
