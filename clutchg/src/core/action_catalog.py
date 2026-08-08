"""
Quick Actions catalog for Optimization Center (V1 practical scope).

This module intentionally keeps the model simple:
- tweak_pack: applies a predefined list of tweak IDs via ProfileManager.apply_tweaks()
- external_link: opens trusted curated links with confirmation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, FrozenSet, Iterable, List, Literal, Optional, Sequence, Tuple
from urllib.parse import unquote, urlparse
import re
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


@dataclass(frozen=True)
class TweakExecutionContract:
    """Audited contract for one atomic or explicitly composite tweak action."""

    id: str
    tweak_ids: Tuple[str, ...]
    script: str
    target_label: str
    persistent_effects: Tuple[str, ...]
    recovery_components: Tuple[str, ...] = field(default_factory=tuple)
    risk: RiskLevel = "LOW"
    reversible: bool = True
    requires_explicit_consent: bool = False


@dataclass(frozen=True)
class ResolvedTweakAction:
    """Immutable executable action produced by contract preflight."""

    contract: TweakExecutionContract
    accepted_argument: str


class TweakExecutionCatalog:
    """Canonical fail-closed boundary between tweak metadata and batch scripts."""

    _DISPATCH_PATTERN = re.compile(
        r'^\s*if\s+"%~1"\s*==\s*"([^"]+)"\s+goto\s+(:[^\s&]+)',
        re.IGNORECASE,
    )
    _RECOVERY_COMPONENTS_PATTERN = re.compile(
        r"\becho\s+components=([A-Za-z0-9_,]+)",
        re.IGNORECASE,
    )

    def __init__(
        self,
        scripts_dir: Path,
        contracts: Optional[Sequence[TweakExecutionContract]] = None,
    ) -> None:
        self.scripts_dir = Path(scripts_dir)
        self.contracts = tuple(contracts or self._build_contracts())
        self._by_id = {contract.id: contract for contract in self.contracts}
        self._by_tweak_id = {
            tweak_id: contract
            for contract in self.contracts
            for tweak_id in contract.tweak_ids
        }

    @property
    def standard_tweak_ids(self) -> FrozenSet[str]:
        """Tweaks safe to expose without a separate explicit-consent flow."""
        standard_ids = set()
        for contract in self.contracts:
            if contract.requires_explicit_consent:
                continue
            _, errors = self.resolve(contract.tweak_ids)
            if not errors:
                standard_ids.update(contract.tweak_ids)
        return frozenset(standard_ids)

    @staticmethod
    def _build_contracts() -> Tuple[TweakExecutionContract, ...]:
        """Return locally audited exact-scope contracts only."""
        return (
            TweakExecutionContract(
                id="disable-xbox-dvr",
                tweak_ids=("tel_xbox_dvr",),
                script="core/telemetry-blocker.bat",
                target_label=":apply_xbox_dvr",
                persistent_effects=(
                    "disable Game DVR and capture policies",
                    "disable Game Bar overlay and presence writer",
                    "keep Windows Game Mode enabled",
                ),
                recovery_components=(
                    "value_gameconfig_dvr",
                    "value_policy_gamedvr",
                    "value_policy_allowgamedvr",
                    "value_machine_gamedvr",
                    "value_user_gamedvr",
                    "value_gamebar_nexus",
                    "value_gamebar_startup",
                    "value_presencewriter_activation",
                    "value_gamebar_allowgamemode",
                    "value_gamebar_automode",
                ),
                risk="LOW",
            ),
            TweakExecutionContract(
                id="disable-copilot-recall",
                tweak_ids=("tel_copilot",),
                script="core/debloater.bat",
                target_label=":apply_copilot",
                persistent_effects=(
                    "disable Copilot for the current user and machine",
                    "disable Recall AI data analysis",
                    "hide the Copilot taskbar button",
                ),
                recovery_components=(
                    "value_copilot_hkcu",
                    "value_copilot_hklm",
                    "value_windowsai_hkcu",
                    "value_windowsai_hklm",
                    "value_copilot_button",
                ),
                risk="LOW",
            ),
            TweakExecutionContract(
                id="disable-hypervisor",
                tweak_ids=("bcd_hypervisor",),
                script="core/bcdedit-manager.bat",
                target_label=":apply_advanced_tweaks",
                persistent_effects=("set hypervisorlaunchtype off",),
                recovery_components=("bcd",),
                risk="HIGH",
                requires_explicit_consent=True,
            ),
        )

    @classmethod
    def get_dispatch_routes(cls, script_path: Path) -> Dict[str, FrozenSet[str]]:
        """Map normalized target labels to accepted command-line arguments."""
        routes: Dict[str, set[str]] = {}
        content = script_path.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            match = cls._DISPATCH_PATTERN.match(line)
            if match:
                argument, target_label = match.groups()
                routes.setdefault(target_label.lower(), set()).add(argument)
        return {label: frozenset(args) for label, args in routes.items()}

    @classmethod
    def get_recovery_components(cls, backup_script_path: Path) -> FrozenSet[str]:
        """Read the exact committed-component contract from the backup engine."""
        content = backup_script_path.read_text(encoding="utf-8", errors="ignore")
        matches = cls._RECOVERY_COMPONENTS_PATTERN.findall(content)
        if len(matches) != 1:
            return frozenset()
        return frozenset(component for component in matches[0].split(",") if component)

    def validate(self) -> List[str]:
        """Validate IDs, rollback claims, script existence, and dispatcher routes."""
        errors: List[str] = []
        seen_contract_ids = set()
        seen_tweak_ids = set()
        backup_script = self.scripts_dir / "backup" / "backup-registry.bat"
        if not backup_script.is_file():
            errors.append(f"Missing recovery contract script: {backup_script}")
            recovery_components = frozenset()
        else:
            recovery_components = self.get_recovery_components(backup_script)
            if not recovery_components:
                errors.append("Recovery component manifest is missing or ambiguous")
        for contract in self.contracts:
            if contract.id in seen_contract_ids:
                errors.append(f"Duplicate execution contract id: {contract.id}")
            seen_contract_ids.add(contract.id)
            if not contract.tweak_ids:
                errors.append(f"Execution contract '{contract.id}' has no tweak IDs")
            for tweak_id in contract.tweak_ids:
                if tweak_id in seen_tweak_ids:
                    errors.append(f"Tweak '{tweak_id}' appears in multiple contracts")
                seen_tweak_ids.add(tweak_id)
            if not contract.persistent_effects:
                errors.append(f"Execution contract '{contract.id}' has no effect scope")
            if contract.reversible and not contract.recovery_components:
                errors.append(
                    f"Reversible execution contract '{contract.id}' has no "
                    "recovery components"
                )
            if not contract.reversible and contract.recovery_components:
                errors.append(
                    f"Irreversible execution contract '{contract.id}' declares "
                    "recovery components"
                )
            missing_recovery = sorted(
                set(contract.recovery_components) - recovery_components
            )
            if missing_recovery:
                errors.append(
                    f"Execution contract '{contract.id}' references missing recovery "
                    f"components: {', '.join(missing_recovery)}"
                )

            script_path = self.scripts_dir / contract.script
            if not script_path.is_file():
                errors.append(f"Missing contract script: {contract.script}")
                continue
            try:
                routes = self.get_dispatch_routes(script_path)
            except OSError as exc:
                errors.append(f"Cannot read {contract.script}: {exc}")
                continue
            accepted = routes.get(contract.target_label.lower(), frozenset())
            if len(accepted) != 1:
                errors.append(
                    f"No unique dispatcher route to {contract.target_label} "
                    f"in {contract.script}"
                )
        return errors

    def resolve(
        self,
        tweak_ids: Sequence[str],
        consented_contract_ids: Iterable[str] = (),
    ) -> Tuple[Tuple[ResolvedTweakAction, ...], Tuple[str, ...]]:
        """Resolve selected tweak IDs to exact actions, returning errors fail-closed."""
        selected = set(tweak_ids)
        consented = set(consented_contract_ids)
        errors: List[str] = []
        contracts: List[TweakExecutionContract] = []

        for tweak_id in dict.fromkeys(tweak_ids):
            contract = self._by_tweak_id.get(tweak_id)
            if contract is None:
                errors.append(f"No audited execution contract for tweak: {tweak_id}")
                continue
            if contract not in contracts:
                contracts.append(contract)

        backup_script = self.scripts_dir / "backup" / "backup-registry.bat"
        if not backup_script.is_file():
            errors.append(f"Missing recovery contract script: {backup_script}")
            recovery_components = frozenset()
        else:
            recovery_components = self.get_recovery_components(backup_script)
            if not recovery_components:
                errors.append("Recovery component manifest is missing or ambiguous")

        resolved: List[ResolvedTweakAction] = []
        for contract in contracts:
            omitted = sorted(set(contract.tweak_ids) - selected)
            if omitted:
                errors.append(
                    f"Contract '{contract.id}' requires complete selection: "
                    f"{', '.join(omitted)}"
                )
                continue
            if contract.requires_explicit_consent and contract.id not in consented:
                errors.append(f"Contract '{contract.id}' requires explicit consent")
                continue
            missing_recovery = sorted(
                set(contract.recovery_components) - recovery_components
            )
            if missing_recovery:
                errors.append(
                    f"Contract '{contract.id}' recovery components are unavailable: "
                    f"{', '.join(missing_recovery)}"
                )
                continue
            script_path = self.scripts_dir / contract.script
            if not script_path.is_file():
                errors.append(f"Missing contract script: {contract.script}")
                continue
            try:
                routes = self.get_dispatch_routes(script_path)
            except OSError as exc:
                errors.append(f"Cannot read {contract.script}: {exc}")
                continue
            accepted = routes.get(contract.target_label.lower(), frozenset())
            if len(accepted) != 1:
                errors.append(
                    f"No unique dispatcher route to {contract.target_label} "
                    f"in {contract.script}"
                )
                continue
            resolved.append(
                ResolvedTweakAction(contract=contract, accepted_argument=next(iter(accepted)))
            )

        if errors:
            return (), tuple(errors)
        return tuple(resolved), ()


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
        execution_catalog: Optional[TweakExecutionCatalog] = None,
    ) -> None:
        self.registry = registry or get_tweak_registry()
        self.project_root = _project_root()  # clutchg/
        self.repo_root = _repo_root()  # repository root
        self.execution_catalog = execution_catalog or TweakExecutionCatalog(
            self.repo_root / "src"
        )
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
        local_documents = (
            (
                "qa_util_source_docs_user_guide",
                "Open User Guide",
                "Open the local user guide in your browser.",
                self.repo_root / "docs" / "16-user-guide-en.md",
            ),
            (
                "qa_util_source_docs_quick_ref",
                "Open Quick Reference",
                "Open the local quick reference in your browser.",
                self.repo_root / "docs" / "clutchg_quick_reference.md",
            ),
            (
                "qa_util_source_readme",
                "Open ClutchG README",
                "Open the local project README.",
                self.project_root / "README.md",
            ),
        )

        # Packaged installs ship the executable, _internal and batch_scripts only.
        # Advertising a file:// link to a document that was never installed would
        # present a broken action, so each local document is offered only when the
        # file is actually present in this deployment.
        document_actions = tuple(
            ActionDefinition(
                id=action_id,
                group="utilities",
                title=title,
                description=description,
                kind="external_link",
                risk="N/A",
                url=path.resolve().as_uri(),
            )
            for action_id, title, description, path in local_documents
            if path.is_file()
        )

        return (
            ActionDefinition(
                id="qa_general_disable_xbox_capture",
                group="general",
                title="Disable Xbox Capture",
                description="Disable Game DVR and Game Bar capture while keeping Game Mode on.",
                kind="tweak_pack",
                risk="LOW",
                tweak_ids=("tel_xbox_dvr",),
                helper_text="Audited action with exact pre-change recovery snapshot.",
            ),
            ActionDefinition(
                id="qa_general_disable_copilot_recall",
                group="general",
                title="Disable Copilot & Recall",
                description="Disable Copilot and Recall policies and hide the taskbar button.",
                kind="tweak_pack",
                risk="LOW",
                tweak_ids=("tel_copilot",),
                helper_text="Audited action with exact pre-change recovery snapshot.",
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
        ) + document_actions

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
                _, resolution_errors = self.execution_catalog.resolve(action.tweak_ids)
                for error in resolution_errors:
                    errors.append(f"Action '{action.id}' is not executable: {error}")

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
