"""
Scripts View — Presets, Custom Builder, and Education Encyclopedia
3-tab layout with spec-based recommendations and full tweak documentation
Updated: 2026-02-11
"""

import customtkinter as ctk
from typing import TYPE_CHECKING, List, Optional, Dict, Set
import threading
from gui.theme import COLORS, SIZES, SPACING, RADIUS, get_risk_colors, NAV_ICONS, ICON, theme_manager
from gui.style import font
from gui.components.glass_card import GlassCard
from gui.components.enhanced_button import EnhancedButton
from gui.components.execution_dialog import ExecutionDialog
from gui.components.refined_dialog import show_confirmation
from core.tweak_registry import get_tweak_registry, Tweak, TWEAK_CATEGORIES
from core.action_catalog import ActionCatalog, ActionDefinition

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


# Risk badge colors
RISK_COLORS = {
    "LOW": {"bg": "#064E3B", "fg": "#34D399", "label": "LOW RISK"},
    "MEDIUM": {"bg": "#78350F", "fg": "#FBBF24", "label": "MEDIUM"},
    "HIGH": {"bg": "#7F1D1D", "fg": "#F87171", "label": "HIGH RISK"},
}

# Preset definitions
PRESET_INFO = {
    "safe": {
        "icon": ICON("safe"), "title": "Safe Mode", # Native Icon
        "subtitle": "Evidence-based, fully reversible",
        "fps": "2-5%", "risk": "LOW",
        "color": "#10B981", "dim": "#064E3B",
        "desc": "Minimal optimizations with maximum safety. Perfect for daily drivers. All changes are easily reversible.",
    },
    "competitive": {
        "icon": ICON("competitive"), "title": "Competitive Mode", # Native Icon
        "subtitle": "Balanced gaming performance",
        "fps": "5-10%", "risk": "MEDIUM",
        "color": "#F59E0B", "dim": "#78350F",
        "desc": "Optimized for competitive gaming. Disables some services and applies aggressive network/input tweaks.",
    },
    "extreme": {
        "icon": ICON("extreme"), "title": "Extreme Mode", # Native Icon
        "subtitle": "Maximum performance, advanced users only",
        "fps": "10-15%", "risk": "HIGH",
        "color": "#EF4444", "dim": "#7F1D1D",
        "desc": "Most aggressive reversible tuning set. Includes advanced boot, service, and latency tweaks for experienced users.",
    },
}


class ScriptsView(ctk.CTkFrame):
    """Scripts view with 3 tabs: Presets, Custom Builder, Education"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Optimization Center",
            "stats": "{tweaks} tweaks  ·  {categories} categories",
            # Tab names
            "tab_presets": "Presets",
            "tab_custom": "Custom Builder",
            "tab_education": "Encyclopedia",
            # Preset info
            "safe_title": "Safe Mode",
            "safe_subtitle": "Evidence-based, fully reversible",
            "safe_desc": "Minimal optimizations with maximum safety. Perfect for daily drivers. All changes are easily reversible.",
            "comp_title": "Competitive Mode",
            "comp_subtitle": "Balanced gaming performance",
            "comp_desc": "Optimized for competitive gaming. Disables some services and applies aggressive network/input tweaks.",
            "ext_title": "Extreme Mode",
            "ext_subtitle": "Maximum performance, advanced users only",
            "ext_desc": "Most aggressive reversible tuning set. Includes advanced boot, service, and latency tweaks for experienced users.",
            # Risk labels
            "low_risk": "LOW RISK",
            "medium_risk": "MEDIUM",
            "high_risk": "HIGH RISK",
            # Common
            "apply": "APPLY",
            "view_tweaks": "View Tweaks",
            "recommended": "★ RECOMMENDED FOR YOU ★",
            "rec_reason": "Recommendation based on your system: {reason}",
            "tweaks_count": "{count} tweaks",
        },
        "th": {
            "title": "Optimization Center",
            "stats": "{tweaks} tweaks  ·  {categories} หมวดหมู่",
            # Tab names
            "tab_presets": "โหมด Preset",
            "tab_custom": "สร้าง Custom",
            "tab_education": "สารบัญ Tweaks",
            # Preset info
            "safe_title": "Safe Mode",
            "safe_subtitle": "ยืนยันได้จากหลักฐาน สามารถย้อนกลับได้",
            "safe_desc": "Optimize ขั้นต่ำแต่ปลอดภัยสูงสุด เหมาะสำหรับใช้งานทั่วไป สามารถยกเลิกการเปลี่ยนแปลงได้ทั้งหมด",
            "comp_title": "Competitive Mode",
            "comp_subtitle": "สมดุลสำหรับเกมเมอร์",
            "comp_desc": "ปรับแต่งสำหรับเกมเมอร์อย่างสมดุล ปิด Services บางตัวและปรับ Network/Input ขั้นสูง",
            "ext_title": "Extreme Mode",
            "ext_subtitle": "ประสิทธิภาพสูงสุด สำหรับผู้ใช้ขั้นสูง",
            "ext_desc": "ชุดการจูนแบบย้อนกลับได้ที่เข้มที่สุด เพิ่ม boot, service และ latency tweaks สำหรับผู้ใช้ขั้นสูง",
            # Risk labels
            "low_risk": "LOW RISK",
            "medium_risk": "MEDIUM",
            "high_risk": "HIGH RISK",
            # Common
            "apply": "ใช้งาน",
            "view_tweaks": "ดู Tweaks",
            "recommended": "★ แนะนำสำหรับคุณ ★",
            "rec_reason": "แนะนำจากสเปคของคุณ: {reason}",
            "tweaks_count": "{count} tweaks",
        }
    }

    UI_STRINGS["en"].update({
        "tab_quick_actions": "Quick Actions",
        "quick_actions_subtitle": "One-click action packs for practical and safe V1 workflows.",
        "quick_group_general": "General",
        "quick_group_advanced": "Advanced",
        "quick_group_cleanup": "Cleanup",
        "quick_group_windows": "Windows",
        "quick_group_utilities": "Utilities",
        "quick_run": "Run Action",
        "quick_open": "Open Link",
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
    })

    UI_STRINGS["th"].update({
        "tab_quick_actions": "Quick Actions",
        "quick_actions_subtitle": "Quick action packs with practical V1-safe defaults.",
        "quick_group_general": "General",
        "quick_group_advanced": "Advanced",
        "quick_group_cleanup": "Cleanup",
        "quick_group_windows": "Windows",
        "quick_group_utilities": "Utilities",
        "quick_run": "Run Action",
        "quick_open": "Open Link",
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
    })

    def __init__(self, parent, app: 'ClutchGApp'):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.registry = get_tweak_registry()
        self.action_catalog = getattr(self.app, "action_catalog", None) or ActionCatalog(self.registry)
        self.quick_actions_errors: List[str] = list(getattr(self.app, "action_catalog_errors", []))
        if not self.quick_actions_errors:
            self.quick_actions_errors = self.action_catalog.validate()
        self.selected_tweaks: Set[str] = set()
        self.active_tab = "quick_actions"
        self.active_quick_group = "general"
        self.active_edu_category: Optional[str] = None

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
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key).format(**kwargs)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Tahoma", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def _get_preset_info(self) -> dict:
        """Get localized preset information"""
        return {
            "safe": {
                "icon": ICON("safe"),
                "title": self._ui("safe_title"),
                "subtitle": self._ui("safe_subtitle"),
                "fps": "2-5%",
                "risk": self._ui("low_risk"),
                "color": "#10B981",
                "dim": "#064E3B",
                "desc": self._ui("safe_desc"),
            },
            "competitive": {
                "icon": ICON("competitive"),
                "title": self._ui("comp_title"),
                "subtitle": self._ui("comp_subtitle"),
                "fps": "5-10%",
                "risk": self._ui("medium_risk"),
                "color": "#F59E0B",
                "dim": "#78350F",
                "desc": self._ui("comp_desc"),
            },
            "extreme": {
                "icon": ICON("extreme"),
                "title": self._ui("ext_title"),
                "subtitle": self._ui("ext_subtitle"),
                "fps": "10-15%",
                "risk": self._ui("high_risk"),
                "color": "#EF4444",
                "dim": "#7F1D1D",
                "desc": self._ui("ext_desc"),
            },
        }

    def _get_risk_colors(self) -> dict:
        """Get localized risk colors"""
        return {
            "LOW": {"bg": "#064E3B", "fg": "#34D399", "label": self._ui("low_risk")},
            "MEDIUM": {"bg": "#78350F", "fg": "#FBBF24", "label": self._ui("medium_risk")},
            "HIGH": {"bg": "#7F1D1D", "fg": "#F87171", "label": self._ui("high_risk")},
        }

    # ================================================================
    # HEADER
    # ================================================================
    def _create_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hdr, text=self._ui("title"),
            font=self._font(24, "bold"), text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        all_tweaks = self.registry.get_all_tweaks()
        stats_text = self._ui("stats", tweaks=len(all_tweaks), categories=len(TWEAK_CATEGORIES))
        ctk.CTkLabel(
            hdr, text=stats_text,
            font=self._font(12), text_color=COLORS["text_tertiary"]
        ).grid(row=0, column=1, sticky="w", padx=(SPACING["md"], 0))

    # ================================================================
    # TAB BAR
    # ================================================================
    def _create_tab_bar(self):
        bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=RADIUS["lg"],
                           border_width=1, border_color=COLORS["border"])
        bar.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["md"]))

        # Native Icons directly used here
        tabs = [
            ("quick_actions", "\uE768", self._ui("tab_quick_actions")),
            ("presets", "\uE762", self._ui("tab_presets")),
            ("custom", "\uE70F", self._ui("tab_custom")),
            ("education", "\uE82D", self._ui("tab_education")),
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
        text_color = colors.get("text_on_accent", "#FFFFFF") if is_active else colors["text_secondary"]
        hover_color = colors["accent_hover"] if is_active else colors["bg_card_hover"]

        # Container Frame
        btn_frame = ctk.CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=RADIUS["md"],
            height=38,
            cursor="hand2"
        )
        # Bind click to frame
        btn_frame.bind("<Button-1>", lambda e, k=key: self._switch_tab(k))

        # Layout container
        content_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Icon Label (Segoe font)
        icon_lbl = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=16),
            text_color=text_color
        )
        icon_lbl.pack(side="left", padx=(10, 5))

        # Text Label (Inter/Tahoma font based on language)
        text_lbl = ctk.CTkLabel(
            content_frame,
            text=label,
            font=self._font(13, "bold") if is_active else self._font(13),
            text_color=text_color
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
            text_color = colors.get("text_on_accent", "#FFFFFF") if is_active else colors["text_secondary"]

            btn.configure(fg_color=fg_color)

            # Update Labels
            if hasattr(btn, "_icon_widget"):
                btn._icon_widget.configure(text_color=text_color)
            if hasattr(btn, "_text_widget"):
                btn._text_widget.configure(
                    text_color=text_color,
                    font=self._font(13, "bold") if is_active else self._font(13)
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
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

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
        
        current_label = self.quick_group_label_map.get(self.active_quick_group, values[0])
        
        for i, val in enumerate(values):
            is_selected = val == current_label
            
            btn = ctk.CTkButton(
                btn_container,
                text=val,
                font=self._font(12, "bold" if is_selected else "normal"),
                fg_color=COLORS["accent"] if is_selected else COLORS["bg_card"],
                text_color=COLORS.get("text_on_accent", "#FFFFFF") if is_selected else COLORS["text_secondary"],
                hover_color=COLORS["accent_hover"] if is_selected else COLORS["bg_card_hover"],
                corner_radius=RADIUS["md"],
                height=32,
                command=lambda v=val: self._on_quick_group_change(v)
            )
            # Add small gap between buttons
            btn.pack(side="left", expand=True, fill="x", padx=(0, SPACING["xs"]) if i < len(values)-1 else 0)
            self.quick_group_buttons[val] = btn

        # self.quick_groups = ... (Removed)
        # self.quick_groups.pack(...) (Removed)
        # self.quick_groups.set(...) (Removed)

        self.quick_actions_container = ctk.CTkFrame(self.content, fg_color="transparent")
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
                    text_color=COLORS.get("text_on_accent", "#FFFFFF") if is_selected else COLORS["text_secondary"],
                    hover_color=COLORS["accent_hover"] if is_selected else COLORS["bg_card_hover"],
                    font=self._font(12, "bold" if is_selected else "normal")
                )

        self.active_quick_group = self.quick_group_key_map.get(selected_value, "general")
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

        for idx, action in enumerate(actions):
            row = idx // 2
            col = idx % 2
            card = self._create_quick_action_card(self.quick_actions_container, action)
            card.grid(row=row, column=col, sticky="nsew", padx=(0, SPACING["md"]) if col == 0 else 0, pady=(0, SPACING["md"]))

    def _create_quick_action_card(self, parent, action: ActionDefinition):
        summary = self.action_catalog.summarize(action)
        display_risk = summary.max_risk if action.kind == "tweak_pack" else "N/A"
        risk_color = RISK_COLORS.get(display_risk, {"bg": COLORS["bg_card"], "fg": COLORS["text_secondary"], "label": "N/A"})
        badge_label = risk_color["label"] if action.kind == "tweak_pack" else "LINK"

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

        button_text = self._ui("quick_run") if action.kind == "tweak_pack" else self._ui("quick_open")
        ctk.CTkButton(
            card,
            text=button_text,
            font=self._font(12, "bold"),
            fg_color=COLORS["accent"],
            text_color=COLORS.get("text_on_accent", "#FFFFFF"),
            hover_color=COLORS["accent_hover"],
            corner_radius=RADIUS["md"],
            height=32,
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
            restart=self._ui("quick_restart_yes") if summary.requires_restart else self._ui("quick_restart_no"),
            backup=self._ui("quick_backup_enabled") if auto_backup else self._ui("quick_backup_disabled"),
        )
        risk = summary.max_risk if summary.max_risk in ("LOW", "MEDIUM", "HIGH") else "LOW"
        if not show_confirmation(
            self.app.window,
            self._ui("quick_confirm_title"),
            confirm_body,
            confirm_text="Run",
            risk_level=risk
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
                dialog.add_output("📸 Taking before-snapshot...")
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
                    dialog.add_output("📸 Taking after-snapshot...")
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
                risk_level="LOW"
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

        # Spec-based recommendation
        suggestion = self._get_spec_suggestion()

        row = 0
        preset_info = self._get_preset_info()
        for preset_key, info in preset_info.items():
            tweaks = self.registry.get_tweaks_for_preset(preset_key)
            is_recommended = suggestion and suggestion["preset"] == preset_key

            card = self._create_preset_card(
                self.content, info, tweaks, preset_key, is_recommended,
                suggestion.get("reason", "") if is_recommended else ""
            )
            card.grid(row=row, column=0, sticky="ew", pady=(0, SPACING["md"]))
            row += 1

        # Recommendation reason
        if suggestion:
            reason_lbl = ctk.CTkLabel(
                self.content,
                text=f"💡 {self._ui('rec_reason', reason=suggestion.get('reason', ''))}",
                font=self._font(12),
                text_color=COLORS["text_tertiary"],
                wraplength=700,
            )
            reason_lbl.grid(row=row, column=0, sticky="w", pady=(SPACING["sm"], 0))

    def _get_spec_suggestion(self) -> Optional[Dict]:
        """Get preset suggestion based on system specs"""
        try:
            from core.system_info import SystemDetector
            detector = SystemDetector()
            profile = detector.detect_all()
            return self.registry.suggest_preset(profile)
        except Exception:
            return {"preset": "safe", "reason": "Default recommendation (system detection unavailable)"}

    def _create_preset_card(self, parent, info: dict, tweaks: List[Tweak],
                            preset_key: str, is_recommended: bool, reason: str):
        """Create a preset card with tweak details"""
        risk_colors = self._get_risk_colors()

        card = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"],
            border_width=2 if is_recommended else 1,
            border_color=info["color"] if is_recommended else COLORS["border"],
        )
        card.grid_columnconfigure(1, weight=1)

        # Left accent stripe
        stripe = ctk.CTkFrame(card, fg_color=info["color"], width=4,
                              corner_radius=2)
        stripe.grid(row=0, column=0, rowspan=4, sticky="ns", padx=(0, SPACING["md"]),
                    pady=SPACING["sm"])

        # Row 0: Title + recommended badge
        title_frame = ctk.CTkFrame(card, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="ew", padx=SPACING["md"],
                         pady=(SPACING["md"], 0))
        title_frame.grid_columnconfigure(1, weight=1)

        # Header Row (Icon + Title)
        header_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="w")

        # Icon Label (Native Font)
        ctk.CTkLabel(
            header_row,
            text=info['icon'],
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=26),
            text_color=info["color"], # Icon matches preset color
        ).pack(side="left", padx=(0, SPACING["sm"]))

        # Title Label
        ctk.CTkLabel(
            header_row,
            text=info['title'],
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        if is_recommended:
            badge = ctk.CTkLabel(
                title_frame, text=self._ui("recommended"),
                font=self._font(12),
                fg_color=info["color"],
                text_color="#FFFFFF",
                corner_radius=RADIUS["full"],
            )
            badge.grid(row=0, column=1, sticky="w", padx=(SPACING["sm"], 0))

        # Risk + FPS badges
        risk_c = risk_colors.get(info["risk"], risk_colors["LOW"])
        badges_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        badges_frame.grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(
            badges_frame, text=f"  {risk_c['label']}  ",
            font=self._font(12), fg_color=risk_c["bg"],
            text_color=risk_c["fg"], corner_radius=RADIUS["sm"],
        ).pack(side="left", padx=(0, SPACING["xs"]))

        ctk.CTkLabel(
            badges_frame, text=f"  +{info['fps']} FPS  ",
            font=self._font(12), fg_color="#1E3A5F",
            text_color="#60A5FA", corner_radius=RADIUS["sm"],
        ).pack(side="left")

        # Row 1: Description
        ctk.CTkLabel(
            card, text=info["desc"],
            font=self._font(13), text_color=COLORS["text_secondary"],
            wraplength=650, anchor="w", justify="left",
        ).grid(row=1, column=1, sticky="ew", padx=SPACING["md"], pady=(SPACING["xs"], 0))

        # Row 2: Tweak count + categories
        cats = set(t.category for t in tweaks)
        cat_labels = [TWEAK_CATEGORIES.get(c, {}).get("label", c) for c in sorted(cats)]
        meta_text = f"{self._ui('tweaks_count', count=len(tweaks))}  ·  {', '.join(cat_labels)}"
        ctk.CTkLabel(
            card, text=meta_text,
            font=self._font(12), text_color=COLORS["text_tertiary"],
            wraplength=650, anchor="w",
        ).grid(row=2, column=1, sticky="ew", padx=SPACING["md"], pady=(SPACING["xs"], 0))

        # Row 3: Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=3, column=1, sticky="ew", padx=SPACING["md"],
                       pady=(SPACING["sm"], SPACING["md"]))

        ctk.CTkButton(
            btn_frame, text=self._ui("view_tweaks"),
            font=self._font(13), fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=RADIUS["md"], height=32, width=120,
            command=lambda k=preset_key: self._show_preset_tweaks(k),
        ).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkButton(
            btn_frame, text=f"Apply {info['title']}",
            font=font("button"), fg_color=info["color"],
            text_color="#FFFFFF", hover_color=info["dim"],
            corner_radius=RADIUS["md"], height=32, width=160,
            command=lambda k=preset_key: self._apply_preset(k),
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
                        dialog.add_output("📸 Taking before-snapshot...")
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
                            dialog.add_output("📸 Taking after-snapshot...")
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

        # Selection summary bar
        self._create_selection_bar()

        # Tweaks grouped by category
        for cat_key, cat_info in TWEAK_CATEGORIES.items():
            tweaks = self.registry.get_tweaks_by_category(cat_key)
            if not tweaks:
                continue
            self._create_category_section(cat_key, cat_info, tweaks)

    def _create_selection_bar(self):
        """Summary bar showing selected tweak count and apply button"""
        bar = ctk.CTkFrame(
            self.content, fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["lg"], border_width=1,
            border_color=COLORS["border"],
        )
        bar.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))
        bar.grid_columnconfigure(1, weight=1)

        count = len(self.selected_tweaks)
        self.selection_label = ctk.CTkLabel(
            bar, text=f"  {count} tweaks selected",
            font=font("body_bold"),
            text_color=COLORS["accent"] if count > 0 else COLORS["text_tertiary"],
        )
        self.selection_label.grid(row=0, column=0, sticky="w",
                                  padx=SPACING["md"], pady=SPACING["sm"])

        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=SPACING["md"],
                       pady=SPACING["sm"])

        # Import button
        ctk.CTkButton(
            btn_frame, text="📥 Import",
            font=font("caption"), fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"], height=28, width=80,
            command=self._import_preset,
        ).pack(side="left", padx=(0, SPACING["xs"]))

        # Export button
        ctk.CTkButton(
            btn_frame, text="📤 Export",
            font=font("caption"), fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"], height=28, width=80,
            command=self._export_preset,
        ).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkButton(
            btn_frame, text="Clear All",
            font=font("caption"), fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"], height=28, width=80,
            command=self._clear_selection,
        ).pack(side="left", padx=(0, SPACING["sm"]))

        self.apply_btn = ctk.CTkButton(
            btn_frame, text=f"Apply {count} Tweaks",
            font=font("button"),
            fg_color=COLORS["accent"] if count > 0 else COLORS["bg_card"],
            text_color="#FFFFFF" if count > 0 else COLORS["text_tertiary"],
            hover_color=COLORS["accent_hover"],
            corner_radius=RADIUS["md"], height=32, width=140,
            state="normal" if count > 0 else "disabled",
            command=self._apply_selected_tweaks,
        )
        self.apply_btn.pack(side="left")

    def _clear_selection(self):
        self.selected_tweaks.clear()
        self._show_custom_tab()

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

    def _create_category_section(self, cat_key: str, cat_info: dict, tweaks: List[Tweak]):
        """Section for a category with tweak toggles"""
        section = ctk.CTkFrame(self.content, fg_color="transparent")
        section.grid(sticky="ew", pady=(0, SPACING["sm"]))
        section.grid_columnconfigure(0, weight=1)

        # Category header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")

        color = cat_info.get("color", COLORS["text_secondary"])
        ctk.CTkLabel(
            header,
            text=f"  {cat_info.get('icon', '')}  {cat_info['label']}  ({len(tweaks)})",
            font=font("body_bold"),
            text_color=color,
        ).pack(side="left")

        # Tweak rows
        for i, tweak in enumerate(tweaks):
            row = self._create_tweak_row(section, tweak, i + 1)
            # Add gap between rows
            row.grid(row=i + 1, column=0, sticky="ew", pady=(0, 6))

    def _create_tweak_row(self, parent, tweak: Tweak, row_idx: int):
        """Single tweak row with toggle, name, risk badge, and expandable info"""
        is_selected = tweak.id in self.selected_tweaks
        risk_c = RISK_COLORS.get(tweak.risk_level, RISK_COLORS["LOW"])

        row = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"] if not is_selected else COLORS["bg_card_hover"],
            corner_radius=RADIUS["sm"],
            border_width=0,
        )
        row.grid_columnconfigure(2, weight=1)

        # Toggle
        var = ctk.BooleanVar(value=is_selected)
        toggle = ctk.CTkSwitch(
            row, text="", variable=var, width=40, height=20,
            switch_width=36, switch_height=18,
            progress_color=COLORS["accent"],
            command=lambda tid=tweak.id, v=var: self._toggle_tweak(tid, v),
        )
        toggle.grid(row=0, column=0, padx=(SPACING["sm"], SPACING["xs"]),
                     pady=SPACING["xs"])

        # Name
        ctk.CTkLabel(
            row, text=tweak.name,
            font=font("body_bold" if is_selected else "body"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=1, sticky="w")

        # Description (short)
        ctk.CTkLabel(
            row, text=tweak.description,
            font=font("caption"),
            text_color=COLORS["text_secondary"],
        ).grid(row=0, column=2, sticky="w", padx=(SPACING["sm"], 0))

        # Risk badge
        ctk.CTkLabel(
            row, text=f"  {risk_c['label']}  ",
            font=ctk.CTkFont(size=10),
            fg_color=risk_c["bg"],
            text_color=risk_c["fg"],
            corner_radius=RADIUS["sm"],
        ).grid(row=0, column=3, padx=SPACING["xs"])

        # Expected gain
        ctk.CTkLabel(
            row, text=tweak.expected_gain,
            font=font("caption"),
            text_color=COLORS["accent"],
        ).grid(row=0, column=4, padx=(0, SPACING["xs"]))

        # Info button
        ctk.CTkButton(
            row, text="\uE946", width=28, height=28,
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=14),
            fg_color="transparent", text_color=COLORS["text_tertiary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["sm"],
            command=lambda t=tweak: self._show_tweak_detail(t),
        ).grid(row=0, column=5, padx=(0, SPACING["sm"]))

        # Restart indicator
        if tweak.requires_restart:
            ctk.CTkLabel(
                row, text="🔄",
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=6, padx=(0, SPACING["sm"]))

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
        if hasattr(self, 'selection_label'):
            self.selection_label.configure(
                text=f"  {count} tweaks selected",
                text_color=COLORS["accent"] if count > 0 else COLORS["text_tertiary"],
            )
        if hasattr(self, 'apply_btn'):
            self.apply_btn.configure(
                text=f"Apply {count} Tweaks",
                fg_color=COLORS["accent"] if count > 0 else COLORS["bg_card"],
                text_color="#FFFFFF" if count > 0 else COLORS["text_tertiary"],
                state="normal" if count > 0 else "disabled",
            )

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
                    dialog.add_output("📸 Taking before-snapshot...")
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
                        dialog.add_output("📸 Taking after-snapshot...")
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

        scroll = ctk.CTkScrollableFrame(detail, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])
        scroll.grid_columnconfigure(0, weight=1)

        risk_c = RISK_COLORS.get(tweak.risk_level, RISK_COLORS["LOW"])
        r = 0

        # Title
        ctk.CTkLabel(scroll, text=tweak.name, font=font("h2"),
                      text_color=COLORS["text_primary"]).grid(row=r, column=0, sticky="w")
        r += 1

        # Risk + Category badges
        badge_f = ctk.CTkFrame(scroll, fg_color="transparent")
        badge_f.grid(row=r, column=0, sticky="w", pady=(SPACING["xs"], SPACING["sm"]))
        r += 1

        ctk.CTkLabel(badge_f, text=f"  {risk_c['label']}  ", font=font("caption"),
                      fg_color=risk_c["bg"], text_color=risk_c["fg"],
                      corner_radius=RADIUS["sm"]).pack(side="left", padx=(0, SPACING["xs"]))

        cat_info = TWEAK_CATEGORIES.get(tweak.category, {})
        ctk.CTkLabel(badge_f, text=f"  {cat_info.get('label', tweak.category)}  ",
                      font=font("caption"), fg_color=COLORS["bg_card"],
                      text_color=cat_info.get("color", COLORS["text_secondary"]),
                      corner_radius=RADIUS["sm"]).pack(side="left", padx=(0, SPACING["xs"]))

        if tweak.requires_restart:
            ctk.CTkLabel(badge_f, text="  🔄 Restart Required  ", font=font("caption"),
                          fg_color="#1E293B", text_color="#94A3B8",
                          corner_radius=RADIUS["sm"]).pack(side="left")

        # Sections
        sections = [
            ("📝 Description", tweak.description),
            ("⚙️ What It Does", tweak.what_it_does),
            ("🚀 Why It Helps", tweak.why_it_helps),
            ("⚠️ Limitations", tweak.limitations),
            ("📊 Expected Gain", tweak.expected_gain),
        ]

        for title, content in sections:
            ctk.CTkLabel(scroll, text=title, font=font("body_bold"),
                          text_color=COLORS["accent"]).grid(row=r, column=0, sticky="w",
                          pady=(SPACING["sm"], 2))
            r += 1
            ctk.CTkLabel(scroll, text=content, font=font("body"),
                          text_color=COLORS["text_secondary"], wraplength=520,
                          anchor="w", justify="left").grid(row=r, column=0, sticky="ew")
            r += 1

        # Warnings
        if tweak.warnings:
            ctk.CTkLabel(scroll, text="🔴 Warnings", font=font("body_bold"),
                          text_color="#F87171").grid(row=r, column=0, sticky="w",
                          pady=(SPACING["sm"], 2))
            r += 1
            for w in tweak.warnings:
                ctk.CTkLabel(scroll, text=f"  • {w}", font=font("body"),
                              text_color="#FBBF24", wraplength=520,
                              anchor="w").grid(row=r, column=0, sticky="ew")
                r += 1

        # Registry keys
        if tweak.registry_keys:
            ctk.CTkLabel(scroll, text="🔑 Registry Keys Modified", font=font("body_bold"),
                          text_color=COLORS["text_tertiary"]).grid(row=r, column=0,
                          sticky="w", pady=(SPACING["sm"], 2))
            r += 1
            for key in tweak.registry_keys:
                ctk.CTkLabel(scroll, text=f"  {key}", font=ctk.CTkFont(size=11, family="Consolas"),
                              text_color=COLORS["text_tertiary"],
                              anchor="w").grid(row=r, column=0, sticky="ew")
                r += 1

        # Meta info
        meta = f"Reversible: {'Yes ✓' if tweak.reversible else 'No ✗'}  |  OS: Windows {', '.join(tweak.compatible_os)}  |  Admin: {'Required' if tweak.requires_admin else 'No'}"
        ctk.CTkLabel(scroll, text=meta, font=font("caption"),
                      text_color=COLORS["text_tertiary"]).grid(row=r, column=0,
                      sticky="w", pady=(SPACING["md"], 0))

        # Close button
        ctk.CTkButton(
            detail, text="Close", font=font("button"),
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["md"], height=36,
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
            search_frame, fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["full"], border_width=1,
            border_color=COLORS["border"],
        )
        search_container.pack(fill="x", ipady=2)

        ctk.CTkLabel(
            search_container, text="\uE721",
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=16),
            text_color=COLORS["text_secondary"],
        ).pack(side="left", padx=(SPACING["md"], SPACING["xs"]))

        self.edu_search = ctk.CTkEntry(
            search_container, placeholder_text="Search tweaks...",
            font=font("body"), fg_color="transparent",
            border_width=0, text_color=COLORS["text_primary"],
        )
        self.edu_search.pack(side="left", fill="x", expand=True, padx=SPACING["xs"])
        self.edu_search.bind("<KeyRelease>", lambda e: self._filter_education())

        # Category filter pills
        pill_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        pill_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["sm"]))

        self.edu_cat_buttons = {}

        # All button
        all_btn = ctk.CTkButton(
            pill_frame, text=f"All ({len(self.registry.get_all_tweaks())})",
            font=font("caption"), fg_color=COLORS["accent"],
            text_color="#FFFFFF", corner_radius=RADIUS["full"],
            height=28, width=0,
            command=lambda: self._set_edu_category(None),
        )
        all_btn.pack(side="left", padx=(0, SPACING["xs"]))
        self.edu_cat_buttons[None] = all_btn

        for cat_key, cat_info in TWEAK_CATEGORIES.items():
            count = len(self.registry.get_tweaks_by_category(cat_key))
            if count == 0:
                continue
            btn = ctk.CTkButton(
                pill_frame, text=f"{cat_info['label']} ({count})",
                font=font("caption"), fg_color=COLORS["bg_card"],
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card_hover"],
                corner_radius=RADIUS["full"], height=28, width=0,
                border_width=1, border_color=COLORS["border"],
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
        if hasattr(self, 'edu_search'):
            query = self.edu_search.get().lower().strip()

        tweaks = self.registry.get_all_tweaks()

        # Filter by category
        if self.active_edu_category:
            tweaks = [t for t in tweaks if t.category == self.active_edu_category]

        # Filter by search
        if query:
            tweaks = [
                t for t in tweaks
                if query in t.name.lower()
                or query in t.description.lower()
                or query in t.what_it_does.lower()
                or query in t.category.lower()
            ]

        if not tweaks:
            ctk.CTkLabel(
                self.edu_list, text="No tweaks found",
                font=font("body"), text_color=COLORS["text_tertiary"],
            ).grid(row=0, column=0, pady=SPACING["xl"])
            return

        for i, tweak in enumerate(tweaks):
            card = self._create_edu_card(self.edu_list, tweak)
            card.grid(row=i, column=0, sticky="ew", pady=(0, SPACING["xs"]))

    def _create_edu_card(self, parent, tweak: Tweak):
        """Education card — read-only tweak info with expandable details"""
        risk_c = RISK_COLORS.get(tweak.risk_level, RISK_COLORS["LOW"])
        cat_info = TWEAK_CATEGORIES.get(tweak.category, {})

        card = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            border_width=1, border_color=COLORS["border"],
        )
        card.grid_columnconfigure(1, weight=1)

        # Category color dot
        ctk.CTkFrame(
            card, fg_color=cat_info.get("color", COLORS["text_secondary"]),
            width=6, height=6, corner_radius=3,
        ).grid(row=0, column=0, padx=(SPACING["sm"], SPACING["xs"]),
               pady=SPACING["sm"])

        # Name + description
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", pady=SPACING["xs"])

        ctk.CTkLabel(
            info_frame, text=tweak.name,
            font=font("body_bold"), text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame, text=tweak.description,
            font=font("caption"), text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        # Risk badge
        ctk.CTkLabel(
            card, text=f"  {risk_c['label']}  ",
            font=ctk.CTkFont(size=10), fg_color=risk_c["bg"],
            text_color=risk_c["fg"], corner_radius=RADIUS["sm"],
        ).grid(row=0, column=2, padx=SPACING["xs"])

        # Gain
        ctk.CTkLabel(
            card, text=tweak.expected_gain,
            font=font("caption"), text_color=COLORS["accent"],
        ).grid(row=0, column=3, padx=SPACING["xs"])

        # Detail button
        ctk.CTkButton(
            card, text="Learn More",
            font=font("caption"), fg_color="transparent",
            text_color=COLORS["accent"],
            hover_color=COLORS["bg_card_hover"],
            corner_radius=RADIUS["sm"], height=26, width=90,
            command=lambda t=tweak: self._show_tweak_detail(t),
        ).grid(row=0, column=4, padx=(0, SPACING["sm"]))

        return card
