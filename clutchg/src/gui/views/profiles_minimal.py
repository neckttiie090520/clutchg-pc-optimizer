"""
Profiles View - Phase 3 Redesign
Stats-grid cards, risk bar, compare panel, no feature bullets
Updated: 2026-03-28 (Phase 3 S2)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING
import threading

from gui.theme import COLORS, SIZES, SPACING, RADIUS, PROFILE_COLORS, NAV_ICONS, ICON
from gui.style import font
from gui.components.glass_card import ProfileCard, GlassCard
from gui.components.enhanced_button import EnhancedButton
from gui.components.refined_dialog import show_confirmation, show_info

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


# Stats for each profile — used by cards and compare table
PROFILE_STATS = {
    "SAFE": {"tweaks": 12, "gain": "+2-5% FPS", "risk": "LOW", "restart": "No"},
    "COMPETITIVE": {
        "tweaks": 24,
        "gain": "+5-10% FPS",
        "risk": "MEDIUM",
        "restart": "Yes",
    },
    "EXTREME": {"tweaks": 35, "gain": "+10-15% FPS", "risk": "HIGH", "restart": "Yes"},
}

REVERSIBLE_MAP = {
    "SAFE": "yes",
    "COMPETITIVE": "mostly",
    "EXTREME": "partial",
}


class ProfilesView(ctk.CTkFrame):
    """Modern Profiles Selection View"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Profiles",
            "hero_title": "Pick a profile. Start with Safe if unsure.",
            "hero_subtitle": "Each profile bundles specific Windows 11 tweaks. All changes are logged and reversible.",
            # Profile descriptions
            "safe_desc": "For everyday use and stability. Applies conservative, reversible optimizations.",
            "competitive_desc": "Balanced for gamers. Improves responsiveness with moderate trade-offs.",
            "extreme_desc": "Aggressive tuning for advanced users who understand backup and rollback.",
            # Risk labels
            "low_risk": "LOW RISK",
            "medium_risk": "MEDIUM RISK",
            "high_risk": "HIGH RISK",
            # Stats & compare
            "preview": "Preview",
            "apply_btn": "Apply {name}",
            "compare_title": "Compare Profiles",
            "stat_tweaks": "Tweaks",
            "stat_gain": "Gain",
            "stat_risk": "Risk",
            "stat_restart": "Restart",
            "stat_reversible": "Reversible",
            "yes": "Yes",
            "no": "No",
            "mostly": "Mostly",
            "partial": "Partial",
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
            "title": "Profiles",
            "hero_title": "เลือก Profile เริ่มจาก Safe ถ้าไม่แน่ใจ",
            "hero_subtitle": "แต่ละ Profile รวม tweak เฉพาะของ Windows 11 ทุกการเปลี่ยนแปลงบันทึกและย้อนกลับได้",
            # Profile descriptions
            "safe_desc": "สำหรับการใช้งานทั่วไปและความเสถียร ใช้การปรับแต่งแบบอนุรักษ์นิยมที่ย้อนกลับได้",
            "competitive_desc": "สมดุลสำหรับเกมเมอร์ เพิ่มความลื่นไหลด้วย trade-off ระดับกลาง",
            "extreme_desc": "การจูนแบบเข้มสำหรับผู้ใช้ขั้นสูงที่เข้าใจ backup และ rollback",
            # Risk labels
            "low_risk": "LOW RISK",
            "medium_risk": "MEDIUM RISK",
            "high_risk": "HIGH RISK",
            # Stats & compare
            "preview": "ดูรายละเอียด",
            "apply_btn": "Apply {name}",
            "compare_title": "เปรียบเทียบ Profiles",
            "stat_tweaks": "Tweaks",
            "stat_gain": "ผลลัพธ์",
            "stat_risk": "ความเสี่ยง",
            "stat_restart": "Restart",
            "stat_reversible": "ย้อนกลับ",
            "yes": "ใช่",
            "no": "ไม่",
            "mostly": "ส่วนใหญ่",
            "partial": "บางส่วน",
            # Error messages
            "error": "ข้อผิดพลาด",
            "profile_not_found": "ไม่พบ Profile {name}!",
            "safety_check": "ตรวจสอบความปลอดภัย",
            "confirm_apply": "ยืนยันการใช้งาน",
            "apply_question": "ใช้งาน Profile {name}?\nClutchG จะพยายามสร้าง backup อัตโนมัติก่อนเริ่มการเปลี่ยนแปลง",
            "continue": "ดำเนินการต่อ?",
            "warning_intro": "Profile นี้มีคำเตือน:\n\n",
        },
    }

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.compare_visible = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        # 1. Header
        self.create_header()

        # 2. Hero Section / Info
        self.create_hero_section()

        # 3. Profile Cards Grid
        self.create_profile_cards()

        # 4. Compare Panel (initially hidden)
        self.create_compare_panel()

    def _ui(self, key: str) -> str:
        """Get UI string in current language"""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Figtree", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def create_header(self):
        """View Header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["xl"]))

        ctk.CTkLabel(
            header,
            text=self._ui("title"),
            font=self._font(24, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

    def create_hero_section(self):
        """Intro text"""
        hero = ctk.CTkFrame(self, fg_color="transparent")
        hero.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["xl"]))

        ctk.CTkLabel(
            hero,
            text=self._ui("hero_title"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            hero,
            text=self._ui("hero_subtitle"),
            font=self._font(13),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(SPACING["xs"], 0))

    def create_profile_cards(self):
        """Create responsive grid of profile cards"""
        cards_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", label_text=""
        )
        cards_container.grid(row=2, column=0, sticky="nsew")

        # Configure columns for responsive layout (3 equal columns)
        cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        cards_container.grid_rowconfigure(0, weight=1)

        # Profile Configurations
        profiles = [
            {
                "name": "SAFE",
                "icon": ICON("safe"),
                "desc": self._ui("safe_desc"),
                "risk": self._ui("low_risk"),
                "stats": PROFILE_STATS["SAFE"],
                "color": COLORS["risk_low"],
            },
            {
                "name": "COMPETITIVE",
                "icon": ICON("competitive"),
                "desc": self._ui("competitive_desc"),
                "risk": self._ui("medium_risk"),
                "stats": PROFILE_STATS["COMPETITIVE"],
                "color": COLORS["risk_medium"],
            },
            {
                "name": "EXTREME",
                "icon": ICON("extreme"),
                "desc": self._ui("extreme_desc"),
                "risk": self._ui("high_risk"),
                "stats": PROFILE_STATS["EXTREME"],
                "color": COLORS["risk_high"],
            },
        ]

        for i, p in enumerate(profiles):
            self.create_single_card(cards_container, i, p)

    def create_single_card(self, parent, col_index, data):
        """Instantiate ProfileCard component"""
        name = data["name"]
        card = ProfileCard(
            parent,
            profile_name=name,
            profile_icon=data["icon"],
            description=data["desc"],
            risk_level=data["risk"],
            stats=data["stats"],
            glow_color=data["color"],
            on_apply=lambda n=name: self.apply_profile(n),
            on_preview=None,
        )
        # Add spacing between cards
        padx = (0, SPACING["lg"]) if col_index < 2 else 0
        card.grid(
            row=0, column=col_index, sticky="nsew", padx=padx, pady=(0, SPACING["lg"])
        )

        # Add hover effect
        card.add_hover_effect()

    # ------------------------------------------------------------------
    # Compare Panel
    # ------------------------------------------------------------------
    def create_compare_panel(self):
        """Collapsible compare-profiles table below the cards grid."""
        # Toggle button — ghost / text-link style
        self.compare_btn = ctk.CTkButton(
            self,
            text=self._ui("compare_title") + "  \u25bc",  # chevron down
            fg_color="transparent",
            hover_color=COLORS.get("bg_tertiary", "#383838"),
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(family="Figtree", size=12),
            border_width=0,
            command=self._toggle_compare,
            anchor="w",
            height=28,
        )
        self.compare_btn.grid(row=3, column=0, sticky="w", pady=(SPACING["sm"], 0))

        # Container for comparison table — hidden initially
        self.compare_container = GlassCard(self, padding=SPACING["md"])
        self.compare_container.grid(
            row=4, column=0, sticky="ew", pady=(SPACING["sm"], 0)
        )
        self.compare_container.grid_remove()
        self.grid_rowconfigure(4, weight=0)

        self._build_compare_table()

    def _toggle_compare(self):
        """Show or hide the compare panel."""
        self.compare_visible = not self.compare_visible
        if self.compare_visible:
            self.compare_container.grid()
            chevron = "\u25b2"  # up
        else:
            self.compare_container.grid_remove()
            chevron = "\u25bc"  # down
        self.compare_btn.configure(text=self._ui("compare_title") + "  " + chevron)

    def _build_compare_table(self):
        """Populate the comparison grid inside compare_container."""
        tbl = ctk.CTkFrame(self.compare_container, fg_color="transparent")
        tbl.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        # 4 columns: label | Safe | Competitive | Extreme
        for c in range(4):
            tbl.grid_columnconfigure(c, weight=1)

        headers = ["", "Safe", "Competitive", "Extreme"]
        profile_keys = ["SAFE", "COMPETITIVE", "EXTREME"]

        row_defs = [
            ("stat_tweaks", lambda k: str(PROFILE_STATS[k]["tweaks"])),
            ("stat_gain", lambda k: PROFILE_STATS[k]["gain"]),
            ("stat_risk", lambda k: PROFILE_STATS[k]["risk"]),
            ("stat_restart", lambda k: PROFILE_STATS[k]["restart"]),
            ("stat_reversible", lambda k: self._ui(REVERSIBLE_MAP[k])),
        ]

        risk_color_map = {
            "LOW": COLORS["success"],
            "MEDIUM": COLORS["warning"],
            "HIGH": COLORS["danger"],
        }

        # Header row
        for c, h in enumerate(headers):
            ctk.CTkLabel(
                tbl,
                text=h,
                font=ctk.CTkFont(family="Figtree", size=12, weight="bold"),
                text_color=COLORS["text_primary"],
            ).grid(
                row=0,
                column=c,
                padx=4,
                pady=(0, SPACING["xs"]),
                sticky="w" if c == 0 else "",
            )

        # Data rows
        for r, (label_key, value_fn) in enumerate(row_defs, start=1):
            # Label column
            ctk.CTkLabel(
                tbl,
                text=self._ui(label_key),
                font=ctk.CTkFont(family="Figtree", size=12),
                text_color=COLORS["text_secondary"],
            ).grid(row=r, column=0, padx=4, pady=2, sticky="w")

            for c, pk in enumerate(profile_keys, start=1):
                val = value_fn(pk)
                # Color risk cells
                text_color = COLORS["text_primary"]
                if label_key == "stat_risk":
                    text_color = risk_color_map.get(val, COLORS["text_primary"])

                ctk.CTkLabel(
                    tbl,
                    text=val,
                    font=ctk.CTkFont(family="Figtree", size=12),
                    text_color=text_color,
                ).grid(row=r, column=c, padx=4, pady=2)

    # ------------------------------------------------------------------
    # Apply profile logic
    # ------------------------------------------------------------------
    def apply_profile(self, name):
        """Apply profile logic (same business logic, better UI interaction)"""
        from gui.components.execution_dialog import ExecutionDialog

        profile = self.app.profile_manager.get_profile(name)
        if not profile:
            show_info(
                self.app.window,
                self._ui("error"),
                self._ui("profile_not_found").format(name=name),
            )
            return

        # Warning Logic
        if profile.warnings:
            warning_msg = (
                self._ui("warning_intro")
                + "\n".join(f"  {w}" for w in profile.warnings)
                + "\n\n"
                + self._ui("continue")
            )
            if not show_confirmation(
                self.app.window,
                self._ui("safety_check"),
                warning_msg,
                confirm_text=self._ui("continue"),
                risk_level="HIGH",
            ):
                return
        else:
            if not show_confirmation(
                self.app.window,
                self._ui("confirm_apply"),
                self._ui("apply_question").format(name=name),
                confirm_text=self._ui("apply_btn").format(name=name),
                risk_level="MEDIUM",
            ):
                return

        dialog = ExecutionDialog(self, profile)

        def run_profile():
            result = self.app.profile_manager.apply_profile(
                profile, on_progress=dialog.set_progress, on_output=dialog.add_output
            )
            dialog.show_result(result)

        threading.Thread(target=run_profile, daemon=True).start()
