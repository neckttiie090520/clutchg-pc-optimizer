"""
Backup & Restore Center - Unified View
Combines simple backup management with advanced timeline visualization
Phase 1.2 - Unified backup/restore experience
"""

import customtkinter as ctk
from datetime import datetime
from typing import TYPE_CHECKING

from gui.theme import COLORS, SIZES, SPACING, RADIUS, ICON, ICON_FONT
from gui.style import font
from gui.components.glass_card import GlassCard
from gui.components.enhanced_button import EnhancedButton

if TYPE_CHECKING:
    from app_minimal import ClutchGApp


class BackupRestoreCenter(ctk.CTkFrame):
    """
    Unified Backup & Restore Center with two modes:
    - Simple Mode: List view of backups (using BackupManager)
    - Advanced Mode: Timeline visualization (using FlightRecorder)
    """

    # Localization strings (EN/TH)
    UI_STRINGS = {
        "en": {
            "title": "Backup & Restore",
            "subtitle": "Manage system backups and restore points",
            "simple": "Simple",
            "advanced": "Advanced",
            "create_backup": "New Backup",
            "restore_point": "RESTORE POINT",
            "registry": "REGISTRY",
            "created": "Created: {date}",
            "restore": "Restore",
            "delete": "Delete",
            "no_backups": "No backups yet",
            "no_backups_desc": "Create one before applying any tweaks.\nTakes a few seconds, saves hours of pain.",
            "create_first": "Create Backup",
            "backup_safety_hint": "Create backups before applying tweaks for safety.",
            "no_timeline": "No timeline history yet",
            "no_timeline_desc": "Apply profiles to see history here",
            "go_to_optimization": "Go to Tweaks",
            "changes": "{count} changes",
            "system_snapshot": "System snapshot",
            "snapshot_details": "Snapshot Details",
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
            "advanced_unavailable": "Advanced mode requires FlightRecorder - using simple mode",
            "snapshot_error": "Error loading snapshot: {msg}",
            "timeline_error": "Timeline component not available: {msg}",
            "timeline_load_error": "Error loading timeline: {msg}",
        },
        "th": {
            "title": "Backup & Restore",
            "subtitle": "จัดการ Backup และจุด Restore ของระบบ",
            "simple": "Simple",
            "advanced": "Advanced",
            "create_backup": "Backup ใหม่",
            "restore_point": "RESTORE POINT",
            "registry": "REGISTRY",
            "created": "สร้างเมื่อ: {date}",
            "restore": "Restore",
            "delete": "ลบ",
            "no_backups": "ยังไม่มี Backup",
            "no_backups_desc": "สร้าง Backup ก่อนใช้ Tweaks\nใช้เวลาไม่กี่วินาที แต่ช่วยประหยัดเวลาได้มาก",
            "create_first": "สร้าง Backup",
            "backup_safety_hint": "สร้าง Backup ก่อนใช้งาน Tweaks เพื่อความปลอดภัย",
            "no_timeline": "ยังไม่มีประวัติ Timeline",
            "no_timeline_desc": "ใช้ Profile เพื่อดูประวัติที่นี่",
            "go_to_optimization": "ไปที่ Tweaks",
            "changes": "{count} การเปลี่ยนแปลง",
            "system_snapshot": "สแนปชอตระบบ",
            "snapshot_details": "รายละเอียดสแนปชอต",
            "error_loading": "เกิดข้อผิดพลาดในการโหลดข้อมูล",
            "retry": "ลองใหม่",
            "loading": "กำลังโหลด...",
            # Dialogs
            "create_dialog_title": "Backup ใหม่",
            "create_dialog_prompt": "ใส่ชื่อสำหรับ Backup นี้:",
            "restore_dialog_title": "Restore Backup",
            "restore_dialog_msg": "Restore จาก '{name}'?\n\nนี่จะคืนค่า Settings ระบบกลับไปสู่สถานะ Backup\nอาจต้อง Restart เครื่อง",
            "delete_dialog_title": "ลบ Backup",
            "delete_dialog_msg": "ลบ '{name}'?\n\nการกระทำนี้ไม่สามารถยกเลิกได้",
            # Toasts
            "backup_created": "สร้าง Backup สำเร็จ: {name}",
            "backup_failed": "สร้าง Backup ไม่สำเร็จ",
            "restore_success": "Restore สำเร็จ ต้อง Restart เครื่องเพื่อให้มีผลเต็มที่",
            "restore_failed": "Restore ไม่สำเร็จ",
            "deleted_success": "ลบ Backup สำเร็จ",
            "delete_failed": "ลบ Backup ไม่สำเร็จ",
            "error_prefix": "ข้อผิดพลาด: {msg}",
            "permission_denied": "ปฏิเสธการเข้าถึง รันเป็น Administrator",
            "advanced_unavailable": "โหมด Advanced ต้องการ FlightRecorder - ใช้โหมด Simple",
            "snapshot_error": "ข้อผิดพลาดในการโหลดสแนปชอต: {msg}",
            "timeline_error": "Timeline component ไม่พร้อมใช้งาน: {msg}",
            "timeline_load_error": "ข้อผิดพลาดในการโหลด Timeline: {msg}",
        },
    }

    def __init__(self, parent, app: "ClutchGApp"):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # State
        self.current_mode = "simple"  # "simple" or "advanced"
        self._init_error = None

        # Initialize managers (wrapped to prevent blank page on failure)
        try:
            from core.backup_manager import BackupManager

            self.backup_mgr = BackupManager()
        except Exception as e:
            print(f"[Backup] ERROR initializing BackupManager: {e}")
            import traceback

            traceback.print_exc()
            self.backup_mgr = None
            self._init_error = str(e)

        # FlightRecorder (for advanced mode)
        try:
            from core.flight_recorder import get_flight_recorder

            self.flight_recorder = get_flight_recorder()
            self.flight_recorder_available = True
        except Exception as e:
            print(f"Warning: FlightRecorder not available: {e}")
            self.flight_recorder = None
            self.flight_recorder_available = False

        # Build UI (always runs, even if managers failed)
        self.create_header()
        self.create_content()

        # Load initial data
        self.refresh_current_view()

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

    def create_header(self):
        """Create header with title, mode toggle, and actions"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["xl"]))
        header.grid_columnconfigure(1, weight=1)

        # Left: Title + Subtitle
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left_frame,
            text=self._ui("title"),
            font=self._font(20, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_frame,
            text=self._ui("subtitle"),
            font=self._font(11),
            text_color=COLORS["text_tertiary"],
        ).pack(anchor="w", pady=(2, 0))

        # Center: Mode Toggle (Segmented Button)
        # Center: Mode Toggle (Custom Buttons for Contrast)
        toggle_container = ctk.CTkFrame(header, fg_color="transparent")
        toggle_container.grid(row=0, column=1, sticky="ew", padx=SPACING["lg"])
        toggle_container.grid_columnconfigure(0, weight=1)
        toggle_container.grid_columnconfigure(1, weight=1)

        self.mode_buttons = {}
        modes = [("simple", self._ui("simple")), ("advanced", self._ui("advanced"))]

        for i, (mode_key, mode_label) in enumerate(modes):
            is_active = mode_key == self.current_mode

            btn = ctk.CTkButton(
                toggle_container,
                text=mode_label,
                font=self._font(13, "bold" if is_active else "normal"),
                fg_color=COLORS["accent"] if is_active else COLORS["bg_tertiary"],
                text_color=COLORS.get("text_on_accent", "#FFFFFF")
                if is_active
                else COLORS["text_secondary"],
                hover_color=COLORS["accent_hover"] if is_active else COLORS["bg_hover"],
                corner_radius=RADIUS["md"],
                height=32,
                command=lambda m=mode_label: self.switch_mode(m),
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
            self.mode_buttons[mode_label] = btn

        header.grid_columnconfigure(1, weight=1)

        # Right: Actions
        actions_frame = ctk.CTkFrame(header, fg_color="transparent")
        actions_frame.grid(row=0, column=2, sticky="e")

        # Create Backup Button
        EnhancedButton.primary(
            actions_frame,
            text=f"{ICON('add')} {self._ui('create_backup')}",
            width=140,
            height=36,
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=13, weight="bold"),
            command=self.create_backup,
        ).pack(side="left")

        # Help Button
        help_btn = ctk.CTkButton(
            actions_frame,
            text=ICON("help"),
            width=36,
            height=36,
            font=ctk.CTkFont(
                family="Segoe MDL2 Assets",
                size=16,
            ),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            corner_radius=RADIUS["md"],
            command=lambda: (
                self.app.switch_view("help")
                if hasattr(self.app, "switch_view")
                else None
            ),
        )
        help_btn.pack(side="left", padx=(SPACING["sm"], 0))

    def create_content(self):
        """Create content area that switches between modes"""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Simple Mode Container (Initial)
        self.simple_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.simple_container.grid(row=0, column=0, sticky="nsew")
        self.simple_container.grid_columnconfigure(0, weight=1)
        self.simple_container.grid_rowconfigure(0, weight=1)

        # Advanced Mode Container (Hidden initially)
        self.advanced_container = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )
        # Don't grid yet, will show when switched

    # ========================================================================
    # MODE SWITCHING
    # ========================================================================

    def switch_mode(self, selected_mode: str):
        """Switch between Simple and Advanced mode"""
        new_mode = "simple" if selected_mode == self._ui("simple") else "advanced"

        if new_mode == self.current_mode:
            return  # Already in this mode

        self.current_mode = new_mode

        # Hide all containers
        self.simple_container.grid_forget()
        self.advanced_container.grid_forget()

        # Show appropriate container
        if new_mode == "simple":
            self.simple_container.grid(row=0, column=0, sticky="nsew")
            self.refresh_simple_mode()
        else:
            if not self.flight_recorder_available:
                # Show warning if FlightRecorder not available
                if hasattr(self.app, "toast"):
                    self.app.toast.warning(self._ui("advanced_unavailable"))
                self.current_mode = "simple"
                self.simple_container.grid(row=0, column=0, sticky="nsew")
                self.refresh_simple_mode()
                self._update_toggle_buttons()
                return

            self.advanced_container.grid(row=0, column=0, sticky="nsew")
            self.refresh_advanced_mode()

        # Update button visuals
        self._update_toggle_buttons()

    def _update_toggle_buttons(self):
        """Update toggle button visual states"""
        simple_label = self._ui("simple")
        advanced_label = self._ui("advanced")

        # Helper to get button if exists
        def get_btn(label):
            return self.mode_buttons.get(label)

        for label, btn in self.mode_buttons.items():
            if not btn:
                continue

            # Determine if this button corresponds to current mode
            is_active = False
            if self.current_mode == "simple" and label == simple_label:
                is_active = True
            elif self.current_mode == "advanced" and label == advanced_label:
                is_active = True

            btn.configure(
                font=self._font(13, "bold" if is_active else "normal"),
                fg_color=COLORS["accent"] if is_active else COLORS["bg_tertiary"],
                text_color=COLORS.get("text_on_accent", "#FFFFFF")
                if is_active
                else COLORS["text_secondary"],
                hover_color=COLORS["accent_hover"] if is_active else COLORS["bg_hover"],
            )

    def refresh_current_view(self):
        """Refresh the current view based on mode"""
        if self.current_mode == "simple":
            self.refresh_simple_mode()
        else:
            self.refresh_advanced_mode()

    # ========================================================================
    # SIMPLE MODE (Backup List)
    # ========================================================================

    def refresh_simple_mode(self):
        """Refresh simple mode - show backup list"""
        # Clear simple container
        for widget in self.simple_container.winfo_children():
            widget.destroy()

        # Check if BackupManager initialization failed
        if self.backup_mgr is None:
            print(f"[Backup] BackupManager not available: {self._init_error}")
            self.show_error_state(
                f"Backup system unavailable: {self._init_error or 'Unknown error'}"
            )
            return

        try:
            print("[Backup] Loading backups...")
            backups = self.backup_mgr.get_all_backups()
            print(f"[Backup] Found {len(backups)} backup(s)")

            if not backups:
                print("[Backup] No backups found, showing empty state")
                self.show_simple_empty_state()
                return

            print("[Backup] Showing backup list")
            self.show_backup_list(backups)

        except Exception as e:
            print(f"[Backup] Error loading backups: {str(e)}")
            import traceback

            traceback.print_exc()
            self.show_error_state(f"Error loading backups: {str(e)}")

    def show_backup_list(self, backups):
        """Show list of backups as cards"""
        # Scrollable list
        scroll_frame = ctk.CTkScrollableFrame(
            self.simple_container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        scroll_frame.pack(fill="both", expand=True)
        scroll_frame.grid_columnconfigure(0, weight=1)

        for backup in backups:
            self.create_backup_card(scroll_frame, backup)

        # Hint text below list (LOW-04)
        ctk.CTkLabel(
            scroll_frame,
            text=self._ui("backup_safety_hint"),
            font=self._font(11),
            text_color=COLORS["text_muted"],
            justify="center",
        ).pack(pady=(SPACING["md"], SPACING["xs"]))

    def create_backup_card(self, parent, backup):
        """Create a backup card (from backup_minimal.py)"""
        from gui.theme import get_score_color

        card = GlassCard(
            parent,
            corner_radius=RADIUS["lg"],
        )
        card.pack(fill="x", pady=SPACING["xs"])
        card.grid_columnconfigure(1, weight=1)

        # Icon with status
        icon_frame = ctk.CTkFrame(
            card,
            fg_color=COLORS["bg_hover"],
            corner_radius=SIZES["radius_md"],
            width=44,
            height=44,
        )
        icon_frame.grid(row=0, column=0, rowspan=2, padx=(16, 16), pady=18)
        icon_frame.pack_propagate(False)

        # Use IconProvider for icons
        icon = ICON("check_circle") if backup.has_restore_point else ICON("inventory_2")
        icon_color = (
            COLORS["success"] if backup.has_restore_point else COLORS["text_tertiary"]
        )

        ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=18),
            text_color=icon_color,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Backup info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", pady=16)

        # Name row
        name_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_row.pack(anchor="w", fill="x")

        ctk.CTkLabel(
            name_row,
            text=backup.name,
            font=self._font(14, "bold"),
            text_color=COLORS["text_primary"],
            wraplength=300,
        ).pack(side="left")

        # Status badges
        if backup.has_restore_point:
            badge = ctk.CTkLabel(
                name_row,
                text=self._ui("restore_point"),
                font=self._font(9, "bold"),
                text_color=COLORS["success"],
                fg_color=COLORS["success_dim"],
                corner_radius=SIZES["radius_sm"],
            )
            badge.pack(side="left", padx=(10, 0))

        if backup.has_registry_backup:
            badge = ctk.CTkLabel(
                name_row,
                text=self._ui("registry"),
                font=self._font(9, "bold"),
                text_color=COLORS["accent"],
                fg_color=COLORS["accent_dim"],
                corner_radius=SIZES["radius_sm"],
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
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        # Actions
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=16)

        # Restore button (if available)
        if backup.has_registry_backup:
            EnhancedButton.success(
                actions,
                text=self._ui("restore"),
                width=70,
                height=32,
                command=lambda b=backup: self.restore_backup(b),
            ).pack(side="left", padx=(0, SPACING["xs"]))

        # Delete button
        EnhancedButton.danger(
            actions,
            text=self._ui("delete"),
            width=70,
            height=32,
            command=lambda b=backup: self.delete_backup(b),
        ).pack(side="left")

    def show_simple_empty_state(self):
        """Show empty state for simple mode"""
        print("[Backup] Creating empty state UI...")
        # Use pack with expand=True + anchor=center for vertical centering
        empty_frame = ctk.CTkFrame(self.simple_container, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True)

        # Vertical spacer for centering
        ctk.CTkFrame(empty_frame, fg_color="transparent", height=1).pack(expand=True)

        # Icon container
        icon_bg = ctk.CTkFrame(
            empty_frame,
            fg_color=COLORS.get("bg_hover", "#333333"),
            corner_radius=SIZES.get("radius_xl", 16),
            width=100,
            height=100,
        )
        icon_bg.pack(pady=(0, 24))
        icon_bg.pack_propagate(False)

        # Center the icon
        icon_label = ctk.CTkLabel(
            icon_bg,
            text=ICON("backup"),
            font=ctk.CTkFont(
                family="Segoe MDL2 Assets",
                size=42,
                weight="bold",
            ),
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(
            empty_frame,
            text=self._ui("no_backups"),
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack()

        # Description
        ctk.CTkLabel(
            empty_frame,
            text=self._ui("no_backups_desc"),
            font=self._font(13),
            text_color=COLORS["text_secondary"],
            justify="center",
        ).pack(pady=(8, 24))

        # CTA Button
        EnhancedButton.primary(
            empty_frame,
            text=f"{ICON('add')} {self._ui('create_first')}",
            height=44,
            width=200,
            font=ctk.CTkFont(family="Segoe MDL2 Assets", size=13, weight="bold"),
            command=self.create_backup,
        ).pack()

        # Bottom spacer for centering
        ctk.CTkFrame(empty_frame, fg_color="transparent", height=1).pack(expand=True)
        print("[Backup] Empty state UI created successfully")

    # ========================================================================
    # ADVANCED MODE (Timeline)
    # ========================================================================

    def refresh_advanced_mode(self):
        """Refresh advanced mode - show timeline"""
        # Clear advanced container
        for widget in self.advanced_container.winfo_children():
            widget.destroy()

        try:
            from gui.components.timeline import Timeline, TimelineNode

            # Create timeline
            self.timeline = Timeline(
                self.advanced_container,
                self.app,
                on_node_click=self.on_timeline_node_clicked,
            )
            self.timeline.pack(fill="both", expand=True)

            # Load snapshots
            self.load_timeline_data()

        except ImportError as e:
            # Timeline component not available
            self.show_error_state(f"Timeline component not available: {str(e)}")
        except Exception as e:
            self.show_error_state(f"Error loading timeline: {str(e)}")

    def load_timeline_data(self):
        """Load snapshots from FlightRecorder and populate timeline"""
        if not self.flight_recorder:
            return

        try:
            snapshots = self.flight_recorder.list_snapshots(limit=50)
            nodes = []

            for snapshot in snapshots:
                # Determine node type
                node_type = "manual"
                if snapshot.operation_type == "profile_applied":
                    node_type = "profile_applied"
                elif "restore" in snapshot.operation_type.lower():
                    node_type = "restore"

                node = TimelineNode(
                    id=snapshot.snapshot_id,
                    timestamp=snapshot.timestamp,
                    title=snapshot.profile,
                    description=self._ui("changes", count=len(snapshot.tweaks))
                    if snapshot.tweaks
                    else self._ui("system_snapshot"),
                    node_type=node_type,
                    status="success" if snapshot.success else "error",
                    metadata={"snapshot_id": snapshot.snapshot_id},
                )
                nodes.append(node)

            if nodes and hasattr(self.timeline, "set_nodes"):
                self.timeline.set_nodes(nodes)
            else:
                self.show_timeline_empty_state()

        except Exception as e:
            print(f"Error loading timeline data: {e}")
            self.show_timeline_empty_state()

    def on_timeline_node_clicked(self, node):
        """Handle timeline node click - show snapshot details"""
        snapshot_id = node.metadata.get("snapshot_id")
        if snapshot_id and self.flight_recorder:
            try:
                snapshot = self.flight_recorder.get_snapshot(snapshot_id)
                if snapshot:
                    self.show_snapshot_details(snapshot)
            except Exception as e:
                if hasattr(self.app, "toast"):
                    self.app.toast.error(self._ui("snapshot_error", msg=str(e)))

    def show_snapshot_details(self, snapshot):
        """Show snapshot details in a dialog"""

        details = f"Profile: {snapshot.profile}\n"
        details += f"Date: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        details += f"Status: {'Success' if snapshot.success else 'Failed'}\n"
        details += f"Changes: {len(snapshot.tweaks)}\n\n"

        if snapshot.tweaks:
            details += "Changes Applied:\n"
            for tweak in snapshot.tweaks[:10]:  # Show first 10
                details += f"  - {tweak.name}: {tweak.old_value} -> {tweak.new_value}\n"

            if len(snapshot.tweaks) > 10:
                details += f"  ... and {len(snapshot.tweaks) - 10} more\n"

        from gui.components.refined_dialog import show_info

        show_info(self.app.window, self._ui("snapshot_details"), details)

    def show_timeline_empty_state(self):
        """Show empty state for timeline"""
        # Use pack with expand for proper centering
        wrapper = ctk.CTkFrame(self.advanced_container, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        ctk.CTkFrame(wrapper, fg_color="transparent", height=1).pack(expand=True)

        empty_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        empty_frame.pack()

        ctk.CTkLabel(
            empty_frame,
            text=ICON("history"),
            font=ctk.CTkFont(
                family="Segoe MDL2 Assets",
                size=48,
            ),
            text_color=COLORS["text_tertiary"],
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            empty_frame,
            text=self._ui("no_timeline"),
            font=self._font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack()

        ctk.CTkLabel(
            empty_frame,
            text=self._ui("no_timeline_desc"),
            font=self._font(13),
            text_color=COLORS["text_secondary"],
        ).pack()

        EnhancedButton.primary(
            empty_frame,
            text=self._ui("go_to_optimization"),
            height=40,
            width=220,
            command=lambda: self.app.switch_view("scripts"),
        ).pack(pady=(16, 0))

        ctk.CTkFrame(wrapper, fg_color="transparent", height=1).pack(expand=True)

    # ========================================================================
    # ACTIONS (Create, Restore, Delete)
    # ========================================================================

    def create_backup(self):
        """Create new backup with dialog"""
        from gui.components.refined_dialog import show_input, show_info

        default_name = f"Backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        name = show_input(
            self.app.window,
            self._ui("create_dialog_title"),
            self._ui("create_dialog_prompt"),
            placeholder=default_name,
        )

        if name:
            try:
                self._show_loading(self._ui("loading"))

                backup = self.backup_mgr.create_backup(name=name)

                self._hide_loading()

                if backup:
                    if hasattr(self.app, "toast"):
                        self.app.toast.success(
                            self._ui("backup_created", name=backup.name)
                        )
                    self.refresh_current_view()
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
                    self.refresh_current_view()
                    if hasattr(self.app, "toast"):
                        self.app.toast.success(self._ui("deleted_success"))
                else:
                    if hasattr(self.app, "toast"):
                        self.app.toast.error(self._ui("delete_failed"))
            except Exception as e:
                if hasattr(self.app, "toast"):
                    self.app.toast.error(self._ui("error_prefix", msg=str(e)))

    # ========================================================================
    # ERROR STATES & HELPERS
    # ========================================================================

    def show_error_state(self, error: str):
        """Show error state (shared between modes)"""
        # Determine which container to show error in
        container = (
            self.simple_container
            if self.current_mode == "simple"
            else self.advanced_container
        )

        # Clear container
        for widget in container.winfo_children():
            widget.destroy()

        # Use pack with expand for proper centering (not .place())
        wrapper = ctk.CTkFrame(container, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        ctk.CTkFrame(wrapper, fg_color="transparent", height=1).pack(expand=True)

        error_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        error_frame.pack()

        ctk.CTkLabel(
            error_frame,
            text=ICON("error"),
            font=ctk.CTkFont(
                family="Segoe MDL2 Assets",
                size=32,
                weight="bold",
            ),
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

        # Retry button
        EnhancedButton.primary(
            error_frame,
            text=self._ui("retry"),
            width=100,
            command=self.refresh_current_view,
        ).pack(pady=(16, 0))

        ctk.CTkFrame(wrapper, fg_color="transparent", height=1).pack(expand=True)

    def _show_loading(self, message: str = None):
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

    def _check_icon_font(self) -> bool:
        """Check if icon font is available"""
        try:
            font_family = ICON_FONT()[0]
            return "Material" in font_family or "Segoe" in font_family
        except Exception:
            return False
