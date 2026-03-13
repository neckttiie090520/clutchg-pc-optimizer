"""
Enhanced Button Components for ClutchG
Multiple button variants with gradient support
"""

import customtkinter as ctk
from gui.theme import theme_manager, RADIUS, SPACING
from gui.components.gradient import GradientButton
from gui.components.icon_provider import get_icon_provider
from typing import Optional, Callable


# Get icon provider instance
icon_provider = get_icon_provider()


class EnhancedButton:
    """Factory for creating enhanced buttons with different styles"""
    
    @staticmethod
    def primary(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        **kwargs
    ):
        """
        Primary button with cyan-to-purple gradient
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
        """
        colors = theme_manager.get_colors()
        
        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)

        return GradientButton(
            master,
            text=text,
            command=command,
            # Use theme accent colors (solid/flat if accent==accent_secondary)
            colors=[colors["accent"], colors["accent_secondary"]], 
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=colors.get("text_on_accent", "#FFFFFF"),
            **kwargs
        )
    
    @staticmethod
    def success(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        **kwargs
    ):
        """
        Success button with green gradient
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
        """
        colors = theme_manager.get_colors()

        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)

        return GradientButton(
            master,
            text=text,
            command=command,
            # Use theme success color (solid)
            colors=[colors["success"], colors["success"]],
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#FFFFFF",
            **kwargs
        )
    
    @staticmethod
    def warning(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        **kwargs
    ):
        """
        Warning button with red/pink gradient
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
        """
        colors = theme_manager.get_colors()

        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)

        return GradientButton(
            master,
            text=text,
            command=command,
            # Use theme warning color (solid)
            colors=[colors["warning"], colors["warning"]],
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#FFFFFF",
            **kwargs
        )
    
    @staticmethod
    def danger(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        **kwargs
    ):
        """
        Danger button with red gradient (alias for warning)
        """
        colors = theme_manager.get_colors()
        
        return GradientButton(
            master,
            text=text,
            command=command,
            # Use theme danger color (solid)
            colors=[colors["danger"], colors["danger"]], 
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#FFFFFF",
            **kwargs
        )
    

    
    @staticmethod
    def info(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        **kwargs
    ):
        """
        Info button with blue gradient
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
        """
        colors = theme_manager.get_colors()

        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)

        return GradientButton(
            master,
            text=text,
            command=command,
            # Use theme info color (solid)
            colors=[colors["info"], colors["info"]],
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#FFFFFF",
            **kwargs
        )
    
    @staticmethod
    def outline(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        border_color: Optional[str] = None,
        **kwargs
    ):
        """
        Outline button (transparent with border)
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
            border_color: Custom border color (optional)
        """
        colors = theme_manager.get_colors()

        if border_color is None:
            border_color = colors["border_medium"]

        # Pop text_color from kwargs if provided, otherwise use default
        text_color = kwargs.pop("text_color", colors["text_secondary"])

        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)

        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            fg_color="transparent",
            border_width=2,
            border_color=border_color,
            text_color=text_color,
            hover_color=colors["bg_hover"],
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14),
            **kwargs
        )
    
    @staticmethod
    def ghost(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        **kwargs
    ):
        """
        Ghost button (transparent, no border)
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
        """
        colors = theme_manager.get_colors()
        
        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)
        
        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            fg_color="transparent",
            border_width=0,
            text_color=colors["text_secondary"],
            hover_color=colors["bg_hover"],
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14),
            **kwargs
        )
    
    @staticmethod
    def solid(
        master,
        text: str,
        command: Optional[Callable] = None,
        width: Optional[int] = None,
        height: int = 40,
        color: Optional[str] = None,
        **kwargs
    ):
        """
        Solid color button (no gradient)
        
        Args:
            master: Parent widget
            text: Button text
            command: Click callback
            width: Button width (optional)
            height: Button height
            color: Custom color (optional, defaults to accent)
        """
        colors = theme_manager.get_colors()
        
        if color is None:
            color = colors["accent"]
        
        # Pop conflicting kwargs
        kwargs.pop("font", None)
        kwargs.pop("text_color", None)
        
        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            fg_color=color,
            hover_color=colors["accent_hover"],
            corner_radius=RADIUS["md"],
            height=height,
            width=width if width else 140,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=colors.get("text_on_accent", "#FFFFFF") if color == colors["accent"] else "#FFFFFF",
            border_width=0,
            **kwargs
        )


class IconButton(ctk.CTkButton):
    """Button with icon (Material Symbols)"""
    
    def __init__(
        self,
        master,
        icon: str,
        command: Optional[Callable] = None,
        size: int = 32,
        icon_size: int = 20,
        tooltip: Optional[str] = None,
        **kwargs
    ):
        """
        Create an icon button
        
        Args:
            master: Parent widget
            icon: Material Symbol unicode character
            command: Click callback
            size: Button size (width and height)
            icon_size: Icon font size
            tooltip: Tooltip text (optional)
        """
        colors = theme_manager.get_colors()
        
        super().__init__(
            master,
            text=icon,
            command=command,
            width=size,
            height=size,
            fg_color="transparent",
            hover_color=colors["bg_hover"],
            text_color=colors["text_secondary"],
            font=ctk.CTkFont(family=icon_provider.get_icon_font()[0], size=icon_size),
            corner_radius=RADIUS["md"],
            **kwargs
        )
        
        # Add tooltip if provided
        if tooltip:
            from gui.components.tooltip import ToolTip
            ToolTip(self, tooltip)
