"""
Settings View - Windows 11 Dark UI
"""

import webbrowser
import customtkinter as ctk
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

from gui.theme import theme_manager, COLORS, SPACING, RADIUS
from gui.style import font
from gui.components.glass_card import GlassCard

if TYPE_CHECKING:
    from app_minimal import ClutchGApp

_ICON_FONT = "Segoe MDL2 Assets"

_SECTION_ICONS = {
    "appearance": "\ue790",
    "language": "\ue775",
    "safety": "\ue81e",
    "about": "\ue897",
}

_GITHUB_URL = "https://github.com/neckttiie090520/clutchg-pc-optimizer"


class SettingsView(ctk.CTkFrame):
    """Settings view with theme customization"""

    UI_STRINGS = {
        "en": {
            "title": "Settings",
            "appearance": "Appearance",
            "appearance_desc": "Choose your visual theme",
            "theme": "Theme",
            "language": "Language",
            "language_desc": "Interface language (app restarts view)",
            "safety": "Safety",
            "auto_backup": "Auto Backup",
            "auto_backup_desc": "Create backup before applying profiles",
            "confirm_actions": "Confirm Actions",
            "confirm_actions_desc": "Show confirmation dialogs before changes",
            "flight_recorder": "Flight Recorder",
            "flight_recorder_desc": "Log every tweak, rollback, and profile apply to a local file",
            "about": "About",
            "about_tagline": "A Windows optimizer built for gamers who want real performance gains, not snake oil.",
            "app_name": "ClutchG PC Optimizer",
            "toast_theme": "Theme \u2192 {value}",
            "toast_language": "Language \u2192 {value}",
        },
        "th": {
            "title": "Settings",
            "appearance": "Appearance",
            "appearance_desc": "\u0e40\u0e25\u0e37\u0e2d\u0e01\u0e18\u0e35\u0e21\u0e17\u0e35\u0e48\u0e0a\u0e2d\u0e1a",
            "theme": "Theme",
            "language": "Language",
            "language_desc": "\u0e20\u0e32\u0e29\u0e32\u0e02\u0e2d\u0e07\u0e41\u0e2d\u0e1b (\u0e23\u0e35\u0e40\u0e1f\u0e23\u0e0a\u0e2b\u0e19\u0e49\u0e32)",
            "safety": "Safety",
            "auto_backup": "Auto Backup",
            "auto_backup_desc": "\u0e2a\u0e23\u0e49\u0e32\u0e07 Backup \u0e2d\u0e31\u0e15\u0e42\u0e19\u0e21\u0e31\u0e15\u0e34\u0e01\u0e48\u0e2d\u0e19\u0e43\u0e0a\u0e49 Profile",
            "confirm_actions": "Confirm Actions",
            "confirm_actions_desc": "\u0e41\u0e2a\u0e14\u0e07\u0e01\u0e25\u0e48\u0e2d\u0e07\u0e22\u0e37\u0e19\u0e22\u0e31\u0e19\u0e01\u0e48\u0e2d\u0e19\u0e40\u0e1b\u0e25\u0e35\u0e48\u0e22\u0e19\u0e41\u0e1b\u0e25\u0e07",
            "flight_recorder": "Flight Recorder",
            "flight_recorder_desc": "\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e17\u0e38\u0e01\u0e01\u0e32\u0e23\u0e1b\u0e23\u0e31\u0e1a\u0e41\u0e15\u0e48\u0e07\u0e41\u0e25\u0e30 rollback \u0e25\u0e07\u0e44\u0e1f\u0e25\u0e4c",
            "about": "About",
            "about_tagline": "\u0e42\u0e1b\u0e23\u0e41\u0e01\u0e23\u0e21 Optimize Windows \u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e40\u0e01\u0e21\u0e40\u0e21\u0e2d\u0e23\u0e4c\u0e17\u0e35\u0e48\u0e15\u0e49\u0e2d\u0e07\u0e01\u0e32\u0e23\u0e1c\u0e25\u0e25\u0e31\u0e1e\u0e18\u0e4c\u0e08\u0e23\u0e34\u0e07 \u0e44\u0e21\u0e48\u0e43\u0e0a\u0e48 snake oil",
            "app_name": "ClutchG PC Optimizer",
            "toast_theme": "Theme \u2192 {value}",
            "toast_language": "Language \u2192 {value}",
        },
    }

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Load config
        self.config = self.app.config_manager.load_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(
            self,
            text=self._ui("title"),
            font=self._font(24, "bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 30))

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
    ) -> ctk.CTkFrame:
        """Create a setting row with label+description on the left and a
        control widget on the right.

        Args:
            parent: Parent widget.
            label: Primary label text (13px).
            description: Secondary description text (11px).
            control_builder: Callable(frame) -> widget placed in column 1.

        Returns:
            The row frame.
        """
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)

        # Left: stacked label + description
        text_frame = ctk.CTkFrame(row, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            text_frame,
            text=label,
            font=self._font(13),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text=description,
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
        ).pack(anchor="w")

        # Right: control
        control_frame = ctk.CTkFrame(row, fg_color="transparent")
        control_frame.grid(row=0, column=1, sticky="e", padx=(SPACING["md"], 0))
        control_builder(control_frame)

        return row

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def create_section(self, parent, title: str, creators, *, icon_char: str = ""):
        """Create settings section with GlassCard and optional icon."""
        section = GlassCard(parent, corner_radius=RADIUS["lg"])
        section.pack(fill="x", pady=SPACING["md"])
        section.grid_columnconfigure(0, weight=1)

        # Header frame: icon + title
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["sm"]))

        if icon_char:
            ctk.CTkLabel(
                header,
                text=icon_char,
                font=ctk.CTkFont(family=_ICON_FONT, size=12),
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            header,
            text=title.upper(),
            font=self._font(10, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        for creator in creators:
            creator(section)

        # Bottom spacer
        ctk.CTkLabel(section, text="", height=SPACING["sm"]).pack()

    # ------------------------------------------------------------------
    # Appearance
    # ------------------------------------------------------------------

    def create_appearance_setting(self, parent):
        """Theme setting using _setting_row."""
        available_themes = theme_manager.get_available_themes()
        current_theme = self.config.get("theme", "modern")
        theme_display = {t: t.capitalize() for t in available_themes}
        display_values = [theme_display[t] for t in available_themes]
        current_display = theme_display.get(current_theme, current_theme.capitalize())

        self.theme_var = ctk.StringVar(value=current_display)

        def _build_control(frame):
            ctk.CTkOptionMenu(
                frame,
                values=display_values,
                variable=self.theme_var,
                command=self.change_theme,
                width=120,
                fg_color=COLORS["bg_elevated"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("theme"),
            description=self._ui("appearance_desc"),
            control_builder=_build_control,
        )

    def change_theme(self, value: str):
        """Apply selected theme"""
        theme_key = value.lower()
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
                width=120,
                fg_color=COLORS["bg_elevated"],
                button_color=COLORS["accent"],
                button_hover_color=COLORS["accent_hover"],
            ).pack()

        self._setting_row(
            parent,
            label=self._ui("language"),
            description=self._ui("language_desc"),
            control_builder=_build_control,
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
        )

    # ------------------------------------------------------------------
    # About
    # ------------------------------------------------------------------

    def create_about(self, parent):
        """About section with app icon, name, tagline, and link buttons."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
        frame.grid_columnconfigure(1, weight=1)

        # App icon (48x48)
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
        if icon_path.is_file():
            try:
                pil_img = Image.open(icon_path).resize((48, 48), Image.LANCZOS)
                ctk_img = ctk.CTkImage(
                    light_image=pil_img, dark_image=pil_img, size=(48, 48)
                )
                ctk.CTkLabel(frame, image=ctk_img, text="").grid(
                    row=0,
                    column=0,
                    rowspan=3,
                    sticky="nw",
                    padx=(0, SPACING["md"]),
                )
            except Exception:
                # Fallback: no icon shown if load fails
                pass

        # App name + version
        ctk.CTkLabel(
            frame,
            text=self._ui("app_name"),
            font=self._font(15, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            frame,
            text="v1.0.0",
            font=self._font(11),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).grid(row=0, column=2, sticky="w", padx=(6, 0))

        # Tagline
        ctk.CTkLabel(
            frame,
            text=self._ui("about_tagline"),
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            anchor="w",
            wraplength=400,
            justify="left",
        ).grid(row=1, column=1, columnspan=2, sticky="w", pady=(2, SPACING["sm"]))

        # Link buttons row
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=2, column=1, columnspan=2, sticky="w")

        ctk.CTkButton(
            btn_row,
            text="GitHub",
            font=self._font(12),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            width=70,
            height=28,
            command=lambda: self._open_url(_GITHUB_URL),
        ).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkButton(
            btn_row,
            text="Docs",
            font=self._font(12),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["accent"],
            width=60,
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
