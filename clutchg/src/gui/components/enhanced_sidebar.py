"""
Enhanced Sidebar Component for ClutchG
Collapsible sidebar with animated transitions and hover effects
"""

import customtkinter as ctk
import logging
from pathlib import Path
from PIL import Image
from gui.theme import theme_manager, SIZES, RADIUS, NAV_ICONS, ANIMATION
from gui.style import font
from gui.components.tooltip import ToolTipBinder

logger = logging.getLogger(__name__)


class EnhancedSidebar(ctk.CTkFrame):
    """
    Enhanced sidebar with expand/collapse and animations

    Features:
    - Collapsible width (60px collapsed -> 210px expanded)
    - Animated labels on expand
    - Active indicator with glow effect
    - Hover effects with smooth transitions
    """

    def __init__(self, parent, app, width_collapsed=60, width_expanded=210):
        """
        Initialize enhanced sidebar

        Args:
            parent: Parent widget
            app: Reference to main ClutchGApp
            width_collapsed: Width when collapsed (default: 60px)
            width_expanded: Width when expanded (default: 210px)
        """
        colors = theme_manager.get_colors()

        super().__init__(
            parent,
            width=width_collapsed,
            corner_radius=0,
            fg_color=colors["bg_secondary"],
        )

        self.app = app
        self.width_collapsed = width_collapsed
        self.width_expanded = width_expanded
        self.is_expanded = False
        self.nav_buttons = {}
        self.animating = False
        self.glow_animations = {}  # Track active glow animations

        # CRITICAL: Prevent packed children from expanding the sidebar beyond
        # its configured width.  Without this the logo_frame, nav_container,
        # and toggle_button (all packed) would request their natural width and
        # the frame would grow to fit them — ignoring the width=width_collapsed
        # value we passed to the CTkFrame constructor.
        self.pack_propagate(False)

        self.setup_layout()
        self.create_toggle_button()
        self.create_navigation()

    def destroy(self):
        """Clean up glow animations before destroying sidebar."""
        # Stop all active glow animations
        for key in list(self.glow_animations.keys()):
            self.glow_animations[key] = False
        self.glow_animations.clear()
        super().destroy()

    def setup_layout(self):
        """Configure internal layout.

        Children are packed (not gridded) inside the sidebar, so
        grid_rowconfigure/grid_columnconfigure on *self* has no effect.
        The method is kept as a hook for future layout changes.
        """
        pass

    def create_navigation(self):
        """Create navigation buttons with enhanced styling"""
        colors = theme_manager.get_colors()

        # Logo area — icon + app name (name hidden when collapsed)
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=8, pady=12)
        logo_frame.grid_columnconfigure(0, weight=0)  # icon
        logo_frame.grid_columnconfigure(1, weight=1)  # name

        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self._logo_image = ctk.CTkImage(
                light_image=Image.open(icon_path),
                dark_image=Image.open(icon_path),
                size=(32, 32),
            )
            self.logo_label = ctk.CTkLabel(logo_frame, image=self._logo_image, text="")
        else:
            # Fallback: text "C" if icon not found
            self.logo_label = ctk.CTkLabel(
                logo_frame, text="C", font=font("title"), text_color=colors["accent"]
            )
        self.logo_label.grid(row=0, column=0, padx=(8, 4))

        # App name label — shown only when sidebar is expanded
        self.logo_name_label = ctk.CTkLabel(
            logo_frame,
            text="ClutchG",
            font=font("body", weight="bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        self.logo_name_label.grid(row=0, column=1, sticky="w")
        self.logo_name_label.grid_remove()  # hidden until expanded

        # Nav items container
        self.nav_container = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_container.pack(fill="both", expand=True)

        # Navigation items with labels
        # Profiles page removed as per user request (duplicates Optimization Center)
        items = [
            ("dashboard", "Dashboard", NAV_ICONS.get("dashboard", "\ue8b0")),
            ("scripts", "Optimize", NAV_ICONS.get("scripts", "\ue86f")),
            ("backup", "Backup", NAV_ICONS.get("backup", "\ue1d7")),
            ("help", "Help", NAV_ICONS.get("help", "\ue88b")),
        ]

        for key, label, icon in items:
            self.create_nav_button(key, label, icon)

        # Divider before Settings
        divider = ctk.CTkFrame(
            self.nav_container,
            height=1,
            fg_color=colors["border"],
        )
        divider.pack(fill="x", padx=12, pady=(8, 4))
        self._settings_divider = divider

        # Settings nav item (below divider)
        self.create_nav_button("settings", "Settings", "\ue713")

    def create_nav_button(self, key: str, label: str, icon: str):
        """
        Create enhanced navigation button

        Args:
            key: Navigation key (e.g., "dashboard")
            label: Display label
            icon: Icon unicode character (Material Symbol)
        """
        colors = theme_manager.get_colors()

        btn_frame = ctk.CTkFrame(
            self.nav_container, fg_color="transparent", height=40
        )  # Reduced height (Compact)
        btn_frame.pack(fill="x", pady=2, padx=6)  # Reduced spacing
        btn_frame.pack_propagate(False)
        btn_frame.grid_columnconfigure(0, weight=0)  # Indicator
        btn_frame.grid_columnconfigure(1, weight=0)  # Icon button
        btn_frame.grid_columnconfigure(2, weight=1)  # Label

        # Active indicator (hidden by default)
        indicator = ctk.CTkFrame(
            btn_frame, width=3, fg_color=colors["accent"], corner_radius=2
        )
        indicator.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        indicator.grid_remove()  # Hide initially

        # Icon button with Segoe MDL2 Assets font
        btn = ctk.CTkButton(
            btn_frame,
            text=icon,
            font=ctk.CTkFont(
                family="Segoe MDL2 Assets", size=18
            ),  # Standard size for Segoe
            width=36,  # Compact touch target
            height=36,
            fg_color="transparent",
            text_color=colors["text_secondary"],
            hover_color=colors["bg_hover"],
            corner_radius=RADIUS["md"],
            command=lambda k=key: self.on_nav_click(k),
        )
        btn.grid(row=0, column=1, sticky="w")

        # Label (hidden when collapsed)
        lbl = ctk.CTkLabel(
            btn_frame,
            text=label,
            font=font("body_small", weight="bold"),  # Smaller font
            text_color=colors["text_primary"],
            anchor="w",
        )
        lbl.grid(row=0, column=2, sticky="w", padx=(10, 0))
        lbl.grid_remove()  # Hide initially

        # Store references
        self.nav_buttons[key] = {
            "frame": btn_frame,
            "button": btn,
            "label": lbl,
            "indicator": indicator,
        }

        # Bind hover effects
        btn.bind("<Enter>", lambda e, k=key: self.on_hover_enter(k))
        btn.bind("<Leave>", lambda e, k=key: self.on_hover_leave(k))

        # Add tooltip for collapsed sidebar accessibility
        self.nav_buttons[key]["tooltip"] = ToolTipBinder(btn, label)

    def on_hover_enter(self, key: str):
        """Highlight non-active nav button on hover."""
        if key != self.app.active_nav:
            btn_data = self.nav_buttons[key]
            colors = theme_manager.get_colors()
            btn_data["button"].configure(fg_color=colors["bg_hover"])

    def on_hover_leave(self, key: str):
        """Remove hover highlight from non-active nav button."""
        if key != self.app.active_nav:
            btn_data = self.nav_buttons[key]
            btn_data["button"].configure(fg_color="transparent")

    def on_nav_click(self, key: str):
        """Handle navigation click"""
        self.app.switch_view(key)
        self.update_active_state(key)

    def update_active_state(self, active_key: str):
        """Update active state for all buttons"""
        colors = theme_manager.get_colors()

        for key, data in self.nav_buttons.items():
            is_active = key == active_key

            # Update button color
            data["button"].configure(
                text_color=colors["accent"] if is_active else colors["text_secondary"]
            )

            # Show/hide indicator (if it exists)
            if data["indicator"] is not None:
                if is_active:
                    data["indicator"].grid()
                else:
                    data["indicator"].grid_remove()

            # Start or stop glow animation
            if is_active:
                if key not in self.glow_animations:
                    self.animate_glow(key)
            else:
                # Stop glow animation
                if key in self.glow_animations:
                    self.glow_animations[key] = False  # Signal to stop
                    del self.glow_animations[key]

    def animate_glow(self, key: str):
        """
        Animate glow effect on active button.

        Creates a smooth breathing effect by interpolating between transparent
        and the accent_dim colour across 20 steps per half-cycle.
        Guarded against TclError when the widget is destroyed.

        RESPECTS reduce_motion: Skip animation if user has enabled reduce motion.
        """
        # Check for reduce_motion setting (accessibility)
        if hasattr(self.app, "config") and self.app.config.get("reduce_motion", False):
            # User prefers reduced motion - just show static active state
            if key not in self.nav_buttons:
                return
            colors = theme_manager.get_colors()
            btn_data = self.nav_buttons[key]
            button = btn_data["button"]
            try:
                button.configure(fg_color=colors.get("accent_dim", "transparent"))
            except Exception as e:
                logger.debug(f"Could not apply static glow state: {e}")
            return

        self.glow_animations[key] = True  # Mark animation as active

        colors = theme_manager.get_colors()
        btn_data = self.nav_buttons[key]
        button = btn_data["button"]

        # Parse accent_dim into RGB for smooth interpolation
        # Derive fallback from accent color (50% darkened) instead of hard-coded Tokyo Night hex
        def _darken_hex(h: str, factor: float = 0.5) -> str:
            h = h.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"

        _accent = colors.get("accent", "#00bcd4")
        accent_dim = colors.get("accent_dim", _darken_hex(_accent))

        def _hex_to_rgb(h: str):
            h = h.lstrip("#")
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

        def _rgb_to_hex(r: int, g: int, b: int) -> str:
            return f"#{r:02x}{g:02x}{b:02x}"

        bg_rgb = _hex_to_rgb(colors.get("bg_secondary", "#131c2e"))
        dim_rgb = _hex_to_rgb(accent_dim)

        duration = 2000  # ms per full breath cycle
        steps = 20  # steps per half-cycle (bright → dim or dim → bright)
        step_delay = max(1, duration // (steps * 2))

        def glow_step(step: int, direction: int):
            """Single glow animation step."""
            if not self.glow_animations.get(key, False):
                try:
                    button.configure(fg_color="transparent")
                except Exception:
                    pass
                return

            # Triangle-wave brightness: 0.0 → 1.0 → 0.0
            t = step / steps  # 0..1
            r = int(bg_rgb[0] + (dim_rgb[0] - bg_rgb[0]) * t)
            g = int(bg_rgb[1] + (dim_rgb[1] - bg_rgb[1]) * t)
            b = int(bg_rgb[2] + (dim_rgb[2] - bg_rgb[2]) * t)
            interp_color = _rgb_to_hex(
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )

            try:
                button.configure(fg_color=interp_color)
            except Exception as e:
                # Widget destroyed — stop animation
                logger.debug(f"Glow animation stopped: {e}")
                if key in self.glow_animations:
                    del self.glow_animations[key]
                return

            # Advance step and flip direction at boundaries
            next_step = step + 1
            next_direction = direction
            if next_step > steps:
                next_step = 0
                next_direction = -direction  # flip

            button.after(step_delay, lambda: glow_step(next_step, next_direction))

        # Start animation
        glow_step(0, 1)

    def create_toggle_button(self):
        """Create sidebar toggle button"""
        colors = theme_manager.get_colors()

        self.toggle_button = ctk.CTkButton(
            self,
            text="☰",
            width=40,
            height=40,
            fg_color="transparent",
            text_color=colors["text_muted"],
            hover_color=colors["bg_hover"],
            command=self.toggle_sidebar,
        )
        self.toggle_button.pack(pady=10)

    def toggle_sidebar(self):
        """Toggle sidebar expand/collapse with animation"""
        if self.animating:
            return  # Prevent double-click during animation

        self.animating = True
        target_expanded = not self.is_expanded

        start_width = self.width_expanded if self.is_expanded else self.width_collapsed
        end_width = self.width_expanded if target_expanded else self.width_collapsed
        steps = 8
        step_delay = ANIMATION["fast"] // steps

        def animate_step(step):
            try:
                if step > steps:
                    self.is_expanded = target_expanded
                    self.animating = False
                    # Update toggle icon
                    self.toggle_button.configure(text="✕" if self.is_expanded else "☰")
                    # Show/hide labels using grid/grid_remove (matches initial setup)
                    for key, data in self.nav_buttons.items():
                        try:
                            if self.is_expanded:
                                data["label"].grid()
                            else:
                                data["label"].grid_remove()
                        except Exception as e:
                            logger.debug(f"Could not update label visibility: {e}")
                    # Show/hide the logo name label alongside nav labels
                    if hasattr(self, "logo_name_label"):
                        if self.is_expanded:
                            self.logo_name_label.grid()
                        else:
                            self.logo_name_label.grid_remove()
                    return

                # Ease-out interpolation
                t = step / steps
                t = 1 - (1 - t) ** 2  # Ease-out quad
                current_width = int(start_width + (end_width - start_width) * t)
                self.configure(width=current_width)
                # Also update the column minsize so the grid column tracks the sidebar width
                try:
                    self.master.grid_columnconfigure(0, minsize=current_width)
                except Exception:
                    pass
                self.after(step_delay, lambda: animate_step(step + 1))
            except Exception as e:
                logger.debug(f"Sidebar animation error: {e}")
                self.animating = False  # Reset on error

        animate_step(0)

    def refresh_colors(self):
        """Refresh colors when theme changes"""
        colors = theme_manager.get_colors()

        # Update sidebar background
        self.configure(fg_color=colors["bg_secondary"])

        # Update logo color (only if logo_label is a text label, not CTkImage)
        if not hasattr(self, "_logo_image"):
            self.logo_label.configure(text_color=colors["accent"])

        # Update all nav buttons
        for key, data in self.nav_buttons.items():
            is_active = key == self.app.active_nav

            # Update button colors
            data["button"].configure(
                text_color=colors["accent"] if is_active else colors["text_secondary"],
                hover_color=colors["bg_hover"],
            )

            # Update indicator color
            data["indicator"].configure(fg_color=colors["accent"])

            # Update label color
            data["label"].configure(text_color=colors["text_primary"])

        # Update toggle button
        self.toggle_button.configure(
            text_color=colors["text_muted"], hover_color=colors["bg_hover"]
        )

        # Restart glow animation for active button
        if self.app.active_nav in self.nav_buttons:
            self.update_active_state(self.app.active_nav)
