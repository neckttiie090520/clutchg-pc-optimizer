"""
Scripts View — Presets, Custom Builder, and Education Encyclopedia
3-tab layout with spec-based recommendations and full tweak documentation
Updated: 2026-02-11
"""

import tkinter as tk
import customtkinter as ctk
from typing import TYPE_CHECKING, List, Optional, Dict, Set
import threading
from gui.theme import (
    COLORS,
    SIZES,
    SPACING,
    RADIUS,
    get_risk_colors,
    NAV_ICONS,
    ICON,
    ICON_FONT,
    theme_manager,
)
from gui.style import font
from gui.components.glass_card import GlassCard
from gui.components.enhanced_button import EnhancedButton
from gui.components.execution_dialog import ExecutionDialog
from gui.components.refined_dialog import show_confirmation
from core.tweak_registry import get_tweak_registry, Tweak, TWEAK_CATEGORIES
from core.action_catalog import ActionCatalog, ActionDefinition

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


def get_risk_display(level: str) -> dict:
    """Get risk level display colors using theme system"""
    level_upper = level.upper()
    if level_upper == "LOW":
        return {
            "bg": COLORS["success_dim"],
            "fg": COLORS["risk_low"],
            "label": "Low Risk",
        }
    if level_upper in ("MEDIUM", "MED"):
        return {
            "bg": COLORS["warning_dim"],
            "fg": COLORS["risk_medium"],
            "label": "Medium",
        }
    if level_upper == "HIGH":
        return {
            "bg": COLORS["danger_dim"],
            "fg": COLORS["risk_high"],
            "label": "High Risk",
        }
    return {"bg": COLORS["bg_card"], "fg": COLORS["text_secondary"], "label": "N/A"}


# Preset definitions
PRESET_INFO = {
    "safe": {
        "icon": ICON("verified_user"),
        "title": "Safe",
        "subtitle": "Evidence-based, fully reversible",
        "fps": "+3-5 FPS",
        "risk": "LOW",
        "color": "#22C55E",
        "dim": "#1a2e1f",
        "desc": "Stable everyday tweaks. Zero risk of breaking anything. Good for most users.",
        "restart": "No",
        "risk_bar_pct": 0.15,
        "services_disabled": "0",
        "registry_changes": "4",
        "bcdedit_changes": "0",
    },
    "competitive": {
        "icon": ICON("speed"),
        "title": "Competitive",
        "subtitle": "Tuned for ranked play",
        "fps": "+8-15 FPS",
        "risk": "MEDIUM",
        "color": "#F59E0B",
        "dim": "#2e2510",
        "desc": "Aggressive tuning for esports. Disables some background services. May need restart.",
        "restart": "Maybe",
        "risk_bar_pct": 0.50,
        "services_disabled": "6",
        "registry_changes": "12",
        "bcdedit_changes": "2",
    },
    "extreme": {
        "icon": ICON("local_fire_department"),
        "title": "Extreme",
        "subtitle": "Max squeeze, advanced users only",
        "fps": "+15-25 FPS",
        "risk": "HIGH",
        "color": "#EF4444",
        "dim": "#2e1616",
        "desc": "Max performance. Strips system to bare minimum. Requires restart. Know what you're doing.",
        "restart": "Yes",
        "risk_bar_pct": 0.85,
        "services_disabled": "14",
        "registry_changes": "22",
        "bcdedit_changes": "5",
    },
}


class ScriptsView(ctk.CTkFrame):
    """Scripts view with 3 tabs: Presets, Custom Builder, Education"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Tweaks",
            "stats": "{tweaks} tweaks  ·  {categories} categories",
            # Tab names
            "tab_presets": "Profiles",
            "tab_custom": "Custom",
            "tab_education": "Info",
            # Preset info
            "safe_title": "Safe",
            "safe_subtitle": "Evidence-based, fully reversible",
            "safe_desc": "Stable everyday tweaks. Zero risk of breaking anything. Good for most users.",
            "comp_title": "Competitive",
            "comp_subtitle": "Tuned for ranked play",
            "comp_desc": "Aggressive tuning for esports. Disables some background services. May need restart.",
            "ext_title": "Extreme",
            "ext_subtitle": "Max squeeze, advanced users only",
            "ext_desc": "Max performance. Strips system to bare minimum. Requires restart. Know what you're doing.",
            # Risk labels
            "low_risk": "Low Risk",
            "medium_risk": "Medium",
            "high_risk": "High Risk",
            # Profiles view header
            "profiles_subtitle": "Pick a preset optimization level for your system",
            "compare": "Compare",
            "compare_title": "Quick Comparison",
            # Stats labels
            "stat_tweaks": "Tweaks",
            "stat_gain": "Gain",
            "stat_risk": "Risk",
            "stat_restart": "Restart",
            "restart_no": "No",
            "restart_maybe": "Maybe",
            "restart_yes": "Yes",
            # Compare row labels
            "cmp_total_tweaks": "Total tweaks",
            "cmp_fps_gain": "FPS gain",
            "cmp_services": "Services disabled",
            "cmp_registry": "Registry changes",
            "cmp_bcdedit": "BCDEdit changes",
            "cmp_restart": "Requires restart",
            # Common
            "apply": "Apply",
            "preview": "Preview",
            "see_details": "View Details",
            "view_tweaks": "View Tweaks",
            "recommended": "Recommended",
            "rec_reason": "Recommendation based on your system: {reason}",
            "tweaks_count": "{count} tweaks",
            "hero_guidance": "Best balance of FPS and stability",
            # Actionable desc (1-line versions for secondary cards)
            "safe_short": "No risk. Ideal for daily use.",
            "comp_short": "Best FPS without sacrificing stability.",
            "ext_short": "Maximum performance. May cause instability.",
        },
        "th": {
            "title": "Tweaks",
            "stats": "{tweaks} tweaks  ·  {categories} หมวดหมู่",
            # Tab names
            "tab_presets": "Profiles",
            "tab_custom": "Custom",
            "tab_education": "Info",
            # Preset info
            "safe_title": "Safe",
            "safe_subtitle": "ยืนยันได้จากหลักฐาน สามารถย้อนกลับได้",
            "safe_desc": "Tweaks ใช้ได้ทุกวัน ไม่มีความเสี่ยง เหมาะกับผู้ใช้ทั่วไป",
            "comp_title": "Competitive",
            "comp_subtitle": "จูนสำหรับเกม Ranked",
            "comp_desc": "จูนแบบจัดหนักสำหรับ Esports ปิด Services บางตัว อาจต้อง Restart",
            "ext_title": "Extreme",
            "ext_subtitle": "บีบสุด สำหรับคนรู้จริง",
            "ext_desc": "ประสิทธิภาพสูงสุด ลดทุกอย่างให้เหลือน้อยที่สุด ต้อง Restart รู้ว่าทำอะไรอยู่ก่อนกด",
            # Risk labels
            "low_risk": "Low Risk",
            "medium_risk": "Medium",
            "high_risk": "High Risk",
            # Profiles view header
            "profiles_subtitle": "เลือกระดับ Optimization สำหรับเครื่องของคุณ",
            "compare": "Compare",
            "compare_title": "เปรียบเทียบ",
            # Stats labels
            "stat_tweaks": "Tweaks",
            "stat_gain": "Gain",
            "stat_risk": "Risk",
            "stat_restart": "Restart",
            "restart_no": "ไม่",
            "restart_maybe": "อาจจะ",
            "restart_yes": "ใช่",
            # Compare row labels
            "cmp_total_tweaks": "Tweaks ทั้งหมด",
            "cmp_fps_gain": "FPS gain",
            "cmp_services": "Services ที่ปิด",
            "cmp_registry": "Registry ที่เปลี่ยน",
            "cmp_bcdedit": "BCDEdit ที่เปลี่ยน",
            "cmp_restart": "ต้อง Restart",
            # Common
            "apply": "ใช้งาน",
            "preview": "ดูรายละเอียด",
            "see_details": "ดูรายละเอียด",
            "view_tweaks": "ดู Tweaks",
            "recommended": "แนะนำ",
            "rec_reason": "แนะนำจากสเปคของคุณ: {reason}",
            "tweaks_count": "{count} tweaks",
            "hero_guidance": "สมดุล FPS และความเสถียรที่ดีที่สุด",
            # Actionable desc (1-line versions for secondary cards)
            "safe_short": "ไม่มีความเสี่ยง เหมาะสำหรับการใช้ทุกวัน",
            "comp_short": "FPS ดีที่สุดโดยไม่เสียเสถียรภาพ",
            "ext_short": "ประสิทธิภาพสูงสุด อาจมีความไม่เสถียร",
        },
    }

    UI_STRINGS["en"].update(
        {
            "tab_quick_actions": "Quick Fix",
            "quick_actions_subtitle": "One-click packs. Pick one, hit run, done.",
            "quick_group_general": "General",
            "quick_group_advanced": "Advanced",
            "quick_group_cleanup": "Cleanup",
            "quick_group_windows": "Windows",
            "quick_group_utilities": "Utilities",
            "quick_run": "Run",
            "quick_open": "Open",
            "quick_confirm_title": "Confirm Quick Action",
            "quick_confirm_body": (
                "Action: {title}\n"
                "Type: {kind}\n"
                "Tweaks: {count}\n"
                "Max Risk: {risk}\n"
                "Restart Required: {restart}\n\n"
                "Auto-backup: {backup}\n"
                "Proceed?"
            ),
            "quick_restart_yes": "Yes",
            "quick_restart_no": "No",
            "quick_backup_enabled": "Enabled",
            "quick_backup_disabled": "Disabled",
            "quick_catalog_error": "Quick Actions unavailable due to catalog validation issues.",
            "quick_catalog_details": "Please review action catalog integrity before running actions.",
            "quick_link_confirm": "Open this trusted link?\n\n{url}",
            "quick_action_done": "Quick action completed.",
            "quick_action_failed": "Quick action failed. Check execution output.",
            "quick_link_opened": "Link opened in browser.",
            "quick_link_blocked": "Link blocked by confirmation or trust policy.",
        }
    )

    UI_STRINGS["th"].update(
        {
            "tab_quick_actions": "Quick Fix",
            "quick_actions_subtitle": "แพ็คสำเร็จรูป เลือก กดรัน จบ",
            "quick_group_general": "General",
            "quick_group_advanced": "Advanced",
            "quick_group_cleanup": "Cleanup",
            "quick_group_windows": "Windows",
            "quick_group_utilities": "Utilities",
            "quick_run": "Run",
            "quick_open": "Open",
            "quick_confirm_title": "Confirm Quick Action",
            "quick_confirm_body": (
                "Action: {title}\n"
                "Type: {kind}\n"
                "Tweaks: {count}\n"
                "Max Risk: {risk}\n"
                "Restart Required: {restart}\n\n"
                "Auto-backup: {backup}\n"
                "Proceed?"
            ),
            "quick_restart_yes": "Yes",
            "quick_restart_no": "No",
            "quick_backup_enabled": "Enabled",
            "quick_backup_disabled": "Disabled",
            "quick_catalog_error": "Quick Actions unavailable due to catalog validation issues.",
            "quick_catalog_details": "Please review action catalog integrity before running actions.",
            "quick_link_confirm": "Open this trusted link?\n\n{url}",
            "quick_action_done": "Quick action completed.",
            "quick_action_failed": "Quick action failed. Check execution output.",
            "quick_link_opened": "Link opened in browser.",
            "quick_link_blocked": "Link blocked by confirmation or trust policy.",
        }
    )

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.registry = get_tweak_registry()
        self.action_catalog = getattr(
            self.app, "action_catalog", None
        ) or ActionCatalog(self.registry)
        self.quick_actions_errors: List[str] = list(
            getattr(self.app, "action_catalog_errors", [])
        )
        if not self.quick_actions_errors:
            self.quick_actions_errors = self.action_catalog.validate()
        self.selected_tweaks: Set[str] = set()
        self.detail_tweak_id: Optional[str] = None
        self.active_tab = "quick_actions"
        self.active_quick_group = "general"
        self.active_edu_category: Optional[str] = None
        self._custom_container = None  # dedicated frame for custom tab

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self._create_header()
        # Tab bar
        self._create_tab_bar()
        # Content area
        self._create_content_area()

        self.after(100, self._show_quick_actions_tab)

    def _ui(self, key: str, **kwargs) -> str:
        """Get UI string in current language"""
        lang = self.app.config.get("language", "en")
        return (
            self.UI_STRINGS.get(lang, self.UI_STRINGS["en"])
            .get(key, key)
            .format(**kwargs)
        )

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Figtree", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def _get_preset_info(self) -> dict:
        """Get localized preset information with stats for profile cards.
        NOTE: 'risk' key must be the canonical key ("LOW"/"MEDIUM"/"HIGH"),
        NOT the display label — _create_preset_card looks it up in _get_risk_colors().
        """
        return {
            "safe": {
                "icon": ICON("verified_user"),
                "title": self._ui("safe_title"),
                "subtitle": self._ui("safe_subtitle"),
                "fps": "+3-5 FPS",
                "risk": "LOW",
                "color": COLORS.get("success", "#22C55E"),
                "dim": COLORS.get("success_dim", "#1a2e1f"),
                "desc": self._ui("safe_desc"),
                "restart": self._ui("restart_no"),
                "risk_bar_pct": 0.15,
                # Compare data
                "services_disabled": 0,
                "registry_changes": 4,
                "bcdedit_changes": 0,
            },
            "competitive": {
                "icon": ICON("speed"),
                "title": self._ui("comp_title"),
                "subtitle": self._ui("comp_subtitle"),
                "fps": "+8-15 FPS",
                "risk": "MEDIUM",
                "color": COLORS.get("warning", "#F59E0B"),
                "dim": COLORS.get("warning_dim", "#2e2510"),
                "desc": self._ui("comp_desc"),
                "restart": self._ui("restart_maybe"),
                "risk_bar_pct": 0.50,
                "services_disabled": 6,
                "registry_changes": 12,
                "bcdedit_changes": 2,
            },
            "extreme": {
                "icon": ICON("local_fire_department"),
                "title": self._ui("ext_title"),
                "subtitle": self._ui("ext_subtitle"),
                "fps": "+15-25 FPS",
                "risk": "HIGH",
                "color": COLORS.get("danger", "#EF4444"),
                "dim": COLORS.get("danger_dim", "#2e1616"),
                "desc": self._ui("ext_desc"),
                "restart": self._ui("restart_yes"),
                "risk_bar_pct": 0.85,
                "services_disabled": 14,
                "registry_changes": 22,
                "bcdedit_changes": 5,
            },
        }

    def _get_risk_colors(self) -> dict:
        """Get risk level colors from theme tokens (not hard-coded hex)."""
        return {
            "LOW": {
                "bg": COLORS.get("success_dim", "#064E3B"),
                "fg": COLORS.get("risk_low", "#34D399"),
                "label": self._ui("low_risk"),
            },
            "MEDIUM": {
                "bg": COLORS.get("warning_dim", "#78350F"),
                "fg": COLORS.get("risk_medium", "#FBBF24"),
                "label": self._ui("medium_risk"),
            },
            "HIGH": {
                "bg": COLORS.get("danger_dim", "#7F1D1D"),
                "fg": COLORS.get("risk_high", "#F87171"),
                "label": self._ui("high_risk"),
            },
        }

    # ================================================================
    # HEADER
    # ================================================================
    def _create_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hdr,
            text=self._ui("title"),
            font=self._font(24, "bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        all_tweaks = self.registry.get_all_tweaks()
        stats_text = self._ui(
            "stats", tweaks=len(all_tweaks), categories=len(TWEAK_CATEGORIES)
        )
        ctk.CTkLabel(
            hdr,
            text=stats_text,
            font=self._font(12),
            text_color=COLORS["text_tertiary"],
        ).grid(row=0, column=1, sticky="w", padx=(SPACING["md"], 0))

    # ================================================================
    # TAB BAR
    # ================================================================
    def _create_tab_bar(self):
        # Wrapper row — left-aligned so bar doesn't stretch full width
        tab_row = ctk.CTkFrame(self, fg_color="transparent")
        tab_row.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["md"]))

        bar = ctk.CTkFrame(
            tab_row,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        bar.pack(side="left")

        # Tabler Icons codepoints (v3.41.1)
        tabs = [
            ("quick_actions", "\uea38", self._ui("tab_quick_actions")),  # bolt
            ("presets", "\uf1f6", self._ui("tab_presets")),  # category
            ("custom", "\uebca", self._ui("tab_custom")),  # tools
            ("education", "\ueac5", self._ui("tab_education")),  # info-circle
        ]

        self.tab_buttons = {}
        for i, (key, icon, label) in enumerate(tabs):
            btn = self._create_tab_button(bar, key, icon, label)
            btn.pack(side="left", padx=SPACING["xs"], pady=SPACING["xs"])
            self.tab_buttons[key] = btn

    def _create_tab_button(self, parent, key: str, icon: str, label: str):
        """Create a custom tab button with separate icon/text labels"""
        is_active = key == self.active_tab
        colors = theme_manager.get_colors()

        # Colors - Dynamic text color for readability
        fg_color = colors["accent"] if is_active else "transparent"
        text_color = (
            colors.get("text_on_accent", "#FFFFFF")
            if is_active
            else colors["text_secondary"]
        )
        hover_color = colors["accent_hover"] if is_active else colors["bg_card_hover"]

        # Container Frame
        btn_frame = ctk.CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=RADIUS["md"],
            height=38,
            cursor="hand2",
        )
        # Bind click to frame
        btn_frame.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))

        # Layout container
        content_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Icon Label (Material Symbols font)
        icon_lbl = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=ctk.CTkFont(family="Tabler Icons", size=16),
            text_color=text_color,
        )
        icon_lbl.pack(side="left", padx=(10, 5))

        # Text Label (Inter/Tahoma font based on language)
        text_lbl = ctk.CTkLabel(
            content_frame,
            text=label,
            font=self._font(13, "bold") if is_active else self._font(13),
            text_color=text_color,
        )
        text_lbl.pack(side="left", padx=(0, 10))

        # Forward clicks to frame
        for widget in [content_frame, icon_lbl, text_lbl]:
            widget.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))

        # Store references for updates
        btn_frame._icon_widget = icon_lbl
        btn_frame._text_widget = text_lbl

        return btn_frame

    def _switch_tab(self, tab_key: str):
        self.active_tab = tab_key
        colors = theme_manager.get_colors()

        # Update custom button styles
        for key, btn in self.tab_buttons.items():
            is_active = key == tab_key

            # Colors
            fg_color = colors["accent"] if is_active else "transparent"
            text_color = (
                colors.get("text_on_accent", "#FFFFFF")
                if is_active
                else colors["text_secondary"]
            )

            btn.configure(fg_color=fg_color)

            # Update Labels
            if hasattr(btn, "_icon_widget"):
                btn._icon_widget.configure(text_color=text_color)
            if hasattr(btn, "_text_widget"):
                btn._text_widget.configure(
                    text_color=text_color,
                    font=self._font(13, "bold") if is_active else self._font(13),
                )

        # Show content
        if tab_key == "quick_actions":
            self._show_quick_actions_tab()
        elif tab_key == "presets":
            self._show_presets_tab()
        elif tab_key == "custom":
            self._show_custom_tab()
        elif tab_key == "education":
            self._show_education_tab()

    # ================================================================
    # CONTENT AREA
    # ================================================================
    def _create_content_area(self):
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        # Destroy the custom tab's dedicated container and restore the
        # shared scrollable content frame that other tabs use.
        if hasattr(self, "_custom_container") and self._custom_container is not None:
            self._custom_container.destroy()
            self._custom_container = None
            # Re-show the shared scrollable content frame
            self.content._parent_frame.grid()

    # ================================================================
    # TAB 1: QUICK ACTIONS
    # ================================================================
    def _show_quick_actions_tab(self):
        self._clear_content()

        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=self._ui("quick_actions_subtitle"),
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            wraplength=900,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        if self.quick_actions_errors:
            err_card = GlassCard(self.content, glow_color=COLORS["danger"])
            err_card.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["md"]))
            ctk.CTkLabel(
                err_card,
                text=self._ui("quick_catalog_error"),
                font=self._font(14, "bold"),
                text_color=COLORS["danger"],
            ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))
            ctk.CTkLabel(
                err_card,
                text=self._ui("quick_catalog_details"),
                font=self._font(12),
                text_color=COLORS["text_secondary"],
                wraplength=860,
                justify="left",
            ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["xs"]))
            preview = "\n".join(f"- {e}" for e in self.quick_actions_errors[:5])
            ctk.CTkLabel(
                err_card,
                text=preview,
                font=self._font(11),
                text_color=COLORS["text_tertiary"],
                wraplength=860,
                justify="left",
            ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))
            return

        groups_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        groups_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["md"]))

        values = [
            self._ui("quick_group_general"),
            self._ui("quick_group_advanced"),
            self._ui("quick_group_cleanup"),
            self._ui("quick_group_windows"),
            self._ui("quick_group_utilities"),
        ]
        self.quick_group_key_map = {
            self._ui("quick_group_general"): "general",
            self._ui("quick_group_advanced"): "advanced",
            self._ui("quick_group_cleanup"): "cleanup",
            self._ui("quick_group_windows"): "windows",
            self._ui("quick_group_utilities"): "utilities",
        }
        self.quick_group_label_map = {v: k for k, v in self.quick_group_key_map.items()}

        # Custom Segmented Control for better contrast
        self.quick_group_buttons = {}

        # Container for buttons
        btn_container = ctk.CTkFrame(groups_frame, fg_color="transparent")
        btn_container.pack(fill="x")

        current_label = self.quick_group_label_map.get(
            self.active_quick_group, values[0]
        )

        for i, val in enumerate(values):
            is_selected = val == current_label

            btn = ctk.CTkButton(
                btn_container,
                text=val,
                font=self._font(12, "bold" if is_selected else "normal"),
                fg_color=COLORS["accent"] if is_selected else COLORS["bg_card"],
                text_color=COLORS.get("text_on_accent", "#FFFFFF")
                if is_selected
                else COLORS["text_secondary"],
                hover_color=COLORS["accent_hover"]
                if is_selected
                else COLORS["bg_card_hover"],
                corner_radius=RADIUS["md"],
                height=36,
                command=lambda v=val: self._on_quick_group_change(v),
            )
            # Add small gap between buttons
            btn.pack(
                side="left",
                padx=(0, SPACING["xs"]) if i < len(values) - 1 else 0,
            )
            self.quick_group_buttons[val] = btn

        # self.quick_groups = ... (Removed)
        # self.quick_groups.pack(...) (Removed)
        # self.quick_groups.set(...) (Removed)

        self.quick_actions_container = ctk.CTkFrame(
            self.content, fg_color="transparent"
        )
        self.quick_actions_container.grid(row=2, column=0, sticky="nsew")
        self.quick_actions_container.grid_columnconfigure(0, weight=1)
        self.quick_actions_container.grid_columnconfigure(1, weight=1)

        self._render_quick_actions()

    def _on_quick_group_change(self, selected_value: str):
        # Update button visual states
        if hasattr(self, "quick_group_buttons"):
            for label, btn in self.quick_group_buttons.items():
                is_selected = label == selected_value
                btn.configure(
                    fg_color=COLORS["accent"] if is_selected else COLORS["bg_card"],
                    text_color=COLORS.get("text_on_accent", "#FFFFFF")
                    if is_selected
                    else COLORS["text_secondary"],
                    hover_color=COLORS["accent_hover"]
                    if is_selected
                    else COLORS["bg_card_hover"],
                    font=self._font(12, "bold" if is_selected else "normal"),
                )

        self.active_quick_group = self.quick_group_key_map.get(
            selected_value, "general"
        )
        self._render_quick_actions()

    def _render_quick_actions(self):
        if not hasattr(self, "quick_actions_container"):
            return

        for widget in self.quick_actions_container.winfo_children():
            widget.destroy()

        actions = self.action_catalog.get_actions(
            self.active_quick_group,
            system_profile=getattr(self.app, "system_profile", None),
        )

        if not actions:
            ctk.CTkLabel(
                self.quick_actions_container,
                text="No actions available for this group on current system.",
                font=self._font(12),
                text_color=COLORS["text_tertiary"],
            ).grid(row=0, column=0, sticky="w", pady=SPACING["md"])
            return

        total = len(actions)
        for idx, action in enumerate(actions):
            row = idx // 2
            col = idx % 2
            is_last_odd = (idx == total - 1) and (total % 2 == 1)
            card = self._create_quick_action_card(self.quick_actions_container, action)
            card.grid(
                row=row,
                column=col,
                columnspan=2 if is_last_odd else 1,
                sticky="nsew",
                padx=(0, SPACING["md"]) if col == 0 and not is_last_odd else 0,
                pady=(0, SPACING["md"]),
            )

    def _create_quick_action_card(self, parent, action: ActionDefinition):
        summary = self.action_catalog.summarize(action)
        display_risk = summary.max_risk if action.kind == "tweak_pack" else "N/A"
        _risk_colors = self._get_risk_colors()
        risk_color = _risk_colors.get(
            display_risk,
            {"bg": COLORS["bg_card"], "fg": COLORS["text_secondary"], "label": "N/A"},
        )
        badge_label = risk_color["label"] if action.kind == "tweak_pack" else "Link"

        card = GlassCard(parent, corner_radius=RADIUS["lg"], padding=SPACING["md"])
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=action.title,
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["xs"]))

        ctk.CTkLabel(
            card,
            text=action.description,
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            wraplength=420,
            justify="left",
        ).pack(anchor="w", padx=SPACING["md"])

        helper_text = action.helper_text or (
            f"{summary.tweak_count} tweaks"
            if action.kind == "tweak_pack"
            else "Trusted curated link"
        )
        ctk.CTkLabel(
            card,
            text=helper_text,
            font=self._font(11),
            text_color=COLORS["text_tertiary"],
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["sm"]))

        meta = ctk.CTkFrame(card, fg_color="transparent")
        meta.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))
        ctk.CTkLabel(
            meta,
            text=f"  {badge_label}  ",
            font=ctk.CTkFont(size=10),
            fg_color=risk_color["bg"],
            text_color=risk_color["fg"],
            corner_radius=RADIUS["sm"],
        ).pack(side="left")

        if action.kind == "tweak_pack":
            ctk.CTkLabel(
                meta,
                text=f"  {summary.tweak_count} tweaks  ",
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["bg_card"],
                text_color=COLORS["text_secondary"],
                corner_radius=RADIUS["sm"],
            ).pack(side="left", padx=(SPACING["xs"], 0))

        button_text = (
            self._ui("quick_run")
            if action.kind == "tweak_pack"
            else self._ui("quick_open")
        )
        EnhancedButton.outline(
            card,
            text=button_text,
            height=38,
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            command=lambda a=action: self._run_quick_action(a),
        ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))

        return card

    def _run_quick_action(self, action: ActionDefinition):
        if action.kind == "tweak_pack":
            self._run_quick_tweak_pack(action)
        else:
            self._run_quick_external_link(action)

    def _run_quick_tweak_pack(self, action: ActionDefinition):
        summary = self.action_catalog.summarize(action)
        auto_backup = bool(self.app.config.get("auto_backup", True))

        confirm_body = self._ui("quick_confirm_body").format(
            title=action.title,
            kind="Tweak Pack",
            count=summary.tweak_count,
            risk=summary.max_risk,
            restart=self._ui("quick_restart_yes")
            if summary.requires_restart
            else self._ui("quick_restart_no"),
            backup=self._ui("quick_backup_enabled")
            if auto_backup
            else self._ui("quick_backup_disabled"),
        )
        risk = (
            summary.max_risk if summary.max_risk in ("LOW", "MEDIUM", "HIGH") else "LOW"
        )
        if not show_confirmation(
            self.app.window,
            self._ui("quick_confirm_title"),
            confirm_body,
            confirm_text="Run",
            risk_level=risk,
        ):
            return

        dialog = ExecutionDialog(self, action.title)
        dialog.add_output(f"[Action] {action.title}")
        dialog.add_output(f"[Group] {action.group}")
        dialog.add_output(f"[Tweaks] {', '.join(action.tweak_ids)}")
        dialog.add_output("")

        def run_action():
            # Before snapshot
            try:
                from core.system_snapshot import SystemSnapshotManager

                snap_mgr = SystemSnapshotManager()
                dialog.add_output("[snap] Taking before-snapshot...")
                before_snap = snap_mgr.take_snapshot()
            except Exception:
                snap_mgr = None
                before_snap = None

            result = self.app.profile_manager.apply_tweaks(
                list(action.tweak_ids),
                on_output=dialog.add_output,
                on_progress=dialog.set_progress,
                on_tweak_status=dialog.add_tweak_status,
                auto_backup=auto_backup,
            )

            # After snapshot + diff
            if snap_mgr and before_snap:
                try:
                    dialog.add_output("[snap] Taking after-snapshot...")
                    after_snap = snap_mgr.take_snapshot()
                    diff = snap_mgr.compare(before_snap, after_snap)
                    dialog.show_diff(diff)
                except Exception:
                    pass

            dialog.show_result(result)
            if hasattr(self.app, "toast"):
                if result.success:
                    self.app.toast.success(self._ui("quick_action_done"))
                else:
                    self.app.toast.error(self._ui("quick_action_failed"))

        threading.Thread(target=run_action, daemon=True).start()

    def _run_quick_external_link(self, action: ActionDefinition):
        def _confirm(url: str) -> bool:
            return show_confirmation(
                self.app.window,
                self._ui("quick_confirm_title"),
                self._ui("quick_link_confirm", url=url),
                confirm_text="Open",
                risk_level="LOW",
            )

        opened = self.action_catalog.open_external_link(action, confirmer=_confirm)
        if hasattr(self.app, "toast"):
            if opened:
                self.app.toast.info(self._ui("quick_link_opened"))
            else:
                self.app.toast.warning(self._ui("quick_link_blocked"))

    # ================================================================
    # TAB 2: PRESETS
    # ================================================================
    def _show_presets_tab(self):
        self._clear_content()

        # ── View header: "Profiles" + subtitle + Compare ghost button ──
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=self._ui("tab_presets"),
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=self._ui("profiles_subtitle"),
            font=self._font(12),
            text_color=COLORS["text_tertiary"],
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        # Compare button (top-right) — icon + text, more discoverable
        compare_inner = ctk.CTkFrame(header, fg_color="transparent")
        compare_inner.grid(row=0, column=1, rowspan=2, sticky="ne")

        ctk.CTkLabel(
            compare_inner,
            text=ICON("compare_arrows"),
            font=ctk.CTkFont(family="Tabler Icons", size=14),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            compare_inner,
            text=self._ui("compare"),
            font=self._font(12),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_hover"],
            border_width=0,
            corner_radius=RADIUS["sm"],
            height=30,
            width=80,
            command=self._toggle_compare_panel,
        ).pack(side="left")

        # ── Hero layout ──
        suggestion = self._get_spec_suggestion()
        preset_info = self._get_preset_info()
        rec_key = suggestion.get("preset", "safe") if suggestion else "safe"
        rec_reason = suggestion.get("reason", "") if suggestion else ""

        # Row 1: Hero card (recommended preset — full width)
        if rec_key in preset_info:
            hero_info = preset_info[rec_key]
            hero_tweaks = self.registry.get_tweaks_for_preset(rec_key)
            hero_card = self._create_hero_card(
                self.content, hero_info, hero_tweaks, rec_key, rec_reason
            )
            hero_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        # Row 2: 2-column grid for the other 2 presets
        secondary_keys = [k for k in preset_info if k != rec_key]
        if secondary_keys:
            sec_grid = ctk.CTkFrame(self.content, fg_color="transparent")
            sec_grid.grid(row=2, column=0, sticky="ew", pady=(0, SPACING["sm"]))
            sec_grid.grid_columnconfigure(0, weight=1, uniform="sec")
            sec_grid.grid_columnconfigure(1, weight=1, uniform="sec")

            for col_idx, sec_key in enumerate(secondary_keys):
                sec_info = preset_info[sec_key]
                sec_tweaks = self.registry.get_tweaks_for_preset(sec_key)
                sec_card = self._create_secondary_card(
                    sec_grid, sec_info, sec_tweaks, sec_key
                )
                padx = (0, 8) if col_idx == 0 else (8, 0)
                sec_card.grid(row=0, column=col_idx, sticky="nsew", padx=padx)

        # ── Collapsible compare panel (hidden by default) ──
        self._compare_panel = None
        self._compare_visible = False

    def _create_hero_card(
        self,
        parent,
        info: dict,
        tweaks: List[Tweak],
        preset_key: str,
        reason: str,
    ):
        """Full-width hero card for the recommended preset.

        Layout (2 columns, compact):
          Left  — icon + name + RECOMMENDED badge (1 row) + guidance + pills
          Right — FPS (26px bold) + Apply + View Details (tight stack)

        Card padding: 10px 20px. Tight internal gaps (4px).
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=2,
            border_color=COLORS["success"],
        )
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0, minsize=140)

        px = 20
        py = 10

        # ── LEFT SECTION: identity + context ──
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(px, 12), pady=py)
        left.grid_columnconfigure(0, weight=1)

        # Row 0: Icon + name + RECOMMENDED badge (all one row)
        icon_name_row = ctk.CTkFrame(left, fg_color="transparent")
        icon_name_row.grid(row=0, column=0, sticky="w", pady=(0, 4))

        ctk.CTkLabel(
            icon_name_row,
            text=info["icon"],
            font=ctk.CTkFont(family="Tabler Icons", size=18),
            text_color=info["color"],
            fg_color=info["dim"],
            corner_radius=RADIUS["md"],
            width=30,
            height=30,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            icon_name_row,
            text=info["title"],
            font=self._font(14, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            icon_name_row,
            text=ICON("star"),
            font=ctk.CTkFont(family="Tabler Icons", size=12),
            text_color=COLORS["success"],
        ).pack(side="left", padx=(0, 3))

        ctk.CTkLabel(
            icon_name_row,
            text=self._ui("recommended").upper(),
            font=self._font(9, "bold"),
            text_color=COLORS["success"],
            anchor="w",
        ).pack(side="left")

        # Row 1: Guidance + pills (compact info line)
        restart_val = info.get("restart", "No")
        info_line = (
            f"{self._ui('hero_guidance')}  \u2022  "
            f"{len(tweaks)} {self._ui('stat_tweaks')}  \u2022  "
            f"{self._ui('stat_risk')}: {info['risk']}  \u2022  "
            f"{self._ui('stat_restart')}: {restart_val}"
        )
        ctk.CTkLabel(
            left,
            text=info_line,
            font=self._font(10),
            text_color=COLORS["text_tertiary"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        # Vertical separator
        ctk.CTkFrame(card, fg_color=COLORS["border"], width=1).grid(
            row=0, column=0, sticky="nse", pady=py
        )

        # ── RIGHT SECTION: decision block ──
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, px), pady=py)
        right.grid_columnconfigure(0, weight=1)

        # FPS — dominant (26px bold, accent)
        ctk.CTkLabel(
            right,
            text=info["fps"],
            font=self._font(26, "bold"),
            text_color=COLORS["accent"],
            anchor="center",
        ).grid(row=0, column=0)

        # Apply button
        ctk.CTkButton(
            right,
            text=self._ui("apply"),
            font=self._font(11, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS.get("text_on_accent", "#000000"),
            hover_color=COLORS.get("accent_hover", COLORS["accent"]),
            border_width=0,
            corner_radius=RADIUS["md"],
            height=28,
            command=lambda k=preset_key: self._apply_preset(k),
        ).grid(row=1, column=0, sticky="ew", pady=(4, 2))

        # View Details — accent ghost
        ctk.CTkButton(
            right,
            text=self._ui("see_details"),
            font=self._font(10),
            fg_color="transparent",
            text_color=COLORS["accent"],
            hover_color=COLORS["bg_hover"],
            border_width=0,
            corner_radius=RADIUS["sm"],
            height=22,
            command=lambda k=preset_key: self._show_preset_tweaks(k),
        ).grid(row=2, column=0, sticky="ew")

        return card

    def _create_secondary_card(
        self,
        parent,
        info: dict,
        tweaks: List[Tweak],
        preset_key: str,
    ):
        """Compact vertical card for non-recommended presets.

        Layout (vertical):
          Row 0 — icon label + name (13px bold) + risk badge (right-aligned)
          Row 1 — FPS gain (18px bold, accent color) — dominant value
          Row 2 — 1-line short description
          Row 3 — "{N} tweaks  •  Restart: {val}" (10px tertiary)
          Row 4 — Apply button (accent filled) + See Details ghost btn

        Spacing scale: 8px / 16px. No progress bar.
        """
        risk_colors = self._get_risk_colors()
        risk_c = risk_colors.get(info["risk"], risk_colors["LOW"])

        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid_columnconfigure(0, weight=1)
        px = 16
        py = 16
        gap = 8

        # ── Row 0: Icon label + Name + Risk badge ──
        icon_row = ctk.CTkFrame(card, fg_color="transparent")
        icon_row.grid(row=0, column=0, sticky="ew", padx=px, pady=(py, gap))
        icon_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            icon_row,
            text=info["icon"],
            font=ctk.CTkFont(family="Tabler Icons", size=17),
            text_color=info["color"],
            fg_color=info["dim"],
            corner_radius=RADIUS["md"],
            width=30,
            height=30,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            icon_row,
            text=info["title"],
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=1, sticky="w", padx=(8, 0))

        ctk.CTkLabel(
            icon_row,
            text=f" {info['risk']} ",
            font=self._font(9, "bold"),
            fg_color=risk_c["bg"],
            text_color=risk_c["fg"],
            corner_radius=RADIUS["sm"],
        ).grid(row=0, column=2, sticky="e")

        # ── Row 1: FPS Gain (18px bold, accent — dominant) ──
        ctk.CTkLabel(
            card,
            text=info["fps"],
            font=self._font(18, "bold"),
            text_color=COLORS["accent"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=px, pady=(0, gap))

        # ── Row 2: Short description (1-line) ──
        short_key = f"{preset_key}_short"
        short_desc = (
            self._ui(short_key)
            if self._ui(short_key) != short_key
            else info.get("desc", "")
        )
        ctk.CTkLabel(
            card,
            text=short_desc,
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=220,
            justify="left",
        ).grid(row=2, column=0, sticky="ew", padx=px, pady=(0, gap))

        # ── Row 3: Quick info line ──
        restart_val = info.get("restart", "No")
        quick_info = (
            f"{len(tweaks)} {self._ui('stat_tweaks')}"
            f"  \u2022  {self._ui('stat_restart')}: {restart_val}"
        )
        ctk.CTkLabel(
            card,
            text=quick_info,
            font=self._font(10),
            text_color=COLORS["text_tertiary"],
            anchor="w",
        ).grid(row=3, column=0, sticky="w", padx=px, pady=(0, gap))

        # ── Row 4: Buttons ──
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=px, pady=(0, py))
        btn_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            btn_frame,
            text=self._ui("apply"),
            font=self._font(11, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS.get("text_on_accent", "#000000"),
            hover_color=COLORS.get("accent_hover", COLORS["accent"]),
            border_width=0,
            corner_radius=RADIUS["md"],
            height=28,
            command=lambda k=preset_key: self._apply_preset(k),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))

        # See Details — accent-colored ghost button
        ctk.CTkButton(
            btn_frame,
            text=self._ui("see_details"),
            font=self._font(10),
            fg_color="transparent",
            text_color=COLORS["accent"],
            hover_color=COLORS["bg_hover"],
            border_width=0,
            corner_radius=RADIUS["sm"],
            height=22,
            command=lambda k=preset_key: self._show_preset_tweaks(k),
        ).grid(row=1, column=0, sticky="ew")

        return card

    def _toggle_compare_panel(self):
        """Toggle the compare panel visibility."""
        if self._compare_visible and self._compare_panel:
            self._compare_panel.grid_forget()
            self._compare_panel.destroy()
            self._compare_panel = None
            self._compare_visible = False
        else:
            self._build_compare_panel()
            self._compare_visible = True

    def _build_compare_panel(self):
        """Build and show the compare panel below the card grid.

        Spec (phase3 Section A – compare-panel):
        - Panel: bg_card, border 1px, r-lg, padding 16px 18px, margin-top 16px
        - Header: 13px bold, mb 12px, flex gap 8px
        - Grid: 140px | 1fr | 1fr | 1fr, gap 0, font 11px
        - All cells: padding 8px 12px, border-bottom 1px border
        - Header cells: weight 600, bg_secondary, text_tertiary (colored overrides)
        - Label cells: weight 500, text_tertiary
        - Value cells: weight 600, text_primary
        """
        preset_info = self._get_preset_info()

        panel = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        panel.grid(row=3, column=0, sticky="ew", pady=(16, 0))

        # Inner wrapper for 16px 18px padding
        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=16)

        # ── Header: icon + title, mb 12px ──
        hdr_frame = ctk.CTkFrame(inner, fg_color="transparent")
        hdr_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            hdr_frame,
            text=ICON("compare_arrows"),
            font=ctk.CTkFont(family="Tabler Icons", size=16),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            hdr_frame,
            text=self._ui("compare_title"),
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # ── Grid container ──
        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        # 140px label column + 3 equal value columns
        grid.grid_columnconfigure(0, minsize=140, weight=0)
        for c in range(1, 4):
            grid.grid_columnconfigure(c, weight=1)

        bg_sec = COLORS.get("bg_secondary", COLORS["bg_primary"])
        cell_padx = 12
        cell_pady = 8

        # ── Column headers: (empty) | Safe | Competitive | Extreme ──
        headers = ["", "Safe", "Competitive", "Extreme"]
        header_colors = [
            COLORS["text_tertiary"],
            COLORS.get("success", "#22C55E"),
            COLORS.get("warning", "#F59E0B"),
            COLORS.get("danger", "#EF4444"),
        ]
        for c, (h, hc) in enumerate(zip(headers, header_colors)):
            cell = ctk.CTkFrame(grid, fg_color=bg_sec, corner_radius=0)
            cell.grid(row=0, column=c, sticky="nsew")
            ctk.CTkLabel(
                cell,
                text=h,
                font=self._font(11, "bold"),
                text_color=hc,
                anchor="w" if c == 0 else "center",
            ).pack(fill="x", padx=cell_padx, pady=cell_pady)
        # Header bottom border
        hdr_sep = ctk.CTkFrame(grid, fg_color=COLORS["border"], height=1)
        hdr_sep.grid(row=1, column=0, columnspan=4, sticky="ew")

        # ── Data rows ──
        rows_data = [
            (self._ui("cmp_total_tweaks"), "tweaks"),
            (self._ui("cmp_fps_gain"), "fps"),
            (self._ui("cmp_services"), "services_disabled"),
            (self._ui("cmp_registry"), "registry_changes"),
            (self._ui("cmp_bcdedit"), "bcdedit_changes"),
            (self._ui("cmp_restart"), "restart"),
        ]

        presets = list(preset_info.values())
        preset_keys = list(preset_info.keys())
        for r_idx, (label, key) in enumerate(rows_data):
            # Each data row occupies 2 grid rows: content + separator
            grid_row = 2 + r_idx * 2
            is_last = r_idx == len(rows_data) - 1

            # Label cell (col 0) — weight 500 = normal font
            ctk.CTkLabel(
                grid,
                text=label,
                font=self._font(11),
                text_color=COLORS["text_tertiary"],
                anchor="w",
            ).grid(
                row=grid_row,
                column=0,
                sticky="ew",
                padx=(cell_padx, cell_padx),
                pady=cell_pady,
            )

            # Value cells (cols 1-3) — weight 600 = bold
            for c_idx, p_info in enumerate(presets):
                if key == "tweaks":
                    tweaks = self.registry.get_tweaks_for_preset(preset_keys[c_idx])
                    val = str(len(tweaks))
                elif key == "fps":
                    val = p_info["fps"]
                else:
                    val = str(p_info.get(key, ""))

                ctk.CTkLabel(
                    grid,
                    text=val,
                    font=self._font(11, "bold"),
                    text_color=COLORS["text_primary"],
                    anchor="center",
                ).grid(
                    row=grid_row,
                    column=c_idx + 1,
                    sticky="ew",
                    padx=cell_padx,
                    pady=cell_pady,
                )

            # Row separator (except after last row)
            if not is_last:
                sep = ctk.CTkFrame(grid, fg_color=COLORS["border"], height=1)
                sep.grid(
                    row=grid_row + 1,
                    column=0,
                    columnspan=4,
                    sticky="ew",
                )

        self._compare_panel = panel

    def _get_spec_suggestion(self) -> Optional[Dict]:
        """Get preset suggestion based on system specs"""
        try:
            from core.system_info import SystemDetector

            detector = SystemDetector()
            profile = detector.detect_all()
            return self.registry.suggest_preset(profile)
        except Exception:
            return {
                "preset": "safe",
                "reason": "Default recommendation (system detection unavailable)",
            }

    def _create_preset_card(
        self,
        parent,
        info: dict,
        tweaks: List[Tweak],
        preset_key: str,
        is_recommended: bool,
        reason: str,
    ):
        """Create a profile card matching the Phase 3 spec:
        icon-in-colored-circle, stats grid, risk bar, colored Apply + Preview buttons.

        Spec ref: phase3-profiles-settings-welcome.html Section A
        - Card padding: 20px top/bottom, 18px sides
        - Flex column gap: 8px between sections
        - Safe = btn-primary (filled accent), Comp = btn-warning, Extreme = btn-danger
        - Recommended card: 2px green border
        """
        risk_colors = self._get_risk_colors()

        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=2 if is_recommended else 1,
            border_color=COLORS["success"] if is_recommended else COLORS["border"],
        )
        card.grid_columnconfigure(0, weight=1)
        # Spec: padding: 20px 18px  →  px=18, py=20
        px = 18
        py_top = 20
        py_bot = 20
        gap = 8  # spec: gap: 8px between flex children

        # ── Row 0: Icon circle + Name + RECOMMENDED tag ──
        # Spec: profile-icon-row: gap 10px, margin-bottom 4px
        icon_row = ctk.CTkFrame(card, fg_color="transparent")
        icon_row.grid(row=0, column=0, sticky="ew", padx=px, pady=(py_top, 4))
        icon_row.grid_columnconfigure(1, weight=1)

        # Icon circle (40x40, rounded r-md)
        circle = ctk.CTkFrame(
            icon_row,
            width=40,
            height=40,
            corner_radius=RADIUS["md"],
            fg_color=info["dim"],
        )
        circle.grid(row=0, column=0, sticky="w")
        circle.grid_propagate(False)
        ctk.CTkLabel(
            circle,
            text=info["icon"],
            font=ctk.CTkFont(family="Tabler Icons", size=22),
            text_color=info["color"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Name (16px bold)
        ctk.CTkLabel(
            icon_row,
            text=info["title"],
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        # RECOMMENDED tag (auto-pushed to right via margin-left: auto)
        if is_recommended:
            ctk.CTkLabel(
                icon_row,
                text=f"  {self._ui('recommended').upper()}  ",
                font=self._font(10, "bold"),
                fg_color=COLORS["success_dim"],
                text_color=COLORS["success"],
                corner_radius=RADIUS["sm"],
            ).grid(row=0, column=2, sticky="e")

        # ── Row 1: Description ──
        # Spec: profile-desc: 12px, text-secondary, line-height 1.5
        ctk.CTkLabel(
            card,
            text=info["desc"],
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            wraplength=250,
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=px, pady=(0, 0))

        # ── Row 2: Stats grid (2x2) ──
        # Spec: profile-stats: grid 1fr 1fr, gap 6px, margin 4px 0
        # Each stat: label (left, tertiary 11px) — value (right, primary bold 11px)
        # Gain & Risk values use badge styling; Tweaks & Restart use plain text
        risk_c = risk_colors.get(info["risk"], risk_colors["LOW"])
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=px, pady=(4, 0))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        stats = [
            (self._ui("stat_tweaks"), str(len(tweaks)), None, None),
            (
                self._ui("stat_gain"),
                info["fps"],
                COLORS.get("accent_dim", COLORS["bg_hover"]),
                COLORS.get("accent", "#57c8ff"),
            ),
            (self._ui("stat_risk"), info["risk"], risk_c["bg"], risk_c["fg"]),
            (self._ui("stat_restart"), info.get("restart", "No"), None, None),
        ]

        for idx, (label, value, badge_bg, badge_fg) in enumerate(stats):
            r, c = divmod(idx, 2)
            # Spec: profile-stat: flex, justify-between, 11px, padding 4px 0
            stat_cell = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_cell.grid(
                row=r,
                column=c,
                sticky="ew",
                pady=3,
                padx=(0, 10) if c == 0 else (10, 0),
            )
            stat_cell.grid_columnconfigure(0, weight=0)
            stat_cell.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                stat_cell,
                text=label,
                font=self._font(11),
                text_color=COLORS["text_tertiary"],
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            if badge_bg and badge_fg:
                ctk.CTkLabel(
                    stat_cell,
                    text=f" {value} ",
                    font=self._font(10, "bold"),
                    fg_color=badge_bg,
                    text_color=badge_fg,
                    corner_radius=RADIUS["sm"],
                    anchor="e",
                ).grid(row=0, column=1, sticky="e")
            else:
                ctk.CTkLabel(
                    stat_cell,
                    text=value,
                    font=self._font(11, "bold"),
                    text_color=COLORS["text_primary"],
                    anchor="e",
                ).grid(row=0, column=1, sticky="e")

        # ── Row 3: Risk bar (3px) ──
        # Spec: profile-risk-bar: height 3px, r-2, margin 4px 0
        bar_bg = ctk.CTkFrame(
            card,
            fg_color=COLORS["bg_hover"],
            height=3,
            corner_radius=2,
        )
        bar_bg.grid(row=3, column=0, sticky="ew", padx=px, pady=(4, 0))
        bar_bg.grid_propagate(False)

        pct = info.get("risk_bar_pct", 0.15)
        bar_fill = ctk.CTkFrame(
            bar_bg,
            fg_color=info["color"],
            height=3,
            corner_radius=2,
        )
        bar_fill.place(relx=0, rely=0, relwidth=pct, relheight=1.0)

        # ── Row 4: Action buttons ──
        # Spec: profile-actions: flex, gap 8px, margin-top auto, padding-top 4px
        # Safe = btn-primary (filled accent bg, dark text)
        # Competitive = btn-warning (outline yellow)
        # Extreme = btn-danger (outline red)
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=px, pady=(gap, py_bot))

        if preset_key == "safe":
            # btn-primary: filled accent background, dark text
            ctk.CTkButton(
                btn_frame,
                text=self._ui("apply"),
                font=self._font(12, "bold"),
                fg_color=COLORS["accent"],
                text_color=COLORS.get("text_on_accent", "#000000"),
                hover_color=COLORS.get("accent_hover", COLORS["accent"]),
                border_width=0,
                corner_radius=RADIUS["md"],
                height=32,
                width=90,
                command=lambda k=preset_key: self._apply_preset(k),
            ).pack(side="left", padx=(0, gap))
        else:
            # btn-warning / btn-danger: outline style, colored text + dim border
            ctk.CTkButton(
                btn_frame,
                text=self._ui("apply"),
                font=self._font(12, "bold"),
                fg_color="transparent",
                text_color=info["color"],
                hover_color=info["dim"],
                border_width=1,
                border_color=info["dim"],
                corner_radius=RADIUS["md"],
                height=32,
                width=90,
                command=lambda k=preset_key: self._apply_preset(k),
            ).pack(side="left", padx=(0, gap))

        # Preview ghost button
        ctk.CTkButton(
            btn_frame,
            text=self._ui("preview"),
            font=self._font(12),
            fg_color="transparent",
            text_color=COLORS["text_tertiary"],
            hover_color=COLORS["bg_hover"],
            border_width=0,
            corner_radius=RADIUS["sm"],
            height=32,
            width=80,
            command=lambda k=preset_key: self._show_preset_tweaks(k),
        ).pack(side="left")

        return card

    def _show_preset_tweaks(self, preset_key: str):
        """Switch to custom tab with preset's tweaks pre-selected"""
        tweaks = self.registry.get_tweaks_for_preset(preset_key)
        self.selected_tweaks = {t.id for t in tweaks}
        self._switch_tab("custom")

    def _apply_preset(self, preset_key: str):
        """Apply a preset profile"""
        try:
            profile = self.app.profile_manager.get_profile(preset_key.upper())
            if profile:
                dialog = ExecutionDialog(self, profile)

                def run():
                    # Before snapshot
                    try:
                        from core.system_snapshot import SystemSnapshotManager

                        snap_mgr = SystemSnapshotManager()
                        dialog.add_output("[snap] Taking before-snapshot...")
                        before_snap = snap_mgr.take_snapshot()
                    except Exception:
                        snap_mgr = None
                        before_snap = None

                    result = self.app.profile_manager.apply_profile(
                        profile,
                        on_output=dialog.add_output,
                        on_progress=dialog.set_progress,
                    )

                    # After snapshot + diff
                    if snap_mgr and before_snap:
                        try:
                            dialog.add_output("[snap] Taking after-snapshot...")
                            after_snap = snap_mgr.take_snapshot()
                            diff = snap_mgr.compare(before_snap, after_snap)
                            dialog.show_diff(diff)
                        except Exception:
                            pass

                    dialog.show_result(result)

                import threading

                threading.Thread(target=run, daemon=True).start()
        except Exception as e:
            print(f"Apply error: {e}")

    # ================================================================
    # TAB 2: CUSTOM BUILDER
    # ================================================================
    def _show_custom_tab(self):
        self._clear_content()

        # Hide the shared scrollable content frame — the custom tab uses its
        # own plain CTkFrame so the inner scrollable list can fill the full
        # remaining height (a CTkScrollableFrame inside another
        # CTkScrollableFrame cannot expand vertically because the outer
        # canvas sizes to content, not to available space).
        self.content._parent_frame.grid_remove()

        # Dedicated non-scrollable container placed directly on the view
        self._custom_container = ctk.CTkFrame(self, fg_color="transparent")
        self._custom_container.grid(row=2, column=0, sticky="nsew")
        self._custom_container.grid_columnconfigure(0, weight=1)
        # row 0 = selection bar (fixed), row 1 = search/filter (fixed),
        # row 2 = split pane (expands)
        self._custom_container.grid_rowconfigure(2, weight=1)

        # Track which tweak detail is shown (preserve across refreshes)
        if not hasattr(self, "_detail_visible"):
            self._detail_visible = False
        if not hasattr(self, "_detail_tweak_obj"):
            self._detail_tweak_obj = None

        # Search/filter state
        if not hasattr(self, "_search_var"):
            self._search_var = ctk.StringVar(value="")
        if not hasattr(self, "_filter_risk"):
            self._filter_risk = "ALL"  # ALL, LOW, MEDIUM, HIGH
        if not hasattr(self, "_filter_category"):
            self._filter_category = "ALL"  # ALL or category key

        # Selection summary bar (full width, above split pane)
        self._create_selection_bar()

        # Search & filter bar
        self._create_search_filter_bar()

        # Split-pane container: left tweak list + right detail panel
        self._custom_split = ctk.CTkFrame(
            self._custom_container, fg_color="transparent"
        )
        self._custom_split.grid(row=2, column=0, sticky="nsew")
        self._custom_split.grid_columnconfigure(0, weight=1)
        self._custom_split.grid_rowconfigure(0, weight=1)

        # Left column — scrollable tweak list (takes full width by default)
        self.custom_left = ctk.CTkScrollableFrame(
            self._custom_split,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self.custom_left.grid(row=0, column=0, sticky="nsew")
        self.custom_left.grid_columnconfigure(0, weight=1)

        # Right column — detail panel (hidden by default, shown on tweak click)
        self.detail_panel = ctk.CTkFrame(
            self._custom_split,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
            width=380,
        )
        self.detail_panel.grid_propagate(False)
        self.detail_panel.grid_columnconfigure(0, weight=1)

        # Restore detail panel if it was visible
        if self._detail_visible and self._detail_tweak_obj:
            self._open_detail_panel(self._detail_tweak_obj)

        # Tweaks grouped by category (into left column)
        self._populate_tweak_list()

    def _create_selection_bar(self):
        """Summary bar showing selected tweak count and apply button"""
        parent = getattr(self, "_custom_container", None) or self.content
        bar = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=COLORS["border"],
        )
        bar.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))
        bar.grid_columnconfigure(1, weight=1)

        count = len(self.selected_tweaks)
        label_text = (
            f"  {count} tweaks selected"
            if count > 0
            else "  Select tweaks to apply optimizations"
        )
        self.selection_label = ctk.CTkLabel(
            bar,
            text=label_text,
            font=font("body_bold"),
            text_color=COLORS["accent"] if count > 0 else COLORS["text_tertiary"],
        )
        self.selection_label.grid(
            row=0, column=0, sticky="w", padx=SPACING["md"], pady=SPACING["sm"]
        )

        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.grid(
            row=0, column=1, sticky="e", padx=SPACING["md"], pady=SPACING["sm"]
        )

        # Import button
        ctk.CTkButton(
            btn_frame,
            text="Import",
            font=font("caption"),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"],
            height=32,
            width=80,
            command=self._import_preset,
        ).pack(side="left", padx=(0, SPACING["xs"]))

        # Export button
        ctk.CTkButton(
            btn_frame,
            text="Export",
            font=font("caption"),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"],
            height=32,
            width=80,
            command=self._export_preset,
        ).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkButton(
            btn_frame,
            text="Clear All",
            font=font("caption"),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"],
            height=32,
            width=80,
            command=self._clear_selection,
        ).pack(side="left", padx=(0, SPACING["sm"]))

        self.apply_btn = ctk.CTkButton(
            btn_frame,
            text=f"Apply {count} Tweaks",
            font=font("button"),
            fg_color=COLORS["accent"] if count > 0 else COLORS["bg_card"],
            text_color="#000000" if count > 0 else COLORS["text_tertiary"],
            hover_color=COLORS["accent_hover"],
            corner_radius=RADIUS["md"],
            height=32,
            width=140,
            state="normal" if count > 0 else "disabled",
            command=self._apply_selected_tweaks,
        )
        self.apply_btn.pack(side="left")

    def _clear_selection(self):
        self.selected_tweaks.clear()
        self._show_custom_tab()

    # ----------------------------------------------------------------
    # Search / Filter bar
    # ----------------------------------------------------------------
    def _create_search_filter_bar(self):
        """Search bar + wrapping category filter chips above the tweak list"""
        parent = getattr(self, "_custom_container", None) or self.content
        bar = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        bar.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        bar.grid_columnconfigure(0, weight=1)

        # Search entry row
        search_frame = ctk.CTkFrame(bar, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text=ICON("search"),
            font=ctk.CTkFont(family="Tabler Icons", size=14),
            text_color=COLORS["text_tertiary"],
        ).grid(row=0, column=0, padx=(SPACING["sm"], SPACING["xs"]))

        self._search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self._search_var,
            placeholder_text="Search tweaks...",
            placeholder_text_color=COLORS["text_muted"],
            font=font("body"),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=RADIUS["md"],
            height=32,
        )
        self._search_entry.grid(row=0, column=1, sticky="ew", padx=(0, SPACING["sm"]))
        self._search_var.trace_add("write", lambda *_: self._on_filter_changed())

        # Risk filter chips (right of search)
        risk_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        risk_frame.grid(row=0, column=2, sticky="e")

        risk_options = [
            ("ALL", "All", COLORS["text_secondary"]),
            ("LOW", "Low", COLORS.get("risk_low", "#34D399")),
            ("MEDIUM", "Med", COLORS.get("risk_medium", "#FBBF24")),
            ("HIGH", "High", COLORS.get("risk_high", "#F87171")),
        ]
        self._filter_chips = {}
        for key, label, color in risk_options:
            is_active = self._filter_risk == key
            chip = ctk.CTkButton(
                risk_frame,
                text=label,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["bg_card"] if is_active else "transparent",
                text_color=color if is_active else COLORS["text_muted"],
                hover_color=COLORS["bg_card_hover"],
                border_width=1 if is_active else 0,
                border_color=color if is_active else COLORS["border"],
                corner_radius=RADIUS["sm"],
                height=28,
                width=44,
                command=lambda k=key: self._set_risk_filter(k),
            )
            chip.pack(side="left", padx=2)
            self._filter_chips[key] = chip

        # Category filter chips — horizontally scrollable row (chips never compress)
        chip_scroll_container = ctk.CTkFrame(bar, fg_color="transparent", height=38)
        chip_scroll_container.grid(
            row=1, column=0, sticky="ew", pady=(SPACING["sm"], 0)
        )
        chip_scroll_container.grid_propagate(False)
        chip_scroll_container.grid_columnconfigure(0, weight=1)
        chip_scroll_container.grid_rowconfigure(0, weight=1)

        chip_canvas = tk.Canvas(
            chip_scroll_container,
            bg=COLORS["bg_primary"],
            height=38,
            highlightthickness=0,
            bd=0,
            xscrollincrement=1,
        )
        chip_canvas.grid(row=0, column=0, sticky="nsew")

        # Inner frame — expands to fit all chips without compression
        cat_wrap = ctk.CTkFrame(chip_canvas, fg_color="transparent")
        cat_wrap_window = chip_canvas.create_window(
            (0, 0), window=cat_wrap, anchor="nw"
        )

        def _update_chip_scroll_region(event=None):
            chip_canvas.configure(scrollregion=chip_canvas.bbox("all"))

        cat_wrap.bind("<Configure>", _update_chip_scroll_region)

        # Horizontal mouse-wheel scroll (Shift+wheel or plain wheel on this row)
        def _on_chip_wheel(event):
            direction = -1 if event.delta > 0 else 1
            chip_canvas.xview_scroll(direction * 3, "units")

        chip_canvas.bind("<MouseWheel>", _on_chip_wheel)
        cat_wrap.bind("<MouseWheel>", _on_chip_wheel)

        # Build category counts from registry
        cat_counts: dict[str, int] = {}
        total_count = 0
        for cat_key in TWEAK_CATEGORIES:
            n = len(self.registry.get_tweaks_by_category(cat_key))
            if n > 0:
                cat_counts[cat_key] = n
                total_count += n

        # "All" chip — primary / dominant style
        if not hasattr(self, "_filter_category"):
            self._filter_category = "ALL"

        self._cat_chips: dict[str, ctk.CTkButton] = {}
        is_all = self._filter_category == "ALL"
        all_chip = ctk.CTkButton(
            cat_wrap,
            text=f"All ({total_count})",
            font=ctk.CTkFont(size=12, weight="bold")
            if is_all
            else ctk.CTkFont(size=11),
            fg_color=COLORS["accent"] if is_all else "transparent",
            text_color="#000000" if is_all else COLORS["text_secondary"],
            hover_color=COLORS["accent_hover"] if is_all else COLORS["bg_card_hover"],
            border_width=0 if is_all else 1,
            border_color=COLORS["border"],
            corner_radius=RADIUS["full"],
            height=30 if is_all else 28,
            command=lambda: self._set_category_filter("ALL"),
        )
        all_chip.pack(side="left", padx=(0, SPACING["xs"]), pady=4)
        self._cat_chips["ALL"] = all_chip

        # Per-category chips — text-only with colored dot prefix (no icon font mixing)
        for cat_key, count in cat_counts.items():
            cat_info = TWEAK_CATEGORIES[cat_key]
            cat_color = cat_info.get("color", COLORS["text_secondary"])
            is_active = self._filter_category == cat_key

            chip_text = f"\u25cf {cat_info['label']} ({count})"
            chip = ctk.CTkButton(
                cat_wrap,
                text=chip_text,
                font=ctk.CTkFont(size=11),
                fg_color=cat_color if is_active else "transparent",
                text_color="#000000" if is_active else COLORS["text_tertiary"],
                hover_color=COLORS["bg_card_hover"],
                border_width=1,
                border_color=cat_color if is_active else COLORS["border"],
                corner_radius=RADIUS["full"],
                height=28,
                command=lambda k=cat_key: self._set_category_filter(k),
            )
            chip.pack(side="left", padx=(0, SPACING["xs"]), pady=4)
            self._cat_chips[cat_key] = chip

        # Propagate mouse-wheel from each chip button to the canvas
        def _bind_chip_wheel(widget):
            widget.bind("<MouseWheel>", _on_chip_wheel)

        for chip_widget in self._cat_chips.values():
            _bind_chip_wheel(chip_widget)

    def _set_risk_filter(self, risk_level: str):
        """Set risk filter and refresh list"""
        self._filter_risk = risk_level
        self._on_filter_changed()

    def _set_category_filter(self, category: str):
        """Set category filter and refresh list"""
        self._filter_category = category
        self._on_filter_changed()

    def _on_filter_changed(self):
        """Re-populate tweak list based on search/filter"""
        self._populate_tweak_list()
        # Also update chip styles
        if hasattr(self, "_filter_chips"):
            risk_colors_map = {
                "ALL": COLORS["text_secondary"],
                "LOW": COLORS.get("risk_low", "#34D399"),
                "MEDIUM": COLORS.get("risk_medium", "#FBBF24"),
                "HIGH": COLORS.get("risk_high", "#F87171"),
            }
            for key, chip in self._filter_chips.items():
                is_active = self._filter_risk == key
                color = risk_colors_map.get(key, COLORS["text_secondary"])
                chip.configure(
                    fg_color=COLORS["bg_card"] if is_active else "transparent",
                    text_color=color if is_active else COLORS["text_muted"],
                    border_width=1 if is_active else 0,
                    border_color=color if is_active else COLORS["border"],
                )

        # Update category chip styles
        if hasattr(self, "_cat_chips"):
            cat_filter = (
                self._filter_category if hasattr(self, "_filter_category") else "ALL"
            )
            for key, chip in self._cat_chips.items():
                is_active = cat_filter == key
                if key == "ALL":
                    # "All" chip — dominant accent style when active
                    chip.configure(
                        fg_color=COLORS["accent"] if is_active else "transparent",
                        text_color="#000000" if is_active else COLORS["text_secondary"],
                        border_width=0 if is_active else 1,
                        border_color=COLORS["border"],
                        font=ctk.CTkFont(size=12, weight="bold")
                        if is_active
                        else ctk.CTkFont(size=11),
                    )
                else:
                    cat_info = TWEAK_CATEGORIES.get(key, {})
                    cat_color = cat_info.get("color", COLORS["text_secondary"])
                    chip.configure(
                        fg_color=cat_color if is_active else "transparent",
                        text_color="#000000" if is_active else COLORS["text_tertiary"],
                        border_color=cat_color if is_active else COLORS["border"],
                    )

    def _populate_tweak_list(self):
        """Populate tweak list with current search/filter applied"""
        if not hasattr(self, "custom_left"):
            return
        for w in self.custom_left.winfo_children():
            w.destroy()

        search_q = (
            self._search_var.get().strip().lower()
            if hasattr(self, "_search_var")
            else ""
        )
        risk_filter = self._filter_risk if hasattr(self, "_filter_risk") else "ALL"
        cat_filter = (
            self._filter_category if hasattr(self, "_filter_category") else "ALL"
        )

        total_visible = 0
        for cat_key, cat_info in TWEAK_CATEGORIES.items():
            # Category filter — skip entire category if not matching
            if cat_filter != "ALL" and cat_key != cat_filter:
                continue

            tweaks = self.registry.get_tweaks_by_category(cat_key)
            if not tweaks:
                continue

            # Apply filters
            filtered = []
            for t in tweaks:
                if risk_filter != "ALL" and t.risk_level.upper() != risk_filter:
                    continue
                if (
                    search_q
                    and search_q not in t.name.lower()
                    and search_q not in t.description.lower()
                ):
                    continue
                filtered.append(t)

            if not filtered:
                continue

            total_visible += len(filtered)
            self._create_category_section(
                cat_key, cat_info, filtered, parent=self.custom_left
            )

        # Show "no results" if empty
        if total_visible == 0:
            wrapper = ctk.CTkFrame(self.custom_left, fg_color="transparent")
            wrapper.grid(sticky="ew", pady=SPACING["xl"])
            ctk.CTkLabel(
                wrapper,
                text=ICON("search"),
                font=ctk.CTkFont(family="Tabler Icons", size=28),
                text_color=COLORS["text_muted"],
            ).pack()
            ctk.CTkLabel(
                wrapper,
                text="No tweaks match your search",
                font=font("body"),
                text_color=COLORS["text_tertiary"],
            ).pack(pady=(SPACING["xs"], 0))

    # ----------------------------------------------------------------
    # Detail panel show/hide
    # ----------------------------------------------------------------
    def _open_detail_panel(self, tweak: Tweak):
        """Show the detail panel (slides in from right)"""
        self._detail_visible = True
        self._detail_tweak_obj = tweak
        self.detail_tweak_id = tweak.id

        # Configure split to show detail column
        self._custom_split.grid_columnconfigure(1, weight=0)
        self.detail_panel.grid(row=0, column=1, sticky="nsew", padx=(SPACING["sm"], 0))

        # Populate detail content
        self._show_inline_detail(tweak)

    def _close_detail_panel(self):
        """Hide the detail panel"""
        self._detail_visible = False
        self._detail_tweak_obj = None
        self.detail_tweak_id = None
        if hasattr(self, "detail_panel"):
            self.detail_panel.grid_forget()
        # Refresh list to remove active row highlight
        self._populate_tweak_list()

    def _export_preset(self):
        """Export selected tweaks as JSON file"""
        if not self.selected_tweaks:
            if hasattr(self.app, "toast"):
                self.app.toast.warning("No tweaks selected to export")
            return

        from tkinter import filedialog

        filepath = filedialog.asksaveasfilename(
            parent=self,
            title="Export Preset",
            defaultextension=".json",
            filetypes=[("ClutchG Preset", "*.json"), ("All Files", "*.*")],
            initialfile="clutchg_preset.json",
        )
        if not filepath:
            return

        ids = list(self.selected_tweaks)
        ok = self.app.profile_manager.export_preset_to_file(
            name="Custom Preset", tweak_ids=ids, filepath=filepath
        )
        if hasattr(self.app, "toast"):
            if ok:
                self.app.toast.success(f"Exported {len(ids)} tweaks")
            else:
                self.app.toast.error("Export failed")

    def _import_preset(self):
        """Import tweaks from a JSON file"""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            parent=self,
            title="Import Preset",
            filetypes=[("ClutchG Preset", "*.json"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        result = self.app.profile_manager.import_preset_from_file(filepath)
        if result is None:
            if hasattr(self.app, "toast"):
                self.app.toast.error("Invalid preset file")
            return

        # Select the valid tweaks
        self.selected_tweaks = set(result["valid_ids"])

        # Notify user
        if hasattr(self.app, "toast"):
            msg = f"Imported {len(result['valid_ids'])} tweaks"
            if result["unknown_ids"]:
                msg += f" ({len(result['unknown_ids'])} unknown skipped)"
            self.app.toast.success(msg)

        # Refresh Custom tab to show selection
        self._show_custom_tab()

    def _create_category_section(
        self, cat_key: str, cat_info: dict, tweaks: List[Tweak], parent=None
    ):
        """Collapsible category section with compact tweak rows"""
        container = parent if parent is not None else self.content

        # Track collapsed state per category
        if not hasattr(self, "_collapsed_cats"):
            self._collapsed_cats: Set[str] = set()

        is_collapsed = cat_key in self._collapsed_cats
        section = ctk.CTkFrame(container, fg_color="transparent")
        section.grid(sticky="ew", pady=(0, SPACING["xs"]))
        section.grid_columnconfigure(0, weight=1)

        # Category header (clickable to collapse/expand)
        header = ctk.CTkFrame(section, fg_color="transparent", cursor="hand2")
        header.grid(row=0, column=0, sticky="ew", pady=(SPACING["xs"], 2))

        color = cat_info.get("color", COLORS["text_secondary"])
        icon_char = cat_info.get("icon", "")

        # Chevron indicator
        chevron = (
            "\uea62" if not is_collapsed else "\uea5f"
        )  # chevron-down / chevron-right
        chevron_lbl = ctk.CTkLabel(
            header,
            text=chevron,
            font=ctk.CTkFont(family="Tabler Icons", size=12),
            text_color=COLORS["text_tertiary"],
        )
        chevron_lbl.pack(side="left", padx=(0, 4))

        if icon_char:
            ctk.CTkLabel(
                header,
                text=icon_char,
                font=ctk.CTkFont(family="Tabler Icons", size=13),
                text_color=color,
            ).pack(side="left", padx=(0, 4))

        ctk.CTkLabel(
            header,
            text=f"{cat_info['label']}  ({len(tweaks)})",
            font=font("body_bold"),
            text_color=color,
        ).pack(side="left")

        # Click handler on header
        def toggle_collapse(e=None):
            if cat_key in self._collapsed_cats:
                self._collapsed_cats.discard(cat_key)
            else:
                self._collapsed_cats.add(cat_key)
            self._populate_tweak_list()

        header.bind("<Button-1>", toggle_collapse)
        for child in header.winfo_children():
            child.bind("<Button-1>", toggle_collapse)

        # Tweak rows (hidden if collapsed)
        if not is_collapsed:
            for i, tweak in enumerate(tweaks):
                row = self._create_tweak_row(section, tweak, i + 1)
                row.grid(row=i + 1, column=0, sticky="ew", pady=(0, 2))

    def _create_tweak_row(self, parent, tweak: Tweak, row_idx: int):
        """Compact single-row tweak item:
        [Toggle] Name                     Gain  -  Risk  -  Restart  Learn More >
        Click row → opens detail panel on the right.
        """
        is_selected = tweak.id in self.selected_tweaks
        is_detail_active = (
            hasattr(self, "detail_tweak_id") and self.detail_tweak_id == tweak.id
        )
        risk_c = self._get_risk_colors().get(
            tweak.risk_level, self._get_risk_colors()["LOW"]
        )

        # Determine row background
        if is_detail_active:
            bg = COLORS.get("bg_hover", COLORS["bg_card_hover"])
            border_w = 1
            border_c = COLORS["accent"]
        elif is_selected:
            bg = COLORS["bg_card_hover"]
            border_w = 0
            border_c = COLORS["border"]
        else:
            bg = COLORS["bg_card"]
            border_w = 0
            border_c = COLORS["border"]

        row = ctk.CTkFrame(
            parent,
            fg_color=bg,
            corner_radius=RADIUS["sm"],
            border_width=border_w,
            border_color=border_c,
            height=38,
            cursor="hand2",
        )
        row.grid_columnconfigure(1, weight=1)  # name expands
        row.grid_propagate(True)

        # Toggle switch
        var = ctk.BooleanVar(value=is_selected)
        toggle = ctk.CTkSwitch(
            row,
            text="",
            variable=var,
            width=36,
            height=18,
            switch_width=32,
            switch_height=16,
            fg_color=COLORS["border"],  # track off
            progress_color=COLORS["accent"],  # track on
            button_color=COLORS["text_secondary"],  # knob off
            button_hover_color=COLORS["text_primary"],  # knob hover
            command=lambda tid=tweak.id, v=var: self._toggle_tweak(tid, v),
        )
        toggle.grid(row=0, column=0, padx=(8, 4), pady=4)

        # Name — slightly heavier for visual balance on the left
        name_lbl = ctk.CTkLabel(
            row,
            text=tweak.name,
            font=ctk.CTkFont(size=13, weight="bold")
            if is_selected
            else ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"],
            anchor="w",
        )
        name_lbl.grid(row=0, column=1, sticky="w", padx=(0, 4))

        # Inline meta: gain + risk badge + restart icon + learn more (packed right)
        meta_frame = ctk.CTkFrame(row, fg_color="transparent")
        meta_frame.grid(row=0, column=2, sticky="e", padx=(4, 8), pady=4)

        # Expected gain (short text like "1-3% FPS")
        if tweak.expected_gain:
            ctk.CTkLabel(
                meta_frame,
                text="\uea38",  # bolt icon
                font=ctk.CTkFont(family="Tabler Icons", size=11),
                text_color=COLORS["accent"],
            ).pack(side="left", padx=(0, 1))
            ctk.CTkLabel(
                meta_frame,
                text=tweak.expected_gain,
                font=ctk.CTkFont(size=10),
                text_color=COLORS["accent"],
            ).pack(side="left", padx=(0, 4))

        # Risk badge (compact)
        ctk.CTkLabel(
            meta_frame,
            text=f" {risk_c['label']} ",
            font=ctk.CTkFont(size=10),
            fg_color=risk_c["bg"],
            text_color=risk_c["fg"],
            corner_radius=4,
        ).pack(side="left", padx=(0, 3))

        # Restart indicator
        if tweak.requires_restart:
            ctk.CTkLabel(
                meta_frame,
                text=ICON("refresh"),
                font=ctk.CTkFont(family="Tabler Icons", size=11),
                text_color=COLORS["text_tertiary"],
            ).pack(side="left", padx=(0, 3))

        # "Details ›" text link with hover effect
        learn_lbl = ctk.CTkLabel(
            meta_frame,
            text="Details \u203a",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"],
            cursor="hand2",
        )
        learn_lbl.pack(side="left", padx=(2, 0))
        learn_lbl.bind(
            "<Enter>",
            lambda e, lbl=learn_lbl: lbl.configure(
                text_color=COLORS["accent"],
            ),
        )
        learn_lbl.bind(
            "<Leave>",
            lambda e, lbl=learn_lbl: lbl.configure(
                text_color=COLORS["text_muted"],
            ),
        )

        # Hover effects on row
        def on_enter(e=None, r=row, b=bg):
            if not is_detail_active:
                r.configure(fg_color=COLORS["bg_card_hover"])

        def on_leave(e=None, r=row, b=bg):
            if not is_detail_active:
                r.configure(fg_color=b)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)

        # Click entire row → open detail panel
        def on_click(e=None, t=tweak):
            self._on_tweak_row_click(t)

        row.bind("<Button-1>", on_click)
        name_lbl.bind("<Button-1>", on_click)
        learn_lbl.bind("<Button-1>", on_click)
        for child in meta_frame.winfo_children():
            child.bind("<Button-1>", on_click)

        return row

    def _toggle_tweak(self, tweak_id: str, var: ctk.BooleanVar):
        """Toggle a tweak selection"""
        if var.get():
            self.selected_tweaks.add(tweak_id)
        else:
            self.selected_tweaks.discard(tweak_id)
        # Update selection bar
        self._update_selection_count()

    def _update_selection_count(self):
        """Update the selection count label and apply button"""
        count = len(self.selected_tweaks)
        if hasattr(self, "selection_label"):
            label_text = (
                f"  {count} tweaks selected"
                if count > 0
                else "  Select tweaks to apply optimizations"
            )
            self.selection_label.configure(
                text=label_text,
                text_color=COLORS["accent"] if count > 0 else COLORS["text_tertiary"],
            )
        if hasattr(self, "apply_btn"):
            self.apply_btn.configure(
                text=f"Apply {count} Tweaks",
                fg_color=COLORS["accent"] if count > 0 else COLORS["bg_card"],
                text_color="#FFFFFF" if count > 0 else COLORS["text_tertiary"],
                state="normal" if count > 0 else "disabled",
            )

    # ----------------------------------------------------------------
    # Split-pane detail panel (Custom tab)
    # ----------------------------------------------------------------
    def _on_tweak_row_click(self, tweak: Tweak):
        """Handle click on a tweak row — open detail panel"""
        self._open_detail_panel(tweak)
        # Refresh list to update row highlights
        self._populate_tweak_list()

    _DETAIL_SCROLLBAR_WIDTH = 14
    _DETAIL_PAD_X = 12
    _DETAIL_WRAP = 320

    def _show_inline_detail(self, tweak: Tweak):
        if not hasattr(self, "detail_panel"):
            return
        for w in self.detail_panel.winfo_children():
            w.destroy()

        close_bar = ctk.CTkFrame(self.detail_panel, fg_color="transparent", height=26)
        close_bar.pack(fill="x", padx=(SPACING["sm"], 4), pady=(3, 0))
        close_bar.pack_propagate(False)
        ctk.CTkButton(
            close_bar,
            text=ICON("close"),
            width=22,
            height=22,
            font=ctk.CTkFont(family="Tabler Icons", size=13),
            fg_color="transparent",
            text_color=COLORS["text_tertiary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["sm"],
            command=self._close_detail_panel,
        ).pack(side="right")

        scroll = ctk.CTkScrollableFrame(
            self.detail_panel,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_tertiary"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        scroll.pack(
            fill="both",
            expand=True,
            padx=(self._DETAIL_PAD_X, 0),
            pady=(0, SPACING["sm"]),
        )
        scroll.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(scroll, fg_color="transparent")
        inner.grid(row=0, column=0, sticky="nsew", padx=(0, self._DETAIL_PAD_X))
        inner.grid_columnconfigure(0, weight=1)

        # Labels whose wraplength must track the inner frame width
        _wrap_labels: list[ctk.CTkLabel] = []

        def _make_wrapping_label(parent, **kwargs) -> ctk.CTkLabel:
            lbl = ctk.CTkLabel(parent, **kwargs)
            _wrap_labels.append(lbl)
            return lbl

        def _update_wraplengths(event=None):
            w = inner.winfo_width()
            if w > 10:
                for lbl in _wrap_labels:
                    try:
                        lbl.configure(wraplength=w)
                    except Exception:
                        pass

        inner.bind("<Configure>", _update_wraplengths)

        risk_colors = self._get_risk_colors()
        risk_c = risk_colors.get(tweak.risk_level.upper(), risk_colors["LOW"])
        r = 0

        _make_wrapping_label(
            inner,
            text=tweak.name,
            font=font("h4"),
            text_color=COLORS["text_primary"],
            wraplength=self._DETAIL_WRAP,
            anchor="w",
            justify="left",
        ).grid(row=r, column=0, sticky="ew")
        r += 1

        badge_f = ctk.CTkFrame(inner, fg_color="transparent")
        badge_f.grid(row=r, column=0, sticky="w", pady=(SPACING["xs"], SPACING["xs"]))
        r += 1

        cat_info = TWEAK_CATEGORIES.get(tweak.category, {})
        cat_label = cat_info.get("label", tweak.category)
        ctk.CTkLabel(
            badge_f,
            text=f"  {cat_label}  ",
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["bg_tertiary"],
            text_color=cat_info.get("color", COLORS["text_secondary"]),
            corner_radius=RADIUS["sm"],
        ).pack(side="left", padx=(0, SPACING["xs"]))

        ctk.CTkLabel(
            badge_f,
            text=f"  {risk_c['label']}  ",
            font=ctk.CTkFont(size=9),
            fg_color=risk_c["bg"],
            text_color=risk_c["fg"],
            corner_radius=RADIUS["sm"],
        ).pack(side="left", padx=(0, SPACING["xs"]))

        if tweak.requires_restart:
            ctk.CTkLabel(
                badge_f,
                text="  Restart  ",
                font=ctk.CTkFont(size=9),
                fg_color=COLORS["bg_tertiary"],
                text_color=COLORS["text_tertiary"],
                corner_radius=RADIUS["sm"],
            ).pack(side="left")

        ctk.CTkFrame(inner, fg_color=COLORS["border"], height=1).grid(
            row=r, column=0, sticky="ew", pady=(SPACING["xs"], SPACING["xs"])
        )
        r += 1

        sections = [
            ("What it does", tweak.what_it_does),
            ("Why it helps", tweak.why_it_helps),
            ("Expected gain", tweak.expected_gain),
            ("Limitations", tweak.limitations),
        ]

        for title, content in sections:
            if not content:
                continue
            ctk.CTkLabel(
                inner,
                text=title,
                font=font("micro"),
                text_color=COLORS["text_tertiary"],
            ).grid(row=r, column=0, sticky="w", pady=(SPACING["sm"], 1))
            r += 1
            _make_wrapping_label(
                inner,
                text=content,
                font=font("body_small"),
                text_color=COLORS["text_secondary"],
                wraplength=self._DETAIL_WRAP,
                anchor="w",
                justify="left",
            ).grid(row=r, column=0, sticky="ew")
            r += 1

        if tweak.warnings:
            ctk.CTkLabel(
                inner,
                text="Warnings",
                font=font("micro"),
                text_color=COLORS.get("warning", "#F59E0B"),
            ).grid(row=r, column=0, sticky="w", pady=(SPACING["sm"], 1))
            r += 1
            for warn in tweak.warnings:
                _make_wrapping_label(
                    inner,
                    text=f"  - {warn}",
                    font=font("micro"),
                    text_color=COLORS.get("warning", "#FBBF24"),
                    wraplength=self._DETAIL_WRAP,
                    anchor="w",
                    justify="left",
                ).grid(row=r, column=0, sticky="ew")
                r += 1

        ctk.CTkFrame(inner, fg_color=COLORS["border"], height=1).grid(
            row=r, column=0, sticky="ew", pady=SPACING["sm"]
        )
        r += 1

        if tweak.registry_keys:
            ctk.CTkLabel(
                inner,
                text="Registry keys",
                font=font("micro"),
                text_color=COLORS["text_muted"],
            ).grid(row=r, column=0, sticky="w", pady=(0, 1))
            r += 1
            for key in tweak.registry_keys:
                _make_wrapping_label(
                    inner,
                    text=key,
                    font=ctk.CTkFont(size=9, family="Consolas"),
                    text_color=COLORS["text_muted"],
                    wraplength=self._DETAIL_WRAP,
                    anchor="w",
                    justify="left",
                ).grid(row=r, column=0, sticky="ew")
                r += 1

        meta_parts = []
        meta_parts.append("Reversible" if tweak.reversible else "Not reversible")
        meta_parts.append(f"OS: Win {', '.join(tweak.compatible_os)}")
        if tweak.requires_admin:
            meta_parts.append("Admin required")
        ctk.CTkLabel(
            inner,
            text="  |  ".join(meta_parts),
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_muted"],
        ).grid(row=r, column=0, sticky="w", pady=(SPACING["sm"], 0))

    def _apply_selected_tweaks(self):
        """Apply selected custom tweaks"""
        if not self.selected_tweaks:
            return
        try:
            ids = list(self.selected_tweaks)
            dialog = ExecutionDialog(self, f"Custom ({len(ids)} tweaks)")

            def run():
                # Before snapshot
                try:
                    from core.system_snapshot import SystemSnapshotManager

                    snap_mgr = SystemSnapshotManager()
                    dialog.add_output("[snap] Taking before-snapshot...")
                    before_snap = snap_mgr.take_snapshot()
                except Exception:
                    snap_mgr = None
                    before_snap = None

                result = self.app.profile_manager.apply_tweaks(
                    ids,
                    on_output=dialog.add_output,
                    on_progress=dialog.set_progress,
                    on_tweak_status=dialog.add_tweak_status,
                )

                # After snapshot + diff
                if snap_mgr and before_snap:
                    try:
                        dialog.add_output("[snap] Taking after-snapshot...")
                        after_snap = snap_mgr.take_snapshot()
                        diff = snap_mgr.compare(before_snap, after_snap)
                        dialog.show_diff(diff)
                    except Exception:
                        pass

                dialog.show_result(result)

            import threading

            threading.Thread(target=run, daemon=True).start()
        except Exception as e:
            print(f"Apply error: {e}")

    def _show_tweak_detail(self, tweak: Tweak):
        """Show detailed modal for a tweak"""
        detail = ctk.CTkToplevel(self)
        detail.title(tweak.name)
        detail.geometry("600x520")
        detail.configure(fg_color=COLORS["bg_primary"])
        detail.transient(self.winfo_toplevel())
        detail.grab_set()

        # Center dialog on main window (HIGH-06)
        detail.update_idletasks()
        root = self.winfo_toplevel()
        x = root.winfo_rootx() + (root.winfo_width() - 600) // 2
        y = root.winfo_rooty() + (root.winfo_height() - 520) // 2
        detail.geometry(f"600x520+{x}+{y}")

        scroll = ctk.CTkScrollableFrame(detail, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])
        scroll.grid_columnconfigure(0, weight=1)

        # Use _get_risk_colors() so it matches preset tab (not global RISK_COLORS)
        risk_colors = self._get_risk_colors()
        risk_c = risk_colors.get(tweak.risk_level.upper(), risk_colors["LOW"])
        r = 0

        # Title
        ctk.CTkLabel(
            scroll, text=tweak.name, font=font("h2"), text_color=COLORS["text_primary"]
        ).grid(row=r, column=0, sticky="w")
        r += 1

        # Risk + Category badges
        badge_f = ctk.CTkFrame(scroll, fg_color="transparent")
        badge_f.grid(row=r, column=0, sticky="w", pady=(SPACING["xs"], SPACING["sm"]))
        r += 1

        ctk.CTkLabel(
            badge_f,
            text=f"  {risk_c['label']}  ",
            font=font("caption"),
            fg_color=risk_c["bg"],
            text_color=risk_c["fg"],
            corner_radius=RADIUS["sm"],
        ).pack(side="left", padx=(0, SPACING["xs"]))

        cat_info = TWEAK_CATEGORIES.get(tweak.category, {})
        ctk.CTkLabel(
            badge_f,
            text=f"  {cat_info.get('label', tweak.category)}  ",
            font=font("caption"),
            fg_color=COLORS["bg_card"],
            text_color=cat_info.get("color", COLORS["text_secondary"]),
            corner_radius=RADIUS["sm"],
        ).pack(side="left", padx=(0, SPACING["xs"]))

        if tweak.requires_restart:
            ctk.CTkLabel(
                badge_f,
                text="  Restart Required  ",
                font=font("caption"),
                fg_color=COLORS.get("bg_elevated", COLORS["bg_card"]),
                text_color=COLORS.get("text_tertiary", COLORS["text_secondary"]),
                corner_radius=RADIUS["sm"],
            ).pack(side="left")

        # Sections — headers use text_primary + bold weight (HIGH-07: was accent teal, failed WCAG AA)
        sections = [
            ("Description", tweak.description),
            ("What It Does", tweak.what_it_does),
            ("Why It Helps", tweak.why_it_helps),
            ("Limitations", tweak.limitations),
            ("Expected Gain", tweak.expected_gain),
        ]

        for title, content in sections:
            ctk.CTkLabel(
                scroll,
                text=title,
                font=font("body_bold"),
                text_color=COLORS["text_primary"],
            ).grid(row=r, column=0, sticky="w", pady=(SPACING["sm"], 2))
            r += 1
            ctk.CTkLabel(
                scroll,
                text=content,
                font=font("body"),
                text_color=COLORS["text_secondary"],
                wraplength=520,
                anchor="w",
                justify="left",
            ).grid(row=r, column=0, sticky="ew")
            r += 1

        # Warnings — use theme tokens instead of hard-coded hex
        if tweak.warnings:
            ctk.CTkLabel(
                scroll,
                text="Warnings",
                font=font("body_bold"),
                text_color=COLORS.get("risk_high", COLORS.get("danger", "#F87171")),
            ).grid(row=r, column=0, sticky="w", pady=(SPACING["sm"], 2))
            r += 1
            for w in tweak.warnings:
                ctk.CTkLabel(
                    scroll,
                    text=f"  • {w}",
                    font=font("body"),
                    text_color=COLORS.get(
                        "risk_medium", COLORS.get("warning", "#FBBF24")
                    ),
                    wraplength=520,
                    anchor="w",
                ).grid(row=r, column=0, sticky="ew")
                r += 1

        # Registry keys
        if tweak.registry_keys:
            ctk.CTkLabel(
                scroll,
                text="Registry Keys Modified",
                font=font("body_bold"),
                text_color=COLORS["text_tertiary"],
            ).grid(row=r, column=0, sticky="w", pady=(SPACING["sm"], 2))
            r += 1
            for key in tweak.registry_keys:
                ctk.CTkLabel(
                    scroll,
                    text=f"  {key}",
                    font=ctk.CTkFont(size=11, family="Consolas"),
                    text_color=COLORS["text_tertiary"],
                    anchor="w",
                ).grid(row=r, column=0, sticky="ew")
                r += 1

        # Meta info
        meta = f"Reversible: {'Yes' if tweak.reversible else 'No'}  |  OS: Windows {', '.join(tweak.compatible_os)}  |  Admin: {'Required' if tweak.requires_admin else 'No'}"
        ctk.CTkLabel(
            scroll, text=meta, font=font("caption"), text_color=COLORS["text_tertiary"]
        ).grid(row=r, column=0, sticky="w", pady=(SPACING["md"], 0))

        # Close button
        ctk.CTkButton(
            detail,
            text="Close",
            font=font("button"),
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"],
            height=36,
            command=detail.destroy,
        ).pack(pady=SPACING["md"])

    # ================================================================
    # TAB 3: EDUCATION ENCYCLOPEDIA
    # ================================================================
    def _show_education_tab(self):
        self._clear_content()

        # Search bar
        search_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))

        search_container = ctk.CTkFrame(
            search_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["full"],
            border_width=1,
            border_color=COLORS["border"],
        )
        search_container.pack(fill="x", ipady=2)

        ctk.CTkLabel(
            search_container,
            text="\ueb1c",
            font=ctk.CTkFont(family="Tabler Icons", size=16),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(SPACING["md"], SPACING["xs"]))

        self.edu_search = ctk.CTkEntry(
            search_container,
            placeholder_text="Search tweaks...",
            font=font("body"),
            fg_color="transparent",
            border_width=0,
            text_color=COLORS["text_primary"],
        )
        self.edu_search.pack(side="left", fill="x", expand=True, padx=SPACING["xs"])
        self.edu_search.bind("<KeyRelease>", lambda e: self._filter_education())

        # Category filter pills with scroll indicator
        pill_container = ctk.CTkFrame(self.content, fg_color="transparent")
        pill_container.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        pill_container.grid_columnconfigure(0, weight=1)

        pill_frame = ctk.CTkFrame(pill_container, fg_color="transparent")
        pill_frame.grid(row=0, column=0, sticky="ew")

        # Right-side scroll indicator (arrow icon)
        scroll_indicator = ctk.CTkFrame(
            pill_container, fg_color="transparent", width=24
        )
        scroll_indicator.grid(row=0, column=1, sticky="ns")
        ctk.CTkLabel(
            scroll_indicator,
            text="\uea1f",  # arrow-right (Tabler)
            font=ctk.CTkFont(family="Tabler Icons", size=12),
            text_color=COLORS["text_muted"],
        ).pack(expand=True)

        self.edu_cat_buttons = {}

        # All button
        all_btn = ctk.CTkButton(
            pill_frame,
            text=f"All ({len(self.registry.get_all_tweaks())})",
            font=font("caption"),
            fg_color=COLORS["accent"],
            text_color="#FFFFFF",
            corner_radius=RADIUS["full"],
            height=28,
            width=0,
            command=lambda: self._set_edu_category(None),
        )
        all_btn.pack(side="left", padx=(0, SPACING["xs"]))
        self.edu_cat_buttons[None] = all_btn

        for cat_key, cat_info in TWEAK_CATEGORIES.items():
            count = len(self.registry.get_tweaks_by_category(cat_key))
            if count == 0:
                continue
            btn = ctk.CTkButton(
                pill_frame,
                text=f"{cat_info['label']} ({count})",
                font=font("caption"),
                fg_color=COLORS["bg_card"],
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card_hover"],
                corner_radius=RADIUS["full"],
                height=28,
                width=0,
                border_width=1,
                border_color=COLORS["border"],
                command=lambda k=cat_key: self._set_edu_category(k),
            )
            btn.pack(side="left", padx=(0, SPACING["xs"]))
            self.edu_cat_buttons[cat_key] = btn

        # Education entries container
        self.edu_list = ctk.CTkFrame(self.content, fg_color="transparent")
        self.edu_list.grid(row=2, column=0, sticky="ew")
        self.edu_list.grid_columnconfigure(0, weight=1)

        self._render_education_entries()

    def _set_edu_category(self, category: Optional[str]):
        self.active_edu_category = category
        for key, btn in self.edu_cat_buttons.items():
            is_active = key == category
            btn.configure(
                fg_color=COLORS["accent"] if is_active else COLORS["bg_card"],
                text_color="#FFFFFF" if is_active else COLORS["text_secondary"],
            )
        self._render_education_entries()

    def _filter_education(self):
        self._render_education_entries()

    def _render_education_entries(self):
        """Render education entries based on filters"""
        for w in self.edu_list.winfo_children():
            w.destroy()

        query = ""
        if hasattr(self, "edu_search"):
            query = self.edu_search.get().lower().strip()

        tweaks = self.registry.get_all_tweaks()

        # Filter by category
        if self.active_edu_category:
            tweaks = [t for t in tweaks if t.category == self.active_edu_category]

        # Filter by search
        if query:
            tweaks = [
                t
                for t in tweaks
                if query in t.name.lower()
                or query in t.description.lower()
                or query in t.what_it_does.lower()
                or query in t.category.lower()
            ]

        if not tweaks:
            ctk.CTkLabel(
                self.edu_list,
                text="No tweaks found",
                font=font("body"),
                text_color=COLORS["text_tertiary"],
            ).grid(row=0, column=0, pady=SPACING["xl"])
            return

        for i, tweak in enumerate(tweaks):
            card = self._create_edu_card(self.edu_list, tweak)
            card.grid(row=i, column=0, sticky="ew", pady=(0, SPACING["xs"]))

    def _create_edu_card(self, parent, tweak: Tweak):
        """Education card — read-only tweak info with expandable details"""
        risk_c = self._get_risk_colors().get(
            tweak.risk_level, self._get_risk_colors()["LOW"]
        )
        cat_info = TWEAK_CATEGORIES.get(tweak.category, {})

        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid_columnconfigure(0, weight=1)

        # Name + description
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(
            row=0, column=0, sticky="ew", pady=SPACING["xs"], padx=SPACING["sm"]
        )

        ctk.CTkLabel(
            info_frame,
            text=tweak.name,
            font=font("body_bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=tweak.description,
            font=font("caption"),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        # Risk badge
        ctk.CTkLabel(
            card,
            text=f"  {risk_c['label']}  ",
            font=ctk.CTkFont(size=10),
            fg_color=risk_c["bg"],
            text_color=risk_c["fg"],
            corner_radius=RADIUS["sm"],
        ).grid(row=0, column=1, padx=SPACING["xs"])

        # Gain
        ctk.CTkLabel(
            card,
            text=tweak.expected_gain,
            font=font("caption"),
            text_color=COLORS["accent"],
        ).grid(row=0, column=2, padx=SPACING["xs"])

        # Detail button
        ctk.CTkButton(
            card,
            text="Learn More",
            font=font("caption"),
            fg_color="transparent",
            text_color=COLORS["accent"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["sm"],
            height=26,
            width=90,
            command=lambda t=tweak: self._show_tweak_detail(t),
        ).grid(row=0, column=3, padx=(0, SPACING["sm"]))

        return card
