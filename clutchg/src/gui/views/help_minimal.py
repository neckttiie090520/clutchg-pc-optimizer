"""
Help View - Minimal Design
Complete documentation viewer
"""

import customtkinter as ctk
import re
from typing import TYPE_CHECKING
from gui.theme import COLORS, SIZES, SPACING, RADIUS, ICON, ICON_FONT
from gui.style import font, bind_dynamic_wraplength
from gui.components.inline_help import InlineHelpBox
from gui.components.glass_card import GlassCard
from gui.components.enhanced_button import EnhancedButton

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class HelpView(ctk.CTkFrame):
    """Help documentation view"""

    UI_STRINGS = {
        "en": {
            "help_header": "Docs",
            "topics": "Topics",
            "search_placeholder": "Search...",
            "search_results": "Search Results",
            "no_matches": "No matches found.",
            "open": "Open",
            "clear": "Clear",
            "quick_links": "Quick Links",
            "common_myths": "Common Myths",
            "what_it_does": "What it does:",
            "features": "Features:",
            "warnings": "Warnings:",
            "category_risk": "Category Risk:",
            "reversibility": "Reversibility:",
            "tweaks_count": "Tweaks:",
            "credits": "Credits",
            "answer": "Answer:",
            "never_touched": "Never Touched",
            "never_touched_desc": "These protections are never disabled by ClutchG:",
        },
        "th": {
            "help_header": "Docs",
            "topics": "หัวข้อ",
            "search_placeholder": "ค้นหาคู่มือ...",
            "search_results": "ผลการค้นหา",
            "no_matches": "ไม่พบผลลัพธ์",
            "open": "เปิด",
            "clear": "ล้าง",
            "quick_links": "ลิงก์ลัด",
            "common_myths": "ความเชื่อที่พบบ่อย",
            "what_it_does": "ทำอะไรบ้าง:",
            "features": "คุณสมบัติ:",
            "warnings": "คำเตือน:",
            "category_risk": "ความเสี่ยงของหมวด:",
            "reversibility": "การย้อนกลับ:",
            "tweaks_count": "จำนวน Tweaks:",
            "credits": "เครดิต",
            "answer": "คำตอบ:",
            "never_touched": "ไม่แตะเด็ดขาด",
            "never_touched_desc": "ระบบป้องกันเหล่านี้ ClutchG ไม่ปิดเลย:",
        },
    }

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Use app's help manager (respects language setting)
        self.help_manager = app.help_manager
        self.current_topic_id = "getting_started"
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *a: self.on_search_change())
        self.search_entry = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self,
            text=self._ui("help_header"),
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Sidebar navigation
        self.create_sidebar()

        # Content area
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=1, sticky="nsew")

        # Show first topic
        self.show_topic("getting_started")

    def _font(
        self, size: int, weight: str = "normal", slant: str = "roman"
    ) -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed.

        Args:
            size: Font size
            weight: Font weight ("normal" or "bold")
            slant: Font slant ("roman" or "italic")
        """
        # Handle old calls where "italic" was passed as weight
        if weight == "italic":
            weight = "normal"
            slant = "italic"

        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Tahoma", size=size, weight=weight, slant=slant)
        return font("body", size=size, weight=weight)

    def _ui(self, key: str) -> str:
        lang = "th" if self.app.config.get("language") == "th" else "en"
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def _icon_label(
        self, parent, icon_key: str, size: int = 14, color: str | None = None
    ) -> ctk.CTkLabel:
        """Create a CTkLabel rendering a Material Symbols icon glyph."""
        return ctk.CTkLabel(
            parent,
            text=ICON(icon_key),
            font=ctk.CTkFont(family="Tabler Icons", size=size),
            text_color=color or COLORS["text_secondary"],
            width=size + 4,
        )

    def create_sidebar(self):
        """Create topic navigation sidebar with GlassCard"""
        self.sidebar = GlassCard(self, corner_radius=RADIUS["lg"], width=200)
        self.sidebar.grid(row=1, column=0, sticky="ns", padx=(0, SPACING["lg"]))
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text=self._ui("topics"),
            font=self._font(14, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(SPACING["md"], SPACING["sm"]), padx=SPACING["md"], anchor="w")

        # Search bar (modernized pill shape)
        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            textvariable=self.search_var,
            placeholder_text=self._ui("search_placeholder"),
            font=self._font(12),
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"],
            corner_radius=RADIUS["full"],
            height=36,
        )
        self.search_entry.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["sm"]))

        EnhancedButton.outline(
            self.sidebar, text=self._ui("clear"), height=36, command=self._clear_search
        ).pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["sm"]))

        # Get all topics
        topics = self.help_manager.get_all_topics()

        # Store button references for highlighting
        self.topic_buttons = {}

        for topic in topics:
            # Compound widget: clickable frame with icon + text labels
            btn_frame = ctk.CTkFrame(
                self.sidebar,
                fg_color="transparent",
                height=36,
                corner_radius=RADIUS["sm"],
                cursor="hand2",
            )
            btn_frame.pack(fill="x", padx=SPACING["sm"], pady=2)
            btn_frame.pack_propagate(False)

            icon_lbl = ctk.CTkLabel(
                btn_frame,
                text=ICON(topic.icon),
                font=ctk.CTkFont(family="Tabler Icons", size=16),
                text_color=COLORS.get("text_muted", COLORS["text_secondary"]),
                width=20,
            )
            icon_lbl.pack(side="left", padx=(SPACING["sm"], 4))

            text_lbl = ctk.CTkLabel(
                btn_frame,
                text=topic.title,
                font=self._font(12),
                text_color=COLORS["text_secondary"],
                anchor="w",
            )
            text_lbl.pack(side="left", fill="x", expand=True)

            # Bind click to frame + both labels
            cmd = lambda t=topic: self.show_topic(t.id)
            btn_frame.bind("<Button-1>", lambda e, c=cmd: c())
            icon_lbl.bind("<Button-1>", lambda e, c=cmd: c())
            text_lbl.bind("<Button-1>", lambda e, c=cmd: c())

            self.topic_buttons[topic.id] = (btn_frame, icon_lbl, text_lbl)

        if self.search_entry:
            self.search_entry.bind("<Control-f>", self._focus_search)

    def _focus_search(self, event=None):
        """Focus search entry."""
        if self.search_entry:
            self.search_entry.focus_set()
            self.search_entry.select_range(0, "end")
        return "break"

    def refresh_language(self):
        """Refresh sidebar and content after language change."""
        self.help_manager = self.app.help_manager
        if hasattr(self, "header_label") and self.header_label:
            self.header_label.configure(
                text=self._ui("help_header"), font=self._font(24, "bold")
            )
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.destroy()
        self.create_sidebar()
        if self.current_topic_id:
            self.show_topic(self.current_topic_id)
        else:
            self.show_topic("getting_started")

    def show_topic(self, topic_id: str):
        """Show a help topic"""
        self.current_topic_id = topic_id
        # Update sidebar highlighting
        for tid, widgets in self.topic_buttons.items():
            frame, icon_lbl, text_lbl = widgets
            if tid == topic_id:
                frame.configure(fg_color=COLORS["bg_hover"])
                icon_lbl.configure(text_color=COLORS["accent"])
                text_lbl.configure(text_color=COLORS["accent"])
            else:
                frame.configure(fg_color="transparent")
                icon_lbl.configure(text_color=COLORS["text_secondary"])
                text_lbl.configure(text_color=COLORS["text_secondary"])

        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        topic = self.help_manager.get_topic(topic_id)
        if not topic:
            return

        # Title (compound: icon + text)
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(
            title_frame,
            text=ICON(topic.icon),
            font=ctk.CTkFont(family="Tabler Icons", size=22),
            text_color=COLORS.get("text_tertiary", COLORS["text_secondary"]),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            title_frame,
            text=topic.title,
            font=self._font(18, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # Quick links removed as per user request
        # self._render_quick_links()

        # Render content based on topic type
        if topic_id == "profiles":
            self._render_profiles(topic.content)
        elif topic_id == "scripts":
            self._render_scripts(topic.content)
        elif topic_id == "backup":
            self._render_sections(topic.content.get("sections", []))
        elif topic_id == "safety":
            self._render_safety(topic.content)
        elif topic_id == "troubleshooting":
            self._render_troubleshooting(topic.content)
        elif topic_id == "about":
            self._render_about(topic.content)
        elif topic_id == "faq":
            self._render_faq(topic.content)
        elif topic_id == "custom_tweaks":
            self._render_sections(topic.content.get("sections", []))
        else:
            self._render_sections(topic.content.get("sections", []))

    def _render_profiles(self, profiles_data: dict):
        """Render profiles explanation"""
        # Overview paragraph
        if "overview" in profiles_data:
            _profiles_overview = ctk.CTkLabel(
                self.content_frame,
                text=profiles_data["overview"],
                font=self._font(12),
                text_color=COLORS["text_secondary"],
                justify="left",
            )
            _profiles_overview.pack(anchor="w", fill="x", pady=(0, 15), padx=20)
            bind_dynamic_wraplength(self.content_frame, _profiles_overview)

        profiles = profiles_data.get("profiles", {})

        for profile_name, profile in profiles.items():
            # Profile card with GlassCard
            card = GlassCard(self.content_frame, corner_radius=RADIUS["lg"])
            card.pack(fill="x", pady=SPACING["sm"])

            # Header
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(15, 10))

            ctk.CTkLabel(
                header,
                text=profile["name"],
                font=self._font(16, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            # Risk badge
            risk_color = profile.get("risk_color", COLORS["text_muted"])
            ctk.CTkLabel(
                header,
                text=f"● {profile['risk_level']}",
                font=self._font(10),
                text_color=risk_color,
            ).pack(side="right")

            # Details
            details_frame = ctk.CTkFrame(card, fg_color="transparent")
            details_frame.pack(fill="x", padx=20, pady=(0, 15))

            for key in ["description", "best_for", "fps_gain"]:
                if key in profile:
                    self._add_detail_row(
                        details_frame, key.replace("_", " ").title(), profile[key]
                    )

            # Tweaks count
            if "tweaks_count" in profile:
                self._add_detail_row(
                    details_frame,
                    self._ui("tweaks_count"),
                    profile["tweaks_count"],
                )

            # What it does
            if "what_it_does" in profile:
                ctk.CTkLabel(
                    details_frame,
                    text=self._ui("what_it_does"),
                    font=self._font(11, "bold"),
                    text_color=COLORS["text_secondary"],
                ).pack(anchor="w", pady=(10, 5))

                for item in profile["what_it_does"]:
                    ctk.CTkLabel(
                        details_frame,
                        text=f"  • {item}",
                        font=self._font(11),
                        text_color=COLORS["text_primary"],
                    ).pack(anchor="w")

            # Who should use (compound: icon + text)
            if "who_should_use" in profile:
                tip_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                tip_frame.pack(anchor="w", pady=(10, 0))

                ctk.CTkLabel(
                    tip_frame,
                    text=ICON("lightbulb"),
                    font=ctk.CTkFont(family="Tabler Icons", size=11),
                    text_color=COLORS["accent"],
                ).pack(side="left", padx=(0, 4))

                _tip_lbl = ctk.CTkLabel(
                    tip_frame,
                    text=profile["who_should_use"],
                    font=self._font(10, "italic"),
                    text_color=COLORS["accent"],
                )
                _tip_lbl.pack(side="left", fill="x", expand=True)
                bind_dynamic_wraplength(tip_frame, _tip_lbl)

            if profile.get("warnings"):
                ctk.CTkLabel(
                    details_frame,
                    text=self._ui("warnings"),
                    font=self._font(11, "bold"),
                    text_color=COLORS["warning"],
                ).pack(anchor="w", pady=(10, 5))

                for item in profile["warnings"]:
                    _warn_lbl = ctk.CTkLabel(
                        details_frame,
                        text=f"  \u2022 {item}",
                        font=self._font(11),
                        text_color=COLORS["text_secondary"],
                        justify="left",
                    )
                    _warn_lbl.pack(anchor="w", fill="x", pady=1)
                    bind_dynamic_wraplength(details_frame, _warn_lbl)

    def _add_detail_row(self, parent, label: str, value: str):
        """Add a detail row"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=self._font(10, "bold"),
            text_color=COLORS["text_muted"],
            width=100,
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            row,
            text=value,
            font=self._font(11),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(side="left")

    def _render_scripts(self, scripts_data: dict):
        """Render script reference"""
        # Overview paragraph
        if "overview" in scripts_data:
            _scripts_ov = ctk.CTkLabel(
                self.content_frame,
                text=scripts_data["overview"],
                font=self._font(12),
                text_color=COLORS["text_secondary"],
                justify="left",
            )
            _scripts_ov.pack(anchor="w", fill="x", pady=(0, 15), padx=20)
            bind_dynamic_wraplength(self.content_frame, _scripts_ov)

        categories = scripts_data.get("categories", {})

        for cat_name, category in categories.items():
            # Category section — compound icon + text
            cat_header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            cat_header.pack(anchor="w", pady=(20, 10))
            ctk.CTkLabel(
                cat_header,
                text=ICON(category["icon"]),
                font=ctk.CTkFont(family="Tabler Icons", size=16),
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(
                cat_header,
                text=category["name"],
                font=self._font(16, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            ctk.CTkLabel(
                self.content_frame,
                text=category["description"],
                font=self._font(11),
                text_color=COLORS["text_secondary"],
            ).pack(anchor="w", pady=(0, 15))

            if "risk" in category:
                ctk.CTkLabel(
                    self.content_frame,
                    text=f"{self._ui('category_risk')} {category['risk']}",
                    font=self._font(10, "bold"),
                    text_color=COLORS["warning"],
                ).pack(anchor="w", pady=(0, 12))

            # Scripts
            for script_name, script in category.get("scripts", {}).items():
                self._render_script_card(script)

    def _render_script_card(self, script: dict):
        """Render a single script card with GlassCard"""
        card = GlassCard(self.content_frame, corner_radius=RADIUS["lg"])
        card.pack(fill="x", pady=SPACING["xs"], padx=(0, SPACING["lg"]))

        ctk.CTkLabel(
            card,
            text=script["name"],
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=15, pady=(12, 5))

        _script_desc = ctk.CTkLabel(
            card,
            text=script["description"],
            font=self._font(11),
            text_color=COLORS["text_secondary"],
        )
        _script_desc.pack(anchor="w", fill="x", padx=15, pady=(0, 10))
        bind_dynamic_wraplength(card, _script_desc)

        if "effects" in script:
            for effect in script["effects"]:
                ctk.CTkLabel(
                    card, text=effect, font=self._font(10), text_color=COLORS["accent"]
                ).pack(anchor="w", padx=15, pady=2)

        if "reversibility" in script:
            _rev_lbl = ctk.CTkLabel(
                card,
                text=f"{self._ui('reversibility')} {script['reversibility']}",
                font=self._font(10),
                text_color=COLORS["text_tertiary"],
                justify="left",
            )
            _rev_lbl.pack(anchor="w", fill="x", padx=15, pady=(8, 12))
            bind_dynamic_wraplength(card, _rev_lbl)

    def _resolve_view_link(self, text: str) -> str | None:
        """Return a view key if a key_point text references a navigable app area."""
        VIEW_KEYWORDS = {
            "dashboard": "dashboard",
            "home": "dashboard",
            "tweaks": "scripts",
            "optimization center": "scripts",
            "backup & restore": "backup",
            "backup and restore": "backup",
            "help & documentation": "help",
            "help and documentation": "help",
            "docs": "help",
        }
        lower = text.lower()
        for keyword, view in VIEW_KEYWORDS.items():
            if lower.startswith(keyword):
                return view
        return None

    def _render_sections(self, sections: list):
        """Render generic sections"""
        for section in sections:
            ctk.CTkLabel(
                self.content_frame,
                text=section.get("heading", ""),
                font=self._font(16, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", pady=(20, 10), padx=20)

            if "content" in section:
                _sec_content = ctk.CTkLabel(
                    self.content_frame,
                    text=section["content"],
                    font=self._font(12),
                    text_color=COLORS["text_secondary"],
                    justify="left",
                )
                _sec_content.pack(anchor="w", fill="x", pady=(0, 10), padx=20)
                bind_dynamic_wraplength(self.content_frame, _sec_content)

            if "steps" in section:
                for step in section["steps"]:
                    ctk.CTkLabel(
                        self.content_frame,
                        text=step,
                        font=self._font(11),
                        text_color=COLORS["text_primary"],
                    ).pack(anchor="w", pady=5, padx=20)

            if "key_points" in section:
                for point in section["key_points"]:
                    view_key = self._resolve_view_link(point)
                    if view_key:
                        EnhancedButton.outline(
                            self.content_frame,
                            text=f"  {point}",
                            height=32,
                            command=lambda v=view_key: self.app.switch_view(v),
                        ).pack(anchor="w", pady=2, padx=20)
                    else:
                        ctk.CTkLabel(
                            self.content_frame,
                            text=point,
                            font=self._font(11),
                            text_color=COLORS["accent"],
                        ).pack(anchor="w", pady=3, padx=20)

    def _render_safety(self, safety_data: dict):
        """Render safety information"""
        # Intro sections (policy paragraph)
        for section in safety_data.get("sections", []):
            ctk.CTkLabel(
                self.content_frame,
                text=section.get("heading", ""),
                font=self._font(16, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", pady=(0, 8))

            if "content" in section:
                _safety_lbl = ctk.CTkLabel(
                    self.content_frame,
                    text=section["content"],
                    font=self._font(12),
                    text_color=COLORS["text_secondary"],
                    justify="left",
                )
                _safety_lbl.pack(anchor="w", fill="x", pady=(0, 15), padx=20)
                bind_dynamic_wraplength(self.content_frame, _safety_lbl)

        # Warning boxes
        warnings = safety_data.get("warnings", [])

        for warning in warnings:
            box = InlineHelpBox(
                self.content_frame,
                title=warning["title"],
                content=warning["content"],
                help_type=warning["level"],
            )
            box.pack(fill="x", pady=10)

        # Never touched list
        never_touched = safety_data.get("never_touched", [])
        if never_touched:
            ctk.CTkLabel(
                self.content_frame,
                text=self._ui("never_touched"),
                font=self._font(16, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", pady=(25, 5))

            ctk.CTkLabel(
                self.content_frame,
                text=self._ui("never_touched_desc"),
                font=self._font(11),
                text_color=COLORS["text_secondary"],
            ).pack(anchor="w", pady=(0, 10), padx=20)

            for item in never_touched:
                item_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
                item_row.pack(anchor="w", padx=20, pady=2)

                ctk.CTkLabel(
                    item_row,
                    text=ICON("shield"),
                    font=ctk.CTkFont(family="Tabler Icons", size=12),
                    text_color=COLORS["success"],
                ).pack(side="left", padx=(0, 6))

                ctk.CTkLabel(
                    item_row,
                    text=item,
                    font=self._font(11),
                    text_color=COLORS["text_primary"],
                ).pack(side="left")

        # Myths section
        ctk.CTkLabel(
            self.content_frame,
            text=self._ui("common_myths"),
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(30, 15))

        for myth in safety_data.get("myths", []):
            myth_frame = GlassCard(self.content_frame, corner_radius=RADIUS["lg"])
            myth_frame.pack(fill="x", pady=SPACING["xs"], padx=(0, SPACING["lg"]))

            # Myth line
            myth_row = ctk.CTkFrame(myth_frame, fg_color="transparent")
            myth_row.pack(anchor="w", padx=15, pady=(10, 5))

            ctk.CTkLabel(
                myth_row,
                text=f"MYTH: {myth['myth']}",
                font=self._font(11),
                text_color=COLORS["danger"],
            ).pack(side="left")

            # Fact line
            fact_row = ctk.CTkFrame(myth_frame, fg_color="transparent")
            fact_row.pack(anchor="w", padx=15, pady=(0, 10))

            ctk.CTkLabel(
                fact_row,
                text=f"FACT: {myth['fact']}",
                font=self._font(11),
                text_color=COLORS["success"],
            ).pack(side="left")

    def _render_troubleshooting(self, trouble_data: dict):
        """Render troubleshooting section"""
        issues = trouble_data.get("issues", [])

        for issue in issues:
            card = GlassCard(self.content_frame, corner_radius=RADIUS["lg"])
            card.pack(fill="x", pady=SPACING["sm"])

            # Problem header (compound: icon + text)
            problem_frame = ctk.CTkFrame(card, fg_color="transparent")
            problem_frame.pack(anchor="w", padx=15, pady=(12, 10))

            ctk.CTkLabel(
                problem_frame,
                text=ICON("build"),
                font=ctk.CTkFont(family="Tabler Icons", size=13),
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                problem_frame,
                text=issue["problem"],
                font=self._font(13, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            for solution in issue["solutions"]:
                ctk.CTkLabel(
                    card,
                    text=f"• {solution}",
                    font=self._font(11),
                    text_color=COLORS["text_secondary"],
                ).pack(anchor="w", padx=15, pady=2)

    def _render_about(self, about_data: dict):
        """Render about section"""
        payload = about_data.get("content", about_data)

        # Version
        ctk.CTkLabel(
            self.content_frame,
            text=f"Version {payload.get('version', '1.0.0')}",
            font=self._font(14, "bold"),
            text_color=COLORS["accent"],
        ).pack(anchor="w", pady=(0, 15))

        # Description
        _about_desc = ctk.CTkLabel(
            self.content_frame,
            text=payload.get("description", ""),
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            justify="left",
        )
        _about_desc.pack(anchor="w", fill="x", pady=(0, 20), padx=20)
        bind_dynamic_wraplength(self.content_frame, _about_desc)

        # Features
        ctk.CTkLabel(
            self.content_frame,
            text=self._ui("features"),
            font=self._font(14, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(10, 10), padx=20)

        for feature in payload.get("features", []):
            ctk.CTkLabel(
                self.content_frame,
                text=f"• {feature}",
                font=self._font(11),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", padx=20, pady=3)

        # Disclaimer
        _discl_lbl = ctk.CTkLabel(
            self.content_frame,
            text=payload.get("disclaimer", ""),
            font=self._font(10, "italic"),
            text_color=COLORS["text_muted"],
        )
        _discl_lbl.pack(anchor="w", fill="x", pady=(30, 0))
        bind_dynamic_wraplength(self.content_frame, _discl_lbl)

        # Credits
        if "credits" in payload:
            ctk.CTkLabel(
                self.content_frame,
                text=self._ui("credits"),
                font=self._font(14, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w", pady=(20, 5), padx=20)

            ctk.CTkLabel(
                self.content_frame,
                text=payload["credits"],
                font=self._font(11),
                text_color=COLORS["text_secondary"],
            ).pack(anchor="w", padx=20)

    def _render_faq(self, faq_data: dict):
        """Render FAQ topic as Q&A cards"""
        questions = faq_data.get("questions", [])

        for i, qa in enumerate(questions):
            card = GlassCard(self.content_frame, corner_radius=RADIUS["lg"])
            card.pack(fill="x", pady=SPACING["sm"])

            # Question row (icon + text)
            q_frame = ctk.CTkFrame(card, fg_color="transparent")
            q_frame.pack(fill="x", padx=15, pady=(12, 8))

            ctk.CTkLabel(
                q_frame,
                text=ICON("help"),
                font=ctk.CTkFont(family="Tabler Icons", size=14),
                text_color=COLORS["accent"],
            ).pack(side="left", padx=(0, 8))

            _q_lbl = ctk.CTkLabel(
                q_frame,
                text=qa["question"],
                font=self._font(13, "bold"),
                text_color=COLORS["text_primary"],
                justify="left",
                anchor="w",
            )
            _q_lbl.pack(side="left", fill="x", expand=True)
            bind_dynamic_wraplength(q_frame, _q_lbl)

            # Answer
            _a_lbl = ctk.CTkLabel(
                card,
                text=qa["answer"],
                font=self._font(11),
                text_color=COLORS["text_secondary"],
                justify="left",
            )
            _a_lbl.pack(anchor="w", fill="x", padx=15, pady=(0, 12))
            bind_dynamic_wraplength(card, _a_lbl)

    def on_search_change(self):
        """Handle help search."""
        query = self.search_var.get().strip()
        if not query:
            self.show_topic(self.current_topic_id or "getting_started")
            return
        self._render_search_results(query)

    def _clear_search(self):
        """Clear search and return to current topic."""
        self.search_var.set("")
        self.show_topic(self.current_topic_id or "getting_started")

    def _render_search_results(self, query: str):
        """Render simple search results in content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.content_frame,
            text=f'{self._ui("search_results")}: "{query}"',
            font=self._font(18, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", pady=(0, 15))

        q = query.lower()
        matches = []
        for topic in self.help_manager.get_all_topics():
            text_blob = " ".join(self._collect_text(topic.content)).lower()
            if q in topic.id.lower() or q in topic.title.lower() or q in text_blob:
                matches.append(topic)

        if not matches:
            ctk.CTkLabel(
                self.content_frame,
                text=self._ui("no_matches"),
                font=self._font(12),
                text_color=COLORS["text_secondary"],
            ).pack(anchor="w")
            return

        for topic in matches:
            card = GlassCard(self.content_frame, corner_radius=RADIUS["lg"])
            card.pack(fill="x", pady=SPACING["xs"], padx=(0, SPACING["lg"]))

            # Compound: icon + title
            result_title = ctk.CTkFrame(card, fg_color="transparent")
            result_title.pack(anchor="w", padx=15, pady=(10, 5))

            ctk.CTkLabel(
                result_title,
                text=ICON(topic.icon),
                font=ctk.CTkFont(family="Tabler Icons", size=13),
                text_color=COLORS["text_primary"],
            ).pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                result_title,
                text=topic.title,
                font=self._font(13, "bold"),
                text_color=COLORS["text_primary"],
            ).pack(side="left")

            snippet = self._make_snippet(topic.content, q)
            _snippet_lbl = ctk.CTkLabel(
                card,
                text=snippet,
                font=self._font(11),
                text_color=COLORS["text_secondary"],
            )
            _snippet_lbl.pack(anchor="w", fill="x", padx=15, pady=(0, 10))
            bind_dynamic_wraplength(card, _snippet_lbl)

            EnhancedButton.outline(
                card,
                text=self._ui("open"),
                height=28,
                command=lambda t=topic: self.show_topic(t.id),
            ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["sm"]))

    def _collect_text(self, data):
        """Collect text from nested dict/list content for search."""
        texts = []
        if isinstance(data, dict):
            for value in data.values():
                texts.extend(self._collect_text(value))
        elif isinstance(data, list):
            for item in data:
                texts.extend(self._collect_text(item))
        elif isinstance(data, str):
            texts.append(data)
        return texts

    def _make_snippet(self, content: dict, query: str, max_len: int = 160) -> str:
        """Create a short snippet around the query."""
        text = " ".join(self._collect_text(content))
        lower = text.lower()
        idx = lower.find(query)
        if idx == -1:
            snippet = self._trim_snippet(text[:max_len])
        else:
            start = max(0, idx - 40)
            end = min(len(text), idx + max_len)
            snippet = self._trim_snippet(text[start:end])
        snippet = snippet.strip() + ("..." if len(snippet) >= max_len else "")
        return self._highlight_query(snippet, query)

    def _trim_snippet(self, text: str, min_len: int = 90) -> str:
        """Trim snippet at a natural break when possible."""
        if len(text) <= min_len:
            return text
        for sep in ["。", "！", "?", "!", ".", " "]:
            cut = text.rfind(sep)
            if cut >= min_len:
                return text[: cut + 1]
        return text

    def _highlight_query(self, text: str, query: str) -> str:
        """Highlight query in snippet using brackets."""
        if not query:
            return text
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return pattern.sub(lambda m: f"[{m.group(0)}]", text)
