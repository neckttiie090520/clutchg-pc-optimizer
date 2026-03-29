"""
Backup Center - Simplified backup management view
Phase 2 redesign — removed Simple/Advanced toggle, aligned with spec
"""

import customtkinter as ctk
from datetime import datetime
from typing import TYPE_CHECKING

from gui.theme import COLORS, SPACING, RADIUS, ICON, ICON_FONT
from gui.style import font
from gui.components.enhanced_button import EnhancedButton

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class BackupRestoreCenter(ctk.CTkFrame):
    """
    Backup Center — flat list of backups with info banner.
    No Simple/Advanced toggle; just a clean card list.
    """

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Backup",
            "subtitle_with_data": "{count} backups \u00b7 Last: {date}",
            "subtitle_empty": "No backups yet",
            "create_backup": "New Backup",
            "restore_point": "RESTORE POINT",
            "registry": "REGISTRY",
            "registry_only": "REGISTRY ONLY",
            "restore": "Restore",
            "delete": "Delete",
            "no_backups": "No backups yet",
            "no_backups_desc": "Create one before applying any tweaks.\nTakes a few seconds, saves hours of pain.",
            "create_first": "Create Backup",
            "info_banner_title": "Auto-backup is on",
            "info_banner_desc": "ClutchG snapshots your registry before every profile apply. You can also create manual backups here.",
            "error_loading": "Error Loading Data",
            "retry": "Retry",
            "loading": "Loading...",
            # Dialogs
            "create_dialog_title": "New Backup",
            "create_dialog_prompt": "Enter a name for this backup:",
            "restore_dialog_title": "Restore Backup",
            "restore_dialog_msg": "Restore from '{name}'?\n\nThis will revert system settings to the backup state.\nA restart may be required.",
            "delete_dialog_title": "Delete Backup",
            "delete_dialog_msg": "Delete '{name}'?\n\nThis action cannot be undone.",
            # Toasts
            "backup_created": "Backup created: {name}",
            "backup_failed": "Failed to create backup",
            "restore_success": "Restored successfully. Restart required for full effect.",
            "restore_failed": "Restore failed",
            "deleted_success": "Backup deleted",
            "delete_failed": "Delete failed",
            "error_prefix": "Error: {msg}",
            "permission_denied": "Permission denied. Run as Administrator",
        },
        "th": {
            "title": "Backup",
            "subtitle_with_data": "{count} backups \u00b7 \u0e25\u0e48\u0e32\u0e2a\u0e38\u0e14: {date}",
            "subtitle_empty": "\u0e22\u0e31\u0e07\u0e44\u0e21\u0e48\u0e21\u0e35 Backup",
            "create_backup": "Backup \u0e43\u0e2b\u0e21\u0e48",
            "restore_point": "RESTORE POINT",
            "registry": "REGISTRY",
            "registry_only": "REGISTRY ONLY",
            "restore": "Restore",
            "delete": "\u0e25\u0e1a",
            "no_backups": "\u0e22\u0e31\u0e07\u0e44\u0e21\u0e48\u0e21\u0e35 Backup",
            "no_backups_desc": "\u0e2a\u0e23\u0e49\u0e32\u0e07 Backup \u0e01\u0e48\u0e2d\u0e19\u0e43\u0e0a\u0e49 Tweaks\n\u0e43\u0e0a\u0e49\u0e40\u0e27\u0e25\u0e32\u0e44\u0e21\u0e48\u0e01\u0e35\u0e48\u0e27\u0e34\u0e19\u0e32\u0e17\u0e35 \u0e41\u0e15\u0e48\u0e0a\u0e48\u0e27\u0e22\u0e1b\u0e23\u0e30\u0e2b\u0e22\u0e31\u0e14\u0e40\u0e27\u0e25\u0e32\u0e44\u0e14\u0e49\u0e21\u0e32\u0e01",
            "create_first": "\u0e2a\u0e23\u0e49\u0e32\u0e07 Backup",
            "info_banner_title": "Auto-backup \u0e40\u0e1b\u0e34\u0e14\u0e2d\u0e22\u0e39\u0e48",
            "info_banner_desc": "ClutchG snapshot registry \u0e01\u0e48\u0e2d\u0e19\u0e43\u0e0a\u0e49 profile \u0e17\u0e38\u0e01\u0e04\u0e23\u0e31\u0e49\u0e07 \u0e2a\u0e23\u0e49\u0e32\u0e07 backup \u0e40\u0e2d\u0e07\u0e44\u0e14\u0e49\u0e17\u0e35\u0e48\u0e19\u0e35\u0e48",
            "error_loading": "\u0e40\u0e01\u0e34\u0e14\u0e02\u0e49\u0e2d\u0e1c\u0e34\u0e14\u0e1e\u0e25\u0e32\u0e14\u0e43\u0e19\u0e01\u0e32\u0e23\u0e42\u0e2b\u0e25\u0e14\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25",
            "retry": "\u0e25\u0e2d\u0e07\u0e43\u0e2b\u0e21\u0e48",
            "loading": "\u0e01\u0e33\u0e25\u0e31\u0e07\u0e42\u0e2b\u0e25\u0e14...",
            # Dialogs
            "create_dialog_title": "Backup \u0e43\u0e2b\u0e21\u0e48",
            "create_dialog_prompt": "\u0e43\u0e2a\u0e48\u0e0a\u0e37\u0e48\u0e2d\u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a Backup \u0e19\u0e35\u0e49:",
            "restore_dialog_title": "Restore Backup",
            "restore_dialog_msg": "Restore \u0e08\u0e32\u0e01 '{name}'?\n\n\u0e19\u0e35\u0e48\u0e08\u0e30\u0e04\u0e37\u0e19\u0e04\u0e48\u0e32 Settings \u0e23\u0e30\u0e1a\u0e1a\u0e01\u0e25\u0e31\u0e1a\u0e44\u0e1b\u0e2a\u0e39\u0e48\u0e2a\u0e16\u0e32\u0e19\u0e30 Backup\n\u0e2d\u0e32\u0e08\u0e15\u0e49\u0e2d\u0e07 Restart \u0e40\u0e04\u0e23\u0e37\u0e48\u0e2d\u0e07",
            "delete_dialog_title": "\u0e25\u0e1a Backup",
            "delete_dialog_msg": "\u0e25\u0e1a '{name}'?\n\n\u0e01\u0e32\u0e23\u0e01\u0e23\u0e30\u0e17\u0e33\u0e19\u0e35\u0e49\u0e44\u0e21\u0e48\u0e2a\u0e32\u0e21\u0e32\u0e23\u0e16\u0e22\u0e01\u0e40\u0e25\u0e34\u0e01\u0e44\u0e14\u0e49",
            # Toasts
            "backup_created": "\u0e2a\u0e23\u0e49\u0e32\u0e07 Backup \u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08: {name}",
            "backup_failed": "\u0e2a\u0e23\u0e49\u0e32\u0e07 Backup \u0e44\u0e21\u0e48\u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08",
            "restore_success": "Restore \u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08 \u0e15\u0e49\u0e2d\u0e07 Restart \u0e40\u0e04\u0e23\u0e37\u0e48\u0e2d\u0e07\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e43\u0e2b\u0e49\u0e21\u0e35\u0e1c\u0e25\u0e40\u0e15\u0e47\u0e21\u0e17\u0e35\u0e48",
            "restore_failed": "Restore \u0e44\u0e21\u0e48\u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08",
            "deleted_success": "\u0e25\u0e1a Backup \u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08",
            "delete_failed": "\u0e25\u0e1a Backup \u0e44\u0e21\u0e48\u0e2a\u0e33\u0e40\u0e23\u0e47\u0e08",
            "error_prefix": "\u0e02\u0e49\u0e2d\u0e1c\u0e34\u0e14\u0e1e\u0e25\u0e32\u0e14: {msg}",
            "permission_denied": "\u0e1b\u0e0f\u0e34\u0e40\u0e2a\u0e18\u0e01\u0e32\u0e23\u0e40\u0e02\u0e49\u0e32\u0e16\u0e36\u0e07 \u0e23\u0e31\u0e19\u0e40\u0e1b\u0e47\u0e19 Administrator",
        },
    }

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # row 0=header, 1=banner, 2=content

        # State
        self._init_error = None

        # Initialize BackupManager (wrapped to prevent blank page on failure)
        try:
            from core.backup_manager import BackupManager

            self.backup_mgr = BackupManager()
        except Exception as e:
            print(f"[Backup] ERROR initializing BackupManager: {e}")
            import traceback

            traceback.print_exc()
            self.backup_mgr = None
            self._init_error = str(e)

        # Build UI
        self._subtitle_label = None
        self.create_header()
        self.create_info_banner()
        self.create_content()

        # Load initial data
        self.refresh_view()

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

    def _material_font(self, size: int) -> ctk.CTkFont:
        """Get Material Symbols Outlined font at given size"""
        return ctk.CTkFont(family=ICON_FONT("shield")[0], size=size)

    # ========================================================================
    # HEADER (C1)
    # ========================================================================

    def create_header(self):
        """Create header: title + dynamic subtitle on left, New Backup button on right"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["md"]))
        header.grid_columnconfigure(0, weight=1)

        # Left: Title + Subtitle
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left_frame,
            text=self._ui("title"),
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        self._subtitle_label = ctk.CTkLabel(
            left_frame,
            text=self._ui("subtitle_empty"),
            font=self._font(11),
            text_color=COLORS["text_tertiary"],
        )
        self._subtitle_label.pack(anchor="w", pady=(2, 0))

        # Right: New Backup button (Material Symbols "add" icon)
        actions_frame = ctk.CTkFrame(header, fg_color="transparent")
        actions_frame.grid(row=0, column=1, sticky="e")

        add_icon = ICON("add")
        EnhancedButton.primary(
            actions_frame,
            text=f"{add_icon}  {self._ui('create_backup')}",
            width=150,
            height=36,
            font=self._font(13, "bold"),
            command=self.create_backup,
        ).pack(side="left")

    def _update_subtitle(self, backups=None):
        """Update subtitle with backup count and last date"""
        if not self._subtitle_label:
            return

        if backups and len(backups) > 0:
            count = len(backups)
            # Get most recent backup date
            try:
                latest = max(backups, key=lambda b: b.created_at)
                dt = datetime.fromisoformat(latest.created_at)
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                date_str = "unknown"
            text = self._ui("subtitle_with_data", count=count, date=date_str)
        else:
            text = self._ui("subtitle_empty")

        self._subtitle_label.configure(text=text)

    # ========================================================================
    # INFO BANNER (C2)
    # ========================================================================

    def create_info_banner(self):
        """Create info banner: shield icon + auto-backup message"""
        banner = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=RADIUS["lg"],
        )
        banner.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["md"]))

        inner = ctk.CTkFrame(banner, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        # Shield icon (Material Symbols)
        ctk.CTkLabel(
            inner,
            text=ICON("shield"),
            font=self._material_font(20),
            text_color=COLORS["success"],
        ).pack(side="left", padx=(0, 12))

        # Text block
        text_frame = ctk.CTkFrame(inner, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            text_frame,
            text=self._ui("info_banner_title"),
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text=self._ui("info_banner_desc"),
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            wraplength=500,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

    # ========================================================================
    # CONTENT AREA (C3 / C4)
    # ========================================================================

    def create_content(self):
        """Create scrollable content area for backup list"""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def refresh_view(self):
        """Refresh the backup list"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Check if BackupManager initialization failed
        if self.backup_mgr is None:
            print(f"[Backup] BackupManager not available: {self._init_error}")
            self._show_error_state(
                f"Backup system unavailable: {self._init_error or 'Unknown error'}"
            )
            self._update_subtitle(None)
            return

        try:
            print("[Backup] Loading backups...")
            backups = self.backup_mgr.get_all_backups()
            print(f"[Backup] Found {len(backups)} backup(s)")

            self._update_subtitle(backups)

            if not backups:
                print("[Backup] No backups found, showing empty state")
                self._show_empty_state()
                return

            print("[Backup] Showing backup list")
            self._show_backup_list(backups)

        except Exception as e:
            print(f"[Backup] Error loading backups: {str(e)}")
            import traceback

            traceback.print_exc()
            self._show_error_state(f"Error loading backups: {str(e)}")

    # ========================================================================
    # BACKUP LIST (C3)
    # ========================================================================

    def _show_backup_list(self, backups):
        """Show list of backups as plain bordered cards"""
        scroll_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        scroll_frame.pack(fill="both", expand=True)
        scroll_frame.grid_columnconfigure(0, weight=1)

        for backup in backups:
            self._create_backup_card(scroll_frame, backup)

    def _create_backup_card(self, parent, backup):
        """Create a single backup card matching spec C3"""
        # Plain bordered card (no GlassCard)
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=RADIUS["lg"],
            height=74,
        )
        card.pack(fill="x", pady=(0, SPACING["xs"]))
        card.pack_propagate(False)
        card.grid_columnconfigure(1, weight=1)

        # Icon box (40x40, bg_hover, rounded)
        icon_frame = ctk.CTkFrame(
            card,
            fg_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            width=40,
            height=40,
        )
        icon_frame.grid(row=0, column=0, padx=(16, 14), pady=17)
        icon_frame.pack_propagate(False)

        # Pick icon + color based on backup type
        if backup.has_restore_point:
            icon_name = "check_circle"
            icon_color = COLORS["success"]
        else:
            icon_name = "inventory_2"
            icon_color = COLORS["text_tertiary"]

        ctk.CTkLabel(
            icon_frame,
            text=ICON(icon_name),
            font=self._material_font(20),
            text_color=icon_color,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Info column (name row + date)
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", pady=14)

        # Name + badges row
        name_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_row.pack(anchor="w", fill="x")

        ctk.CTkLabel(
            name_row,
            text=backup.name,
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"],
            wraplength=280,
        ).pack(side="left")

        # Badges
        if backup.has_restore_point:
            ctk.CTkLabel(
                name_row,
                text=self._ui("restore_point"),
                font=self._font(9, "bold"),
                text_color=COLORS["success"],
                fg_color=COLORS["success_dim"],
                corner_radius=RADIUS["sm"],
            ).pack(side="left", padx=(8, 0))

        if backup.has_registry_backup:
            if backup.has_restore_point:
                # Full backup: show REGISTRY badge
                ctk.CTkLabel(
                    name_row,
                    text=self._ui("registry"),
                    font=self._font(9, "bold"),
                    text_color=COLORS["accent"],
                    fg_color=COLORS["accent_dim"],
                    corner_radius=RADIUS["sm"],
                ).pack(side="left", padx=(6, 0))
            else:
                # Registry-only backup: show REGISTRY ONLY badge (neutral)
                ctk.CTkLabel(
                    name_row,
                    text=self._ui("registry_only"),
                    font=self._font(9, "bold"),
                    text_color=COLORS["text_secondary"],
                    fg_color=COLORS["bg_hover"],
                    corner_radius=RADIUS["sm"],
                ).pack(side="left", padx=(8, 0))

        # Date
        try:
            dt = datetime.fromisoformat(backup.created_at)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_str = backup.created_at

        ctk.CTkLabel(
            info_frame,
            text=date_str,
            font=self._font(10),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(3, 0))

        # Action buttons (right side)
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=2, padx=16)

        if backup.has_registry_backup:
            restore_icon = ICON("restore")
            EnhancedButton.success(
                actions,
                text=f"{restore_icon} {self._ui('restore')}",
                width=90,
                height=32,
                font=self._font(12),
                command=lambda b=backup: self.restore_backup(b),
            ).pack(side="left", padx=(0, 6))

        delete_icon = ICON("delete")
        EnhancedButton.danger(
            actions,
            text=f"{delete_icon} {self._ui('delete')}",
            width=80,
            height=32,
            font=self._font(12),
            command=lambda b=backup: self.delete_backup(b),
        ).pack(side="left")

    # ========================================================================
    # EMPTY STATE (C4)
    # ========================================================================

    def _show_empty_state(self):
        """Show empty state matching spec C4"""
        # Card container with border
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=RADIUS["lg"],
        )
        card.pack(fill="x")

        # Inner centered content
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(pady=64)

        # Icon background (80x80, rounded 20px)
        icon_bg = ctk.CTkFrame(
            inner,
            fg_color=COLORS["bg_hover"],
            corner_radius=20,
            width=80,
            height=80,
        )
        icon_bg.pack(pady=(0, 12))
        icon_bg.pack_propagate(False)

        ctk.CTkLabel(
            icon_bg,
            text=ICON("backup"),
            font=self._material_font(36),
            text_color=COLORS["text_tertiary"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(
            inner,
            text=self._ui("no_backups"),
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, 0))

        # Description
        ctk.CTkLabel(
            inner,
            text=self._ui("no_backups_desc"),
            font=self._font(12),
            text_color=COLORS["text_secondary"],
            justify="center",
            wraplength=320,
        ).pack(pady=(4, 12))

        # CTA Button
        add_icon = ICON("add")
        EnhancedButton.primary(
            inner,
            text=f"{add_icon}  {self._ui('create_first')}",
            height=40,
            width=180,
            font=self._font(13, "bold"),
            command=self.create_backup,
        ).pack()

    # ========================================================================
    # ERROR STATE
    # ========================================================================

    def _show_error_state(self, error: str):
        """Show error state with Material Symbols icon"""
        wrapper = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        ctk.CTkFrame(wrapper, fg_color="transparent", height=1).pack(expand=True)

        error_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        error_frame.pack()

        ctk.CTkLabel(
            error_frame,
            text=ICON("error"),
            font=self._material_font(32),
            text_color=COLORS.get("danger", "#EF4444"),
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            error_frame,
            text=self._ui("error_loading"),
            font=self._font(14, "bold"),
            text_color=COLORS.get("danger", "#EF4444"),
        ).pack()

        ctk.CTkLabel(
            error_frame,
            text=error,
            font=self._font(13),
            text_color=COLORS.get("text_muted", "#6B7280"),
            wraplength=400,
        ).pack(pady=(4, 0))

        EnhancedButton.primary(
            error_frame,
            text=self._ui("retry"),
            width=100,
            command=self.refresh_view,
        ).pack(pady=(16, 0))

        ctk.CTkFrame(wrapper, fg_color="transparent", height=1).pack(expand=True)

    # ========================================================================
    # ACTIONS (Create, Restore, Delete)
    # ========================================================================

    def create_backup(self):
        """Create new backup with dialog"""
        from gui.components.refined_dialog import show_input

        default_name = f"Backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        name = show_input(
            self.app.window,
            self._ui("create_dialog_title"),
            self._ui("create_dialog_prompt"),
            placeholder=default_name,
        )

        if name:
            try:
                self._show_loading()

                backup = self.backup_mgr.create_backup(name=name)

                self._hide_loading()

                if backup:
                    if hasattr(self.app, "toast"):
                        self.app.toast.success(
                            self._ui("backup_created", name=backup.name)
                        )
                    self.refresh_view()
                else:
                    if hasattr(self.app, "toast"):
                        self.app.toast.error(self._ui("backup_failed"))

            except PermissionError:
                self._hide_loading()
                if hasattr(self.app, "toast"):
                    self.app.toast.error(self._ui("permission_denied"))
            except Exception as e:
                self._hide_loading()
                if hasattr(self.app, "toast"):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))

    def restore_backup(self, backup):
        """Restore from backup with confirmation"""
        from gui.components.refined_dialog import show_confirmation

        if show_confirmation(
            self.app.window,
            self._ui("restore_dialog_title"),
            self._ui("restore_dialog_msg", name=backup.name),
            confirm_text=self._ui("restore"),
            risk_level="MEDIUM",
        ):
            try:
                success = self.backup_mgr.restore_registry(backup.id)
                if success:
                    if hasattr(self.app, "toast"):
                        self.app.toast.info(self._ui("restore_success"))
                else:
                    if hasattr(self.app, "toast"):
                        self.app.toast.error(self._ui("restore_failed"))
            except Exception as e:
                if hasattr(self.app, "toast"):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))

    def delete_backup(self, backup):
        """Delete backup with confirmation"""
        from gui.components.refined_dialog import show_confirmation

        if show_confirmation(
            self.app.window,
            self._ui("delete_dialog_title"),
            self._ui("delete_dialog_msg", name=backup.name),
            confirm_text=self._ui("delete"),
            risk_level="HIGH",
        ):
            try:
                success = self.backup_mgr.delete_backup(backup.id)
                if success:
                    self.refresh_view()
                    if hasattr(self.app, "toast"):
                        self.app.toast.success(self._ui("deleted_success"))
                else:
                    if hasattr(self.app, "toast"):
                        self.app.toast.error(self._ui("delete_failed"))
            except Exception as e:
                if hasattr(self.app, "toast"):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _show_loading(self):
        """Show loading state via busy cursor"""
        try:
            self.app.window.config(cursor="watch")
            self.app.window.update_idletasks()
        except Exception:
            pass

    def _hide_loading(self):
        """Restore normal cursor"""
        try:
            self.app.window.config(cursor="")
            self.app.window.update_idletasks()
        except Exception:
            pass

    # Legacy compat — old callers may use refresh_current_view()
    def refresh_current_view(self):
        """Alias for refresh_view() — backward compatibility"""
        self.refresh_view()
