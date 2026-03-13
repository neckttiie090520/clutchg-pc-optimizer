"""
Dashboard View - Modern Redesign (Phase 2)
Featuring Glassmorphism, Gradients, and Enhanced Visualization
Updated: 2026-02-10 (Bug fixes: duplicate labels, missing create_content, duplicate RAM card)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING, List, Tuple
from gui.theme import theme_manager, COLORS, SIZES, SPACING, RADIUS, get_score_color, NAV_ICONS
from gui.style import font
from gui.components.glass_card import GlassCard, HardwareCard
from gui.components.circular_progress import CircularProgress
from gui.components.enhanced_button import EnhancedButton, IconButton
from gui.components.gradient import GradientLabel
from core.tweak_registry import get_tweak_registry
import threading
import time


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
        }
    }

    UI_STRINGS["en"].update({
        "action_hub_title": "Action Hub",
        "action_hub_subtitle": "Open Quick Actions in Optimization Center for one-click packs.",
        "open_quick_actions": "Open Quick Actions",
        "health_snapshot": "System Snapshot",
        "tile_storage": "Storage",
        "tile_tweaks": "Optimizations",
        "tile_profile": "Active Profile",
        "tile_status": "Status",
    })

    UI_STRINGS["th"].update({
        "action_hub_title": "Action Hub",
        "action_hub_subtitle": "เปิด Quick Actions ใน Optimization Center เพื่อใช้งานชุดคำสั่ง",
        "open_quick_actions": "เปิด Quick Actions",
        "health_snapshot": "ข้อมูลระบบ",
        "tile_storage": "Storage",
        "tile_tweaks": "การปรับแต่ง",
        "tile_profile": "โปรไฟล์",
        "tile_status": "สถานะ",
    })

    def __init__(self, parent, app: 'ClutchGApp'):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header Section
        self.create_header()

        # 2. Main Content Grid
        self.create_content()

        # 3. Footer / Status Bar
        self.create_footer()

    def _ui(self, key: str) -> str:
        """Get UI string in current language"""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Tahoma", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def destroy(self):
        super().destroy()
        
    def create_header(self):
        """Create modern header with status badge"""
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["xl"]))
        header.grid_columnconfigure(1, weight=1)  # Spacer
        
        # Dashboard Title
        ctk.CTkLabel(
            header,
            text=self._ui("title"),
            font=self._font(24, "bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        # System Status Badge (Glassmorphism Pilled)
        status_container = ctk.CTkFrame(
            header,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["full"],
            border_width=1,
            border_color=COLORS["success_dim"]
        )
        status_container.grid(row=0, column=2, sticky="e")

        # Dot indicator
        ctk.CTkLabel(
            status_container,
            text="●",
            font=self._font(12),
            text_color=COLORS["success"]
        ).pack(side="left", padx=(SPACING["md"], SPACING["xs"]), pady=SPACING["xs"])

        # Status Text
        ctk.CTkLabel(
            status_container,
            text=self._ui("system_ready") if self.app.system_profile else self._ui("initializing"),
            font=self._font(12, "bold"),
            text_color=COLORS["success"] if self.app.system_profile else COLORS["text_muted"]
        ).pack(side="left", padx=(0, SPACING["md"]), pady=SPACING["sm"])
        
    def create_content(self):
        """Create main content area with score and hardware info"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        
        # Grid Layout: Left (Score) | Right (Actions & Stats)
        content.grid_columnconfigure(0, weight=4)  # Score area (slightly larger)
        content.grid_columnconfigure(1, weight=5)  # Stats area
        content.grid_rowconfigure(0, weight=1)
        
        # --- Left Panel: System Score ---
        self.create_left_panel(content)
        
        # --- Right Panel: Quick Actions & Hardware ---
        self.create_right_panel(content)
        
    def create_left_panel(self, parent):
        """Left panel containing Score Ring and Recommendation"""
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["xl"]))
        panel.grid_rowconfigure(0, weight=1)  # Center score vertically
        panel.grid_columnconfigure(0, weight=1)
        
        # Main Score Card (Glassmorphism)
        score_card = GlassCard(panel, corner_radius=RADIUS["2xl"])
        score_card.grid(row=0, column=0, sticky="nsew")
        score_card.grid_columnconfigure(0, weight=1)
        score_card.grid_rowconfigure(0, weight=1) # Center content
        
        # Container for centering
        center_container = ctk.CTkFrame(score_card, fg_color="transparent")
        center_container.grid(row=0, column=0)
        
        # 1. Circular Progress
        score = 0
        if self.app.system_profile:
            score = self.app.system_profile.total_score
            
        color = get_score_color(score)
        
        # Get dynamic theme colors
        theme_colors = theme_manager.get_colors()
        
        # Solid colors based on score (Minimal Design)
        if score >= 80:
            ring_colors = [theme_colors["success"], theme_colors["success"]]
        elif score >= 50:
            ring_colors = [theme_colors["info"], theme_colors["info"]] # Info/Blue for average
        else:
            ring_colors = [theme_colors["danger"], theme_colors["danger"]]
            
        self.score_display = CircularProgress(
            center_container,
            size=220,
            thickness=20,
            value=score,
            max_value=100,
            colors=ring_colors,
            bg_color=theme_colors["bg_card"] # Match card bg
        )
        self.score_display.pack(pady=SPACING["xl"])
        
        # 2. Score Label (Below ring)
        ctk.CTkLabel(
            center_container,
            text=self._ui("system_score") if self.app.system_profile else self._ui("scanning"),
            font=self._font(13, "bold"),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(SPACING["sm"], 0))

        # 3. Current Mode Badge — show actual active/recommended profile
        active_profile = self._get_active_profile_name()
        mode_badge = ctk.CTkFrame(
            center_container,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADIUS["full"]
        )
        mode_badge.pack(pady=SPACING["lg"])

        ctk.CTkLabel(
            mode_badge,
            text=active_profile,
            font=self._font(12),
            text_color=COLORS["text_secondary"]
        ).pack(padx=SPACING["md"], pady=SPACING["xs"])

        # 4. Component Score Breakdown (NEW)
        if self.app.system_profile:
            self.create_component_scores(center_container)

    def _get_active_profile_name(self) -> str:
        """Get the active or recommended profile name for display"""
        # Check if a profile is currently active
        if hasattr(self.app, 'profile_manager'):
            active = self.app.profile_manager.get_active_profile()
            if active:
                return f"{active} {self._ui('mode')}"

        # Fall back to recommendation based on system profile
        if self.app.system_profile:
            recommended = self.app.system_detector.recommend_profile(self.app.system_profile)
            return f"{recommended} {self._ui('mode')}{self._ui('recommended_suffix')}"

        return self._ui("safe_mode")

    def create_component_scores(self, parent):
        """Display individual component scores with progress bars (Grid Layout)"""
        system = self.app.system_profile
        if not system:
            return

        # Container for component scores - Use Grid for perfect alignment
        scores_container = ctk.CTkFrame(parent, fg_color="transparent")
        scores_container.pack(pady=SPACING["lg"], fill="x", padx=SPACING["xl"])
        
        # Configure grid columns
        # 0: Icon, 1: Label, 2: Bar (Expand), 3: Score
        scores_container.grid_columnconfigure(2, weight=1)

        # Component scores: CPU (0-30), GPU (0-30), RAM (0-20), Storage (0-20)
        components = [
            ("CPU", system.cpu.score, 30, NAV_ICONS["cpu"]),
            ("GPU", system.gpu.score, 30, NAV_ICONS["gpu"]),
            ("RAM", system.ram.score, 20, NAV_ICONS["ram"]),
            ("Storage", system.storage.score, 20, "💾"),
        ]

        for i, (label, score, max_score, icon) in enumerate(components):
            # 1. Icon
            ctk.CTkLabel(
                scores_container,
                text=icon,
                font=self._font(12),
            ).grid(row=i, column=0, sticky="w", padx=(0, SPACING["xs"]), pady=SPACING["xs"])

            # 2. Label
            ctk.CTkLabel(
                scores_container,
                text=f"{label}:",
                font=self._font(11, "bold"),
                text_color=COLORS["text_secondary"]
            ).grid(row=i, column=1, sticky="w", padx=(0, SPACING["md"]), pady=SPACING["xs"])

            # 3. Progress Bar Container
            progress_frame = ctk.CTkFrame(scores_container, fg_color="transparent", height=6)
            progress_frame.grid(row=i, column=2, sticky="ew", padx=(0, SPACING["md"]), pady=SPACING["xs"])
            
            # Background track
            ctk.CTkFrame(
                progress_frame,
                fg_color=COLORS["bg_tertiary"],
                height=6,
                corner_radius=3
            ).pack(fill="x", expand=True) # expand=True is important here to fill height if needed, though usually fill=x is enough

            # Progress fill
            percentage = (score / max_score) * 100
            bar_color = self._get_progress_color(percentage)

            progress_fill = ctk.CTkFrame(
                progress_frame,
                fg_color=bar_color,
                height=6,
                corner_radius=3
            )
            progress_fill.place(relx=0, rely=0, relwidth=percentage / 100, anchor="nw")

            # 4. Score Text
            ctk.CTkLabel(
                scores_container,
                text=f"{score}/{max_score}",
                font=self._font(11),
                text_color=COLORS["text_muted"]
            ).grid(row=i, column=3, sticky="e", pady=SPACING["xs"])

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

        # 2. Action Hub shortcut
        self.create_action_hub(panel)

        # 3. Health tiles (System Info)
        self.create_health_tiles(panel)

        # 4. Recent Activity (Timeline)
        self.create_recent_activity(panel)

    def create_quick_actions(self, parent):
        """Quick Actions Section"""
        actions_card = GlassCard(parent, padding=SPACING["lg"])
        actions_card.pack(fill="x", pady=(0, SPACING["lg"]))

        # Title inside card
        ctk.CTkLabel(
            actions_card,
            text=self._ui("rec_optimization"),
            font=self._font(18, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        # Dynamic recommendation text
        rec_text = self._ui("rec_safe")
        if self.app.system_profile:
            recommended = self.app.system_detector.recommend_profile(self.app.system_profile)
            rec_text = self._ui("rec_optimal").format(profile=recommended)

        ctk.CTkLabel(
            actions_card,
            text=rec_text,
            font=self._font(13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["lg"]))

        # Action Buttons Row
        btn_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Main Action Button (Gradient)
        # Fix: ensure parent is btn_row, NOT self.header
        action_btn = EnhancedButton.primary(
            btn_row,
            text=self._ui("apply_optimization"),
            command=lambda: self.app.switch_view("scripts"), # Redirect to Optimization Center
            width=200
        )
        action_btn.pack(side="left", padx=(0, SPACING["md"]))

        # Secondary Action
        EnhancedButton.outline(
            btn_row,
            text=self._ui("scan_system"),
            command=self.scan_system
        ).pack(side="left")

    def create_action_hub(self, parent):
        """Compact action hub card linking to Optimization Center quick actions."""
        hub_card = GlassCard(parent, padding=SPACING["md"])
        hub_card.pack(fill="x", pady=(0, SPACING["md"]))

        ctk.CTkLabel(
            hub_card,
            text=self._ui("action_hub_title"),
            font=self._font(14, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        ctk.CTkLabel(
            hub_card,
            text=self._ui("action_hub_subtitle"),
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            wraplength=520,
            justify="left",
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        ctk.CTkButton(
            hub_card,
            text=self._ui("open_quick_actions"),
            font=self._font(12, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS.get("text_on_accent", "#FFFFFF"),
            hover_color=COLORS["accent_hover"],
            corner_radius=RADIUS["md"],
            height=32,
            command=lambda: self.app.switch_view("scripts"),
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["sm"]))

    def create_health_tiles(self, parent):
        """Hardware info tiles (CPU/RAM/VGA)."""
        ctk.CTkLabel(
            parent,
            text=self._ui("health_snapshot"),
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, SPACING["sm"]))

        tiles = ctk.CTkFrame(parent, fg_color="transparent")
        tiles.pack(fill="x", pady=(0, SPACING["md"]))
        for col in range(3):
            tiles.grid_columnconfigure(col, weight=1)

        system = self.app.system_profile
        
        # Get hardware info or placeholders
        cpu_text = "N/A"
        ram_text = "N/A"
        gpu_text = "N/A"
        
        if system:
            # CPU: Use simple name/family if possible, otherwise full name
            cpu_text = system.cpu.name
            # Simplify common CPU prefixes to save space
            cpu_text = cpu_text.replace("AMD ", "").replace("Intel ", "").replace("Processor", "").strip()
            
            # RAM
            ram_text = f"{system.ram.total_gb} GB"
            
            # GPU/VGA
            gpu_text = system.gpu.name
            gpu_text = gpu_text.replace("NVIDIA ", "").replace("AMD ", "").replace("GeForce ", "").strip()

        tile_items = [
            (self._ui("cpu"), cpu_text),
            (self._ui("ram"), ram_text),
            (self._ui("gpu"), gpu_text),
        ]

        for idx, (label, value) in enumerate(tile_items):
            tile = ctk.CTkFrame(
                tiles,
                fg_color=COLORS["bg_card"],
                corner_radius=RADIUS["md"],
                border_width=1,
                border_color=COLORS["border"],
            )
            tile.grid(row=0, column=idx, sticky="ew", padx=(0, SPACING["xs"]) if idx < 2 else 0)
            
            # Label (Small)
            ctk.CTkLabel(
                tile,
                text=str(label),
                font=self._font(11),
                text_color=COLORS["text_tertiary"],
            ).pack(anchor="w", padx=SPACING["sm"], pady=(SPACING["xs"], 0))
            
            # Value (Bold)
            ctk.CTkLabel(
                tile,
                text=str(value),
                font=self._font(12, "bold"),
                text_color=COLORS["text_primary"],
                wraplength=120,
                justify="left",
            ).pack(anchor="w", padx=SPACING["sm"], pady=(0, SPACING["xs"]))

    def create_hardware_section(self, parent):
        """Hardware Information Cards"""
        ctk.CTkLabel(parent, text=self._ui("system_hardware"), font=self._font(16, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, SPACING["md"]))

        system = self.app.system_profile

        # Helper to safely get data
        cpu_name = system.cpu.name if system else self._ui("scanning_cpu")
        gpu_name = system.gpu.name if system else self._ui("scanning_gpu")
        ram_info = f"{system.ram.total_gb}GB {system.ram.type.upper()}" if system else self._ui("scanning_ram")

        # 1. CPU Card
        self.cpu_card = HardwareCard(
            parent,
            icon=NAV_ICONS["cpu"],
            title=self._ui("cpu"),
            subtitle=cpu_name,
            show_usage=False
        )
        self.cpu_card.pack(fill="x", pady=(0, SPACING["md"]))

        # 2. GPU Card
        self.gpu_card = HardwareCard(
            parent,
            icon=NAV_ICONS["gpu"],
            title=self._ui("gpu"),
            subtitle=gpu_name,
            show_usage=False
        )
        self.gpu_card.pack(fill="x", pady=(0, SPACING["md"]))

        # 3. RAM Card
        self.ram_card = HardwareCard(
            parent,
            icon=NAV_ICONS["ram"],
            title=self._ui("ram"),
            subtitle=ram_info,
            show_usage=False
        )
        self.ram_card.pack(fill="x", pady=(0, SPACING["md"]))

    def create_recent_activity(self, parent):
        """Recent Activity Section (Timeline Preview)"""
        # Just a simple list for now, full timeline in Restore Center
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=SPACING["lg"])

        ctk.CTkLabel(container, text=self._ui("recent_activity"), font=self._font(16, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, SPACING["md"]))

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
                font=self._font(13),
                text_color=COLORS["text_muted"]
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
        except Exception:
            pass  # FlightRecorder not available or no data

        return activities

    def create_activity_item(self, parent, text, time_str, dot_color):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=(0, SPACING["sm"]))

        # Colored dot
        ctk.CTkLabel(item, text="●", text_color=dot_color, font=self._font(12)).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkLabel(item, text=text, font=self._font(13), text_color=COLORS["text_secondary"]).pack(side="left")
        ctk.CTkLabel(item, text=time_str, font=self._font(12), text_color=COLORS["text_muted"]).pack(side="right")

    def create_footer(self):
        """Status footer"""
        footer = ctk.CTkFrame(self, fg_color="transparent", height=30)
        footer.grid(row=2, column=0, sticky="ew", pady=(SPACING["md"], 0))
        
        version_text = f"ClutchG v{self.app.get_version()}"
        ctk.CTkLabel(footer, text=version_text, text_color=COLORS["text_muted"], font=font("micro")).pack(side="left")

    def scan_system(self):
        """Re-run system detection and refresh dashboard"""
        self.app.detect_system()
        # View will refresh automatically when detection completes
        # But we refresh now to show "Scanning..." state immediately
        self.app.refresh_current_view()
