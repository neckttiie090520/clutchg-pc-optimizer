"""
Dashboard View - Modern Redesign (Phase 2)
Featuring Glassmorphism, Gradients, and Enhanced Visualization
Updated: 2026-02-10 (Bug fixes: duplicate labels, missing create_content, duplicate RAM card)
"""

import customtkinter as ctk
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple
import logging
from PIL import Image
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
        """Create header: title + plain subtitle (left), Scan System button (right)."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        header.grid_columnconfigure(1, weight=1)  # Spacer pushes button right

        # Title block — title + subtitle stacked
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_block,
            text=self._ui("title"),
            font=self._font(22, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        subtitle_text = (
            self._ui("system_ready")
            if self.app.system_profile
            else self._ui("initializing")
        )
        ctk.CTkLabel(
            title_block,
            text=subtitle_text,
            font=self._font(12),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        # Scan System button — outline style, top-right
        EnhancedButton.outline(
            header,
            text=self._ui("scan_system"),
            command=self.scan_system,
            height=32,
        ).grid(row=0, column=2, sticky="e")

    def create_content(self):
        """Create main content area: score-section row, then hardware + activity."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=0)  # score section — natural height
        content.grid_rowconfigure(1, weight=0)  # hardware section label
        content.grid_rowconfigure(2, weight=0)  # hardware grid
        content.grid_rowconfigure(3, weight=0)  # recent activity label
        content.grid_rowconfigure(4, weight=1)  # recent activity content

        self.create_score_section(content)

        if self.app.system_profile:
            self.create_hardware_section(content)

        self.create_recent_activity_section(content)

    def create_score_section(self, parent):
        """Score ring (left) + recommendation card (right) — side by side in one row."""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))
        section.grid_columnconfigure(0, weight=0)  # ring — fixed width
        section.grid_columnconfigure(1, weight=1)  # rec card — fills remaining
        section.grid_rowconfigure(0, weight=1)

        # ── Score Ring (left) ─────────────────────────────────────────
        score_card = GlassCard(section, corner_radius=RADIUS["xl"])
        score_card.grid(row=0, column=0, sticky="ns", padx=(0, SPACING["sm"]))

        score = self.app.system_profile.total_score if self.app.system_profile else 0
        theme_colors = theme_manager.get_colors()

        if score >= 80:
            ring_colors = [theme_colors["success"], theme_colors["success"]]
        elif score >= 50:
            ring_colors = [theme_colors["info"], theme_colors["info"]]
        else:
            ring_colors = [theme_colors["danger"], theme_colors["danger"]]

        self.score_display = CircularProgress(
            score_card,
            size=120,
            thickness=12,
            value=score,
            max_value=100,
            colors=ring_colors,
            bg_color=theme_colors["bg_card"],
            value_font=("Figtree", 28, "bold"),
        )
        self.score_display.pack(padx=SPACING["lg"], pady=(SPACING["md"], 2))

        ctk.CTkLabel(
            score_card,
            text=self._ui("system_score")
            if self.app.system_profile
            else self._ui("scanning"),
            font=self._font(10, "bold"),
            text_color=COLORS["text_muted"],
        ).pack(pady=(0, SPACING["md"]))

        # ── Recommendation Card (right) ───────────────────────────────
        rec_card = GlassCard(section, corner_radius=RADIUS["xl"], padding=SPACING["md"])
        rec_card.grid(row=0, column=1, sticky="nsew")

        # "Recommended" — overline label
        ctk.CTkLabel(
            rec_card,
            text="Recommended",
            font=self._font(10, "bold"),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        # Recommendation text — body
        rec_text = self._ui("rec_safe")
        if self.app.system_profile:
            recommended = self.app.system_detector.recommend_profile(
                self.app.system_profile
            )
            rec_text = self._ui("rec_optimal").format(profile=recommended)

        ctk.CTkLabel(
            rec_card,
            text=rec_text,
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            wraplength=320,
            justify="left",
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Apply Optimization button
        EnhancedButton.primary(
            rec_card,
            text="Apply Optimization",
            command=lambda: self.app.switch_view("scripts"),
            height=36,
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))

    def create_hardware_section(self, parent):
        """Section label + 1×3 hardware grid (CPU, GPU, RAM) — full width."""
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
            row=1, column=0, sticky="w", pady=(SPACING["md"], SPACING["xs"])
        )
        ctk.CTkLabel(
            section_label,
            text="SYSTEM HARDWARE",
            font=self._font(11, "bold"),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w")

        components = [
            (self._ui("cpu"), "cpu", cpu_spec),
            (self._ui("gpu"), "gpu", gpu_spec),
            (self._ui("ram"), "ram", ram_spec),
        ]

        # Load hardware PNG images (28x28 for card header)
        # Source PNGs are pre-tinted #b0b0b0 for dark theme visibility
        _hw_size = 28
        _assets = Path(__file__).parent.parent.parent / "assets"
        _hw_imgs: dict = {}
        for key, fname in [
            ("cpu", "hw-cpu.png"),
            ("gpu", "hw-gpu.png"),
            ("ram", "hw-ram.png"),
        ]:
            try:
                pil = Image.open(_assets / fname).resize(
                    (_hw_size, _hw_size), Image.LANCZOS
                )
                _hw_imgs[key] = ctk.CTkImage(
                    light_image=pil, dark_image=pil, size=(_hw_size, _hw_size)
                )
            except Exception:
                _hw_imgs[key] = None

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="ew", pady=(0, SPACING["md"]))
        grid.grid_columnconfigure(0, weight=1, uniform="hw")
        grid.grid_columnconfigure(1, weight=1, uniform="hw")
        grid.grid_columnconfigure(2, weight=1, uniform="hw")
        grid.grid_rowconfigure(0, weight=1)

        for col, (label, hw_key, spec) in enumerate(components):
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

            img = _hw_imgs.get(hw_key)
            if img:
                ctk.CTkLabel(
                    header,
                    image=img,
                    text="",
                ).pack(side="left", padx=(0, SPACING["xs"]))
            else:
                # Fallback: Tabler icon codepoint
                _fallback = {"cpu": "\ueb87", "gpu": "\uf50d", "ram": "\uefce"}
                ctk.CTkLabel(
                    header,
                    text=_fallback.get(hw_key, ""),
                    font=ctk.CTkFont(family="Tabler Icons", size=13),
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

    def create_recent_activity_section(self, parent):
        """Recent Activity section — rows 3+4 of content grid."""
        ctk.CTkLabel(
            parent,
            text=self._ui("recent_activity"),
            font=self._font(11, "bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=3, column=0, sticky="w", pady=(0, SPACING["xs"]))

        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=4, column=0, sticky="nsew")

        activities = self._load_recent_activities()

        if activities:
            for text, time_str, color in activities:
                self.create_activity_item(container, text, time_str, color)
        else:
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
