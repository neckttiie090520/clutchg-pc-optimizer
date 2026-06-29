"""
Auto-Update System for ClutchG

Checks GitHub Releases API for new versions, downloads the installer,
launches it, and **restarts the app automatically** after install completes.

Uses only stdlib (urllib, winreg, subprocess) — no external dependencies.

Flow:
    1. check_for_update() → queries GitHub API for latest release
    2. If newer version found → returns UpdateInfo
    3. download_update() → downloads .exe to temp dir with progress callback
    4. install_update() → launches Inno Setup installer, spawns a detached
       relauncher script, then exits the app
    5. Relauncher waits for the installer to finish, locates the new
       ClutchG.exe (via registry + filesystem fallbacks), and launches it

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

# Inno Setup identity — used to locate install path after update
# Mirrors installer/ClutchG.iss AppId (without surrounding braces here)
INNO_APP_ID = "{B4C9E2A1-3D7F-4E8B-A5C0-2F1D6E9B0374}"
APP_EXE_NAME = "ClutchG.exe"
APP_DIR_NAME = "ClutchG"


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
        version_str: Version string to parse (None is tolerated)

    Returns:
        Tuple of integers for comparison; (0,) on parse failure
    """
    if version_str is None:
        return (0,)
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

    def install_update(self, installer_path: Path, silent: bool = False) -> bool:
        """
        Launch the downloaded installer, restart the app afterwards.

        Spawns a detached relauncher script that polls by process name
        (not PID — robust against UAC elevation which respawns the
        installer with a new PID), then starts the newly installed
        ClutchG.exe from the install location (registry-backed lookup
        with Program Files and per-user fallbacks).

        For Inno Setup installers:
            - No flags → normal interactive installer
            - /SILENT → minimal UI, shows progress bar
            - /VERYSILENT → completely hidden
            - /CLOSEAPPLICATIONS → auto-close running instance
            - /RESTARTAPPLICATIONS → ask installer to restart closed apps

        Args:
            installer_path: Path to the downloaded .exe
            silent: If True, run with /SILENT flag

        Returns:
            True if installer was launched successfully, False on failure.
            The caller can use this to revert UI state if launch fails.
        """
        if not installer_path.exists():
            logger.error(f"Installer not found: {installer_path}")
            return False

        cmd = [str(installer_path)]
        if silent:
            cmd.append("/SILENT")
        # Ask Inno Setup to close the running app and restart it after install
        cmd.append("/CLOSEAPPLICATIONS")
        cmd.append("/RESTARTAPPLICATIONS")

        logger.info(f"Launching installer: {' '.join(cmd)}")

        try:
            # Detach the installer so it survives our exit
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            proc = subprocess.Popen(
                cmd,
                creationflags=creation_flags,
                close_fds=True,
            )
            logger.info(f"Installer started, launcher PID={proc.pid}")

            # Spawn a detached relauncher. We pass the installer FILENAME
            # (not PID) so the relauncher can survive UAC elevation —
            # elevation respawns the installer with a new PID, but the
            # process name stays the same.
            self._spawn_relauncher(installer_path.name)

        except Exception as exc:
            logger.error(f"Failed to launch installer: {exc}")
            return False

        # Give the installer a moment to start, then exit.
        # The relauncher (detached cmd) will outlive us and relaunch
        # ClutchG.exe once the installer process disappears.
        logger.info("Exiting app for update installation; relauncher will restart ClutchG")
        sys.exit(0)

    def _spawn_relauncher(self, installer_name: str) -> None:
        """
        Write a temp .cmd file that waits for the installer to finish,
        then launches the new ClutchG.exe. Spawn it detached so it
        survives our sys.exit().

        The script self-deletes after running.

        Args:
            installer_name: Filename of the installer (e.g. ClutchG-Setup-1.0.2.exe).
                Used to poll by name — robust against UAC elevation.
        """
        try:
            script_path = self._create_relauncher_script(installer_name)
        except Exception as exc:
            logger.warning(f"Could not create relauncher script: {exc}")
            return

        try:
            # DETACHED_PROCESS (0x00000008) + CREATE_NEW_PROCESS_GROUP (0x00000200)
            # ensures the cmd window stays hidden and survives parent exit
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = (
                    subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                )

            subprocess.Popen(
                ["cmd.exe", "/c", str(script_path)],
                creationflags=creation_flags,
                close_fds=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"Relauncher spawned: {script_path}")
        except Exception as exc:
            logger.warning(f"Could not spawn relauncher: {exc}")

    @staticmethod
    def _create_relauncher_script(installer_name: str) -> Path:
        """
        Generate the .cmd relauncher script in the system temp dir.

        Polling strategy:
          1. Polls by process NAME (findstr ClutchG-Setup) instead of PID,
             because UAC elevation respawns the installer with a new PID.
          2. Has a 30-second startup window for the installer to appear
             (handles slow UAC prompt response).
          3. Has a 10-minute maximum wait (600s) before giving up.
          4. After installer exits, waits 2s for file handles to release.
          5. Locates ClutchG.exe via registry, then Program Files, then per-user.
          6. Launches it via `start`.
          7. Self-deletes.

        Args:
            installer_name: Filename of the installer (e.g. ClutchG-Setup-1.0.2.exe).
                The "ClutchG-Setup" prefix is used for name-based polling.

        Returns:
            Path to the generated .cmd script.
        """
        download_dir = Path(tempfile.gettempdir()) / "clutchg_updates"
        download_dir.mkdir(exist_ok=True)
        # Stable filename so we don't accumulate copies across runs
        script_path = download_dir / "relaunch.cmd"

        uninstall_key_hklm = (
            rf"HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\{INNO_APP_ID}_is1"
        )
        uninstall_key_hkcu = (
            rf"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{INNO_APP_ID}_is1"
        )

        script = f"""@echo off
:: ClutchG auto-update relauncher (auto-generated; self-deletes)
:: Polls by installer process name (NOT PID) so it survives UAC elevation.
:: UAC re-spawns the elevated installer with a new PID, but the process
:: name stays the same.
setlocal enabledelayedexpansion

:: Phase 1: wait up to 30s for installer to appear in process list.
:: (Handles UAC prompt delay.)
set "STARTUP_WAIT=0"
:startup_loop
tasklist 2>nul | findstr /i "ClutchG-Setup" >nul
if errorlevel 1 (
    set /a STARTUP_WAIT+=1
    if !STARTUP_WAIT! geq 30 goto launch
    timeout /t 1 /nobreak >nul
    goto startup_loop
)

:: Phase 2: installer found. Wait for it to finish (max 10 minutes = 600s).
set "INSTALL_WAIT=0"
:install_loop
tasklist 2>nul | findstr /i "ClutchG-Setup" >nul
if not errorlevel 1 (
    set /a INSTALL_WAIT+=1
    if !INSTALL_WAIT! geq 600 goto launch
    timeout /t 1 /nobreak >nul
    goto install_loop
)

:launch
:: Installer finished - give it a moment to release file handles
timeout /t 2 /nobreak >nul

:: Locate ClutchG.exe
set "CLUTCHG_EXE="

:: 1. Try registry InstallLocation (admin install: HKLM)
for /f "tokens=2,*" %%a in ('reg query "{uninstall_key_hklm}" /v InstallLocation 2^>nul ^| findstr InstallLocation') do (
    if exist "%%b{APP_EXE_NAME}" set "CLUTCHG_EXE=%%b{APP_EXE_NAME}"
)

:: 2. Try HKCU (per-user install)
if not defined CLUTCHG_EXE (
    for /f "tokens=2,*" %%a in ('reg query "{uninstall_key_hkcu}" /v InstallLocation 2^>nul ^| findstr InstallLocation') do (
        if exist "%%b{APP_EXE_NAME}" set "CLUTCHG_EXE=%%b{APP_EXE_NAME}"
    )
)

:: 3. Default Program Files
if not defined CLUTCHG_EXE if exist "%ProgramFiles%\\{APP_DIR_NAME}\\{APP_EXE_NAME}" set "CLUTCHG_EXE=%ProgramFiles%\\{APP_DIR_NAME}\\{APP_EXE_NAME}"
if not defined CLUTCHG_EXE if exist "%ProgramFiles(x86)%\\{APP_DIR_NAME}\\{APP_EXE_NAME}" set "CLUTCHG_EXE=%ProgramFiles(x86)%\\{APP_DIR_NAME}\\{APP_EXE_NAME}"

:: 4. Per-user Programs
if not defined CLUTCHG_EXE if exist "%LOCALAPPDATA%\\Programs\\{APP_DIR_NAME}\\{APP_EXE_NAME}" set "CLUTCHG_EXE=%LOCALAPPDATA%\\Programs\\{APP_DIR_NAME}\\{APP_EXE_NAME}"

:: Launch if found
if defined CLUTCHG_EXE (
    start "" "%CLUTCHG_EXE%"
)

:: Self-delete
endlocal
(del "%~f0") 2>nul
"""
        script_path.write_text(script, encoding="ascii")
        return script_path

    @staticmethod
    def find_installed_clutchg_exe() -> Optional[Path]:
        """
        Locate the installed ClutchG.exe on this machine.

        Lookup order:
          1. HKLM uninstall key InstallLocation (admin install)
          2. HKCU uninstall key InstallLocation (per-user install)
          3. Default Program Files paths
          4. %LOCALAPPDATA%\\Programs\\ClutchG

        Returns:
            Path to ClutchG.exe if found, None otherwise.
        """
        import winreg

        # 1 & 2: registry
        for hive, root in (
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        ):
            key_path = f"{root}\\{INNO_APP_ID}_is1"
            try:
                with winreg.OpenKey(hive, key_path) as key:
                    install_loc, _ = winreg.QueryValueEx(key, "InstallLocation")
                    if install_loc:
                        candidate = Path(install_loc) / APP_EXE_NAME
                        if candidate.exists():
                            return candidate
            except OSError:
                continue

        # 3 & 4: filesystem fallbacks
        candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / APP_DIR_NAME / APP_EXE_NAME,
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / APP_DIR_NAME / APP_EXE_NAME,
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / APP_DIR_NAME / APP_EXE_NAME,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

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

    def install(self, installer_path: Path, silent: bool = False) -> bool:
        """Launch installer and exit app.

        Returns:
            True if installer launched (app will exit shortly after),
            False if launch failed. Caller should revert UI on False.
        """
        return self.checker.install_update(installer_path, silent=silent)
