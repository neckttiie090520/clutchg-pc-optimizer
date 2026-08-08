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

import csv
import ctypes
from ctypes import wintypes
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================
GITHUB_OWNER = "neckttiie090520"
GITHUB_REPO = "clutchg-pc-optimizer"
API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
ASSET_PATTERN = "ClutchG-Setup-{version}.exe"
RELEASE_VERSION_PATTERN = re.compile(r"^v(\d+\.\d+\.\d+)$")
INSTALLER_NAME_PATTERN = re.compile(r"^ClutchG-Setup-(\d+\.\d+\.\d+)\.exe$")
EXPECTED_PUBLISHER = "CN=ClutchG Project"
COOLDOWN_HOURS = 6  # Minimum hours between update checks
REQUEST_TIMEOUT = 15  # Seconds for API/download timeout
SIGNATURE_TIMEOUT = 30


class _GUID(ctypes.Structure):
    """Windows GUID structure used by WinVerifyTrust."""

    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class _WINTRUST_FILE_INFO(ctypes.Structure):
    _fields_ = [
        ("cbStruct", wintypes.DWORD),
        ("pcwszFilePath", wintypes.LPCWSTR),
        ("hFile", wintypes.HANDLE),
        ("pgKnownSubject", ctypes.POINTER(_GUID)),
    ]


class _WINTRUST_DATA(ctypes.Structure):
    _fields_ = [
        ("cbStruct", wintypes.DWORD),
        ("pPolicyCallbackData", wintypes.LPVOID),
        ("pSIPClientData", wintypes.LPVOID),
        ("dwUIChoice", wintypes.DWORD),
        ("fdwRevocationChecks", wintypes.DWORD),
        ("dwUnionChoice", wintypes.DWORD),
        ("pFile", ctypes.POINTER(_WINTRUST_FILE_INFO)),
        ("dwStateAction", wintypes.DWORD),
        ("hWVTStateData", wintypes.HANDLE),
        ("pwszURLReference", wintypes.LPCWSTR),
        ("dwProvFlags", wintypes.DWORD),
        ("dwUIContext", wintypes.DWORD),
        ("pSignatureSettings", wintypes.LPVOID),
    ]


def _win_verify_trust(path: Path) -> bool:
    """Return whether WinVerifyTrust accepts the Authenticode signature."""
    if sys.platform != "win32":
        return False

    action = _GUID(
        0x00AAC56B,
        0xCD44,
        0x11D0,
        (ctypes.c_ubyte * 8)(0x8C, 0xC2, 0x00, 0xC0, 0x4F, 0xC2, 0x95, 0xEE),
    )
    file_info = _WINTRUST_FILE_INFO(
        ctypes.sizeof(_WINTRUST_FILE_INFO),
        str(path),
        None,
        None,
    )
    trust_data = _WINTRUST_DATA(
        ctypes.sizeof(_WINTRUST_DATA),
        None,
        None,
        2,  # WTD_UI_NONE
        1,  # WTD_REVOKE_WHOLECHAIN
        1,  # WTD_CHOICE_FILE
        ctypes.pointer(file_info),
        0,  # WTD_STATEACTION_IGNORE
        None,
        None,
        0x00000080,  # WTD_REVOCATION_CHECK_CHAIN_EXCLUDE_ROOT
        0,
        None,
    )
    try:
        win_verify_trust = ctypes.windll.wintrust.WinVerifyTrust
        win_verify_trust.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(_GUID),
            ctypes.POINTER(_WINTRUST_DATA),
        ]
        win_verify_trust.restype = ctypes.c_long
        return win_verify_trust(
            wintypes.HWND(-1),
            ctypes.byref(action),
            ctypes.byref(trust_data),
        ) == 0
    except (AttributeError, OSError) as exc:
        logger.error(f"WinVerifyTrust is unavailable: {exc}")
        return False

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

    @staticmethod
    def _release_version(tag: str) -> Optional[str]:
        """Return a strict three-part release version or None."""
        match = RELEASE_VERSION_PATTERN.fullmatch(tag.strip()) if tag else None
        return match.group(1) if match else None

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
            release_version = self._release_version(tag)
            if release_version is None:
                logger.warning(f"Invalid release tag: {tag!r}")
                return None

            if not is_newer_version(self.current_version, release_version):
                logger.debug(
                    f"Current {self.current_version} >= latest {tag}, no update"
                )
                self._record_check_time()
                return None

            asset = self._find_installer_asset(
                data.get("assets", []), release_version
            )
            if asset is None:
                logger.warning(
                    "Release %s does not contain exactly one valid %s asset",
                    tag,
                    ASSET_PATTERN.format(version=release_version),
                )
                return None

            self._record_check_time()

            return UpdateInfo(
                current_version=self.current_version,
                latest_version=release_version,
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
        expected_name = ASSET_PATTERN.format(version=info.latest_version)
        if info.asset_name != expected_name or not self._is_release_asset_url(
            info.download_url, expected_name
        ):
            logger.error("Refusing update with mismatched installer identity")
            return None

        try:
            download_dir = Path(
                tempfile.mkdtemp(prefix="clutchg-update-")
            )
        except OSError as exc:
            logger.error(f"Could not create unique download directory: {exc}")
            return None
        dest = download_dir / expected_name

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
                            self._cleanup_download(dest)
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
                self._cleanup_download(dest)
                return None

            logger.info(f"Downloaded update to {dest}")
            return dest

        except Exception as exc:
            logger.error(f"Download failed: {exc}")
            self._cleanup_download(dest)
            return None

    def cancel_download(self):
        """Cancel an in-progress download (thread-safe)."""
        self._cancel_download = True

    def install_update(self, installer_path: Path, silent: bool = False) -> bool:
        """Stage, verify, fingerprint, and launch the downloaded installer.

        The downloaded file is copied into a unique, access-controlled
        ProgramData directory before Authenticode verification. The staged
        bytes are hashed around verification and again immediately before
        process creation. The detached relauncher owns staging cleanup.

        Returns:
            True when installer and relauncher handoff both succeed. The caller
            owns application shutdown after receiving True.
        """
        installer_path = Path(installer_path)
        if not installer_path.is_file():
            logger.error(f"Installer not found: {installer_path}")
            return False
        if INSTALLER_NAME_PATTERN.fullmatch(installer_path.name) is None:
            logger.error("Installer filename is not an exact versioned asset")
            self._cleanup_download(installer_path)
            return False

        staging_dir = self._create_secure_staging_dir()
        if staging_dir is None:
            self._cleanup_download(installer_path)
            return False

        staged_installer = staging_dir / installer_path.name
        try:
            shutil.copyfile(installer_path, staged_installer)
            verified_fingerprint = self._sha256_file(staged_installer)
        except (OSError, ValueError) as exc:
            logger.error(f"Could not stage installer: {exc}")
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False

        if not self.verify_installer(staged_installer):
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False

        try:
            post_verify_fingerprint = self._sha256_file(staged_installer)
        except OSError as exc:
            logger.error(f"Could not fingerprint verified installer: {exc}")
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False
        if not hmac.compare_digest(
            verified_fingerprint, post_verify_fingerprint
        ):
            logger.error("Staged installer changed during Authenticode verification")
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False

        try:
            relauncher_path = self._create_relauncher_script(
                staging_dir, staged_installer.name
            )
        except (OSError, ValueError) as exc:
            logger.error(f"Could not prepare relaunch handoff: {exc}")
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False

        cmd = [str(staged_installer)]
        if silent:
            cmd.append("/SILENT")
        cmd.extend(["/CLOSEAPPLICATIONS", "/CLUTCHGUPDATE"])
        logger.info(f"Launching staged verified installer: {' '.join(cmd)}")

        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            launch_fingerprint = self._sha256_file(staged_installer)
            if not hmac.compare_digest(
                verified_fingerprint, launch_fingerprint
            ):
                logger.error("Staged installer changed before launch")
                self._cleanup_tree(staging_dir)
                self._cleanup_download(installer_path)
                return False
            proc = subprocess.Popen(
                cmd,
                creationflags=creation_flags,
                close_fds=True,
            )
            logger.info(f"Installer started, launcher PID={proc.pid}")
        except Exception as exc:
            logger.error(f"Failed to launch installer: {exc}")
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False

        if not self._spawn_relauncher_script(relauncher_path):
            logger.error("Installer started, but relaunch handoff failed")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except (OSError, subprocess.SubprocessError) as exc:
                logger.warning(f"Could not stop installer after handoff failure: {exc}")
            self._cleanup_tree(staging_dir)
            self._cleanup_download(installer_path)
            return False

        self._cleanup_download(installer_path)
        logger.info("Installer and relauncher handoff completed")
        return True

    def verify_installer(self, installer_path: Path) -> bool:
        """Fail closed unless name, PE version, trust, and publisher all match."""
        installer_path = Path(installer_path)
        name_match = INSTALLER_NAME_PATTERN.fullmatch(installer_path.name)
        if name_match is None:
            logger.error("Installer filename is not an exact versioned asset")
            return False
        if sys.platform != "win32":
            logger.error("Authenticode verification is only available on Windows")
            return False
        if not _win_verify_trust(installer_path):
            logger.error(f"Authenticode trust verification failed: {installer_path}")
            return False

        metadata = self._get_installer_metadata(installer_path)
        if metadata is None:
            return False
        publisher, product_version = metadata
        if publisher != EXPECTED_PUBLISHER:
            logger.error(
                "Installer publisher mismatch: expected %r, received %r",
                EXPECTED_PUBLISHER,
                publisher,
            )
            return False
        if product_version != name_match.group(1):
            logger.error(
                "Installer PE version mismatch: filename=%r, PE=%r",
                name_match.group(1),
                product_version,
            )
            return False
        return True

    @staticmethod
    def _get_installer_metadata(
        installer_path: Path,
    ) -> Optional[tuple[str, str]]:
        """Read signer subject and PE product version without executing the file."""
        escaped_path = str(installer_path).replace("'", "''")
        script = (
            "$ErrorActionPreference='Stop';"
            f"$p='{escaped_path}';"
            "$s=Get-AuthenticodeSignature -LiteralPath $p;"
            "if($s.Status -ne 'Valid' -or $null -eq $s.SignerCertificate){exit 2};"
            "$v=(Get-Item -LiteralPath $p).VersionInfo.ProductVersion;"
            "if([string]::IsNullOrWhiteSpace($v)){exit 3};"
            "[Console]::Out.Write(($s.SignerCertificate.Subject+'|'+$v.Trim()))"
        )
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    script,
                ],
                capture_output=True,
                text=True,
                timeout=SIGNATURE_TIMEOUT,
                check=False,
                creationflags=creation_flags,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            logger.error(f"Could not inspect installer metadata: {exc}")
            return None
        if result.returncode != 0:
            logger.error("PowerShell rejected installer signature or PE metadata")
            return None
        publisher, separator, product_version = result.stdout.strip().partition("|")
        if not separator or not publisher or not product_version:
            logger.error("PowerShell returned incomplete installer metadata")
            return None
        return publisher, product_version

    @classmethod
    def _create_secure_staging_dir(cls) -> Optional[Path]:
        """Create a unique high-integrity ProgramData directory or fail closed."""
        if sys.platform != "win32":
            logger.error("Secure update staging is only available on Windows")
            return None

        program_data = os.environ.get("ProgramData")
        if not program_data:
            logger.error("ProgramData is unavailable; refusing insecure staging")
            return None

        staging_root = Path(program_data) / "ClutchG" / "Updates"
        staging_dir = staging_root / f"update-{secrets.token_hex(16)}"
        try:
            staging_root.mkdir(parents=True, exist_ok=True)
            if cls._is_reparse_point(staging_root):
                raise OSError("staging root is a reparse point")
        except OSError as exc:
            logger.error(f"Could not prepare ProgramData staging root: {exc}")
            return None

        if not cls._secure_staging_dir(staging_root):
            return None

        try:
            staging_dir.mkdir(exist_ok=False)
            if cls._is_reparse_point(staging_dir):
                raise OSError("staging directory is a reparse point")
        except OSError as exc:
            logger.error(f"Could not create unique ProgramData staging: {exc}")
            cls._cleanup_tree(staging_dir)
            return None

        if not cls._secure_staging_dir(staging_dir):
            cls._cleanup_tree(staging_dir)
            return None
        return staging_dir

    @staticmethod
    def _is_reparse_point(path: Path) -> bool:
        """Return whether a Windows path is a reparse point, failing closed."""
        stat_result = path.stat(follow_symlinks=False)
        attributes = getattr(stat_result, "st_file_attributes", 0)
        return bool(attributes & 0x400)

    @staticmethod
    def _secure_staging_dir(staging_dir: Path) -> bool:
        """Apply and verify an Administrators/SYSTEM-only high-integrity ACL."""
        acl_command = [
            "icacls.exe",
            str(staging_dir),
            "/inheritance:r",
            "/grant:r",
            "*S-1-5-18:(OI)(CI)F",
            "*S-1-5-32-544:(OI)(CI)F",
        ]
        integrity_command = [
            "icacls.exe",
            str(staging_dir),
            "/setintegritylevel",
            "(OI)(CI)H",
        ]
        escaped_path = str(staging_dir).replace("'", "''")
        verify_script = (
            "$ErrorActionPreference='Stop';"
            f"$a=Get-Acl -LiteralPath '{escaped_path}';"
            "if(-not $a.AreAccessRulesProtected){exit 10};"
            "$r=@($a.Access);if($r.Count -ne 2){exit 11};"
            "$seen=@{};foreach($x in $r){"
            "$s=$x.IdentityReference.Translate("
            "[System.Security.Principal.SecurityIdentifier]).Value;"
            "if($s -ne 'S-1-5-18' -and $s -ne 'S-1-5-32-544'){exit 12};"
            "if($seen.ContainsKey($s) -or $x.IsInherited -or "
            "$x.AccessControlType -ne 'Allow'){exit 13};"
            "$full=[System.Security.AccessControl.FileSystemRights]::FullControl;"
            "if(($x.FileSystemRights -band $full) -ne $full){exit 14};"
            "$oi=[System.Security.AccessControl.InheritanceFlags]::ObjectInherit;"
            "$ci=[System.Security.AccessControl.InheritanceFlags]::ContainerInherit;"
            "if(($x.InheritanceFlags -band ($oi -bor $ci)) -ne ($oi -bor $ci))"
            "{exit 15};$seen[$s]=$true};"
            "if(-not $seen.ContainsKey('S-1-5-18') -or "
            "-not $seen.ContainsKey('S-1-5-32-544')){exit 16};"
            "if($a.Sddl -notmatch 'S:.*\\(ML;OICI;NW;;;HI\\)'){exit 17}"
        )
        commands = [
            acl_command,
            integrity_command,
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                verify_script,
            ],
        ]
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            for command in commands:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=SIGNATURE_TIMEOUT,
                    check=False,
                    creationflags=creation_flags,
                )
                if result.returncode != 0:
                    logger.error(
                        "Secure staging ACL/integrity operation failed: %s",
                        result.stderr.strip() or result.stdout.strip(),
                    )
                    return False
        except (OSError, subprocess.SubprocessError) as exc:
            logger.error(f"Could not secure ProgramData staging: {exc}")
            return False
        return True

    @staticmethod
    def _sha256_file(path: Path) -> str:
        """Return a SHA256 fingerprint for a file."""
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _spawn_relauncher_script(self, script_path: Path) -> bool:
        """Detach a previously prepared post-install relaunch script."""
        script_path = Path(script_path)
        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = (
                    subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                )
            subprocess.Popen(
                ["cmd.exe", "/d", "/c", str(script_path)],
                creationflags=creation_flags,
                close_fds=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"Relauncher spawned: {script_path}")
            return True
        except Exception as exc:
            logger.warning(f"Could not spawn relauncher: {exc}")
            return False

    @staticmethod
    def _create_relauncher_script(
        staging_dir: Path, installer_name: str
    ) -> Path:
        """Generate the post-install relauncher inside secure staging."""
        if INSTALLER_NAME_PATTERN.fullmatch(installer_name) is None:
            raise ValueError("Invalid installer filename for relaunch handoff")
        staging_dir = Path(staging_dir)
        if not staging_dir.is_dir():
            raise ValueError("Secure staging directory does not exist")
        script_path = staging_dir / "relaunch.cmd"

        uninstall_key_hklm = (
            rf"HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\{INNO_APP_ID}_is1"
        )
        uninstall_key_hkcu = (
            rf"HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{INNO_APP_ID}_is1"
        )

        expected_version = INSTALLER_NAME_PATTERN.fullmatch(installer_name).group(1)
        script = f"""@echo off
:: ClutchG auto-update relauncher (auto-generated; self-deletes)
:: The updater is the sole post-install relaunch owner.
setlocal enabledelayedexpansion
set "INSTALLER_NAME={installer_name}"
set "EXPECTED_VERSION={expected_version}"

:: Wait up to 30s for the exact installer process to appear after UAC.
set "STARTUP_WAIT=0"
:startup_loop
tasklist /fi "IMAGENAME eq %INSTALLER_NAME%" 2>nul | find /i "%INSTALLER_NAME%" >nul
if errorlevel 1 (
    set /a STARTUP_WAIT+=1
    if !STARTUP_WAIT! geq 30 goto cleanup
    timeout /t 1 /nobreak >nul
    goto startup_loop
)

:: Installer appeared. Wait up to 10 minutes for the exact process to finish.
set "INSTALL_WAIT=0"
:install_loop
tasklist /fi "IMAGENAME eq %INSTALLER_NAME%" 2>nul | find /i "%INSTALLER_NAME%" >nul
if not errorlevel 1 (
    set /a INSTALL_WAIT+=1
    if !INSTALL_WAIT! geq 600 goto cleanup
    timeout /t 1 /nobreak >nul
    goto install_loop
)

:: Relaunch only if the expected version was actually installed.
set "INSTALLED_VERSION="
for /f "tokens=2,*" %%a in ('reg query "{uninstall_key_hklm}" /v DisplayVersion 2^>nul ^| findstr DisplayVersion') do set "INSTALLED_VERSION=%%b"
if not defined INSTALLED_VERSION for /f "tokens=2,*" %%a in ('reg query "{uninstall_key_hkcu}" /v DisplayVersion 2^>nul ^| findstr DisplayVersion') do set "INSTALLED_VERSION=%%b"
if /i not "!INSTALLED_VERSION!"=="%EXPECTED_VERSION%" goto cleanup

:launch
:: Installer completed - give it a moment to release file handles
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

if defined CLUTCHG_EXE start "" "%CLUTCHG_EXE%"

:cleanup
endlocal
del /f /q "%~dp0{installer_name}" >nul 2>&1
(del /f /q "%~f0" & for %%D in ("%~dp0.") do rd "%%~fD") >nul 2>&1
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

    @staticmethod
    def _is_release_asset_url(url: str, expected_name: str) -> bool:
        """Require an exact GitHub release download URL for this repository."""
        try:
            parsed = urlparse(url)
        except (TypeError, ValueError):
            return False
        expected_prefix = f"/{GITHUB_OWNER}/{GITHUB_REPO}/releases/download/"
        parts = parsed.path.split("/")
        return (
            parsed.scheme == "https"
            and parsed.netloc.lower() == "github.com"
            and parsed.path.startswith(expected_prefix)
            and len(parts) >= 7
            and RELEASE_VERSION_PATTERN.fullmatch(unquote(parts[-2])) is not None
            and unquote(parts[-1]) == expected_name
            and not parsed.query
            and not parsed.fragment
        )

    def _find_installer_asset(
        self, assets: list, release_version: Optional[str] = None
    ) -> Optional[dict]:
        """Return exactly one installer matching version, URL, and asset state."""
        version = release_version or self.current_version
        expected_name = ASSET_PATTERN.format(version=version)
        matches = []
        for asset in assets:
            if asset.get("name") != expected_name:
                continue
            url = asset.get("browser_download_url", "")
            if not self._is_release_asset_url(url, expected_name):
                continue
            if asset.get("state", "uploaded") != "uploaded":
                continue
            matches.append(asset)
        return matches[0] if len(matches) == 1 else None

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

    @staticmethod
    def _cleanup_tree(path: Path) -> None:
        """Remove one updater-owned directory tree, ignoring errors."""
        try:
            if path.exists():
                shutil.rmtree(path)
        except OSError:
            pass

    @classmethod
    def _cleanup_download(cls, installer_path: Path) -> None:
        """Remove a download and its unique updater-owned directory."""
        installer_path = Path(installer_path)
        cls._cleanup_file(installer_path)
        parent = installer_path.parent
        if parent.name.startswith("clutchg-update-"):
            try:
                parent.rmdir()
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
