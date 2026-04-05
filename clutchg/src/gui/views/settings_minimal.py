"""
Settings View - Windows 11 Dark UI (Phase 3B Redesign)
"""

import webbrowser
import customtkinter as ctk
from typing import TYPE_CHECKING

from gui.theme import COLORS, SPACING, RADIUS
from gui.style import font, bind_dynamic_wraplength
from gui.components.icon_provider import get_icon

if TYPE_CHECKING:
    from app_minimal import ClutchGApp

_ICON_FONT = "Tabler Icons"

_SECTION_ICONS = {
    "safety": "\ueb22",  # shield-check (Tabler)
    "about": "\ueac5",  # info-circle (Tabler)
}

_GITHUB_URL = "https://github.com/neckttiie090520/clutchg-pc-optimizer"


class SettingsView(ctk.CTkFrame):
    """Settings view with theme customization"""

    UI_STRINGS = {
        "en": {
            "title": "Settings",
            "settings_subtitle": "Customize your experience",
            "safety": "Safety",
            "auto_backup": "Auto Backup",
            "auto_backup_desc": "Create a restore point before applying any profile",
            "confirm_actions": "Confirm Actions",
            "confirm_actions_desc": "Ask for confirmation before running tweaks",
            "flight_recorder": "Flight Recorder",
            "flight_recorder_desc": "Log every change for easy rollback and debugging",
            "about": "About",
            "about_tagline": "A Windows optimizer built for gamers who want real performance gains, not snake oil.",
            "about_version": "v1.0.0 · Windows 10/11",
            "app_name": "ClutchG PC Optimizer",
        },
        "th": {
            "title": "Settings",
            "settings_subtitle": "ปรับแต่งประสบการณ์การใช้งาน",
            "safety": "Safety",
            "auto_backup": "Auto Backup",
            "auto_backup_desc": "สร้าง Restore Point ก่อนใช้ Profile ทุกครั้ง",
            "confirm_actions": "Confirm Actions",
            "confirm_actions_desc": "ถามยืนยันก่อนรัน Tweak",
            "flight_recorder": "Flight Recorder",
            "flight_recorder_desc": "บันทึกทุกการเปลี่ยนแปลงเพื่อ rollback ได้ง่าย",
            "about": "About",
            "about_tagline": "โปรแกรม Optimize Windows สำหรับเกมเมอร์ที่ต้องการผลลัพธ์จริง ไม่ใช่ snake oil",
            "about_version": "v1.0.0 · Windows 10/11",
            "app_name": "ClutchG PC Optimizer",
        },
    }

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Load config
        self.config = self.app.config_manager.load_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header — 20px title + subtitle
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="w", pady=(0, SPACING["lg"]))

        ctk.CTkLabel(
            header,
            text=self._ui("title"),
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=self._ui("settings_subtitle"),
            font=self._font(12),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", pady=(2, 0))

        # Settings content
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)

        # Safety
        self.create_section(
            content,
            self._ui("safety"),
            [self.create_safety_settings],
            icon_char=_SECTION_ICONS["safety"],
        )

        # About
        self.create_section(
            content,
            self._ui("about"),
            [self.create_about],
            icon_char=_SECTION_ICONS["about"],
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed."""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Figtree", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def _ui(self, key: str) -> str:
        """Get UI string in current language."""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    @staticmethod
    def _open_url(url: str) -> None:
        """Open a URL in the default browser."""
        webbrowser.open(url)

    # ------------------------------------------------------------------
    # Setting row helper
    # ------------------------------------------------------------------

    def _setting_row(
        self,
        parent,
        label: str,
        description: str,
        control_builder,
        *,
        is_last: bool = False,
    ) -> ctk.CTkFrame:
        """Create a setting row with label+description on the left and a
        control widget on the right. Rows have border-bottom separators
        except the last row.

        Args:
            parent: Parent widget.
            label: Primary label text (13px bold).
            description: Secondary description text (11px, text_tertiary).
            control_builder: Callable(frame) -> widget placed in column 1.
            is_last: If True, omit the bottom border separator.

        Returns:
            The row frame.
        """
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=0)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)

        # Inner content with vertical padding
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.grid(row=0, column=0, columnspan=2, sticky="ew", pady=14)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=0)

        # Left: stacked label + description
        text_frame = ctk.CTkFrame(inner, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            text_frame,
            text=label,
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text=description,
            font=self._font(11),
            text_color=COLORS["text_tertiary"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Right: control
        control_frame = ctk.CTkFrame(inner, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e", padx=(SPACING["md"], 0))
        control_builder(control_frame)

        # Border-bottom separator (skip on last row)
        if not is_last:
            ctk.CTkFrame(
                row,
                fg_color=COLORS["border"],
                height=1,
            ).grid(row=1, column=0, columnspan=2, sticky="ew")

        return row

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def create_section(self, parent, title: str, creators, *, icon_char: str = ""):
        """Create settings section with bordered CTkFrame, icon + uppercase title,
        and a border-bottom separator after the header."""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=RADIUS["lg"],
        )
        section.pack(fill="x", pady=SPACING["sm"])
        section.grid_columnconfigure(0, weight=1)

        # Header frame: icon + uppercase title
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 0))

        if icon_char:
            ctk.CTkLabel(
                header,
                text=icon_char,
                font=ctk.CTkFont(family=_ICON_FONT, size=18),
                text_color=COLORS["text_tertiary"],
            ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header,
            text=title.upper(),
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # Separator line after header
        sep_wrap = ctk.CTkFrame(section, fg_color="transparent")
        sep_wrap.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkFrame(sep_wrap, fg_color=COLORS["border"], height=1).pack(fill="x")

        for creator in creators:
            creator(section)

    # ------------------------------------------------------------------
    # Safety
    # ------------------------------------------------------------------

    def create_safety_settings(self, parent):
        """Safety settings with CTkSwitch controls."""
        # Auto backup
        self.auto_backup_var = ctk.BooleanVar(
            value=self.config.get("auto_backup", True)
        )

        def _build_auto_backup(frame):
            ctk.CTkSwitch(
                frame,
                text="",
                variable=self.auto_backup_var,
                fg_color=COLORS["bg_tertiary"],
                progress_color=COLORS["accent"],
                button_color=COLORS["text_primary"],
                button_hover_color=COLORS["accent_hover"],
                command=self.save_config,
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("auto_backup"),
            description=self._ui("auto_backup_desc"),
            control_builder=_build_auto_backup,
        )

        # Confirm actions
        self.confirm_var = ctk.BooleanVar(
            value=self.config.get("confirm_actions", True)
        )

        def _build_confirm(frame):
            ctk.CTkSwitch(
                frame,
                text="",
                variable=self.confirm_var,
                fg_color=COLORS["bg_tertiary"],
                progress_color=COLORS["accent"],
                button_color=COLORS["text_primary"],
                button_hover_color=COLORS["accent_hover"],
                command=self.save_config,
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("confirm_actions"),
            description=self._ui("confirm_actions_desc"),
            control_builder=_build_confirm,
        )

        # Flight recorder
        self.flight_recorder_var = ctk.BooleanVar(
            value=self.config.get("flight_recorder", True)
        )

        def _build_flight_recorder(frame):
            ctk.CTkSwitch(
                frame,
                text="",
                variable=self.flight_recorder_var,
                fg_color=COLORS["bg_tertiary"],
                progress_color=COLORS["accent"],
                button_color=COLORS["text_primary"],
                button_hover_color=COLORS["accent_hover"],
                command=self.save_config,
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("flight_recorder"),
            description=self._ui("flight_recorder_desc"),
            control_builder=_build_flight_recorder,
            is_last=True,
        )

    # ------------------------------------------------------------------
    # About
    # ------------------------------------------------------------------

    def create_about(self, parent):
        """About section with app logo, name, version, tagline, and links."""
        from pathlib import Path
        from PIL import Image

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=18, pady=(SPACING["lg"], SPACING["md"]))
        frame.grid_columnconfigure(1, weight=1)

        # App logo (48x48)
        logo_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        try:
            pil_img = Image.open(logo_path).resize((48, 48), Image.LANCZOS)
            logo_img = ctk.CTkImage(
                light_image=pil_img, dark_image=pil_img, size=(48, 48)
            )
            logo_label = ctk.CTkLabel(frame, image=logo_img, text="")
        except Exception:
            # Fallback: plain frame with bolt icon if image fails
            logo_box = ctk.CTkFrame(
                frame,
                width=48,
                height=48,
                fg_color=COLORS["accent_dim"],
                corner_radius=RADIUS["lg"],
            )
            logo_box.grid_propagate(False)
            ctk.CTkLabel(
                logo_box,
                text=get_icon("bolt"),
                font=ctk.CTkFont(family=_ICON_FONT, size=24),
                text_color=COLORS["accent"],
            ).place(relx=0.5, rely=0.5, anchor="center")
            logo_label = logo_box

        logo_label.grid(row=0, column=0, rowspan=4, sticky="nw", padx=(0, 16))

        # App name + version on same line
        name_row = ctk.CTkFrame(frame, fg_color="transparent")
        name_row.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            name_row,
            text=self._ui("app_name"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        ctk.CTkLabel(
            frame,
            text=self._ui("about_version"),
            font=self._font(11),
            text_color=COLORS["text_tertiary"],
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(2, 0))

        # Tagline
        _tagline_lbl = ctk.CTkLabel(
            frame,
            text=self._ui("about_tagline"),
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
            justify="left",
        )
        _tagline_lbl.grid(row=2, column=1, sticky="ew", pady=(4, 0))
        bind_dynamic_wraplength(frame, _tagline_lbl)

        # Link buttons row
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=3, column=1, sticky="w", pady=(8, 0))

        # GitHub link with open_in_new icon
        open_icon = get_icon("open_in_new")
        ctk.CTkButton(
            btn_row,
            text=f"{open_icon}  GitHub",
            font=ctk.CTkFont(family=_ICON_FONT, size=12),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            width=80,
            height=28,
            command=lambda: self._open_url(_GITHUB_URL),
        ).pack(side="left", padx=(0, SPACING["md"]))

        # Docs link with description icon
        docs_icon = get_icon("description")
        ctk.CTkButton(
            btn_row,
            text=f"{docs_icon}  Docs",
            font=ctk.CTkFont(family=_ICON_FONT, size=12),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            width=70,
            height=28,
            command=lambda: self.app.switch_view("help"),
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------

    def save_config(self):
        """Save configuration when settings change"""
        self.config["auto_backup"] = self.auto_backup_var.get()
        self.config["confirm_actions"] = self.confirm_var.get()
        self.config["flight_recorder"] = self.flight_recorder_var.get()

        self.app.config_manager.save_config(self.config)
