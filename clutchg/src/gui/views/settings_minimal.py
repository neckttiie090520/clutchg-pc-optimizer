"""
Settings View - Windows 11 Dark UI
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

from gui.theme import theme_manager, COLORS, SPACING, RADIUS
from gui.style import font
from gui.components.glass_card import GlassCard

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class SettingsView(ctk.CTkFrame):
    """Settings view with theme customization"""

    UI_STRINGS = {
        "en": {
            "title": "Settings",
            "appearance": "Appearance",
            "theme": "Theme",
            "language": "Language",
            "safety": "Safety",
            "about": "About",
            "auto_backup": "Auto-create backup before applying profiles",
            "confirm_actions": "Show confirmation dialogs",
            "app_name": "ClutchG v1.0.0",
            "app_description": "Windows PC Optimizer",
        },
        "th": {
            "title": "Settings",
            "appearance": "Appearance",
            "theme": "Theme",
            "language": "Language",
            "safety": "Safety",
            "about": "About",
            "auto_backup": "Auto-Backup (สำรองข้อมูลอัตโนมัติ)",
            "confirm_actions": "Confirmation Dialogs (แสดงกล่องยืนยัน)",
            "app_name": "ClutchG v1.0.0",
            "app_description": "Windows PC Optimizer",
        },
    }

    def __init__(self, parent, app: 'ClutchGApp'):
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
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 30))
        
        # Settings content
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)

        # Appearance (Theme)
        self.create_section(content, self._ui("appearance"), [
            self.create_appearance_setting
        ])

        # Language
        self.create_section(content, self._ui("language"), [
            self.create_language_setting
        ])

        # Safety
        self.create_section(content, self._ui("safety"), [
            self.create_safety_settings
        ])

        # About
        self.create_section(content, self._ui("about"), [
            self.create_about
        ])

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed."""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Figtree", size=size, weight=weight)
        return font("body", size=size, weight=weight)

    def _ui(self, key: str) -> str:
        """Get UI string in current language."""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def create_section(self, parent, title, creators):
        """Create settings section with GlassCard"""
        section = GlassCard(parent, corner_radius=RADIUS["lg"])
        section.pack(fill="x", pady=SPACING["md"])
        section.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            section,
            text=title.upper(),
            font=self._font(10, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["sm"]))
        
        for creator in creators:
            creator(section)
        
        ctk.CTkLabel(section, text="", height=SPACING["sm"]).pack()
    
    def create_appearance_setting(self, parent):
        """Theme setting"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text=self._ui("theme"),
            font=self._font(13),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        available_themes = theme_manager.get_available_themes()
        current_theme = self.config.get("theme", "modern")
        # Capitalize for display
        theme_display = {t: t.capitalize() for t in available_themes}
        display_values = [theme_display[t] for t in available_themes]
        current_display = theme_display.get(current_theme, current_theme.capitalize())

        self.theme_var = ctk.StringVar(value=current_display)
        ctk.CTkOptionMenu(
            frame,
            values=display_values,
            variable=self.theme_var,
            command=self.change_theme,
            width=120,
            fg_color=COLORS["bg_elevated"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"]
        ).grid(row=0, column=1, sticky="e")

    def change_theme(self, value: str):
        """Apply selected theme"""
        theme_key = value.lower()
        theme_manager.set_theme(theme_key)
        self.config["theme"] = theme_key
        self.app.config["theme"] = theme_key
        self.app.config_manager.save_config(self.config)
        self.app.refresh_current_view()
        if hasattr(self.app, "toast"):
            self.app.toast.info(f"Theme changed to {value}")

    def create_language_setting(self, parent):
        """Language setting"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text=self._ui("language"),
            font=self._font(13),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        current_lang = self.config.get("language", "en")
        lang_display = "English" if current_lang == "en" else "ไทย"

        self.lang_var = ctk.StringVar(value=lang_display)
        ctk.CTkOptionMenu(
            frame,
            values=["English", "ไทย"],
            variable=self.lang_var,
            command=self.change_language,
            width=120,
            fg_color=COLORS["bg_elevated"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"]
        ).grid(row=0, column=1, sticky="e")

    def create_safety_settings(self, parent):
        """Safety settings"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        # Load values from config
        self.auto_backup_var = ctk.BooleanVar(value=self.config.get("auto_backup", True))
        ctk.CTkCheckBox(
            frame,
            text=self._ui("auto_backup"),
            font=self._font(12),
            variable=self.auto_backup_var,
            text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.save_config
        ).pack(anchor="w", pady=SPACING["xs"])

        self.confirm_var = ctk.BooleanVar(value=self.config.get("confirm_actions", True))
        ctk.CTkCheckBox(
            frame,
            text=self._ui("confirm_actions"),
            font=self._font(12),
            variable=self.confirm_var,
            text_color=COLORS["text_primary"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.save_config
        ).pack(anchor="w", pady=SPACING["xs"])

    def create_about(self, parent):
        """About section"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])

        ctk.CTkLabel(
            frame,
            text=self._ui("app_name"),
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text=self._ui("app_description"),
            font=self._font(11),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, SPACING["sm"]))
    
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
        if hasattr(self.app, 'toast'):
            message = f"Language changed to Hybrid (TH)" if lang == "th" else f"Language changed to {value}"
            self.app.toast.info(message)

    def save_config(self):
        """Save configuration when settings change"""
        # Update config from current widget values
        self.config["auto_backup"] = self.auto_backup_var.get()
        self.config["confirm_actions"] = self.confirm_var.get()

        # Save to file
        self.app.config_manager.save_config(self.config)
