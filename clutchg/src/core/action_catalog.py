"""
Quick Actions catalog for Optimization Center (V1 practical scope).

This module intentionally keeps the model simple:
- tweak_pack: applies a predefined list of tweak IDs via ProfileManager.apply_tweaks()
- external_link: opens trusted curated links with confirmation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Literal, Optional, Sequence, Tuple
from urllib.parse import unquote, urlparse
import webbrowser

from core.paths import project_root as _project_root, repo_root as _repo_root
from core.tweak_registry import Tweak, TweakRegistry, get_tweak_registry


ActionKind = Literal["tweak_pack", "external_link"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "N/A"]

RISK_ORDER: Dict[str, int] = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "N/A": -1,
}


@dataclass(frozen=True)
class ActionDefinition:
    """Single quick action definition."""

    id: str
    group: str
    title: str
    description: str
    kind: ActionKind
    risk: RiskLevel
    tweak_ids: Tuple[str, ...] = field(default_factory=tuple)
    url: str = ""
    requires_confirmation: bool = True
    requires_nvidia: bool = False
    helper_text: str = ""


@dataclass(frozen=True)
class ActionSummary:
    """Computed metadata for confirmation and execution UX."""

    tweak_count: int
    max_risk: RiskLevel
    requires_restart: bool


class ActionCatalog:
    """Static quick actions catalog with validation and helper operations."""

    GROUPS: Tuple[str, ...] = ("general", "advanced", "cleanup", "windows", "utilities")

    TRUSTED_DOMAINS: Tuple[str, ...] = (
        "discord.com",
        "7-zip.org",
        "learn.microsoft.com",
        "techpowerup.com",
        "store.steampowered.com",
        "steampowered.com",
        "github.com",
    )

    def __init__(
        self,
        registry: Optional[TweakRegistry] = None,
        actions: Optional[Sequence[ActionDefinition]] = None,
    ) -> None:
        self.registry = registry or get_tweak_registry()
        self.project_root = _project_root()  # clutchg/
        self.repo_root = _repo_root()  # repository root
        self.allowed_file_roots = (
            self.project_root.resolve(),
            (self.repo_root / "docs").resolve(),
        )

        self._actions: Tuple[ActionDefinition, ...] = tuple(
            actions or self._build_actions()
        )
        self._index: Dict[str, ActionDefinition] = {a.id: a for a in self._actions}

    def _build_actions(self) -> Tuple[ActionDefinition, ...]:
        """Build V1 action mapping (decision-complete set)."""
        docs_user_guide = (
            (self.repo_root / "docs" / "16-user-guide-en.md").resolve().as_uri()
        )
        docs_quick_ref = (
            (self.repo_root / "docs" / "clutchg_quick_reference.md").resolve().as_uri()
        )
        clutchg_readme = (self.project_root / "README.md").resolve().as_uri()

        return (
            ActionDefinition(
                id="qa_general_gaming_baseline",
                group="general",
                title="Gaming Baseline",
                description="Balanced starter pack for common gaming scenarios.",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=(
                    "pwr_ultimate",
                    "tel_xbox_dvr",
                    "inp_mouse_accel",
                    "inp_keyboard",
                    "gpu_hags",
                    "net_throttling",
                ),
                helper_text="Recommended first action if you are unsure.",
            ),
            ActionDefinition(
                id="qa_general_telemetry_cleanup",
                group="general",
                title="Telemetry Cleanup",
                description="Reduce telemetry and background data collection.",
                kind="tweak_pack",
                risk="LOW",
                tweak_ids=(
                    "tel_diagtrack",
                    "tel_ads_suggestions",
                    "tel_activity",
                    "svc_telemetry",
                ),
            ),
            ActionDefinition(
                id="qa_general_input_responsiveness",
                group="general",
                title="Input Responsiveness",
                description="Lower input latency and improve control consistency.",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=("inp_mmcss", "inp_priority_sep", "inp_data_queue"),
            ),
            ActionDefinition(
                id="qa_advanced_memory_pack",
                group="advanced",
                title="Memory Pack",
                description="Memory-related tweaks for lower stutter on heavy workloads.",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=(
                    "mem_svchost",
                    "mem_paging_exec",
                    "mem_large_cache",
                    "mem_paging_combining",
                ),
            ),
            ActionDefinition(
                id="qa_advanced_bcd_latency_safe",
                group="advanced",
                title="BCDEdit Latency Pack",
                description="Safe subset of BCDEdit latency-oriented options.",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=(
                    "bcd_dynamic_tick",
                    "bcd_tsc_sync",
                    "bcd_x2apic",
                    "bcd_configaccess",
                ),
            ),
            ActionDefinition(
                id="qa_advanced_nvidia_consistency",
                group="advanced",
                title="NVIDIA Consistency Pack",
                description="NVIDIA-specific consistency tweaks (hidden on non-NVIDIA systems).",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=("gpu_nvidia_telemetry", "gpu_nvidia_pstate", "gpu_directx"),
                requires_nvidia=True,
            ),
            ActionDefinition(
                id="qa_cleanup_debloat_starter",
                group="cleanup",
                title="Debloat Starter",
                description="Remove common bloat and reduce startup overhead.",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=("cln_bloatware", "cln_onedrive"),
            ),
            ActionDefinition(
                id="qa_cleanup_storage_ntfs",
                group="cleanup",
                title="Storage / NTFS Tune",
                description="Lightweight filesystem tuning for responsiveness.",
                kind="tweak_pack",
                risk="LOW",
                tweak_ids=("cln_ntfs",),
            ),
            ActionDefinition(
                id="qa_windows_visual_performance",
                group="windows",
                title="Visual Performance",
                description="Reduce visual effects for snappier UI and lower GPU overhead.",
                kind="tweak_pack",
                risk="LOW",
                tweak_ids=(
                    "vis_animations",
                    "vis_transparency",
                    "vis_visual_fx",
                    "vis_drag_full",
                ),
            ),
            ActionDefinition(
                id="qa_windows_network_reliability",
                group="windows",
                title="Network Reliability",
                description="Conservative network adjustments for stable connectivity.",
                kind="tweak_pack",
                risk="MEDIUM",
                tweak_ids=("net_dns", "net_netbios", "net_window_size"),
            ),
            ActionDefinition(
                id="qa_util_download_discord",
                group="utilities",
                title="Download Discord",
                description="Open official Discord download page.",
                kind="external_link",
                risk="N/A",
                url="https://discord.com/download",
            ),
            ActionDefinition(
                id="qa_util_download_7zip",
                group="utilities",
                title="Download 7-Zip",
                description="Open official 7-Zip download page.",
                kind="external_link",
                risk="N/A",
                url="https://www.7-zip.org/download.html",
            ),
            ActionDefinition(
                id="qa_util_download_autoruns",
                group="utilities",
                title="Autoruns (Sysinternals)",
                description="Open official Autoruns download page by Microsoft.",
                kind="external_link",
                risk="N/A",
                url="https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns",
            ),
            ActionDefinition(
                id="qa_util_download_msi_utility_docs",
                group="utilities",
                title="MSI Utility Docs",
                description="Open MSI utility documentation page.",
                kind="external_link",
                risk="N/A",
                url="https://github.com/Singularitati/MSI-Utility",
            ),
            ActionDefinition(
                id="qa_util_download_nvcleanstall",
                group="utilities",
                title="NVCleanstall",
                description="Open NVCleanstall official page.",
                kind="external_link",
                risk="N/A",
                url="https://www.techpowerup.com/nvcleanstall/",
            ),
            ActionDefinition(
                id="qa_util_download_steam",
                group="utilities",
                title="Download Steam",
                description="Open Steam download page.",
                kind="external_link",
                risk="N/A",
                url="https://store.steampowered.com/about/",
            ),
            ActionDefinition(
                id="qa_util_source_github",
                group="utilities",
                title="Open Source (GitHub)",
                description="Open GitHub home for source navigation.",
                kind="external_link",
                risk="N/A",
                url="https://github.com/",
            ),
            ActionDefinition(
                id="qa_util_source_docs_user_guide",
                group="utilities",
                title="Open User Guide",
                description="Open local user guide markdown in your browser.",
                kind="external_link",
                risk="N/A",
                url=docs_user_guide,
            ),
            ActionDefinition(
                id="qa_util_source_docs_quick_ref",
                group="utilities",
                title="Open Quick Reference",
                description="Open local quick reference markdown in your browser.",
                kind="external_link",
                risk="N/A",
                url=docs_quick_ref,
            ),
            ActionDefinition(
                id="qa_util_source_readme",
                group="utilities",
                title="Open ClutchG README",
                description="Open local project README.",
                kind="external_link",
                risk="N/A",
                url=clutchg_readme,
            ),
        )

    def get_groups(self) -> Tuple[str, ...]:
        return self.GROUPS

    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        return self._index.get(action_id)

    def get_actions(
        self, group: str, system_profile: Optional[object] = None
    ) -> List[ActionDefinition]:
        return [
            a
            for a in self._actions
            if a.group == group and self.is_visible(a, system_profile)
        ]

    def is_visible(
        self, action: ActionDefinition, system_profile: Optional[object] = None
    ) -> bool:
        if not action.requires_nvidia:
            return True
        if not system_profile:
            return False
        gpu_name = getattr(getattr(system_profile, "gpu", None), "name", "")
        return "nvidia" in str(gpu_name).lower()

    def summarize(self, action: ActionDefinition) -> ActionSummary:
        if action.kind != "tweak_pack":
            return ActionSummary(tweak_count=0, max_risk="N/A", requires_restart=False)

        tweaks = [self.registry.get_tweak(tid) for tid in action.tweak_ids]
        valid_tweaks = [t for t in tweaks if t is not None]
        max_risk = self._max_risk(valid_tweaks)
        requires_restart = any(t.requires_restart for t in valid_tweaks)
        return ActionSummary(
            tweak_count=len(valid_tweaks),
            max_risk=max_risk,
            requires_restart=requires_restart,
        )

    def validate(self) -> List[str]:
        """Validate catalog integrity. Returns list of errors."""
        errors: List[str] = []
        seen_ids = set()

        for action in self._actions:
            if action.id in seen_ids:
                errors.append(f"Duplicate action id: {action.id}")
            seen_ids.add(action.id)

            if action.group not in self.GROUPS:
                errors.append(
                    f"Action '{action.id}' has unknown group '{action.group}'"
                )

            if action.kind == "tweak_pack":
                if not action.tweak_ids:
                    errors.append(f"Action '{action.id}' must include tweak_ids")
                if action.url:
                    errors.append(f"Action '{action.id}' tweak_pack cannot define url")
                for tid in action.tweak_ids:
                    tweak = self.registry.get_tweak(tid)
                    if not tweak:
                        errors.append(
                            f"Action '{action.id}' references unknown tweak '{tid}'"
                        )
                        continue
                    if tweak.risk_level.upper() == "HIGH":
                        errors.append(
                            f"Action '{action.id}' includes HIGH risk tweak '{tid}'"
                        )

            elif action.kind == "external_link":
                if action.tweak_ids:
                    errors.append(
                        f"Action '{action.id}' external_link cannot define tweak_ids"
                    )
                if not action.url:
                    errors.append(
                        f"Action '{action.id}' external_link must include url"
                    )
                elif not self.is_trusted_url(action.url):
                    errors.append(
                        f"Action '{action.id}' uses non-trusted url '{action.url}'"
                    )
            else:
                errors.append(f"Action '{action.id}' has invalid kind '{action.kind}'")

        return errors

    def open_external_link(
        self,
        action: ActionDefinition,
        confirmer: Optional[Callable[[str], bool]] = None,
        opener: Optional[Callable[[str], bool]] = None,
    ) -> bool:
        """
        Open external link with optional confirmation gate.

        Returns True when link open is attempted and accepted, else False.
        """
        if action.kind != "external_link":
            return False
        if not self.is_trusted_url(action.url):
            return False

        should_open = True
        if action.requires_confirmation and confirmer:
            should_open = bool(confirmer(action.url))
        if not should_open:
            return False

        def default_opener(url: str) -> bool:
            import os
            import platform

            try:
                # os.startfile is more reliable on Windows
                if platform.system() == "Windows":
                    os.startfile(url)
                    return True
            except Exception:
                pass

            # Fallback
            try:
                return webbrowser.open(url, new=2)
            except Exception:
                return False

        open_fn = opener or default_opener
        try:
            return bool(open_fn(action.url))
        except Exception:
            return False

    def is_trusted_url(self, url: str) -> bool:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()

        if scheme == "https":
            host = (parsed.netloc or "").lower()
            if not host:
                return False
            return any(
                host == d or host.endswith(f".{d}") for d in self.TRUSTED_DOMAINS
            )

        if scheme == "file":
            candidate = self._path_from_file_url(url)
            if not candidate:
                return False
            return any(
                candidate.is_relative_to(root) for root in self.allowed_file_roots
            )

        return False

    def _path_from_file_url(self, url: str) -> Optional[Path]:
        try:
            parsed = urlparse(url)
            raw_path = unquote(parsed.path)
            normalized = raw_path.lstrip("/") if raw_path.startswith("/") else raw_path
            return Path(normalized).resolve()
        except Exception:
            return None

    @staticmethod
    def _max_risk(tweaks: Iterable[Tweak]) -> RiskLevel:
        max_level = "LOW"
        for tweak in tweaks:
            level = tweak.risk_level.upper()
            if RISK_ORDER.get(level, 0) > RISK_ORDER.get(max_level, 0):
                max_level = level
        return max_level  # type: ignore[return-value]
