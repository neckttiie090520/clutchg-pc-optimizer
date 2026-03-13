"""
Unit tests for Quick Actions catalog.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.action_catalog import ActionCatalog, ActionDefinition


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

    def test_risk_aggregation_for_memory_pack(self):
        catalog = ActionCatalog()
        action = catalog.get_action("qa_advanced_memory_pack")
        assert action is not None
        summary = catalog.summarize(action)
        assert summary.tweak_count == 4
        assert summary.max_risk == "MEDIUM"
        assert isinstance(summary.requires_restart, bool)

    def test_nvidia_action_visibility(self):
        catalog = ActionCatalog()

        class _GPU:
            def __init__(self, name):
                self.name = name

        class _System:
            def __init__(self, gpu_name):
                self.gpu = _GPU(gpu_name)

        non_nvidia = _System("AMD Radeon RX 7600")
        nvidia = _System("NVIDIA GeForce RTX 4070")

        advanced_non_nvidia = {a.id for a in catalog.get_actions("advanced", non_nvidia)}
        advanced_nvidia = {a.id for a in catalog.get_actions("advanced", nvidia)}

        assert "qa_advanced_nvidia_consistency" not in advanced_non_nvidia
        assert "qa_advanced_nvidia_consistency" in advanced_nvidia

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

    def test_high_risk_tweaks_not_in_quick_actions(self):
        catalog = ActionCatalog()
        excluded = {"pwr_spectre", "gpu_vbs", "bcd_hypervisor"}

        quick_tweak_ids = set()
        for group in catalog.get_groups():
            for action in catalog.get_actions(group):
                if action.kind == "tweak_pack":
                    quick_tweak_ids.update(action.tweak_ids)

        assert excluded.isdisjoint(quick_tweak_ids)
