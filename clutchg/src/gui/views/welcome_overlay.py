"""
Welcome/Tutorial Overlay
First-time user walkthrough — Phase 3C redesign

Layout (per spec):
  Header:  bolt-icon + "ClutchG" left  |  Skip ghost-button right  (no skip on step 5)
  Body:    centered step icon (72x72, 18px radius) → title → description → highlight rows
  Footer:  dot indicators left  |  Back / Next buttons right  (border-top separator)

Dialog: 660px wide, bg_secondary, border-medium, r-xl radius.
Step 5 uses success-dim icon bg + success color; "Get Started" replaces "Next".
"""

import customtkinter as ctk
from typing import TYPE_CHECKING, List, Optional

from gui.theme import COLORS, SIZES, SPACING, RADIUS, ICON, ICON_FONT
from gui.style import font, style_primary_button, style_outline_button
from gui.components.icon_provider import get_icon

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


# ── Step definitions ────────────────────────────────────────────────
# Each step: icon_name, icon_color_key, icon_bg_key, title, desc, highlights
# highlights = list of (icon_name, icon_color_override|None, text)

STEP_DEFS = [
    {
        "icon": "waving_hand",
        "icon_color": "accent",
        "icon_bg": "accent_dim",
    },
    {
        "icon": "dashboard_ms",
        "icon_color": "accent",
        "icon_bg": "accent_dim",
    },
    {
        "icon": "tune",
        "icon_color": "accent",
        "icon_bg": "accent_dim",
    },
    {
        "icon": "backup_ms",
        "icon_color": "accent",
        "icon_bg": "accent_dim",
    },
    {
        "icon": "rocket_launch",
        "icon_color": "success",
        "icon_bg": "success_dim",
    },
]


class WelcomeOverlay(ctk.CTkToplevel):
    """Welcome overlay for first-time users — Phase 3C redesign"""

    # ── Localization strings (EN / TH) ───────────────────────────────
    UI_STRINGS = {
        "en": {
            "window_title": "Welcome to ClutchG",
            "logo_text": "ClutchG",
            "skip_btn": "Skip",
            # Step 1 — Welcome
            "step1_title": "Welcome to ClutchG",
            "step1_desc": "A Windows optimizer built for gamers. Real tweaks, no placebo.\nEverything is logged and reversible.",
            "step1_h1": "Evidence-based tweaks only",
            "step1_h2": "Full backup before every change",
            "step1_h3": "One-click rollback if anything goes wrong",
            # Step 2 — Home
            "step2_title": "Home",
            "step2_desc": "Your dashboard. See system status, recent activity,\nand jump to any section from here.",
            # Step 3 — Choose a Profile
            "step3_title": "Choose a Profile",
            "step3_desc": "Three levels to match your comfort zone.\nStart with Safe if you're not sure.",
            "step3_h1_bold": "Safe",
            "step3_h1": "Low risk, stable tweaks",
            "step3_h2_bold": "Competitive",
            "step3_h2": "Aggressive, for ranked play",
            "step3_h3_bold": "Extreme",
            "step3_h3": "Max FPS, know the risks",
            # Step 4 — Backup
            "step4_title": "Automatic Backups",
            "step4_desc": "ClutchG creates a System Restore point before any optimization.\nIf something breaks, one click rolls it back.",
            "step4_h1": "System Restore point created before every apply",
            "step4_h2": "Registry keys backed up separately",
            "step4_h3": "Full change log in the Backup section",
            # Step 5 — Ready
            "step5_title": "You're All Set",
            "step5_desc": "Head to Profiles to pick your optimization level,\nor explore Tweaks to handpick individual changes.\nCheck Docs if you want to learn more.",
            # Buttons
            "back_btn": "Back",
            "next_btn": "Next",
            "get_started": "Get Started",
        },
        "th": {
            "window_title": "ยินดีต้อนรับสู่ ClutchG",
            "logo_text": "ClutchG",
            "skip_btn": "ข้าม",
            # Step 1 — Welcome
            "step1_title": "ยินดีต้อนรับสู่ ClutchG",
            "step1_desc": "Optimizer สำหรับ Windows ที่สร้างมาเพื่อเกมเมอร์\nปรับแต่งจริง ไม่มี Placebo ทุกอย่าง Log ไว้และย้อนกลับได้",
            "step1_h1": "ปรับแต่งที่มีหลักฐานรองรับเท่านั้น",
            "step1_h2": "Backup ก่อนทุกการเปลี่ยนแปลง",
            "step1_h3": "กดย้อนกลับได้ทันทีหากมีปัญหา",
            # Step 2 — Home
            "step2_title": "หน้าหลัก",
            "step2_desc": "Dashboard ของคุณ ดูสถานะระบบ กิจกรรมล่าสุด\nและเข้าถึงทุกส่วนได้จากที่นี่",
            # Step 3 — Choose a Profile
            "step3_title": "เลือก Profile",
            "step3_desc": "3 ระดับให้เลือกตามความถนัด\nแนะนำ Safe ถ้ายังไม่แน่ใจ",
            "step3_h1_bold": "Safe",
            "step3_h1": "ความเสี่ยงต่ำ ปรับแต่งพื้นฐาน",
            "step3_h2_bold": "Competitive",
            "step3_h2": "ดุดัน สำหรับเล่น Ranked",
            "step3_h3_bold": "Extreme",
            "step3_h3": "FPS สูงสุด ต้องรู้ความเสี่ยง",
            # Step 4 — Backup
            "step4_title": "Backup อัตโนมัติ",
            "step4_desc": "ClutchG สร้าง System Restore point ก่อน Optimize ทุกครั้ง\nถ้ามีปัญหา กดย้อนกลับได้เลย",
            "step4_h1": "สร้าง Restore point ก่อนทุกครั้งที่ Apply",
            "step4_h2": "Backup Registry key แยกต่างหาก",
            "step4_h3": "Log การเปลี่ยนแปลงทั้งหมดในส่วน Backup",
            # Step 5 — Ready
            "step5_title": "พร้อมแล้ว!",
            "step5_desc": "ไปที่ Profiles เพื่อเลือกระดับ Optimize\nหรือเข้า Tweaks เพื่อเลือกปรับแต่งทีละตัว\nดู Docs ถ้าอยากเรียนรู้เพิ่มเติม",
            # Buttons
            "back_btn": "ย้อนกลับ",
            "next_btn": "ถัดไป",
            "get_started": "เริ่มใช้งาน",
        },
    }

    # highlight rows per step: list of (icon_name, color_key_or_None, text_key, bold_key_or_None)
    # color_key=None → use accent
    STEP_HIGHLIGHTS = {
        0: [
            ("check_circle", None, "step1_h1", None),
            ("check_circle", None, "step1_h2", None),
            ("check_circle", None, "step1_h3", None),
        ],
        1: [],  # Step 2 has no highlights
        2: [
            ("verified_user", "success", "step3_h1", "step3_h1_bold"),
            ("speed", "warning", "step3_h2", "step3_h2_bold"),
            ("local_fire_department", "danger", "step3_h3", "step3_h3_bold"),
        ],
        3: [
            ("restore_ms", None, "step4_h1", None),
            ("inventory_2", None, "step4_h2", None),
            ("history_ms", None, "step4_h3", None),
        ],
        4: [],  # Step 5 has no highlights
    }

    def __init__(self, parent, app: Optional["ClutchGApp"] = None, on_close=None):
        super().__init__(parent)

        self.app = app
        self.on_close = on_close
        self.step = 0
        self.total_steps = 5

        # Get language from app or default to English
        self.language = "en"
        if app and hasattr(app, "config"):
            self.language = app.config.get("language", "en")

        # Configure window — 660px wide (spec), auto height
        self.title(self._ui("window_title"))
        self.geometry("660x520")
        self.configure(fg_color=COLORS["bg_secondary"])
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.show_step(0)

    # ── Helpers ──────────────────────────────────────────────────────

    def _ui(self, key: str) -> str:
        """Get UI string in current language"""
        return self.UI_STRINGS.get(self.language, self.UI_STRINGS["en"]).get(key, key)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        w = weight if weight in ("normal", "bold") else "normal"
        if self.language == "th":
            return ctk.CTkFont(family="Figtree", size=size, weight=w)
        return font("body", size=size, weight=w)

    def _icon_font(self, size: int) -> ctk.CTkFont:
        """Material Symbols font at given size"""
        return ctk.CTkFont(family="Material Symbols Outlined", size=size)

    # ── Build UI ─────────────────────────────────────────────────────

    def _build_ui(self):
        """Build the full overlay layout.

        Structure:
          self (CTkToplevel, bg_secondary)
            ├─ header_frame   (row 0)  — bolt icon + "ClutchG" … Skip
            ├─ body_frame     (row 1, weight=1)  — step icon, title, desc, highlights
            └─ footer_frame   (row 2)  — dots … Back / Next
        """
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()

    # ── Header ───────────────────────────────────────────────────────

    def _build_header(self):
        """Header bar: bolt icon (36x36 accent-dim bg) + 'ClutchG' + Skip button"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 0))
        header.grid_columnconfigure(1, weight=1)

        # Logo icon — 36x36 accent-dim rounded box with bolt
        logo_box = ctk.CTkFrame(
            header,
            width=36,
            height=36,
            fg_color=COLORS["accent_dim"],
            corner_radius=RADIUS["md"],
        )
        logo_box.grid(row=0, column=0, padx=(0, 10))
        logo_box.grid_propagate(False)

        bolt_label = ctk.CTkLabel(
            logo_box,
            text=get_icon("bolt"),
            font=self._icon_font(20),
            text_color=COLORS["accent"],
        )
        bolt_label.place(relx=0.5, rely=0.5, anchor="center")

        # "ClutchG" text
        logo_text = ctk.CTkLabel(
            header,
            text=self._ui("logo_text"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"],
        )
        logo_text.grid(row=0, column=1, sticky="w")

        # Skip ghost button (right side)
        self.skip_btn = ctk.CTkButton(
            header,
            text=self._ui("skip_btn"),
            width=60,
            height=26,
            fg_color="transparent",
            text_color=COLORS["text_muted"],
            hover_color=COLORS.get("bg_hover", "#333333"),
            font=self._font(11),
            corner_radius=RADIUS["sm"],
            command=self.close,
        )
        self.skip_btn.grid(row=0, column=2, sticky="e")

    # ── Body ─────────────────────────────────────────────────────────

    def _build_body(self):
        """Centered body area: step icon → title → desc → highlight box"""
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=28, pady=(24, 0))
        self.body_frame.grid_columnconfigure(0, weight=1)

        # Step icon container (72x72, 18px radius)
        self.step_icon_box = ctk.CTkFrame(
            self.body_frame,
            width=72,
            height=72,
            fg_color=COLORS["accent_dim"],
            corner_radius=18,
        )
        self.step_icon_box.pack(pady=(0, 16))
        self.step_icon_box.pack_propagate(False)

        self.step_icon_label = ctk.CTkLabel(
            self.step_icon_box,
            text="",
            font=self._icon_font(32),
            text_color=COLORS["accent"],
        )
        self.step_icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Step title
        self.title_label = ctk.CTkLabel(
            self.body_frame,
            text="",
            font=self._font(18, "bold"),
            text_color=COLORS["text_primary"],
        )
        self.title_label.pack(pady=(0, 8))

        # Step description
        self.desc_label = ctk.CTkLabel(
            self.body_frame,
            text="",
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            wraplength=480,
            justify="center",
        )
        self.desc_label.pack(pady=(0, 20))

        # Highlight box container — will be filled/cleared per step
        self.highlight_frame = ctk.CTkFrame(
            self.body_frame,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADIUS["lg"],
        )
        # Don't pack yet — show_step manages visibility

    # ── Footer ───────────────────────────────────────────────────────

    def _build_footer(self):
        """Footer bar: dots (left) … Back / Next (right), with border-top"""
        footer = ctk.CTkFrame(
            self,
            fg_color="transparent",
            border_width=0,
        )
        footer.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        footer.grid_columnconfigure(1, weight=1)

        # Top separator line
        sep = ctk.CTkFrame(footer, height=1, fg_color=COLORS["border"])
        sep.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Dots container (left)
        dots_wrapper = ctk.CTkFrame(footer, fg_color="transparent")
        dots_wrapper.grid(row=1, column=0, sticky="w", padx=28, pady=(16, 20))

        self.dots: List[ctk.CTkFrame] = []
        for _ in range(self.total_steps):
            dot = ctk.CTkFrame(
                dots_wrapper,
                width=8,
                height=8,
                corner_radius=4,
                fg_color=COLORS["bg_active"],
            )
            dot.pack(side="left", padx=3)
            dot.pack_propagate(False)
            self.dots.append(dot)

        # Buttons container (right)
        btn_wrapper = ctk.CTkFrame(footer, fg_color="transparent")
        btn_wrapper.grid(row=1, column=2, sticky="e", padx=28, pady=(16, 20))

        # Back button (outline style)
        self.back_btn = ctk.CTkButton(
            btn_wrapper,
            text="",
            width=100,
            height=SIZES["button_height_sm"],
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS.get("bg_hover", "#333333"),
            font=self._font(12, "bold"),
            corner_radius=RADIUS["md"],
            command=self.prev_step,
        )
        self.back_btn.pack(side="left", padx=(0, 8))

        # Next / Get Started button (primary style)
        self.next_btn = ctk.CTkButton(
            btn_wrapper,
            text="",
            width=110,
            height=SIZES["button_height_sm"],
            fg_color=COLORS["accent"],
            text_color="#000000",
            hover_color=COLORS.get("accent_hover", "#6fd4ff"),
            font=self._font(12, "bold"),
            corner_radius=RADIUS["md"],
            command=self.next_step,
        )
        self.next_btn.pack(side="left")

    # ── Step navigation ──────────────────────────────────────────────

    def show_step(self, step: int):
        """Update all UI elements for the given step index."""
        self.step = step
        step_def = STEP_DEFS[step]
        highlights = self.STEP_HIGHLIGHTS.get(step, [])

        # --- Step icon ---
        icon_bg = COLORS[step_def["icon_bg"]]
        icon_color = COLORS[step_def["icon_color"]]
        self.step_icon_box.configure(fg_color=icon_bg)
        self.step_icon_label.configure(
            text=get_icon(step_def["icon"]),
            text_color=icon_color,
        )

        # --- Title & description ---
        self.title_label.configure(text=self._ui(f"step{step + 1}_title"))
        self.desc_label.configure(text=self._ui(f"step{step + 1}_desc"))

        # --- Highlight box ---
        # Destroy old highlight children and hide/show frame
        for child in self.highlight_frame.winfo_children():
            child.destroy()

        if highlights:
            self.highlight_frame.pack(pady=(0, 8))
            for idx, (h_icon, h_color_key, h_text_key, h_bold_key) in enumerate(
                highlights
            ):
                row = ctk.CTkFrame(self.highlight_frame, fg_color="transparent")
                row.pack(
                    fill="x",
                    padx=18,
                    pady=(6 if idx == 0 else 0, 6 if idx == len(highlights) - 1 else 0),
                )

                # Icon (16px)
                color = COLORS[h_color_key] if h_color_key else COLORS["accent"]
                icon_label = ctk.CTkLabel(
                    row,
                    text=get_icon(h_icon),
                    font=self._icon_font(16),
                    text_color=color,
                    width=20,
                )
                icon_label.pack(side="left", padx=(0, 10), pady=6)

                # Text — if bold_key exists, show "Bold — rest" pattern
                if h_bold_key:
                    bold_text = self._ui(h_bold_key)
                    rest_text = self._ui(h_text_key)
                    # Bold part
                    bold_label = ctk.CTkLabel(
                        row,
                        text=bold_text,
                        font=self._font(12, "bold"),
                        text_color=COLORS["text_primary"],
                    )
                    bold_label.pack(side="left")
                    # " — rest" part
                    dash_label = ctk.CTkLabel(
                        row,
                        text=f" \u2014 {rest_text}",
                        font=self._font(12),
                        text_color=COLORS["text_secondary"],
                    )
                    dash_label.pack(side="left")
                else:
                    text_label = ctk.CTkLabel(
                        row,
                        text=self._ui(h_text_key),
                        font=self._font(12),
                        text_color=COLORS["text_secondary"],
                    )
                    text_label.pack(side="left")
        else:
            self.highlight_frame.pack_forget()

        # --- Dot indicators ---
        for i, dot in enumerate(self.dots):
            if i == step:
                dot.configure(fg_color=COLORS["accent"])
            else:
                dot.configure(fg_color=COLORS["bg_active"])

        # --- Skip button visibility (hidden on step 5) ---
        if step == self.total_steps - 1:
            self.skip_btn.grid_remove()
        else:
            self.skip_btn.grid()

        # --- Back button (disabled on step 0, hidden on step 0 for cleanliness) ---
        if step == 0:
            self.back_btn.pack_forget()
        else:
            # Make sure it's visible and before next_btn
            self.back_btn.pack(side="left", padx=(0, 8), before=self.next_btn)
            back_icon = get_icon("arrow_back_ms")
            self.back_btn.configure(text=f"{back_icon} {self._ui('back_btn')}")

        # --- Next / Get Started button ---
        if step == self.total_steps - 1:
            rocket = get_icon("rocket_launch")
            self.next_btn.configure(
                text=f"{rocket} {self._ui('get_started')}",
                fg_color=COLORS["success"],
                hover_color=COLORS.get("success", "#22C55E"),
                width=130,
            )
        else:
            arrow = get_icon("arrow_forward_ms")
            self.next_btn.configure(
                text=f"{self._ui('next_btn')} {arrow}",
                fg_color=COLORS["accent"],
                hover_color=COLORS.get("accent_hover", "#6fd4ff"),
                width=110,
            )

    def next_step(self):
        """Go to next step or close on last step"""
        if self.step < self.total_steps - 1:
            self.show_step(self.step + 1)
        else:
            self.close()

    def prev_step(self):
        """Go to previous step"""
        if self.step > 0:
            self.show_step(self.step - 1)

    def close(self):
        """Close overlay and call on_close callback"""
        self.destroy()
        if self.on_close:
            self.on_close()
