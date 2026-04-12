"""
Auto-Update System for ClutchG

Checks GitHub Releases API for new versions, downloads the installer,
and launches it. Uses only stdlib (urllib) — no external dependencies.

Flow:
    1. check_for_update() → queries GitHub API for latest release
    2. If newer version found → returns UpdateInfo
    3. download_update() → downloads .exe to temp dir with progress callback
    4. install_update() → launches Inno Setup installer and exits app

Rate limiting:
    - Checks at most once per COOLDOWN_HOURS (default 6)
    - Respects GitHub API rate limits (60/hour unauthenticated)
    - All network errors handled silently (never blocks the user)
"""

from __future__ import annotations

import json
import logging
import os
import ssl
import subprocess
import sys
import tempfile
import time
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================
GITHUB_OWNER = "neckttiie090520"
GITHUB_REPO = "clutchg-pc-optimizer"
API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
ASSET_PATTERN = ".exe"  # Match installer asset by extension
COOLDOWN_HOURS = 6  # Minimum hours between update checks
REQUEST_TIMEOUT = 15  # Seconds for API/download timeout


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class UpdateInfo:
    """Information about an available update"""

    current_version: str
    latest_version: str
    download_url: str
    asset_name: str
    asset_size: int  # bytes, 0 if unknown
    release_notes: str = ""
    html_url: str = ""  # Link to release page on GitHub


@dataclass
class DownloadProgress:
    """Progress state for download callback"""

    downloaded: int = 0
    total: int = 0
    speed_bps: float = 0.0  # bytes per second

    @property
    def percent(self) -> float:
        if self.total <= 0:
            return 0.0
        return min(100.0, (self.downloaded / self.total) * 100)

    @property
    def speed_display(self) -> str:
        """Human-readable download speed"""
        if self.speed_bps < 1024:
            return f"{self.speed_bps:.0f} B/s"
        if self.speed_bps < 1024 * 1024:
            return f"{self.speed_bps / 1024:.1f} KB/s"
        return f"{self.speed_bps / (1024 * 1024):.1f} MB/s"

    @property
    def size_display(self) -> str:
        """Human-readable total size"""
        if self.total < 1024 * 1024:
            return f"{self.total / 1024:.0f} KB"
        return f"{self.total / (1024 * 1024):.1f} MB"


# ============================================================================
# VERSION COMPARISON
# ============================================================================
def parse_version(version_str: str) -> tuple:
    """
    Parse a version string into a comparable tuple.

    Handles: "1.0.0", "v1.0.0", "1.2", "1.2.3.4"

    Args:
        version_str: Version string to parse

    Returns:
        Tuple of integers for comparison
    """
    # Strip leading 'v' or 'V'
    cleaned = version_str.strip().lstrip("vV")
    try:
        return tuple(int(x) for x in cleaned.split("."))
    except (ValueError, AttributeError):
        logger.warning(f"Could not parse version: {version_str!r}")
        return (0,)


def is_newer_version(current: str, latest: str) -> bool:
    """
    Check if latest version is newer than current.

    Args:
        current: Current app version (e.g. "1.0.0")
        latest: Latest release version (e.g. "v1.1.0")

    Returns:
        True if latest > current
    """
    return parse_version(latest) > parse_version(current)


# ============================================================================
# UPDATE CHECKER
# ============================================================================
class UpdateChecker:
    """
    Handles checking for updates and downloading installers.

    Usage:
        checker = UpdateChecker(current_version="1.0.0")

        # Quick check (non-blocking)
        info = checker.check_for_update()
        if info:
            print(f"Update available: {info.latest_version}")

        # Download with progress
        path = checker.download_update(info, on_progress=callback)

        # Launch installer
        checker.install_update(path)
    """

    def __init__(
        self,
        current_version: str,
        config_manager=None,
    ):
        """
        Args:
            current_version: Current app version string
            config_manager: Optional ConfigManager for cooldown tracking
        """
        self.current_version = current_version
        self.config_manager = config_manager
        self._cancel_download = False

    # ── Public API ────────────────────────────────────────────────────

    def should_check(self) -> bool:
        """
        Determine if we should check for updates based on cooldown
        and user preference.

        Returns:
            True if enough time has passed since last check
        """
        if self.config_manager is None:
            return True

        config = self.config_manager.load_config()

        # User opted out of update checks
        if not config.get("check_updates", True):
            return False

        # Check cooldown
        last_check = config.get("last_update_check", 0)
        elapsed_hours = (time.time() - last_check) / 3600
        return elapsed_hours >= COOLDOWN_HOURS

    def check_for_update(self) -> Optional[UpdateInfo]:
        """
        Query GitHub Releases API for the latest version.

        Returns:
            UpdateInfo if a newer version is available, None otherwise.
            Returns None on any error (network, parse, rate limit).
        """
        try:
            data = self._fetch_latest_release()
            if data is None:
                return None

            tag = data.get("tag_name", "")
            if not tag:
                logger.warning("GitHub release has no tag_name")
                return None

            if not is_newer_version(self.current_version, tag):
                logger.debug(
                    f"Current {self.current_version} >= latest {tag}, no update"
                )
                self._record_check_time()
                return None

            # Find installer asset
            asset = self._find_installer_asset(data.get("assets", []))
            if asset is None:
                logger.warning(f"No .exe asset found in release {tag}")
                return None

            self._record_check_time()

            return UpdateInfo(
                current_version=self.current_version,
                latest_version=tag.lstrip("vV"),
                download_url=asset["browser_download_url"],
                asset_name=asset["name"],
                asset_size=asset.get("size", 0),
                release_notes=data.get("body", "") or "",
                html_url=data.get("html_url", ""),
            )

        except Exception as exc:
            logger.warning(f"Update check failed: {exc}")
            return None

    def download_update(
        self,
        info: UpdateInfo,
        on_progress: Optional[Callable[[DownloadProgress], None]] = None,
    ) -> Optional[Path]:
        """
        Download the installer to a temp directory.

        Args:
            info: UpdateInfo from check_for_update()
            on_progress: Callback called with DownloadProgress on each chunk

        Returns:
            Path to the downloaded installer, or None on failure
        """
        self._cancel_download = False

        # Create temp directory that persists after app closes
        download_dir = Path(tempfile.gettempdir()) / "clutchg_updates"
        download_dir.mkdir(exist_ok=True)
        dest = download_dir / info.asset_name

        # Remove stale download if exists
        if dest.exists():
            try:
                dest.unlink()
            except OSError:
                pass

        try:
            req = Request(
                info.download_url,
                headers={"User-Agent": f"ClutchG/{self.current_version}"},
            )

            ctx = self._make_ssl_context()

            with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                progress = DownloadProgress(total=total or info.asset_size)

                chunk_size = 8192
                downloaded = 0
                start_time = time.monotonic()

                with open(dest, "wb") as f:
                    while True:
                        if self._cancel_download:
                            logger.info("Download cancelled by user")
                            self._cleanup_file(dest)
                            return None

                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded += len(chunk)

                        elapsed = time.monotonic() - start_time
                        progress.downloaded = downloaded
                        if elapsed > 0:
                            progress.speed_bps = downloaded / elapsed

                        if on_progress:
                            on_progress(progress)

            # Verify download size if known
            if info.asset_size > 0 and dest.stat().st_size != info.asset_size:
                logger.error(
                    f"Size mismatch: expected {info.asset_size}, "
                    f"got {dest.stat().st_size}"
                )
                self._cleanup_file(dest)
                return None

            logger.info(f"Downloaded update to {dest}")
            return dest

        except Exception as exc:
            logger.error(f"Download failed: {exc}")
            self._cleanup_file(dest)
            return None

    def cancel_download(self):
        """Cancel an in-progress download (thread-safe)."""
        self._cancel_download = True

    def install_update(self, installer_path: Path, silent: bool = False) -> None:
        """
        Launch the downloaded installer and exit the app.

        For Inno Setup installers:
            - No flags → normal interactive installer
            - /SILENT → minimal UI, shows progress bar
            - /VERYSILENT → completely hidden
            - /CLOSEAPPLICATIONS → auto-close running instance

        Args:
            installer_path: Path to the downloaded .exe
            silent: If True, run with /SILENT flag
        """
        if not installer_path.exists():
            logger.error(f"Installer not found: {installer_path}")
            return

        cmd = [str(installer_path)]
        if silent:
            cmd.append("/SILENT")
        # Always ask Inno Setup to close the running app
        cmd.append("/CLOSEAPPLICATIONS")

        logger.info(f"Launching installer: {' '.join(cmd)}")

        try:
            # Detach the installer process so it survives our exit
            # CREATE_NEW_PROCESS_GROUP on Windows ensures this
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            subprocess.Popen(
                cmd,
                creationflags=creation_flags,
                close_fds=True,
            )
        except Exception as exc:
            logger.error(f"Failed to launch installer: {exc}")
            return

        # Give the installer a moment to start, then exit
        logger.info("Exiting app for update installation...")
        sys.exit(0)

    # ── Private helpers ───────────────────────────────────────────────

    def _fetch_latest_release(self) -> Optional[dict]:
        """Fetch latest release JSON from GitHub API."""
        req = Request(
            API_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": f"ClutchG/{self.current_version}",
            },
        )

        ctx = self._make_ssl_context()

        try:
            with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
                # Check rate limit
                remaining = resp.headers.get("X-RateLimit-Remaining")
                if remaining is not None and int(remaining) < 5:
                    logger.warning(f"GitHub API rate limit low: {remaining} remaining")

                return json.loads(resp.read().decode("utf-8"))

        except HTTPError as exc:
            if exc.code == 404:
                logger.debug("No releases found (404)")
            elif exc.code == 403:
                logger.warning("GitHub API rate limited (403)")
            else:
                logger.warning(f"GitHub API error: {exc.code}")
            return None

        except (URLError, TimeoutError, OSError) as exc:
            logger.debug(f"Network error checking for updates: {exc}")
            return None

    def _find_installer_asset(self, assets: list) -> Optional[dict]:
        """Find the .exe installer asset from release assets."""
        for asset in assets:
            name = asset.get("name", "")
            if name.lower().endswith(ASSET_PATTERN):
                return asset
        return None

    def _record_check_time(self) -> None:
        """Store the current time as last update check."""
        if self.config_manager is None:
            return
        try:
            config = self.config_manager.load_config()
            config["last_update_check"] = time.time()
            self.config_manager.save_config(config)
        except Exception as exc:
            logger.debug(f"Could not save update check time: {exc}")

    @staticmethod
    def _make_ssl_context() -> ssl.SSLContext:
        """Create an SSL context for HTTPS requests."""
        ctx = ssl.create_default_context()
        # On some corporate/antivirus setups, certs may fail.
        # We still verify by default but log clearly if it fails.
        return ctx

    @staticmethod
    def _cleanup_file(path: Path) -> None:
        """Remove a file, ignoring errors."""
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass


# ============================================================================
# ASYNC WRAPPER (for GUI integration)
# ============================================================================
class AsyncUpdateChecker:
    """
    Non-blocking wrapper around UpdateChecker for GUI use.

    Runs check_for_update() in a daemon thread, then calls back on
    the Tk main thread via window.after().

    Usage:
        async_checker = AsyncUpdateChecker(app.window, "1.0.0", config_manager)
        async_checker.check_async(on_update_available=show_update_dialog)
    """

    def __init__(
        self,
        tk_window,
        current_version: str,
        config_manager=None,
    ):
        self.window = tk_window
        self.checker = UpdateChecker(current_version, config_manager)
        self._download_thread: Optional[threading.Thread] = None

    def check_async(
        self,
        on_update_available: Optional[Callable[[UpdateInfo], None]] = None,
        on_no_update: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Check for updates in a background thread.

        Args:
            on_update_available: Called on main thread with UpdateInfo
            on_no_update: Called on main thread if no update found
        """
        if not self.checker.should_check():
            logger.debug("Skipping update check (cooldown or disabled)")
            return

        def _worker():
            info = self.checker.check_for_update()
            if info:
                self.window.after(0, lambda: on_update_available(info))
            elif on_no_update:
                self.window.after(0, on_no_update)

        thread = threading.Thread(target=_worker, daemon=True, name="update-check")
        thread.start()

    def download_async(
        self,
        info: UpdateInfo,
        on_progress: Optional[Callable[[DownloadProgress], None]] = None,
        on_complete: Optional[Callable[[Optional[Path]], None]] = None,
    ) -> None:
        """
        Download the update in a background thread.

        Args:
            info: UpdateInfo from the check
            on_progress: Called on main thread with DownloadProgress
            on_complete: Called on main thread with Path or None
        """

        def _progress_wrapper(progress: DownloadProgress):
            if on_progress:
                self.window.after(0, lambda p=progress: on_progress(p))

        def _worker():
            path = self.checker.download_update(info, on_progress=_progress_wrapper)
            if on_complete:
                self.window.after(0, lambda: on_complete(path))

        self._download_thread = threading.Thread(
            target=_worker, daemon=True, name="update-download"
        )
        self._download_thread.start()

    def cancel_download(self):
        """Cancel an in-progress download."""
        self.checker.cancel_download()

    def install(self, installer_path: Path, silent: bool = False):
        """Launch installer and exit."""
        self.checker.install_update(installer_path, silent=silent)
