"""
ClutchG Application - Windows 11 Dark UI
Main controller with multi-theme system and smooth transitions
Updated: 2026-02-03 (Redesign)
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional
from core.paths import assets_dir, batch_scripts_dir
from gui.theme import theme_manager
from core.config import ConfigManager
from core.system_info import SystemDetector
from utils.logger import get_logger

logger = get_logger(__name__)


class ClutchGApp:
    def __init__(self, test_mode: bool = False, config_path: Optional[str] = None):
        config_dir = Path(config_path) if config_path else None
        self.config_manager = ConfigManager(config_dir)
        self.config = self.config_manager.load_config()
        self.test_mode = test_mode
        self.system_detector = SystemDetector()

        # Init Theme Manager
        saved_theme = self.config.get("theme", "modern")
        saved_accent = self.config.get("accent", "sunvalley")
        theme_manager.set_theme(saved_theme, saved_accent)

        # Init Managers
        self.batch_scripts_dir = batch_scripts_dir()
        from core.profile_manager import ProfileManager
        from core.help_manager import HelpManager
        from core.action_catalog import ActionCatalog

        self.profile_manager = ProfileManager(self.batch_scripts_dir)
        self.help_manager = HelpManager()
        self.action_catalog_errors = []
        self.action_catalog = None
        try:
            self.action_catalog = ActionCatalog()
            self.action_catalog_errors = self.action_catalog.validate()
        except Exception as exc:
            self.action_catalog_errors = [f"Catalog initialization error: {exc}"]

        # UI Setup
        self.window = ctk.CTk()
        self.window.title("ClutchG")
        self.window.geometry("1000x700")
        self.window.minsize(900, 600)  # Minimum window size to prevent layout breaks

        # Load bundled fonts (requires Tk root to exist)
        from gui.font_loader import register_fonts, is_font_available

        register_fonts()

        # Set window icon (taskbar + title bar)
        # Prefer .ico via iconbitmap() — most reliable on Windows frozen builds.
        # Fall back to iconphoto() with PNG if .ico not available.
        ico_path = assets_dir() / "icon.ico"
        png_path = assets_dir() / "icon.png"
        if ico_path.exists():
            try:
                self.window.iconbitmap(str(ico_path))
            except Exception:
                logger.debug("iconbitmap failed, trying iconphoto")
                self._set_icon_photo(png_path)
        elif png_path.exists():
            self._set_icon_photo(png_path)

        self._refresh_window_colors()

        # Check Tabler Icons font availability (after window exists)
        self.tabler_icons_available = self._check_tabler_icons()

        # State
        self.current_view = None
        self.active_nav = "dashboard"

        self.detect_system()
        self.setup_ui()

        from gui.components.toast import ToastManager

        self.toast = ToastManager(self.window)

        if self.action_catalog_errors:
            self.toast.warning(
                f"Quick Actions catalog has {len(self.action_catalog_errors)} issue(s). "
                "Quick Actions will be in safe mode."
            )

        # Show font warning if needed
        if not self.tabler_icons_available:
            self._show_font_warning()

        # Auto-update check (non-blocking, respects cooldown + opt-out)
        self._init_update_checker()

    def get_version(self) -> str:
        from __init__ import __version__

        return __version__

    # ------------------------------------------------------------------
    # Auto-update
    # ------------------------------------------------------------------

    def _init_update_checker(self):
        """Start a non-blocking update check (respects cooldown + opt-out)."""
        try:
            from core.updater import AsyncUpdateChecker

            self._async_updater = AsyncUpdateChecker(
                self.window, self.get_version(), self.config_manager
            )
            self._async_updater.check_async(
                on_update_available=self._show_update_dialog
            )
        except Exception as e:
            logger.debug(f"Update checker init skipped: {e}")

    def _show_update_dialog(self, info):
        """Show the update notification dialog on the main thread."""
        try:
            from gui.components.update_dialog import UpdateDialog

            UpdateDialog(self.window, self, info)
        except Exception as e:
            logger.debug(f"Could not show update dialog: {e}")

    def _set_icon_photo(self, png_path: Path) -> None:
        """Set window icon using iconphoto() with a PNG file."""
        try:
            from PIL import Image, ImageTk

            icon_img = Image.open(png_path)
            self._icon_photo = ImageTk.PhotoImage(icon_img.resize((32, 32)))
            self.window.iconphoto(False, self._icon_photo)
        except Exception:
            logger.debug("Could not set window icon via iconphoto")

    def _check_tabler_icons(self) -> bool:
        """Check if Tabler Icons font is available (bundled or system)."""
        from gui.font_loader import is_font_available

        if is_font_available("Tabler Icons"):
            return True
        # Fallback: try creating a CTkLabel (catches system-installed font)
        try:
            test_label = ctk.CTkLabel(
                self.window,
                text="\uea38",
                font=ctk.CTkFont(family="Tabler Icons", size=12),
            )
            test_label.destroy()
            return True
        except Exception:
            return False

    def _show_font_warning(self):
        """Show non-blocking warning about missing Tabler Icons font"""
        logger.warning(
            "Tabler Icons font not available — icons may display as boxes. "
            "The font should have been bundled; check tkextrafont installation."
        )
        if hasattr(self, "toast"):
            self.toast.warning(
                "Icon font not loaded — icons may show as boxes. "
                "Ensure tkextrafont is installed: pip install tkextrafont"
            )

    def _refresh_window_colors(self):
        """Refresh window colors from current theme"""
        colors = theme_manager.get_colors()
        self.window.configure(fg_color=colors["bg_primary"])

    def detect_system(self):
        """Start async detection"""
        import threading

        self.system_profile = None
        # Run in background to prevent UI freeze on startup
        threading.Thread(target=self._run_detection, daemon=True).start()

    def _run_detection(self):
        """Worker thread for system detection"""
        try:
            profile = self.system_detector.detect_all()
            # Schedule UI update on main thread
            self.window.after(0, lambda: self._on_detection_complete(profile))
        except Exception as e:
            logger.error(f"Detection error: {e}")
            self.window.after(0, lambda: self._on_detection_complete(None))

    def _on_detection_complete(self, profile):
        """Handle detection completion on main thread"""
        self.system_profile = profile
        logger.info(
            f"System detection complete. Score: {profile.total_score if profile else 'N/A'}"
        )

        # Refresh dashboard if currently active to show new data
        if self.active_nav == "dashboard":
            self.refresh_current_view()

            # Show toast if available
            if hasattr(self, "toast"):
                self.toast.info("System scan complete")

    def setup_ui(self):
        """Setup UI with enhanced sidebar and view transitions"""
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

        # Enhanced Sidebar
        from gui.components.enhanced_sidebar import EnhancedSidebar

        self.sidebar = EnhancedSidebar(self.window, self)
        # column 0 must NOT have weight — its width is driven solely by the sidebar widget
        self.window.grid_columnconfigure(
            0, weight=0, minsize=self.sidebar.width_collapsed
        )
        self.sidebar.grid(
            row=0, column=0, sticky="ns"
        )  # ns only — do NOT stretch horizontally
        self.sidebar.grid_propagate(False)  # Children must not override sidebar width

        # Main Area
        colors = theme_manager.get_colors()
        self.main_frame = ctk.CTkFrame(
            self.window, corner_radius=0, fg_color=colors["bg_primary"]
        )
        self.main_frame.grid(
            row=0, column=1, sticky="nsew", padx=(12, 16), pady=(12, 16)
        )
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Initialize View Transition Manager
        from gui.components.view_transition import ViewTransition

        self.view_transition = ViewTransition(self.main_frame, self)

        # Load initial view (immediate, no animation)
        self.switch_view("dashboard", immediate=True)

    def switch_view(self, name, immediate=False):
        """
        Switch to a view with smooth transition

        Args:
            name: View name (e.g., "dashboard", "profiles")
            immediate: If True, skip transition animation
        """
        # Update active nav state
        self.active_nav = name

        # Update sidebar active state
        if hasattr(self.sidebar, "update_active_state"):
            self.sidebar.update_active_state(name)

        # Use view transition or immediate switch
        if immediate:
            self.view_transition.immediate_transition(self._create_view)
        else:
            self.view_transition.transition_to(self._create_view)

    def _create_view(self):
        """Create and return view instance based on active_nav"""
        name = self.active_nav

        if name == "dashboard":
            from gui.views.dashboard_minimal import DashboardView

            return DashboardView(self.main_frame, self)
        elif name == "profiles":
            from gui.views.profiles_minimal import ProfilesView

            return ProfilesView(self.main_frame, self)
        elif name == "scripts":
            from gui.views.scripts_minimal import ScriptsView

            return ScriptsView(self.main_frame, self)
        elif name == "backup":
            # Unified Backup & Restore Center (Phase 1.2)
            from gui.views.backup_restore_center import BackupRestoreCenter

            return BackupRestoreCenter(self.main_frame, self)
        elif name == "help":
            from gui.views.help_minimal import HelpView

            return HelpView(self.main_frame, self)
        elif name == "settings":
            from gui.views.settings_minimal import SettingsView

            return SettingsView(self.main_frame, self)

        return None

    def refresh_current_view(self):
        """Rebuild current view with new theme/colors"""
        if self.view_transition.current_widget:
            # Store current view name
            current_view_name = self.active_nav

            # Destroy current view
            self.view_transition.current_widget.destroy()
            self.view_transition.current_widget = None

            # Recreate view
            new_view = self._create_view()
            if new_view:
                new_view.grid(row=0, column=0, sticky="nsew")
                self.view_transition.current_widget = new_view

    def run(self):
        """Start the application main loop"""
        self.window.mainloop()


if __name__ == "__main__":
    import sys
    import ctypes

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    if is_admin():
        logger.info("Running with Administrator privileges")
        ClutchGApp().run()
    else:
        # Re-run the program with admin rights
        # Use shell execute to prompt UAC
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
