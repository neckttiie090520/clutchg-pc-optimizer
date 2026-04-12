"""
Update Notification Dialog - Windows 11 Dark UI

Shows when a new version is available.
Three states: notification → downloading → ready to install.

Integrates with core/updater.py's AsyncUpdateChecker.
"""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import customtkinter as ctk

from gui.theme import COLORS, SPACING, RADIUS
from gui.style import font, bind_dynamic_wraplength
from gui.components.icon_provider import get_icon

if TYPE_CHECKING:
    from app_minimal import ClutchGApp
    from core.updater import UpdateInfo, DownloadProgress

_ICON_FONT = "Tabler Icons"

# Tabler icon codepoints
_ICON_DOWNLOAD = "\uea59"  # download
_ICON_REFRESH = "\ueb13"  # refresh
_ICON_CLOSE = "\ueb55"  # x
_ICON_EXTERNAL = "\uea99"  # external-link
_ICON_ROCKET = "\uec90"  # rocket
_ICON_CHECK = "\uea67"  # circle-check


class UpdateDialog(ctk.CTkToplevel):
    """
    Modal dialog for update notifications.

    States:
        - "notify": Shows version info and release notes
        - "downloading": Shows progress bar during download
        - "ready": Download complete, ready to install
        - "error": Download failed, offer retry
    """

    def __init__(self, parent, app: "ClutchGApp", info: "UpdateInfo"):
        super().__init__(parent)

        self.app = app
        self.info = info
        self._installer_path: Optional[Path] = None

        # Window setup
        self.title("Update Available")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_primary"])

        # Center on parent
        self.geometry("420x380")
        self.after(10, self._center_on_parent)

        # Protocol for window close button
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_notify_state()

    def _center_on_parent(self):
        """Center dialog over parent window."""
        self.update_idletasks()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        px = self.master.winfo_x()
        py = self.master.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    # ── State: Notify ─────────────────────────────────────────────────

    def _build_notify_state(self):
        """Build the initial notification UI."""
        self._clear_content()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # Icon + Title
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING["md"]))

        ctk.CTkLabel(
            header,
            text=_ICON_ROCKET,
            font=ctk.CTkFont(family=_ICON_FONT, size=28),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=(0, SPACING["sm"]))

        ctk.CTkLabel(
            header,
            text="Update Available",
            font=font("h3"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")

        # Version info
        version_frame = ctk.CTkFrame(
            container,
            fg_color=COLORS["bg_card"],
            corner_radius=RADIUS["md"],
            border_width=1,
            border_color=COLORS["border"],
        )
        version_frame.pack(fill="x", pady=(0, SPACING["md"]))

        version_inner = ctk.CTkFrame(version_frame, fg_color="transparent")
        version_inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        ctk.CTkLabel(
            version_inner,
            text=f"v{self.info.current_version}",
            font=font("body"),
            text_color=COLORS["text_secondary"],
        ).pack(side="left")

        ctk.CTkLabel(
            version_inner,
            text="  ->  ",
            font=font("body"),
            text_color=COLORS["text_muted"],
        ).pack(side="left")

        ctk.CTkLabel(
            version_inner,
            text=f"v{self.info.latest_version}",
            font=font("body_bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        if self.info.asset_size > 0:
            size_mb = self.info.asset_size / (1024 * 1024)
            ctk.CTkLabel(
                version_inner,
                text=f"({size_mb:.1f} MB)",
                font=font("caption"),
                text_color=COLORS["text_muted"],
            ).pack(side="right")

        # Release notes (scrollable, truncated)
        if self.info.release_notes:
            notes_label = ctk.CTkLabel(
                container,
                text="What's New",
                font=font("body_bold"),
                text_color=COLORS["text_primary"],
                anchor="w",
            )
            notes_label.pack(fill="x", pady=(0, SPACING["xs"]))

            # Truncate notes to first ~300 chars
            notes = self.info.release_notes.strip()
            if len(notes) > 300:
                notes = notes[:297] + "..."

            notes_text = ctk.CTkLabel(
                container,
                text=notes,
                font=font("caption"),
                text_color=COLORS["text_secondary"],
                anchor="nw",
                justify="left",
            )
            notes_text.pack(fill="x", pady=(0, SPACING["md"]))
            bind_dynamic_wraplength(notes_text, container, padding=0)

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        # "View on GitHub" link
        if self.info.html_url:
            link_btn = ctk.CTkButton(
                btn_frame,
                text=f"{_ICON_EXTERNAL} View Release",
                font=font("caption"),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_hover"],
                height=28,
                width=100,
                command=lambda: webbrowser.open(self.info.html_url),
            )
            link_btn.pack(side="left")

        # Later button
        ctk.CTkButton(
            btn_frame,
            text="Later",
            font=font("button"),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            height=36,
            width=80,
            command=self._on_close,
        ).pack(side="right", padx=(SPACING["sm"], 0))

        # Download button
        ctk.CTkButton(
            btn_frame,
            text=f"{_ICON_DOWNLOAD}  Download Update",
            font=font("button"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_primary"],
            corner_radius=RADIUS["md"],
            height=36,
            command=self._start_download,
        ).pack(side="right")

    # ── State: Downloading ────────────────────────────────────────────

    def _build_downloading_state(self):
        """Build the download progress UI."""
        self._clear_content()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # Header
        ctk.CTkLabel(
            container,
            text="Downloading Update...",
            font=font("h3"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, SPACING["lg"]))

        # Progress bar
        self._progress_bar = ctk.CTkProgressBar(
            container,
            fg_color=COLORS["bg_card"],
            progress_color=COLORS["accent"],
            height=8,
            corner_radius=4,
        )
        self._progress_bar.pack(fill="x", pady=(0, SPACING["sm"]))
        self._progress_bar.set(0)

        # Progress text
        self._progress_label = ctk.CTkLabel(
            container,
            text="Starting download...",
            font=font("caption"),
            text_color=COLORS["text_secondary"],
        )
        self._progress_label.pack(fill="x", pady=(0, SPACING["lg"]))

        # Cancel button
        ctk.CTkButton(
            container,
            text="Cancel",
            font=font("button"),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            height=36,
            width=100,
            command=self._cancel_download,
        ).pack(side="bottom")

    # ── State: Ready ──────────────────────────────────────────────────

    def _build_ready_state(self):
        """Build the 'ready to install' UI."""
        self._clear_content()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        # Success icon
        ctk.CTkLabel(
            container,
            text=_ICON_CHECK,
            font=ctk.CTkFont(family=_ICON_FONT, size=48),
            text_color=COLORS["success"],
        ).pack(pady=(SPACING["lg"], SPACING["sm"]))

        ctk.CTkLabel(
            container,
            text="Download Complete",
            font=font("h3"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(0, SPACING["sm"]))

        ctk.CTkLabel(
            container,
            text="The installer will close ClutchG and\ninstall the update automatically.",
            font=font("body_small"),
            text_color=COLORS["text_secondary"],
            justify="center",
        ).pack(pady=(0, SPACING["xl"]))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        ctk.CTkButton(
            btn_frame,
            text="Later",
            font=font("button"),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            height=36,
            width=80,
            command=self._on_close,
        ).pack(side="right", padx=(SPACING["sm"], 0))

        ctk.CTkButton(
            btn_frame,
            text=f"{_ICON_ROCKET}  Install Now",
            font=font("button"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_primary"],
            corner_radius=RADIUS["md"],
            height=36,
            command=self._install_now,
        ).pack(side="right")

    # ── State: Error ──────────────────────────────────────────────────

    def _build_error_state(self, error_msg: str = "Download failed"):
        """Build the error/retry UI."""
        self._clear_content()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            container,
            text="Download Failed",
            font=font("h3"),
            text_color=COLORS["text_primary"],
        ).pack(pady=(SPACING["lg"], SPACING["sm"]))

        ctk.CTkLabel(
            container,
            text=error_msg,
            font=font("body_small"),
            text_color=COLORS["text_secondary"],
            justify="center",
        ).pack(pady=(0, SPACING["xl"]))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")

        ctk.CTkButton(
            btn_frame,
            text="Close",
            font=font("button"),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_hover"],
            corner_radius=RADIUS["md"],
            height=36,
            width=80,
            command=self._on_close,
        ).pack(side="right", padx=(SPACING["sm"], 0))

        ctk.CTkButton(
            btn_frame,
            text=f"{_ICON_REFRESH}  Retry",
            font=font("button"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_primary"],
            corner_radius=RADIUS["md"],
            height=36,
            width=100,
            command=self._start_download,
        ).pack(side="right")

    # ── Actions ───────────────────────────────────────────────────────

    def _start_download(self):
        """Begin downloading the update."""
        self._build_downloading_state()

        if not hasattr(self.app, "_async_updater"):
            return

        self.app._async_updater.download_async(
            self.info,
            on_progress=self._on_download_progress,
            on_complete=self._on_download_complete,
        )

    def _on_download_progress(self, progress: "DownloadProgress"):
        """Update progress bar (called on main thread)."""
        try:
            pct = progress.percent
            self._progress_bar.set(pct / 100)
            self._progress_label.configure(
                text=f"{pct:.0f}%  ·  {progress.speed_display}  ·  {progress.size_display}"
            )
        except Exception:
            pass  # Widget may be destroyed

    def _on_download_complete(self, path: Optional[Path]):
        """Handle download completion (called on main thread)."""
        if path is not None:
            self._installer_path = path
            self._build_ready_state()
        else:
            self._build_error_state(
                "Could not download the update.\n"
                "Check your internet connection and try again."
            )

    def _cancel_download(self):
        """Cancel the download."""
        if hasattr(self.app, "_async_updater"):
            self.app._async_updater.cancel_download()
        self._on_close()

    def _install_now(self):
        """Launch installer and exit app."""
        if self._installer_path and hasattr(self.app, "_async_updater"):
            self.app._async_updater.install(self._installer_path, silent=False)

    def _on_close(self):
        """Close the dialog."""
        self.grab_release()
        self.destroy()

    def _clear_content(self):
        """Remove all child widgets."""
        for widget in self.winfo_children():
            widget.destroy()
