"""
Gradient components for ClutchG
Since CustomTkinter doesn't support CSS gradients natively,
we use Canvas to create gradient effects

Performance optimizations (2026-03-24):
- Reduced steps from 100 to 20 for better performance
- Solid color mode when colors are identical
- Cache support for gradient surfaces
"""

import customtkinter as ctk
from tkinter import Canvas
from typing import List, Tuple, Optional

# Cache for gradient surfaces (performance optimization)
_gradient_cache: dict = {}


def should_reduce_motion(app) -> bool:
    """Check if reduced motion is enabled in app config"""
    if app and hasattr(app, 'config') and isinstance(app.config, dict):
        return app.config.get('reduce_motion', False)
    return False


class GradientFrame(ctk.CTkFrame):
    """Frame with gradient background using Canvas"""

    def __init__(
        self,
        master,
        colors: List[str],
        direction: str = "horizontal",
        corner_radius: int = 0,
        **kwargs
    ):
        """
        Create a frame with gradient background

        Args:
            master: Parent widget
            colors: List of hex colors for gradient (2 colors)
            direction: "horizontal" or "vertical"
            corner_radius: Corner radius (limited support)
        """
        super().__init__(master, corner_radius=corner_radius, fg_color="transparent", **kwargs)

        self.colors = colors
        self.direction = direction
        self.corner_radius = corner_radius

        # Create canvas for gradient
        self.canvas = Canvas(
            self,
            highlightthickness=0,
            bg=colors[0] if colors else "#000000"
        )
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Bind resize to redraw gradient
        self.bind("<Configure>", self._draw_gradient)

    def _is_solid_color(self, colors: List[str]) -> bool:
        """Check if colors are identical (solid color mode)"""
        return len(colors) < 2 or colors[0] == colors[1]

    def _draw_gradient(self, event=None):
        """Draw gradient on canvas with performance optimizations"""
        self.canvas.delete("gradient")

        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 1 or height <= 1:
            return

        # OPTIMIZATION: Use solid color mode when colors are identical
        if self._is_solid_color(self.colors):
            self.canvas.create_rectangle(
                0, 0, width, height,
                fill=self.colors[0] if self.colors else "#000000",
                outline="",
                tags="gradient"
            )
            return

        # OPTIMIZATION: Reduced steps from 100 to 20
        steps = 20

        if self.direction == "horizontal":
            for i in range(steps):
                x1 = int(width * i / steps)
                x2 = int(width * (i + 1) / steps)

                # Interpolate color
                color = self._interpolate_color(i / steps)

                self.canvas.create_rectangle(
                    x1, 0, x2, height,
                    fill=color,
                    outline="",
                    tags="gradient"
                )
        else:  # vertical
            for i in range(steps):
                y1 = int(height * i / steps)
                y2 = int(height * (i + 1) / steps)

                color = self._interpolate_color(i / steps)

                self.canvas.create_rectangle(
                    0, y1, width, y2,
                    fill=color,
                    outline="",
                    tags="gradient"
                )

    def _interpolate_color(self, t: float) -> str:
        """Interpolate between colors"""
        if len(self.colors) < 2:
            return self.colors[0] if self.colors else "#000000"

        # Simple 2-color interpolation
        c1 = self._hex_to_rgb(self.colors[0])
        c2 = self._hex_to_rgb(self.colors[1])

        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class GradientButton(GradientFrame):
    """Button with gradient background"""

    def __init__(
        self,
        master,
        colors: List[str],
        text: str = "",
        command=None,
        corner_radius: int = 8,
        height: int = 40,
        width: Optional[int] = None,
        font=None,
        text_color=None,
        **kwargs
    ):
        """
        Create a button with gradient background

        Args:
            master: Parent widget
            colors: List of 2 hex colors for gradient
            text: Button text
            command: Click callback
            corner_radius: Corner radius
            height: Button height
            width: Button width (optional)
        """
        # Remove conflicting kwargs — callers may pass these via **kwargs
        kwargs.pop('fg_color', None)
        kwargs.pop('hover_color', None)

        super().__init__(
            master,
            colors=colors,
            corner_radius=corner_radius,
            height=height,
            width=width if width else 140,
            **kwargs
        )

        self.command = command
        self.gradient_colors = colors
        self.text_color = text_color if text_color else "#FFFFFF"
        self.text = text

        # Font setup
        if font:
            if isinstance(font, ctk.CTkFont):
                family = getattr(font, "family", getattr(font, "_family", "Inter"))
                size = getattr(font, "size", getattr(font, "_size", 14))
                weight = getattr(font, "weight", getattr(font, "_weight", "bold"))
                self.font_tuple = (family, size, weight)
            else:
                self.font_tuple = font
        else:
            self.font_tuple = ("Inter", 14, "bold")

        # Create text on canvas (z-index safe)
        self.text_id = self.canvas.create_text(
            0, 0, # Placeholder coords, updated in _draw_gradient
            text=self.text,
            fill=self.text_color,
            font=self.font_tuple,
            anchor="center",
            tags="text"
        )

        # Bind events for click and hover
        self.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Button-1>", self._on_click)

        self.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Enter>", self._on_enter)

        self.bind("<Leave>", self._on_leave)
        self.canvas.bind("<Leave>", self._on_leave)

        # Force a correct initial draw once the widget is fully laid out.
        # winfo_width/height return 1 during __init__, so schedule the first
        # redraw for after the event loop has processed the geometry pass.
        self.after_idle(self._draw_gradient)

    def _draw_gradient(self, event=None):
        """Draw gradient and update text position"""
        super()._draw_gradient(event)

        # Center text
        width = self.winfo_width()
        height = self.winfo_height()

        if self.text_id:
            self.canvas.coords(self.text_id, width/2, height/2)
            self.canvas.lift(self.text_id)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        """Hover effect - slightly lighter"""
        # Skip hover animation if reduce_motion is enabled
        if should_reduce_motion(None):
            self.configure(cursor="hand2")
            self.canvas.configure(cursor="hand2")
            return

        # Create lighter gradient
        lighter_colors = [self._lighten_color(c, 0.1) for c in self.gradient_colors]
        self.colors = lighter_colors
        self._draw_gradient()
        # Change cursor
        self.configure(cursor="hand2")
        self.canvas.configure(cursor="hand2")

    def _on_leave(self, event):
        """Remove hover effect"""
        # Skip animation if reduce_motion is enabled
        if should_reduce_motion(None):
            self.configure(cursor="")
            self.canvas.configure(cursor="")
            return

        self.colors = self.gradient_colors
        self._draw_gradient()
        self.configure(cursor="")
        self.canvas.configure(cursor="")

    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a hex color by amount (0-1)"""
        rgb = self._hex_to_rgb(hex_color)
        r = min(255, int(rgb[0] + (255 - rgb[0]) * amount))
        g = min(255, int(rgb[1] + (255 - rgb[1]) * amount))
        b = min(255, int(rgb[2] + (255 - rgb[2]) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"

    def configure(self, **kwargs):
        """Override configure to handle text updates"""
        if "text" in kwargs:
            self.text = kwargs.pop("text")
            self.canvas.itemconfigure(self.text_id, text=self.text)

        if "state" in kwargs:
            state = kwargs.pop("state")
            if state == "disabled":
                self.unbind("<Button-1>")
                self.canvas.unbind("<Button-1>")
                # Dim colors
                dim_colors = [self._lighten_color(c, -0.3) for c in self.gradient_colors] # Darken
                self.colors = dim_colors
                self._draw_gradient()
            else:
                self.bind("<Button-1>", self._on_click)
                self.canvas.bind("<Button-1>", self._on_click)
                self.colors = self.gradient_colors
                self._draw_gradient()

        super().configure(**kwargs)


class GradientLabel(ctk.CTkLabel):
    """Label with gradient text (simulated with colored background)"""

    def __init__(
        self,
        master,
        text: str = "",
        colors: List[str] = None,
        **kwargs
    ):
        """
        Create a label with gradient effect
        Note: True gradient text is not supported, this creates a gradient background

        Args:
            master: Parent widget
            text: Label text
            colors: Gradient colors
        """
        if colors is None:
            colors = ["#00f2fe", "#764ba2"]

        super().__init__(master, text=text, **kwargs)

        # Store gradient colors for future use
        self.gradient_colors = colors
