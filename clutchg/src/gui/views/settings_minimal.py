"""
Settings View - Windows 11 Dark UI (Phase 3B Redesign)
"""

import webbrowser
import customtkinter as ctk
from typing import TYPE_CHECKING

from gui.theme import theme_manager, COLORS, SPACING, RADIUS
from gui.style import font
from gui.components.icon_provider import get_icon

if TYPE_CHECKING:
    from app_minimal import ClutchGApp

_ICON_FONT = "Material Symbols Outlined"

_SECTION_ICONS = {
    "appearance": "\ue40a",  # palette
    "language": "\ue8e2",  # translate
    "safety": "\ue914",  # shield
    "about": "\ue88e",  # info
}

_GITHUB_URL = "https://github.com/neckttiie090520/clutchg-pc-optimizer"


class SettingsView(ctk.CTkFrame):
    """Settings view with theme customization"""

    UI_STRINGS = {
        "en": {
            "title": "Settings",
            "settings_subtitle": "Customize your experience",
            "appearance": "Appearance",
            "appearance_desc": "Choose your preferred color scheme",
            "theme": "Theme",
            "language": "Language",
            "language_desc": "Changes labels and descriptions throughout the app",
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
            "toast_theme": "Theme → {value}",
            "toast_language": "Language → {value}",
        },
        "th": {
            "title": "Settings",
            "settings_subtitle": "ปรับแต่งประสบการณ์การใช้งาน",
            "appearance": "Appearance",
            "appearance_desc": "เลือกธีมสีที่ชอบ",
            "theme": "Theme",
            "language": "Language",
            "language_desc": "เปลี่ยนภาษาข้อความทั่วทั้งแอป",
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
            "toast_theme": "Theme → {value}",
            "toast_language": "Language → {value}",
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

        # Appearance (Theme)
        self.create_section(
            content,
            self._ui("appearance"),
            [self.create_appearance_setting],
            icon_char=_SECTION_ICONS["appearance"],
        )

        # Language
        self.create_section(
            content,
            self._ui("language"),
            [self.create_language_setting],
            icon_char=_SECTION_ICONS["language"],
        )

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
    # Appearance
    # ------------------------------------------------------------------

    def create_appearance_setting(self, parent):
        """Theme setting using _setting_row."""
        available_themes = theme_manager.get_available_themes()
        current_theme = self.config.get("theme", "modern")
        theme_display = {t: t.capitalize() for t in available_themes}
        theme_display["modern"] = "Sun Valley"
        display_values = [theme_display[t] for t in available_themes]
        current_display = theme_display.get(current_theme, current_theme.capitalize())

        self.theme_var = ctk.StringVar(value=current_display)

        def _build_control(frame):
            ctk.CTkOptionMenu(
                frame,
                values=display_values,
                variable=self.theme_var,
                command=self.change_theme,
                width=140,
                fg_color=COLORS["bg_secondary"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                corner_radius=RADIUS["md"],
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("theme"),
            description=self._ui("appearance_desc"),
            control_builder=_build_control,
            is_last=True,
        )

    def change_theme(self, value: str):
        """Apply selected theme"""
        display_to_key = {
            "Sun Valley": "modern",
            "Dark": "dark",
            "Zinc": "zinc",
            "Light": "light",
        }
        theme_key = display_to_key.get(value, value.lower())
        theme_manager.set_theme(theme_key)
        self.config["theme"] = theme_key
        self.app.config["theme"] = theme_key
        self.app.config_manager.save_config(self.config)
        self.app.refresh_current_view()
        if hasattr(self.app, "toast"):
            self.app.toast.info(self._ui("toast_theme").format(value=value))

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def create_language_setting(self, parent):
        """Language setting using _setting_row."""
        current_lang = self.config.get("language", "en")
        lang_display = "English" if current_lang == "en" else "\u0e44\u0e17\u0e22"

        self.lang_var = ctk.StringVar(value=lang_display)

        def _build_control(frame):
            ctk.CTkOptionMenu(
                frame,
                values=["English", "\u0e44\u0e17\u0e22"],
                variable=self.lang_var,
                command=self.change_language,
                width=140,
                fg_color=COLORS["bg_secondary"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
                corner_radius=RADIUS["md"],
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("language"),
            description=self._ui("language_desc"),
            control_builder=_build_control,
            is_last=True,
        )

    def change_language(self, value):
        """Change language"""
        lang = "en" if value == "English" else "th"
        self.config["language"] = lang
        # IMPORTANT: Update app-wide config so _ui() picks it up immediately
        self.app.config["language"] = lang

        self.save_config()

        # Reload help manager with new language
        from core.help_manager import HelpManager

        self.app.help_manager = HelpManager(language=lang)

        # Refresh the current view to apply new language
        self.app.refresh_current_view()

        # Show toast notification
        if hasattr(self.app, "toast"):
            display = "\u0e44\u0e17\u0e22" if lang == "th" else value
            self.app.toast.info(self._ui("toast_language").format(value=display))

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
        """About section with bolt icon box, name, version, tagline, and links."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=18, pady=(SPACING["lg"], SPACING["md"]))
        frame.grid_columnconfigure(1, weight=1)

        # Bolt icon in accent-dim box (48x48)
        icon_box = ctk.CTkFrame(
            frame,
            width=48,
            height=48,
            fg_color=COLORS["accent_dim"],
            corner_radius=RADIUS["lg"],
        )
        icon_box.grid(row=0, column=0, rowspan=4, sticky="nw", padx=(0, 16))
        icon_box.grid_propagate(False)

        bolt_codepoint = get_icon("bolt")
        ctk.CTkLabel(
            icon_box,
            text=bolt_codepoint,
            font=ctk.CTkFont(family=_ICON_FONT, size=24),
            text_color=COLORS["accent"],
        ).place(relx=0.5, rely=0.5, anchor="center")

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
        ctk.CTkLabel(
            frame,
            text=self._ui("about_tagline"),
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=400,
            justify="left",
        ).grid(row=2, column=1, sticky="w", pady=(4, 0))

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
