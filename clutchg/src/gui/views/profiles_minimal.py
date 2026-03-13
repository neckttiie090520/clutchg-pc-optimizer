"""
Profiles View - Modern Redesign (Phase 2)
Premium cards with glassmorphism and clear risk indicators
Updated: 2026-02-03 (Modern UI)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING
import threading

from gui.theme import COLORS, SIZES, SPACING, RADIUS, PROFILE_COLORS, NAV_ICONS, ICON
from gui.style import font
from gui.components.glass_card import ProfileCard
from gui.components.enhanced_button import EnhancedButton
from gui.components.refined_dialog import show_confirmation, show_info

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class ProfilesView(ctk.CTkFrame):
    """Modern Profiles Selection View"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Optimization Profiles",
            "hero_title": "Choose a performance profile tailored to your needs.",
            "hero_subtitle": "Each profile includes specific tweaks for Windows 11. Start with SAFE if you are unsure.",
            # Profile descriptions
            "safe_desc": "For everyday use and stability. Applies conservative, reversible optimizations.",
            "competitive_desc": "Balanced for gamers. Improves responsiveness with moderate trade-offs.",
            "extreme_desc": "Aggressive tuning for advanced users who understand backup and rollback.",
            # Risk labels
            "low_risk": "LOW RISK",
            "medium_risk": "MEDIUM RISK",
            "high_risk": "HIGH RISK",
            # Features
            "safe_feat1": "Basic Optimization",
            "safe_feat2": "Privacy Tweaks",
            "safe_feat3": "Safe Service Disabling",
            "comp_feat1": "Network Optimization",
            "comp_feat2": "Power Plan High Perf",
            "comp_feat3": "Gaming Service Tweaks",
            "ext_feat1": "BCDEdit Tweaks",
            "ext_feat2": "Aggressive Service Tuning",
            "ext_feat3": "Maximum Power Override",
            # Error messages
            "error": "Error",
            "profile_not_found": "Profile {name} not found!",
            "safety_check": "Safety Check",
            "confirm_apply": "Confirm Apply",
            "apply_question": "Apply {name} profile?\nClutchG will attempt an automatic backup before running changes.",
            "continue": "Continue?",
            "warning_intro": "This profile has warnings:\n\n",
        },
        "th": {
            "title": "Optimization Profiles",
            "hero_title": "เลือก Profile สำหรับเพิ่มประสิทธิภาพตามความต้องการของคุณ",
            "hero_subtitle": "แต่ละ Profile มีการปรับแต่งเฉพาะสำหรับ Windows 11 หากไม่แน่ใจ ให้เริ่มจาก SAFE",
            # Profile descriptions
            "safe_desc": "สำหรับการใช้งานทั่วไปและความเสถียร ใช้การปรับแต่งแบบอนุรักษ์นิยมที่ย้อนกลับได้",
            "competitive_desc": "สมดุลสำหรับเกมเมอร์ เพิ่มความลื่นไหลด้วย trade-off ระดับกลาง",
            "extreme_desc": "การจูนแบบเข้มสำหรับผู้ใช้ขั้นสูงที่เข้าใจ backup และ rollback",
            # Risk labels
            "low_risk": "LOW RISK",
            "medium_risk": "MEDIUM RISK",
            "high_risk": "HIGH RISK",
            # Features
            "safe_feat1": "Optimize พื้นฐาน",
            "safe_feat2": "ปรับแต่งความเป็นส่วนตัว",
            "safe_feat3": "ปิด Services ที่ปลอดภัย",
            "comp_feat1": "Optimize เครือข่าย",
            "comp_feat2": "โหมดประสิทธิภาพสูงสุด",
            "comp_feat3": "ปรับ Services สำหรับเกม",
            "ext_feat1": "ปรับ BCDEdit",
            "ext_feat2": "ปรับ Services ขั้นสูง",
            "ext_feat3": "บังคับใช้พลังงานสูงสุด",
            # Error messages
            "error": "ข้อผิดพลาด",
            "profile_not_found": "ไม่พบ Profile {name}!",
            "safety_check": "ตรวจสอบความปลอดภัย",
            "confirm_apply": "ยืนยันการใช้งาน",
            "apply_question": "ใช้งาน Profile {name}?\nClutchG จะพยายามสร้าง backup อัตโนมัติก่อนเริ่มการเปลี่ยนแปลง",
            "continue": "ดำเนินการต่อ?",
            "warning_intro": "Profile นี้มีคำเตือน:\n\n",
        }
    }

    def __init__(self, parent, app: 'ClutchGApp'):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header
        self.create_header()

        # 2. Hero Section / Info
        self.create_hero_section()

        # 3. Profile Cards Grid
        self.create_profile_cards()

    def _ui(self, key: str) -> str:
        """Get UI string in current language"""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Tahoma", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def create_header(self):
        """View Header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["xl"]))

        ctk.CTkLabel(
            header,
            text=self._ui("title"),
            font=self._font(24, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

    def create_hero_section(self):
        """Intro text"""
        hero = ctk.CTkFrame(self, fg_color="transparent")
        hero.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["xl"]))

        ctk.CTkLabel(
            hero,
            text=self._ui("hero_title"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            hero,
            text=self._ui("hero_subtitle"),
            font=self._font(13),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(SPACING["xs"], 0))

    def create_profile_cards(self):
        """Create responsive grid of profile cards"""
        cards_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            label_text=""
        )
        cards_container.grid(row=2, column=0, sticky="nsew")

        # Configure columns for responsive layout (3 equal columns)
        cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        cards_container.grid_rowconfigure(0, weight=1)

        # Profile Configurations
        # Using native icons via ICON() helper
        profiles = [
            {
                "name": "SAFE",
                "icon": ICON("safe"), # Shield
                "desc": self._ui("safe_desc"),
                "risk": self._ui("low_risk"),
                "features": [self._ui("safe_feat1"), self._ui("safe_feat2"), self._ui("safe_feat3")],
                "color": COLORS["risk_low"]
            },
            {
                "name": "COMPETITIVE",
                "icon": ICON("competitive"), # Lightning
                "desc": self._ui("competitive_desc"),
                "risk": self._ui("medium_risk"),
                "features": [self._ui("comp_feat1"), self._ui("comp_feat2"), self._ui("comp_feat3")],
                "color": COLORS["risk_medium"]
            },
            {
                "name": "EXTREME",
                "icon": ICON("extreme"), # Fire/Warning
                "desc": self._ui("extreme_desc"),
                "risk": self._ui("high_risk"),
                "features": [self._ui("ext_feat1"), self._ui("ext_feat2"), self._ui("ext_feat3")],
                "color": COLORS["risk_high"]
            }
        ]

        for i, p in enumerate(profiles):
            self.create_single_card(cards_container, i, p)

    def create_single_card(self, parent, col_index, data):
        """Instantiate ProfileCard component"""
        card = ProfileCard(
            parent,
            profile_name=data["name"],
            profile_icon=data["icon"],
            description=data["desc"],
            risk_level=data["risk"],
            features=data["features"],
            glow_color=data["color"],
            on_apply=lambda n=data["name"]: self.apply_profile(n)
        )
        # Add spacing between cards
        padx = (0, SPACING["lg"]) if col_index < 2 else 0
        card.grid(row=0, column=col_index, sticky="nsew", padx=padx, pady=(0, SPACING["lg"]))

        # Add hover effect
        card.add_hover_effect()

    def apply_profile(self, name):
        """Apply profile logic (same business logic, better UI interaction)"""
        from gui.components.execution_dialog import ExecutionDialog

        profile = self.app.profile_manager.get_profile(name)
        if not profile:
            show_info(
                self.app.window,
                self._ui("error"),
                self._ui("profile_not_found").format(name=name)
            )
            return

        # Warning Logic
        if profile.warnings:
            warning_msg = (
                self._ui("warning_intro")
                + "\n".join(f"• {w}" for w in profile.warnings)
                + "\n\n"
                + self._ui("continue")
            )
            if not show_confirmation(
                self.app.window,
                self._ui("safety_check"),
                warning_msg,
                confirm_text=self._ui("continue"),
                risk_level="HIGH"
            ):
                return
        else:
            if not show_confirmation(
                self.app.window,
                self._ui("confirm_apply"),
                self._ui("apply_question").format(name=name),
                confirm_text="Apply",
                risk_level="MEDIUM"
            ):
                return

        dialog = ExecutionDialog(self, profile)

        def run_profile():
            result = self.app.profile_manager.apply_profile(
                profile,
                on_progress=dialog.set_progress,
                on_output=dialog.add_output
            )
            dialog.show_result(result)

        threading.Thread(target=run_profile, daemon=True).start()
