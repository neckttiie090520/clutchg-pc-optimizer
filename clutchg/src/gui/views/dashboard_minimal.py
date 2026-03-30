"""
Dashboard View - Modern Redesign (Phase 2)
Featuring Glassmorphism, Gradients, and Enhanced Visualization
Updated: 2026-02-10 (Bug fixes: duplicate labels, missing create_content, duplicate RAM card)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING, List, Tuple
import logging
from gui.theme import (
    theme_manager,
    COLORS,
    SIZES,
    SPACING,
    RADIUS,
    get_score_color,
    NAV_ICONS,
)
from gui.style import font
from gui.components.glass_card import GlassCard, HardwareCard
from gui.components.circular_progress import CircularProgress
from gui.components.enhanced_button import EnhancedButton, IconButton
from core.tweak_registry import get_tweak_registry
import threading
import time

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class DashboardView(ctk.CTkFrame):
    """Modern Dashboard with Glassmorphism and Gradients"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Dashboard",
            "system_ready": "System Ready",
            "initializing": "Initializing...",
            "system_score": "SYSTEM SCORE",
            "scanning": "SCANNING...",
            "mode": "Mode",
            "recommended_suffix": " (Recommended)",
            "rec_optimization": "Recommended Optimization",
            "rec_safe": "Apply SAFE Profile for better stability",
            "rec_optimal": "Apply {profile} Profile for optimal performance",
            "apply_optimization": "APPLY OPTIMIZATION",
            "scan_system": "Scan System",
            "system_hardware": "System Hardware",
            "cpu": "CPU",
            "gpu": "GPU",
            "ram": "RAM",
            "scanning_cpu": "Scanning Processor...",
            "scanning_gpu": "Scanning Graphics...",
            "scanning_ram": "Scanning Memory...",
            "recent_activity": "Recent Activity",
            "no_recent_activity": "No recent activity",
            "profile_applied": "Profile '{profile}' applied",
            "safe_mode": "Safe Mode",
        },
        "th": {
            "title": "Dashboard",
            "system_ready": "ระบบพร้อมใช้งาน",
            "initializing": "กำลังโหลด...",
            "system_score": "คะแนนระบบ",
            "scanning": "กำลังสแกน...",
            "mode": "โหมด",
            "recommended_suffix": " (แนะนำ)",
            "rec_optimization": "การ Optimize ที่แนะนำ",
            "rec_safe": "ใช้ SAFE Profile เพื่อความเสถียรที่สุด",
            "rec_optimal": "ใช้ {profile} Profile เพื่อประสิทธิภาพสูงสุด",
            "apply_optimization": "เริ่มการ OPTIMIZE",
            "scan_system": "สแกนระบบ",
            "system_hardware": "ฮาร์ดแวร์ในระบบ",
            "cpu": "CPU",
            "gpu": "VGA",
            "ram": "RAM",
            "scanning_cpu": "กำลังสแกนหา CPU...",
            "scanning_gpu": "กำลังสแกนหา GPU...",
            "scanning_ram": "กำลังสแกนหาหน่วยความจำ...",
            "recent_activity": "กิจกรรมล่าสุด",
            "no_recent_activity": "ยังไม่มีกิจกรรม",
            "profile_applied": "ใช้งาน Profile '{profile}' แล้ว",
            "safe_mode": "Safe Mode",
        },
    }

    UI_STRINGS["en"].update(
        {
            "health_snapshot": "System Snapshot",
            "tile_storage": "Storage",
            "tile_tweaks": "Optimizations",
            "tile_profile": "Active Profile",
            "tile_status": "Status",
            "score_context": "Score out of 100 — higher is better",
        }
    )

    UI_STRINGS["th"].update(
        {
            "health_snapshot": "ข้อมูลระบบ",
            "tile_storage": "Storage",
            "tile_tweaks": "การปรับแต่ง",
            "tile_profile": "โปรไฟล์",
            "tile_status": "สถานะ",
            "score_context": "คะแนนจาก 100 — ยิ่งสูงยิ่งดี",
        }
    )

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_content()

    def _ui(self, key: str) -> str:
        """Get UI string in current language"""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Use Figtree for all languages"""
        return ctk.CTkFont(family="Figtree", size=size, weight=weight)

    def destroy(self):
        super().destroy()

    def create_header(self):
        """Create modern header with status badge and scan button"""
        header = ctk.CTkFrame(self, fg_color="transparent", height=36)
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        header.grid_columnconfigure(1, weight=1)  # Spacer

        # Dashboard Title — h1 level
        ctk.CTkLabel(
            header,
            text=self._ui("title"),
            font=self._font(22, "bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        # Scan System button — outline style, top-right
        EnhancedButton.outline(
            header,
            text=self._ui("scan_system"),
            command=self.scan_system,
            height=32,
        ).grid(row=0, column=2, sticky="e", padx=(0, SPACING["sm"]))

        # System Status Badge (Glassmorphism Pill)
        status_container = ctk.CTkFrame(
            header,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["full"],
            border_width=1,
            border_color=COLORS["success_dim"],
        )
        status_container.grid(row=0, column=3, sticky="e")

        # Dot indicator
        ctk.CTkLabel(
            status_container,
            text="\u25cf",
            font=self._font(10),
            text_color=COLORS["success"],
        ).pack(side="left", padx=(SPACING["sm"], SPACING["xs"]), pady=SPACING["xs"])

        # Status Text
        ctk.CTkLabel(
            status_container,
            text=self._ui("system_ready")
            if self.app.system_profile
            else self._ui("initializing"),
            font=self._font(11, "bold"),
            text_color=COLORS["success"]
            if self.app.system_profile
            else COLORS["text_muted"],
        ).pack(side="left", padx=(0, SPACING["sm"]), pady=SPACING["xs"])

    def create_content(self):
        """Create main content area with score and hardware info."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")

        content.grid_columnconfigure(0, weight=6)  # left panel — score + hardware
        content.grid_columnconfigure(1, weight=4)  # right panel — actions + activity
        content.grid_rowconfigure(0, weight=1)

        self.create_left_panel(content)
        self.create_right_panel(content)

    def create_left_panel(self, parent):
        """Left panel: score card (top) + 2×2 hardware grid (bottom)."""
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["sm"]))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=0)  # score card — natural height
        panel.grid_rowconfigure(1, weight=1)  # hardware grid — fills remaining

        # ── Score Card (pure pack inside) ────────────────────────────
        score_card = GlassCard(panel, corner_radius=RADIUS["2xl"])
        score_card.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))

        score = self.app.system_profile.total_score if self.app.system_profile else 0
        theme_colors = theme_manager.get_colors()
        badge_color = self._get_progress_color(score)

        if score >= 80:
            ring_colors = [theme_colors["success"], theme_colors["success"]]
        elif score >= 50:
            ring_colors = [theme_colors["info"], theme_colors["info"]]
        else:
            ring_colors = [theme_colors["danger"], theme_colors["danger"]]

        # Ring — compact 120px
        self.score_display = CircularProgress(
            score_card,
            size=120,
            thickness=12,
            value=score,
            max_value=100,
            colors=ring_colors,
            bg_color=theme_colors["bg_card"],
        )
        self.score_display.pack(pady=(SPACING["sm"], 2))

        # "SYSTEM SCORE" — overline style: small, bold, muted
        ctk.CTkLabel(
            score_card,
            text=self._ui("system_score")
            if self.app.system_profile
            else self._ui("scanning"),
            font=self._font(10, "bold"),
            text_color=COLORS["text_muted"],
        ).pack()

        # Mode badge — compact pill
        active_profile = self._get_active_profile_name()
        mode_badge = ctk.CTkFrame(
            score_card,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADIUS["full"],
        )
        mode_badge.pack(pady=(SPACING["xs"], SPACING["sm"]))
        ctk.CTkLabel(
            mode_badge,
            text=active_profile,
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            wraplength=180,
        ).pack(padx=SPACING["sm"], pady=2)

        # ── Hardware 2×2 Grid ─────────────────────────────────────────
        if self.app.system_profile:
            self.create_hardware_grid(panel)

    def create_hardware_grid(self, parent):
        """1×3 row of hardware spec cards (CPU, GPU, RAM only)."""
        system = self.app.system_profile
        if not system:
            return

        cpu_spec = (
            (system.cpu.name or "Unknown")
            .replace("AMD ", "")
            .replace("Intel ", "")
            .replace("Processor", "")
            .strip()
        )

        gpu_spec = (
            (system.gpu.name or "Unknown")
            .replace("NVIDIA ", "")
            .replace("AMD ", "")
            .replace("GeForce ", "")
            .strip()
        )
        if system.gpu.vram:
            gpu_spec = (
                f"{gpu_spec} {system.gpu.vram}GB" if len(gpu_spec) < 16 else gpu_spec
            )

        ram_spec = f"{system.ram.total_gb} GB"
        if system.ram.type and system.ram.type != "unknown":
            ram_spec += f" {system.ram.type.upper()}"
        if system.ram.speed:
            ram_spec += f" {system.ram.speed}MHz"

        section_label = ctk.CTkFrame(parent, fg_color="transparent")
        section_label.grid(
            row=0, column=0, sticky="w", pady=(SPACING["md"], SPACING["xs"])
        )
        ctk.CTkLabel(
            section_label,
            text="SYSTEM HARDWARE",
            font=self._font(11, "bold"),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        components = [
            (self._ui("cpu"), NAV_ICONS.get("cpu", "\ue950"), cpu_spec),
            (self._ui("gpu"), NAV_ICONS.get("gpu", "\ue7fd"), gpu_spec),
            (self._ui("ram"), NAV_ICONS.get("ram", "\ue964"), ram_spec),
        ]

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="nsew")
        grid.grid_columnconfigure(0, weight=1, uniform="hw")
        grid.grid_columnconfigure(1, weight=1, uniform="hw")
        grid.grid_columnconfigure(2, weight=1, uniform="hw")
        grid.grid_rowconfigure(0, weight=1)

        for col, (label, icon, spec) in enumerate(components):
            card = GlassCard(grid, corner_radius=RADIUS["xl"])
            card.grid(
                row=0,
                column=col,
                sticky="nsew",
                padx=(0 if col == 0 else SPACING["xs"], 0),
            )
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(2, weight=1)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=SPACING["sm"],
                pady=(SPACING["sm"], 0),
            )

            ctk.CTkLabel(
                header,
                text=icon,
                font=ctk.CTkFont(family="Segoe MDL2 Assets", size=13),
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(0, SPACING["xs"]))

            ctk.CTkLabel(
                header,
                text=label,
                font=self._font(13, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            ctk.CTkLabel(
                card,
                text=spec,
                font=self._font(14, "bold"),
                text_color=COLORS["text_primary"],
                wraplength=160,
                justify="left",
            ).grid(
                row=1,
                column=0,
                sticky="w",
                padx=SPACING["sm"],
                pady=(SPACING["xs"], SPACING["sm"]),
            )

    def _get_active_profile_name(self) -> str:
        """Get the active or recommended profile name for display"""
        # Check if a profile is currently active
        if hasattr(self.app, "profile_manager"):
            active = self.app.profile_manager.get_active_profile()
            if active:
                return f"{active} {self._ui('mode')}"

        # Fall back to recommendation based on system profile
        if self.app.system_profile:
            recommended = self.app.system_detector.recommend_profile(
                self.app.system_profile
            )
            return f"{recommended} {self._ui('mode')}{self._ui('recommended_suffix')}"

        return self._ui("safe_mode")

    def _get_progress_color(self, percentage: float) -> str:
        """Get progress bar color based on percentage"""
        if percentage >= 80:
            return COLORS["success"]  # Green
        elif percentage >= 60:
            return COLORS["info"]  # Blue
        elif percentage >= 40:
            return COLORS["warning"]  # Orange
        else:
            return COLORS["danger"]  # Red

    def create_right_panel(self, parent):
        """Right panel containing Actions and Hardware Stats"""
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        # 1. Quick Actions Card
        self.create_quick_actions(panel)

        # 2. Recent Activity (Timeline)
        self.create_recent_activity(panel)

    def create_quick_actions(self, parent):
        """Quick Actions Section"""
        actions_card = GlassCard(parent, padding=SPACING["md"])
        actions_card.pack(fill="x", pady=(0, SPACING["sm"]))

        # Title inside card — section level (15px bold)
        ctk.CTkLabel(
            actions_card,
            text=self._ui("rec_optimization"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        # Dynamic recommendation text — body (13px)
        rec_text = self._ui("rec_safe")
        if self.app.system_profile:
            recommended = self.app.system_detector.recommend_profile(
                self.app.system_profile
            )
            rec_text = self._ui("rec_optimal").format(profile=recommended)

        ctk.CTkLabel(
            actions_card,
            text=rec_text,
            font=self._font(13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Action Buttons Row
        btn_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        # Main Action Button — title case, not ALL CAPS
        action_btn = EnhancedButton.primary(
            btn_row,
            text="Apply Optimization",
            command=lambda: self.app.switch_view("scripts"),
            width=180,
            height=36,
        )
        action_btn.pack(side="left")

    def create_recent_activity(self, parent):
        """Recent Activity Section (Timeline Preview)"""
        # Just a simple list for now, full timeline in Restore Center
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(SPACING["sm"], 0))

        ctk.CTkLabel(
            container,
            text=self._ui("recent_activity"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, SPACING["sm"]))

        # Try to load real activity from FlightRecorder
        activities = self._load_recent_activities()

        if activities:
            for text, time_str, color in activities:
                self.create_activity_item(container, text, time_str, color)
        else:
            # Empty state
            ctk.CTkLabel(
                container,
                text=self._ui("no_recent_activity"),
                font=self._font(12),
                text_color=COLORS["text_muted"],
            ).pack(anchor="w")

    def _load_recent_activities(self):
        """Load recent activities from FlightRecorder if available"""
        activities = []
        try:
            from core.flight_recorder import get_flight_recorder

            recorder = get_flight_recorder()
            snapshots = recorder.list_snapshots(limit=3)

            for snapshot in snapshots:
                text = self._ui("profile_applied").format(profile=snapshot.profile)
                time_str = snapshot.timestamp.strftime("%Y-%m-%d %H:%M")
                color = COLORS["success"] if snapshot.success else COLORS["danger"]
                activities.append((text, time_str, color))
        except Exception as e:
            logger.debug(f"Could not load recent activities: {e}")

        return activities

    def create_activity_item(self, parent, text, time_str, dot_color):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=(0, SPACING["xs"]))

        # Colored dot
        ctk.CTkLabel(
            item, text="\u25cf", text_color=dot_color, font=self._font(10)
        ).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkLabel(
            item, text=text, font=self._font(12), text_color=COLORS["text_secondary"]
        ).pack(side="left")
        ctk.CTkLabel(
            item, text=time_str, font=self._font(11), text_color=COLORS["text_muted"]
        ).pack(side="right")

    def scan_system(self):
        """Re-run system detection and refresh dashboard"""
        self.app.detect_system()
        # View will refresh automatically when detection completes
        # But we refresh now to show "Scanning..." state immediately
        self.app.refresh_current_view()
