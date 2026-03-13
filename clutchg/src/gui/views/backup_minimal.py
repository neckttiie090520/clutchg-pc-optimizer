"""
Backup View - Premium Design
Enhanced backup management with better empty states
Enhanced: 2026-02-02 (UX/UI Overhaul)
"""

import customtkinter as ctk
from datetime import datetime
from typing import TYPE_CHECKING

from gui.theme import COLORS, SIZES, SPACING, RADIUS
from gui.style import font
from gui.components.glass_card import GlassCard
from gui.components.enhanced_button import EnhancedButton

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class BackupView(ctk.CTkFrame):
    """Premium backup view with enhanced UI"""

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Backup",
            "create_btn": "+ Create Backup",
            "info_title": "Backup & Safety",
            "info_desc": "ClutchG automatically creates backups before applying profiles. You can also create manual backups here. Always have a backup before making system changes.",
            "empty_title": "No backups yet",
            "empty_desc": "Create a backup before applying profiles to ensure\nyou can restore your system if needed.",
            "empty_cta": "Create Your First Backup",
            "error_title": "Error loading backups",
            "restore_point": "RESTORE POINT",
            "registry": "REGISTRY",
            "created": "Created: {date}",
            "restore": "Restore",
            "delete": "Delete",
            # Dialogs
            "create_dialog_title": "Create Backup",
            "create_dialog_prompt": "Enter a name for this backup:",
            "restore_dialog_title": "Restore Backup",
            "restore_dialog_msg": "Restore from '{name}'?\n\nThis will revert system settings to the backup state.\nA restart may be required.",
            "delete_dialog_title": "Delete Backup",
            "delete_dialog_msg": "Delete '{name}'?\n\nThis action cannot be undone.",
            # Toasts
            "no_backups_hint": "No backups yet. Create one manually or apply a profile (auto-creates backup).",
            "backup_created": "Backup created: {name}",
            "backup_failed": "Failed to create backup",
            "restored_success": "Restored successfully. Restart required for full effect.",
            "restore_failed": "Restore failed",
            "deleted_success": "Backup deleted",
            "delete_failed": "Delete failed",
            "error_prefix": "Error: {msg}",
        },
        "th": {
            "title": "Backup",
            "create_btn": "+ สร้าง Backup",
            "info_title": "Backup & ความปลอดภัย",
            "info_desc": "ClutchG จะสร้าง Backup อัตโนมัติก่อนใช้ Profile คุณสามารถสร้าง Backup ด้วยตัวเองที่นี่ได้ ควรมี Backup ก่อนทำการเปลี่ยนแปลงระบบเสมอะ",
            "empty_title": "ยังไม่มี Backup",
            "empty_desc": "สร้าง Backup ก่อนใช้ Profile เพื่อให้แน่ใจว่า\nคุณจะสามารถคืนค่าระบบได้หากจำเป็น",
            "empty_cta": "สร้าง Backup ครั้งแรก",
            "error_title": "เกิดข้อผิดพลาดในการโหลด Backup",
            "restore_point": "RESTORE POINT",
            "registry": "REGISTRY",
            "created": "สร้างเมื่อ: {date}",
            "restore": "Restore",
            "delete": "ลบ",
            # Dialogs
            "create_dialog_title": "สร้าง Backup",
            "create_dialog_prompt": "ใส่ชื่อสำหรับ Backup นี้:",
            "restore_dialog_title": "Restore Backup",
            "restore_dialog_msg": "Restore จาก '{name}'?\n\nนี่จะคืนค่า Settings ระบบกลับไปสู่สถานะ Backup\nอาจต้อง Restart เครื่อง",
            "delete_dialog_title": "ลบ Backup",
            "delete_dialog_msg": "ลบ '{name}'?\n\nการกระทำนี้ไม่สามารถยกเลิกได้",
            # Toasts
            "no_backups_hint": "ยังไม่มี Backup สร้างด้วยตัวเอง หรือใช้ Profile (จะสร้างอัตโนมัติ)",
            "backup_created": "สร้าง Backup สำเร็จ: {name}",
            "backup_failed": "สร้าง Backup ไม่สำเร็จ",
            "restored_success": "Restore สำเร็จ ต้อง Restart เครื่องเพื่อให้มีผลเต็มที่",
            "restore_failed": "Restore ไม่สำเร็จ",
            "deleted_success": "ลบ Backup สำเร็จ",
            "delete_failed": "ลบ Backup ไม่สำเร็จ",
            "error_prefix": "ข้อผิดพลาด: {msg}",
        }
    }

    def __init__(self, parent, app: 'ClutchGApp'):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.create_header()

        # Info box
        self.create_info_box()

        # Backup list
        self.create_backup_list()

        # Load backups
        from core.backup_manager import BackupManager
        self.backup_mgr = BackupManager()
        self.refresh_list()

    def _ui(self, key: str, **kwargs) -> str:
        """Get UI string in current language"""
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key).format(**kwargs)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        """Choose a Thai-friendly font when needed"""
        if self.app.config.get("language") == "th":
            return ctk.CTkFont(family="Tahoma", size=size, weight=weight)
        return font("body", size=size, weight=weight)
    
    def create_header(self):
        """Create premium header with action button"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=self._ui("title"),
            font=self._font(28, "bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        # Create backup button (enhanced)
        EnhancedButton.primary(
            header,
            text=self._ui("create_btn"),
            width=140,
            command=self.create_backup
        ).grid(row=0, column=1, sticky="e")

    def create_info_box(self):
        """Create enhanced info box with GlassCard"""
        info_frame = GlassCard(
            self,
            corner_radius=RADIUS["lg"]
        )
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0, SPACING["lg"]))

        # Left accent
        accent = ctk.CTkFrame(
            info_frame,
            width=4,
            fg_color=COLORS["success"],
            corner_radius=2
        )
        accent.pack(side="left", fill="y", padx=(0, 16))

        # Content
        content = ctk.CTkFrame(info_frame, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=14, padx=(0, 16))

        # Icon + Title
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="ℹ",
            font=self._font(14),
            text_color=COLORS["success"]
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            title_frame,
            text=self._ui("info_title"),
            font=self._font(13, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        # Description
        ctk.CTkLabel(
            content,
            text=self._ui("info_desc"),
            font=self._font(11),
            text_color=COLORS["text_secondary"],
            wraplength=800,
            justify="left"
        ).pack(anchor="w", pady=(SPACING["xs"], 0))
    
    def create_backup_list(self):
        """Create backup list container"""
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"]
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
    
    def refresh_list(self):
        """Refresh backup list with enhanced cards"""
        try:
            for w in self.list_frame.winfo_children():
                w.destroy()

            backups = self.backup_mgr.get_all_backups()

            if not backups:
                self.show_empty_state()
                # Add helpful toast for first-time users
                if hasattr(self.app, 'toast'):
                    self.app.toast.info(self._ui("no_backups_hint"))
                return

            for backup in backups:
                self.create_backup_card(backup)

        except Exception as e:
            self.show_error_state(str(e))
    
    def show_empty_state(self):
        """Show beautiful empty state"""
        empty_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        empty_frame.pack(pady=80)

        # Icon container with gradient-like background
        icon_bg = ctk.CTkFrame(
            empty_frame,
            fg_color=COLORS["success_dim"],
            corner_radius=SIZES["radius_xl"],
            width=100,
            height=100
        )
        icon_bg.pack(pady=(0, 24))
        icon_bg.pack_propagate(False)

        ctk.CTkLabel(
            icon_bg,
            text="💾",
            font=self._font(42, "bold")
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(
            empty_frame,
            text=self._ui("empty_title"),
            font=self._font(18, "bold"),
            text_color=COLORS["text_primary"]
        ).pack()

        # Description
        ctk.CTkLabel(
            empty_frame,
            text=self._ui("empty_desc"),
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            justify="center"
        ).pack(pady=(8, 24))

        # CTA Button
        EnhancedButton.primary(
            empty_frame,
            text=self._ui("empty_cta"),
            height=44,
            width=200,
            command=self.create_backup
        ).pack()

    def show_error_state(self, error: str):
        """Show error state"""
        error_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        error_frame.pack(pady=60)

        ctk.CTkLabel(
            error_frame,
            text="❌",
            font=self._font(32, "bold")
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            error_frame,
            text=self._ui("error_title"),
            font=self._font(14, "bold"),
            text_color=COLORS["danger"]
        ).pack()

        ctk.CTkLabel(
            error_frame,
            text=error,
            font=self._font(12),
            text_color=COLORS["text_muted"]
        ).pack(pady=(4, 0))
    
    def create_backup_card(self, backup):
        """Create enhanced backup card with GlassCard"""
        card = GlassCard(
            self.list_frame,
            corner_radius=RADIUS["lg"],
            glow_color=COLORS["success"] if backup.has_restore_point else COLORS["warning"]
        )
        card.configure(height=80)
        card.pack(fill="x", pady=SPACING["xs"])
        card.pack_propagate(False)
        card.grid_columnconfigure(2, weight=1)
        
        # Left indicator
        indicator_color = COLORS["success"] if backup.has_restore_point else COLORS["warning"]
        indicator = ctk.CTkFrame(
            card,
            width=4,
            fg_color=indicator_color,
            corner_radius=2
        )
        indicator.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 16))
        
        # Icon with status
        icon_frame = ctk.CTkFrame(
            card,
            fg_color=COLORS["bg_hover"],
            corner_radius=SIZES["radius_md"],
            width=44,
            height=44
        )
        icon_frame.grid(row=0, column=1, rowspan=2, padx=(0, 16), pady=18)
        icon_frame.pack_propagate(False)
        
        icon = "✓" if backup.has_restore_point else "◉"
        icon_color = COLORS["success"] if backup.has_restore_point else COLORS["warning"]
        
        ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=font("body", size=18),
            text_color=icon_color
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Backup info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", pady=16)
        
        # Name row
        name_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_row.pack(anchor="w", fill="x")
        
        ctk.CTkLabel(
            name_row,
            text=backup.name,
            font=self._font(14, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        # Status badges
        if backup.has_restore_point:
            badge = ctk.CTkLabel(
                name_row,
                text=self._ui("restore_point"),
                font=self._font(9, "bold"),
                text_color=COLORS["success"],
                fg_color=COLORS["success_dim"],
                corner_radius=SIZES["radius_sm"]
            )
            badge.pack(side="left", padx=(10, 0))

        if backup.has_registry_backup:
            badge = ctk.CTkLabel(
                name_row,
                text=self._ui("registry"),
                font=self._font(9, "bold"),
                text_color=COLORS["accent"],
                fg_color=COLORS["accent_dim"],
                corner_radius=SIZES["radius_sm"]
            )
            badge.pack(side="left", padx=(6, 0))

        # Date
        try:
            dt = datetime.fromisoformat(backup.created_at)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_str = backup.created_at

        ctk.CTkLabel(
            info_frame,
            text=self._ui("created", date=date_str),
            font=self._font(11),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(4, 0))

        # Actions
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=3, rowspan=2, padx=16)

        # Restore button (if available)
        if backup.has_registry_backup:
            EnhancedButton.success(
                actions,
                text=self._ui("restore"),
                width=70,
                command=lambda b=backup: self.restore_backup(b)
            ).pack(side="left", padx=(0, SPACING["xs"]))

        # Delete button
        EnhancedButton.danger(
            actions,
            text=self._ui("delete"),
            width=70,
            command=lambda b=backup: self.delete_backup(b)
        ).pack(side="left")
    
    def create_backup(self):
        """Create new backup with enhanced dialog"""
        import tkinter.simpledialog as sd

        default_name = f"Backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        name = sd.askstring(
            self._ui("create_dialog_title"),
            self._ui("create_dialog_prompt"),
            initialvalue=default_name
        )

        if name:
            try:
                backup = self.backup_mgr.create_backup(name=name)
                if backup:
                    if hasattr(self.app, 'toast'):
                        self.app.toast.success(self._ui("backup_created", name=backup.name))
                    self.refresh_list()
                else:
                    if hasattr(self.app, 'toast'):
                        self.app.toast.error(self._ui("backup_failed"))
            except Exception as e:
                if hasattr(self.app, 'toast'):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))

    def restore_backup(self, backup):
        """Restore backup with confirmation"""
        import tkinter.messagebox as mb

        if mb.askyesno(
            self._ui("restore_dialog_title"),
            self._ui("restore_dialog_msg", name=backup.name)
        ):
            try:
                success = self.backup_mgr.restore_registry(backup.id)
                if success:
                    if hasattr(self.app, 'toast'):
                        self.app.toast.info(self._ui("restored_success"))
                else:
                    if hasattr(self.app, 'toast'):
                        self.app.toast.error(self._ui("restore_failed"))
            except Exception as e:
                if hasattr(self.app, 'toast'):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))

    def delete_backup(self, backup):
        """Delete backup with confirmation"""
        import tkinter.messagebox as mb

        if mb.askyesno(
            self._ui("delete_dialog_title"),
            self._ui("delete_dialog_msg", name=backup.name)
        ):
            try:
                success = self.backup_mgr.delete_backup(backup.id)
                if success:
                    self.refresh_list()
                    if hasattr(self.app, 'toast'):
                        self.app.toast.success(self._ui("deleted_success"))
                else:
                    if hasattr(self.app, 'toast'):
                        self.app.toast.error(self._ui("delete_failed"))
            except Exception as e:
                if hasattr(self.app, 'toast'):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))
