"""
View Transition System for ClutchG
Smooth fade transitions between views
"""

import customtkinter as ctk
from typing import Callable, Optional
from gui.theme import theme_manager, ANIMATION


class ViewTransition:
    """Manages smooth view transitions with fade effects"""

    def __init__(self, parent_frame, app):
        """
        Initialize view transition manager

        Args:
            parent_frame: The frame that will contain the views
            app: Reference to main app for theme access
        """
        self.parent = parent_frame
        self.app = app
        self.current_widget = None
        self.transitioning = False

    def transition_to(self, view_builder: Callable, duration: int = None):
        """
        Transition to new view with fade effect

        Args:
            view_builder: Callable that creates and returns the new view widget
            duration: Transition duration in ms (default: ANIMATION["normal"])
        """
        if duration is None:
            duration = ANIMATION["normal"]

        if self.transitioning:
            return  # Already transitioning, ignore

        old_view = self.current_widget

        if old_view is None:
            # No current view, just create new one
            new_view = view_builder()
            new_view.grid(row=0, column=0, sticky="nsew")
            self.current_widget = new_view
            return

        self.transitioning = True

        # Fade out old view
        self.fade_out(old_view, duration, lambda: self._create_new_view(view_builder, duration))

    def _create_new_view(self, view_builder: Callable, duration: int):
        """Create new view and fade it in"""
        # Destroy old view
        if self.current_view_exists():
            self.current_widget.destroy()

        # Create new view with error handling
        try:
            new_view = view_builder()
        except Exception as e:
            import traceback
            traceback.print_exc()
            new_view = self._create_error_view(str(e))

        new_view.grid(row=0, column=0, sticky="nsew")

        self.current_widget = new_view

        # Fade in new view
        self.fade_in(new_view, duration, lambda: setattr(self, 'transitioning', False))

    def current_view_exists(self) -> bool:
        """Check if current view widget still exists"""
        if self.current_widget is None:
            return False
        try:
            self.current_widget.winfo_exists()
            return True
        except Exception:
            return False

    def fade_out(self, widget, duration: int, callback: Optional[Callable] = None):
        """
        Fade widget from current opacity to 0

        Since CustomTkinter doesn't support alpha transparency directly,
        we simulate this by placing a semi-transparent overlay.

        Args:
            widget: Widget to fade out
            duration: Fade duration in ms
            callback: Function to call when fade completes
        """
        self._animate_opacity(widget, 1.0, 0.0, duration, callback)

    def fade_in(self, widget, duration: int, callback: Optional[Callable] = None):
        """
        Fade widget from 0 to full opacity

        Args:
            widget: Widget to fade in
            duration: Fade duration in ms
            callback: Function to call when fade completes
        """
        self._animate_opacity(widget, 0.0, 1.0, duration, callback)

    def _animate_opacity(self, widget, start: float, end: float,
                        duration: int, callback: Optional[Callable] = None):
        """
        Animate widget opacity (simulated with overlay)

        Note: CustomTkinter doesn't support direct opacity on widgets.
        We simulate this with a temporary overlay frame that transitions
        from transparent to the background color.

        Args:
            widget: Widget to animate
            start: Starting opacity (0.0 to 1.0)
            end: Ending opacity (0.0 to 1.0)
            duration: Animation duration in ms
            callback: Function to call when animation completes
        """
        steps = 20
        step_duration = duration // steps
        step_size = (end - start) / steps

        # Get current theme background color
        colors = theme_manager.get_colors()
        bg_color = colors["bg_primary"]

        # Create overlay if fading in
        overlay = None
        if end > start:  # Fading in (start transparent, end opaque)
            overlay = ctk.CTkFrame(
                widget,
                fg_color=bg_color,
                corner_radius=0
            )
            overlay.place(x=0, y=0, relwidth=1, relheight=1)
            widget._fade_overlay = overlay

        def step(current_step):
            if current_step >= steps:
                # Animation complete
                if callback:
                    callback()
                # Clean up overlay if it exists
                if hasattr(widget, '_fade_overlay') and widget._fade_overlay:
                    if end > start:  # Fading in, remove overlay
                        widget._fade_overlay.destroy()
                        delattr(widget, '_fade_overlay')
                return

            # Calculate current opacity
            opacity = start + (step_size * current_step)

            # For fade out: create/update overlay
            if end < start:  # Fading out
                if not hasattr(widget, '_fade_overlay'):
                    overlay = ctk.CTkFrame(
                        widget,
                        fg_color=bg_color,
                        corner_radius=0
                    )
                    overlay.place(x=0, y=0, relwidth=1, relheight=1)
                    widget._fade_overlay = overlay

                # Simulate opacity by adjusting overlay color
                # (This is a simplification - true opacity would require
                # more complex color blending)
                if current_step >= steps - 1:  # Final step - fully cover
                    widget._fade_overlay.configure(fg_color=bg_color)

            # Schedule next step
            widget.after(step_duration, lambda: step(current_step + 1))

        step(0)

    def immediate_transition(self, view_builder: Callable):
        """
        Immediately switch views without animation

        Useful for initialization or when animation is not desired.

        Args:
            view_builder: Callable that creates and returns the new view widget
        """
        # Destroy current view if exists
        if self.current_view_exists():
            self.current_widget.destroy()

        # Create new view with error handling
        try:
            new_view = view_builder()
        except Exception as e:
            import traceback
            traceback.print_exc()
            new_view = self._create_error_view(str(e))

        new_view.grid(row=0, column=0, sticky="nsew")

        self.current_widget = new_view
        self.transitioning = False

    def _create_error_view(self, error_message: str) -> ctk.CTkFrame:
        """Create a view to display an error message"""
        colors = theme_manager.get_colors()
        
        frame = ctk.CTkFrame(self.parent, fg_color=colors["bg_primary"])
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Error Icon
        ctk.CTkLabel(
            content,
            text="❌",
            font=ctk.CTkFont(size=48),
            text_color=colors["danger"]
        ).pack(pady=(0, 20))
        
        # Title
        ctk.CTkLabel(
            content,
            text="Error Loading View",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=colors["text_primary"]
        ).pack(pady=(0, 10))
        
        # Message
        ctk.CTkLabel(
            content,
            text=f"An error occurred while loading this view:\n\n{error_message}",
            font=ctk.CTkFont(size=14),
            text_color=colors["text_secondary"],
            wraplength=600,
            justify="center"
        ).pack()
        
        return frame
