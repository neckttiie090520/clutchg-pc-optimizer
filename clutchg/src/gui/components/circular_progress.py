"""
Circular Progress Component for ClutchG
Beautiful circular progress indicator with gradient support
"""

import customtkinter as ctk
from tkinter import Canvas
from typing import List, Tuple
import math
from gui.theme import theme_manager


class CircularProgress(ctk.CTkFrame):
    """
    Circular progress ring with gradient effect
    Enhanced: Larger default size (240px), static rendering, improved typography
    """

    def __init__(
        self,
        master,
        size: int = 240,  # Increased from 200 to 240 (per UI redesign plan)
        thickness: int = 20,
        value: float = 0,
        max_value: float = 100,
        colors: List[str] = None,
        bg_color: str = None,
        show_value: bool = True,
        value_font: Tuple = None,
        **kwargs
    ):
        """
        Create a circular progress indicator

        Args:
            master: Parent widget
            size: Diameter of the circle (default: 240px, larger for better visibility)
            thickness: Thickness of the ring
            value: Current value
            max_value: Maximum value
            colors: List of 2 colors for gradient [start, end]
            bg_color: Background color
            show_value: Whether to show value text in center
            value_font: Font for value text (family, size, weight)
        """
        theme_colors = theme_manager.get_colors()

        if colors is None:
            # Use theme accent (monotone if accent==accent_secondary)
            colors = [theme_colors["accent"], theme_colors["accent_secondary"]]

        if bg_color is None:
            bg_color = theme_colors["bg_card"]

        if value_font is None:
            # Improved typography: larger font for 240px ring
            value_font = ("Inter", 56, "bold")  # Increased from 48 to 56
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.size = size
        self.thickness = thickness
        self.value = value
        self.max_value = max_value
        self.colors = colors
        self.bg_color = bg_color
        self.show_value = show_value
        self.value_font = value_font
        
        # Create canvas
        self.canvas = Canvas(
            self,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Create value label if needed
        if show_value:
            self.value_label = ctk.CTkLabel(
                self,
                text=str(int(value)),
                font=ctk.CTkFont(family=value_font[0], size=value_font[1], weight=value_font[2]),
                text_color=theme_colors["text_primary"]
            )
            self.value_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Draw initial state
        self.draw_ring()
    
    def set_value(self, value: float, animate: bool = False):
        """
        Update progress value
        
        Args:
            value: New value
            animate: Whether to animate the change (not implemented yet)
        """
        self.value = min(max(0, value), self.max_value)
        self.draw_ring()
        
        if self.show_value and hasattr(self, 'value_label'):
            self.value_label.configure(text=str(int(self.value)))
    
    def draw_ring(self):
        """Draw the circular progress"""
        theme_colors = theme_manager.get_colors()

        self.canvas.delete("all")
        
        # Calculate dimensions
        # Calculate dimensions
        center = self.size / 2
        radius = (self.size - self.thickness) / 2
        
        # Draw background track
        self.canvas.create_oval(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            # Use 'bg_active' or 'border' so it stands out against 'bg_card'
            outline=theme_colors.get("bg_active", "#323D54"),
            width=self.thickness,
            tags="bg"
        )
        
        # Calculate progress angle
        progress_ratio = self.value / self.max_value
        extent = -(progress_ratio * 360)  # Negative for clockwise (CW)
        
        # Optimization: Draw solid arc if colors are identical (ANTI-ALIASING FIX)
        # Gradient drawing (multiple small arcs) causes pixelation/aliasing.
        # Single arc is vector-smooth.
        if not self.colors or len(self.colors) < 2 or self.colors[0] == self.colors[1]:
            color = self.colors[0] if self.colors else theme_colors["accent"]
            
            self.canvas.create_arc(
                center - radius,
                center - radius,
                center + radius,
                center + radius,
                start=90,
                extent=extent,
                outline=color,
                width=self.thickness,
                style="arc",
                tags="progress"
            )
        else:
            # Gradient fallback (only used if colors differ)
            steps = max(1, int(abs(extent)))
            
            for i in range(steps):
                t = i / max(1, steps - 1) if steps > 1 else 0
                color = self._interpolate_color(t)
                
                # Draw Clockwise (CW)
                step_extent = extent / steps
                # Start at 90 and move CW (negative extent means decreasing angle)
                # i=0 -> start=90
                # i=1 -> start=90 + step_extent (which is negative)
                start_angle = 90 + (extent * i / steps)
                
                self.canvas.create_arc(
                    center - radius,
                    center - radius,
                    center + radius,
                    center + radius,
                    start=start_angle,
                    extent=step_extent * 1.5, # Slight overlap to reduce gaps
                    outline=color,
                    width=self.thickness,
                    style="arc",
                    tags="progress"
                )
    
    def _interpolate_color(self, t: float) -> str:
        """Interpolate between gradient colors"""
        if len(self.colors) < 2:
            return self.colors[0] if self.colors else "#00f2fe"
        
        c1 = self._hex_to_rgb(self.colors[0])
        c2 = self._hex_to_rgb(self.colors[1])
        
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_color_for_value(self, value: float) -> str:
        """Get appropriate color based on value (for score-based coloring)"""
        theme_colors = theme_manager.get_colors()
        if value >= 80:
            return theme_colors["success"]  # Green
        elif value >= 60:
            return theme_colors["info"]  # Blue/Info
        elif value >= 40:
            return theme_colors["warning"]  # Orange
        else:
            return theme_colors["danger"]  # Red


class CircularProgressWithLabel(ctk.CTkFrame):
    """Circular progress with label below"""
    
    def __init__(
        self,
        master,
        size: int = 200,
        thickness: int = 20,
        value: float = 0,
        max_value: float = 100,
        colors: List[str] = None,
        label_text: str = "",
        **kwargs
    ):
        """
        Create circular progress with label
        
        Args:
            master: Parent widget
            size: Circle size
            thickness: Ring thickness
            value: Current value
            max_value: Maximum value
            colors: Gradient colors
            label_text: Text to show below circle
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Create progress circle
        self.progress = CircularProgress(
            self,
            size=size,
            thickness=thickness,
            value=value,
            max_value=max_value,
            colors=colors
        )
        self.progress.pack(pady=(0, 8))
        
        # Create label
        if label_text:
            self.label = ctk.CTkLabel(
                self,
                text=label_text,
                font=ctk.CTkFont(family="Inter", size=14),
                text_color="#A0AEC0"
            )
            self.label.pack()
    
    def set_value(self, value: float):
        """Update progress value"""
        self.progress.set_value(value)
    
    def set_label(self, text: str):
        """Update label text"""
        if hasattr(self, 'label'):
            self.label.configure(text=text)
