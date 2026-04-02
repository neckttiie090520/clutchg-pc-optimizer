"""
Enhanced Glass Card Component for ClutchG
Glassmorphism cards with glow effects and better styling
"""

import customtkinter as ctk
from gui.theme import theme_manager, SPACING, RADIUS
from typing import Optional


class GlassCard(ctk.CTkFrame):
    """
    Card with glassmorphism effect
    Features: semi-transparent background, subtle border, optional glow
    """

    def __init__(
        self,
        master,
        corner_radius: Optional[int] = None,
        border_width: int = 1,
        border_color: Optional[str] = None,
        glow_color: Optional[str] = None,
        padding: int = SPACING["md"],
        **kwargs,
    ):
        """
        Create a glassmorphism card

        Args:
            master: Parent widget
            corner_radius: Corner radius (defaults to RADIUS["lg"])
            border_width: Border width
            border_color: Border color (defaults to theme border_subtle)
            glow_color: Optional glow color for accent
            padding: Internal padding
        """
        colors = theme_manager.get_colors()

        if corner_radius is None:
            corner_radius = RADIUS["lg"]

        if border_color is None:
            border_color = colors.get("border_subtle", "#2D3748")

        # Use bg_card for glassmorphism effect
        fg_color = colors.get("bg_card", "#1A2332")

        super().__init__(
            master,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=border_color,
            fg_color=fg_color,
            **kwargs,
        )

        self.glow_color = glow_color
        self.default_border_color = border_color
        self.default_border_width = border_width
        self._padding = padding

        # Apply internal padding via pack/grid on children — CTkFrame doesn't support padx/pady in configure()

        # Apply glow if specified
        if glow_color:
            self.set_glow(glow_color)

    def set_glow(self, color: str, width: int = 2):
        """
        Set glow effect on the card

        Args:
            color: Glow color
            width: Border width for glow
        """
        self.configure(border_color=color, border_width=width)
        self.glow_color = color

    def remove_glow(self):
        """Remove glow effect"""
        self.configure(
            border_color=self.default_border_color,
            border_width=self.default_border_width,
        )
        self.glow_color = None

    def add_hover_effect(self):
        """Add hover glow effect.

        If the card has a glow_color (e.g. risk-coloured profile cards), the
        hover intensifies the existing glow by widening the border to 3 px.
        If there is no glow_color, the accent colour is shown on hover.
        Child-widget enter/leave events bubble up so the bind on `self` is
        extended to all direct children.
        """
        colors = theme_manager.get_colors()

        def on_enter(event):
            if self.glow_color:
                # Intensify existing risk-colour glow
                self.configure(border_color=self.glow_color, border_width=3)
            else:
                self.configure(border_color=colors["accent"], border_width=2)

        def on_leave(event):
            if self.glow_color:
                # Return to normal glow width
                self.configure(border_color=self.glow_color, border_width=2)
            else:
                self.configure(
                    border_color=self.default_border_color,
                    border_width=self.default_border_width,
                )

        self.bind("<Enter>", on_enter, add="+")
        self.bind("<Leave>", on_leave, add="+")


class ProfileCard(GlassCard):
    """
    Profile card with stats grid, risk bar, and action buttons.
    No colored left-stripe. No features bullet list.
    """

    RISK_FILL = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}
    RISK_COLORS = {"LOW": "#22C55E", "MEDIUM": "#F59E0B", "HIGH": "#EF4444"}

    def __init__(
        self,
        master,
        profile_name: str,
        profile_icon: str,
        description: str,
        risk_level: str,
        stats: dict,
        glow_color: str,
        on_apply=None,
        on_preview=None,
        **kwargs,
    ):
        """
        Create a profile card with stats grid and risk bar.

        Args:
            master: Parent widget
            profile_name: Profile name (e.g., "SAFE")
            profile_icon: Segoe MDL2 icon character
            description: Profile description text
            risk_level: Risk level text (e.g., "LOW RISK")
            stats: Dict with keys tweaks, gain, risk, restart
            glow_color: Border glow color
            on_apply: Callback when Apply button is clicked
            on_preview: Callback when Preview button is clicked
        """
        super().__init__(
            master,
            corner_radius=RADIUS["xl"],
            border_width=2,
            glow_color=glow_color,
            **kwargs,
        )

        colors = theme_manager.get_colors()
        risk_key = stats.get("risk", "LOW")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Internal padding frame
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])
        inner.grid_columnconfigure(0, weight=1)

        # --- Row 0: Icon in colored rounded square ---
        icon_circle = ctk.CTkFrame(
            inner, width=48, height=48, fg_color=glow_color, corner_radius=8
        )
        icon_circle.grid(row=0, column=0, pady=(0, SPACING["xs"]))
        icon_circle.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_circle,
            text=profile_icon,
            font=ctk.CTkFont(family="Tabler Icons", size=22),
            text_color="#FFFFFF",
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- Row 1: Profile name ---
        ctk.CTkLabel(
            inner,
            text=profile_name,
            font=ctk.CTkFont(family="Figtree", size=20, weight="bold"),
            text_color=colors["text_primary"],
        ).grid(row=1, column=0, pady=(0, SPACING["xs"]))

        # --- Row 2: Description ---
        desc_label = ctk.CTkLabel(
            inner,
            text=description,
            font=ctk.CTkFont(family="Figtree", size=13),
            text_color=colors["text_secondary"],
            wraplength=220,
            justify="left",
        )
        desc_label.grid(row=2, column=0, pady=(0, SPACING["md"]))

        # Dynamic wraplength on resize
        def _update_wraplength(event):
            new_wrap = max(120, event.width - 40)
            desc_label.configure(wraplength=new_wrap)

        inner.bind("<Configure>", _update_wraplength)

        # --- Row 3: Stats grid (2x4) ---
        stats_frame = ctk.CTkFrame(inner, fg_color="transparent")
        stats_frame.grid(row=3, column=0, sticky="ew", pady=(0, SPACING["md"]))
        for c in range(4):
            stats_frame.grid_columnconfigure(c, weight=1)

        stat_labels = ["Tweaks", "Gain", "Risk", "Restart"]
        stat_values = [
            str(stats.get("tweaks", "")),
            str(stats.get("gain", "")),
            str(stats.get("risk", "")),
            str(stats.get("restart", "")),
        ]

        for c, label_text in enumerate(stat_labels):
            # Row 0: muted label
            ctk.CTkLabel(
                stats_frame,
                text=label_text,
                font=ctk.CTkFont(family="Figtree", size=10),
                text_color=colors.get("text_muted", "#595959"),
            ).grid(row=0, column=c, padx=2, pady=(0, 2))

        for c, val_text in enumerate(stat_values):
            # Row 1: bold value
            val_color = colors["text_primary"]
            if c == 2:  # Risk column — color by risk level
                val_color = self.RISK_COLORS.get(risk_key, colors["text_primary"])

            ctk.CTkLabel(
                stats_frame,
                text=val_text,
                font=ctk.CTkFont(family="Figtree", size=13, weight="bold"),
                text_color=val_color,
            ).grid(row=1, column=c, padx=2)

        # --- Row 4: Thin risk bar ---
        bar_height = 4
        risk_fill = self.RISK_FILL.get(risk_key, 0.2)

        bar_bg = ctk.CTkFrame(
            inner,
            height=bar_height,
            fg_color=colors.get("bg_tertiary", "#383838"),
            corner_radius=2,
        )
        bar_bg.grid(row=4, column=0, sticky="ew", pady=(0, SPACING["md"]))
        bar_bg.grid_propagate(False)

        bar_fill = ctk.CTkFrame(
            bar_bg, height=bar_height, fg_color=glow_color, corner_radius=2
        )
        bar_fill.place(relx=0, rely=0, relwidth=risk_fill, relheight=1.0)

        # --- Row 5: Button row ---
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="ew", pady=(0, SPACING["xs"]))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        # Preview button (ghost / outline)
        preview_btn = ctk.CTkButton(
            btn_frame,
            text="Preview",
            command=on_preview,
            width=80,
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color=colors.get("border", "#3d3d3d"),
            hover_color=colors.get("bg_tertiary", "#383838"),
            text_color=colors["text_secondary"],
            font=ctk.CTkFont(family="Figtree", size=12),
            corner_radius=RADIUS.get("md", 8),
        )
        preview_btn.grid(row=0, column=0, padx=(0, SPACING["xs"]), sticky="ew")

        # Apply button — colored by risk
        apply_color = self.RISK_COLORS.get(risk_key, colors.get("accent", "#57c8ff"))
        # Dark text for warning (yellow) button, white otherwise
        apply_text_color = "#18181b" if risk_key == "MEDIUM" else "#FFFFFF"

        apply_btn = ctk.CTkButton(
            btn_frame,
            text=f"Apply {profile_name}",
            command=on_apply,
            width=80,
            height=34,
            fg_color=apply_color,
            hover_color=apply_color,
            text_color=apply_text_color,
            font=ctk.CTkFont(family="Figtree", size=12, weight="bold"),
            corner_radius=RADIUS.get("md", 8),
        )
        apply_btn.grid(row=0, column=1, sticky="ew")


class HardwareCard(GlassCard):
    """Card for displaying hardware information"""

    def __init__(
        self,
        master,
        icon: str,
        title: str,
        subtitle: str,
        usage: int = 0,
        usage_color: str = "#00f2fe",
        show_usage: bool = False,  # Default to False as per request
        **kwargs,
    ):
        """
        Create a hardware info card

        Args:
            master: Parent widget
            icon: Material Symbol icon
            title: Hardware name (e.g., "AMD Ryzen 7")
            subtitle: Hardware details (e.g., "8C/16T")
            usage: Usage percentage (0-100)
            usage_color: Color for usage bar
            show_usage: Whether to show the usage bar (default: False)
        """
        super().__init__(master, **kwargs)

        colors = theme_manager.get_colors()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Icon and title row
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=SPACING["md"],
            pady=(SPACING["md"], SPACING["sm"]),
        )
        header_frame.grid_columnconfigure(1, weight=1)

        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(family="Tabler Icons", size=20),
            text_color=usage_color,
        )
        icon_label.grid(row=0, column=0, padx=(0, SPACING["sm"]))

        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Figtree", size=14, weight="bold"),
            text_color=colors["text_primary"],
            anchor="w",
        )
        title_label.grid(row=0, column=1, sticky="w")

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(family="Figtree", size=12),
            text_color=colors["text_secondary"],
        )
        subtitle_label.grid(
            row=1, column=0, sticky="w", padx=SPACING["md"], pady=(0, SPACING["sm"])
        )

        # Usage bar (Hidden by default unless show_usage=True)
        self.usage_frame = ctk.CTkFrame(self, fg_color="transparent")
        if show_usage:
            self.usage_frame.grid(
                row=2,
                column=0,
                sticky="ew",
                padx=SPACING["md"],
                pady=(0, SPACING["md"]),
            )

        self.usage_frame.grid_columnconfigure(0, weight=1)

        # Background bar
        bg_bar = ctk.CTkFrame(
            self.usage_frame,
            height=6,
            fg_color=colors["bg_elevated"],
            corner_radius=RADIUS["full"],
        )
        bg_bar.grid(row=0, column=0, sticky="ew", padx=(0, SPACING["sm"]))

        # Usage bar (gradient would be nice, but using solid color for now)
        self.usage_bar = ctk.CTkFrame(
            bg_bar, height=6, fg_color=usage_color, corner_radius=RADIUS["full"]
        )
        self.usage_bar.place(relx=0, rely=0, relwidth=usage / 100, relheight=1)

        # Usage percentage
        self.usage_label = ctk.CTkLabel(
            self.usage_frame,
            text=f"{usage}%",
            font=ctk.CTkFont(family="Figtree", size=12, weight="bold"),
            text_color=colors["text_secondary"],
        )
        self.usage_label.grid(row=0, column=1)

    def update_usage(self, usage: float):
        """Update usage bar and label"""
        usage = max(0, min(100, usage))  # Clamp 0-100
        self.usage_bar.place(relwidth=usage / 100)
        self.usage_label.configure(text=f"{int(usage)}%")

        # Ensure visible
        if not self.usage_frame.winfo_ismapped():
            self.usage_frame.grid(
                row=2,
                column=0,
                sticky="ew",
                padx=SPACING["md"],
                pady=(0, SPACING["md"]),
            )

    def hide_usage(self):
        """Hide usage section if data unavailable"""
        self.usage_frame.grid_remove()
