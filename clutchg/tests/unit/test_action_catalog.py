"""
Unit tests for Quick Actions catalog.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.action_catalog import (
    ActionCatalog,
    ActionDefinition,
    TweakExecutionCatalog,
    TweakExecutionContract,
)


@pytest.mark.unit
class TestActionCatalog:

    def test_validation_fails_for_unknown_tweak_id(self):
        bad_actions = [
            ActionDefinition(
                id="bad_action",
                group="general",
                title="Bad",
                description="Invalid tweak id",
                kind="tweak_pack",
                risk="LOW",
                tweak_ids=("unknown_tweak_id",),
            )
        ]
        catalog = ActionCatalog(actions=bad_actions)
        errors = catalog.validate()
        assert any("unknown tweak" in err.lower() for err in errors)

    def test_risk_aggregation_for_audited_pack(self):
        catalog = ActionCatalog()
        action = catalog.get_action("qa_general_disable_xbox_capture")
        assert action is not None
        summary = catalog.summarize(action)
        assert summary.tweak_count == 1
        assert summary.max_risk == "LOW"
        assert isinstance(summary.requires_restart, bool)

    def test_default_quick_tweak_packs_are_resolvable(self):
        scripts_dir = Path(__file__).parents[3] / "src"
        action_catalog = ActionCatalog()
        execution_catalog = TweakExecutionCatalog(scripts_dir)

        for group in action_catalog.get_groups():
            for action in action_catalog.get_actions(group):
                if action.kind != "tweak_pack":
                    continue
                plan, errors = execution_catalog.resolve(action.tweak_ids)
                assert errors == (), action.id
                assert plan, action.id

    def test_external_link_requires_confirmation_gate(self):
        catalog = ActionCatalog()
        action = catalog.get_action("qa_util_download_discord")
        assert action is not None

        opened = []

        def _opener(url: str) -> bool:
            opened.append(url)
            return True

        blocked = catalog.open_external_link(
            action,
            confirmer=lambda _url: False,
            opener=_opener,
        )
        assert blocked is False
        assert opened == []

        allowed = catalog.open_external_link(
            action,
            confirmer=lambda _url: True,
            opener=_opener,
        )
        assert allowed is True
        assert opened == [action.url]

    def test_execution_contracts_validate_against_real_dispatchers(self):
        scripts_dir = Path(__file__).parents[3] / "src"

        errors = TweakExecutionCatalog(scripts_dir).validate()

        assert errors == []

    def test_high_risk_contract_requires_explicit_consent(self):
        scripts_dir = Path(__file__).parents[3] / "src"
        catalog = TweakExecutionCatalog(scripts_dir)

        blocked_plan, blocked_errors = catalog.resolve(["bcd_hypervisor"])
        allowed_plan, allowed_errors = catalog.resolve(
            ["bcd_hypervisor"],
            consented_contract_ids=["disable-hypervisor"],
        )

        assert blocked_plan == ()
        assert any("explicit consent" in error for error in blocked_errors)
        assert allowed_errors == ()
        assert allowed_plan[0].accepted_argument == ":apply_advanced_tweaks"

    def test_no_irreversible_contract_is_exposed(self):
        scripts_dir = Path(__file__).parents[3] / "src"
        catalog = TweakExecutionCatalog(scripts_dir)

        assert all(contract.reversible for contract in catalog.contracts)

    def test_missing_recovery_component_rejects_contract(self):
        scripts_dir = Path(__file__).parents[3] / "src"
        bad_contract = TweakExecutionContract(
            id="bad-recovery",
            tweak_ids=("tel_xbox_dvr",),
            script="core/telemetry-blocker.bat",
            target_label=":apply_xbox_dvr",
            persistent_effects=("test effect",),
            recovery_components=("missing_component",),
        )
        catalog = TweakExecutionCatalog(scripts_dir, contracts=(bad_contract,))

        assert any("missing recovery components" in error for error in catalog.validate())
        plan, errors = catalog.resolve(["tel_xbox_dvr"])
        assert plan == ()
        assert any("recovery components are unavailable" in error for error in errors)

    def test_high_risk_tweaks_not_in_quick_actions(self):
        catalog = ActionCatalog()
        excluded = {"bcd_hypervisor"}

        quick_tweak_ids = set()
        for group in catalog.get_groups():
            for action in catalog.get_actions(group):
                if action.kind == "tweak_pack":
                    quick_tweak_ids.update(action.tweak_ids)

        assert excluded.isdisjoint(quick_tweak_ids)
