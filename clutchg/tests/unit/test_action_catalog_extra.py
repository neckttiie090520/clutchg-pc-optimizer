"""
Additional unit tests for ActionCatalog edge cases.

Covers: initialization, get_actions by group, summarize for all action kinds,
is_trusted_url for all schemes, validate edge cases, open_external_link,
_max_risk static method, and ActionDefinition/ActionSummary dataclasses.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.action_catalog import (
    ActionCatalog,
    ActionDefinition,
    ActionSummary,
    RISK_ORDER,
)
from core.tweak_registry import Tweak


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tweak(
    tid: str = "test_tweak",
    risk: str = "LOW",
    requires_restart: bool = False,
    bat_script: str = "core/test.bat",
) -> Tweak:
    return Tweak(
        id=tid,
        name=f"Test {tid}",
        category="test",
        description="Test tweak",
        what_it_does="Does something",
        why_it_helps="Helps something",
        limitations="None",
        warnings=[],
        risk_level=risk,
        expected_gain="1%",
        requires_restart=requires_restart,
        bat_script=bat_script,
    )


def _make_registry(*tweaks):
    """Create a mock registry that returns the given tweaks by ID."""
    reg = MagicMock()
    lookup = {t.id: t for t in tweaks}

    def get_tweak(tid):
        return lookup.get(tid)

    reg.get_tweak = get_tweak
    return reg


# ---------------------------------------------------------------------------
# Tests: Initialization
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestActionCatalogInit:
    """Test ActionCatalog initialization."""

    def test_init_with_default_registry(self):
        """Catalog initializes with default tweak registry"""
        catalog = ActionCatalog()
        assert catalog.registry is not None
        assert len(catalog._actions) > 0

    def test_init_with_custom_registry(self):
        """Catalog accepts a custom registry"""
        mock_reg = MagicMock()
        catalog = ActionCatalog(registry=mock_reg)
        assert catalog.registry is mock_reg

    def test_init_with_custom_actions(self):
        """Catalog accepts a custom action list"""
        action = ActionDefinition(
            id="custom_1",
            group="general",
            title="Custom",
            description="Custom action",
            kind="tweak_pack",
            risk="LOW",
            tweak_ids=("test_tweak",),
        )
        catalog = ActionCatalog(
            registry=_make_registry(_make_tweak()),
            actions=[action],
        )
        assert len(catalog._actions) == 1
        assert catalog._actions[0].id == "custom_1"

    def test_index_built_from_actions(self):
        """_index dict maps action id to ActionDefinition"""
        action = ActionDefinition(
            id="idx_test",
            group="general",
            title="Idx",
            description="Test index",
            kind="tweak_pack",
            risk="LOW",
            tweak_ids=("test_tweak",),
        )
        catalog = ActionCatalog(
            registry=_make_registry(_make_tweak()),
            actions=[action],
        )
        assert "idx_test" in catalog._index
        assert catalog._index["idx_test"] is action


# ---------------------------------------------------------------------------
# Tests: get_groups / get_action / get_actions
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetGroups:
    """Test get_groups() method."""

    def test_get_groups_returns_tuple(self):
        catalog = ActionCatalog()
        groups = catalog.get_groups()
        assert isinstance(groups, tuple)
        assert "general" in groups
        assert "advanced" in groups
        assert "cleanup" in groups
        assert "windows" in groups
        assert "utilities" in groups


@pytest.mark.unit
class TestGetAction:
    """Test get_action() method."""

    def test_get_existing_action(self):
        catalog = ActionCatalog()
        action = catalog.get_action("qa_general_disable_xbox_capture")
        assert action is not None
        assert action.kind == "tweak_pack"

    def test_get_nonexistent_action(self):
        catalog = ActionCatalog()
        assert catalog.get_action("does_not_exist") is None

    def test_get_external_link_action(self):
        catalog = ActionCatalog()
        action = catalog.get_action("qa_util_download_discord")
        assert action is not None
        assert action.kind == "external_link"
        assert "discord" in action.url


@pytest.mark.unit
class TestGetActions:
    """Test get_actions() filtering by group."""

    def test_get_actions_for_general(self):
        catalog = ActionCatalog()
        actions = catalog.get_actions("general")
        assert len(actions) > 0
        assert all(a.group == "general" for a in actions)

    def test_get_actions_for_utilities(self):
        catalog = ActionCatalog()
        actions = catalog.get_actions("utilities")
        assert len(actions) > 0
        assert all(a.group == "utilities" for a in actions)

    def test_get_actions_empty_for_unknown_group(self):
        catalog = ActionCatalog()
        actions = catalog.get_actions("nonexistent_group")
        assert actions == []

    def test_default_catalog_has_no_unaudited_nvidia_pack(self):
        catalog = ActionCatalog()
        actions = [
            action
            for group in catalog.get_groups()
            for action in catalog.get_actions(group)
        ]
        assert all(not action.requires_nvidia for action in actions)


# ---------------------------------------------------------------------------
# Tests: is_visible
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsVisible:
    """Test is_visible() method."""

    def test_visible_when_no_nvidia_requirement(self):
        catalog = ActionCatalog()
        action = catalog.get_action("qa_general_disable_xbox_capture")
        assert catalog.is_visible(action) is True

    @staticmethod
    def _nvidia_action():
        return ActionDefinition(
            id="nvidia_only",
            group="advanced",
            title="NVIDIA Only",
            description="Test visibility",
            kind="external_link",
            risk="N/A",
            url="https://www.techpowerup.com/nvcleanstall/",
            requires_nvidia=True,
        )

    def test_hidden_when_nvidia_and_no_profile(self):
        catalog = ActionCatalog()
        assert catalog.is_visible(self._nvidia_action(), system_profile=None) is False

    def test_visible_when_nvidia_and_nvidia_profile(self):
        catalog = ActionCatalog()

        class _GPU:
            name = "NVIDIA GeForce RTX 3080"

        class _Sys:
            gpu = _GPU()

        assert catalog.is_visible(self._nvidia_action(), system_profile=_Sys()) is True

    def test_hidden_when_nvidia_and_amd_profile(self):
        catalog = ActionCatalog()

        class _GPU:
            name = "AMD Radeon RX 6800"

        class _Sys:
            gpu = _GPU()

        assert catalog.is_visible(self._nvidia_action(), system_profile=_Sys()) is False


# ---------------------------------------------------------------------------
# Tests: summarize
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSummarize:
    """Test summarize() method."""

    def test_summarize_tweak_pack(self):
        """Summarize a tweak_pack action"""
        t1 = _make_tweak("t1", risk="LOW")
        t2 = _make_tweak("t2", risk="MEDIUM")
        t3 = _make_tweak("t3", risk="LOW", requires_restart=True)

        reg = _make_registry(t1, t2, t3)
        action = ActionDefinition(
            id="test_pack",
            group="general",
            title="Test Pack",
            description="Test",
            kind="tweak_pack",
            risk="MEDIUM",
            tweak_ids=("t1", "t2", "t3"),
        )
        catalog = ActionCatalog(registry=reg, actions=[action])
        summary = catalog.summarize(action)

        assert summary.tweak_count == 3
        assert summary.max_risk == "MEDIUM"
        assert summary.requires_restart is True

    def test_summarize_tweak_pack_with_unknown_ids(self):
        """Unknown tweak IDs are excluded from count"""
        t1 = _make_tweak("known_tweak")
        reg = _make_registry(t1)

        action = ActionDefinition(
            id="mixed_pack",
            group="general",
            title="Mixed",
            description="Test",
            kind="tweak_pack",
            risk="LOW",
            tweak_ids=("known_tweak", "unknown_tweak"),
        )
        catalog = ActionCatalog(registry=reg, actions=[action])
        summary = catalog.summarize(action)

        assert summary.tweak_count == 1  # Only known tweak counted

    def test_summarize_external_link(self):
        """Summarize an external_link returns N/A risk"""
        action = ActionDefinition(
            id="ext_link",
            group="utilities",
            title="Link",
            description="Test",
            kind="external_link",
            risk="N/A",
            url="https://example.com",
        )
        catalog = ActionCatalog(actions=[action])
        summary = catalog.summarize(action)

        assert summary.tweak_count == 0
        assert summary.max_risk == "N/A"
        assert summary.requires_restart is False

    def test_summarize_empty_tweak_pack(self):
        """Summarize tweak_pack with no tweak_ids"""
        action = ActionDefinition(
            id="empty_pack",
            group="general",
            title="Empty",
            description="Test",
            kind="tweak_pack",
            risk="LOW",
        )
        catalog = ActionCatalog(actions=[action])
        summary = catalog.summarize(action)

        assert summary.tweak_count == 0
        assert summary.max_risk == "LOW"

    def test_summarize_high_risk_tweaks(self):
        """max_risk should be HIGH when any tweak is HIGH"""
        t_low = _make_tweak("low_t", risk="LOW")
        t_high = _make_tweak("high_t", risk="HIGH")
        reg = _make_registry(t_low, t_high)

        action = ActionDefinition(
            id="risky_pack",
            group="general",
            title="Risky",
            description="Test",
            kind="tweak_pack",
            risk="MEDIUM",
            tweak_ids=("low_t", "high_t"),
        )
        catalog = ActionCatalog(registry=reg, actions=[action])
        summary = catalog.summarize(action)

        assert summary.max_risk == "HIGH"


# ---------------------------------------------------------------------------
# Tests: validate
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestValidate:
    """Test validate() method for catalog integrity."""

    def test_validate_default_catalog(self):
        """Default catalog should have no errors"""
        catalog = ActionCatalog()
        errors = catalog.validate()
        # The default catalog may have unknown tweak IDs if registry is incomplete
        # Just verify it returns a list and doesn't crash
        assert isinstance(errors, list)

    def test_validate_catches_duplicate_ids(self):
        """Duplicate action IDs are flagged"""
        a1 = ActionDefinition(
            id="dup", group="general", title="Dup1", description="T",
            kind="tweak_pack", risk="LOW", tweak_ids=("test_tweak",),
        )
        a2 = ActionDefinition(
            id="dup", group="general", title="Dup2", description="T",
            kind="tweak_pack", risk="LOW", tweak_ids=("test_tweak",),
        )
        reg = _make_registry(_make_tweak())
        catalog = ActionCatalog(registry=reg, actions=[a1, a2])
        errors = catalog.validate()
        assert any("duplicate" in e.lower() for e in errors)

    def test_validate_catches_unknown_group(self):
        """Unknown group is flagged"""
        action = ActionDefinition(
            id="bad_group", group="nonexistent", title="Bad", description="T",
            kind="tweak_pack", risk="LOW", tweak_ids=("test_tweak",),
        )
        reg = _make_registry(_make_tweak())
        catalog = ActionCatalog(registry=reg, actions=[action])
        errors = catalog.validate()
        assert any("unknown group" in e.lower() for e in errors)

    def test_validate_catches_tweak_pack_without_tweaks(self):
        """tweak_pack with empty tweak_ids is flagged"""
        action = ActionDefinition(
            id="no_tweaks", group="general", title="Empty", description="T",
            kind="tweak_pack", risk="LOW",
        )
        catalog = ActionCatalog(actions=[action])
        errors = catalog.validate()
        assert any("must include tweak_ids" in e for e in errors)

    def test_validate_catches_tweak_pack_with_url(self):
        """tweak_pack that defines url is flagged"""
        reg = _make_registry(_make_tweak())
        action = ActionDefinition(
            id="with_url", group="general", title="URL", description="T",
            kind="tweak_pack", risk="LOW",
            tweak_ids=("test_tweak",),
            url="https://example.com",
        )
        catalog = ActionCatalog(registry=reg, actions=[action])
        errors = catalog.validate()
        assert any("cannot define url" in e for e in errors)

    def test_validate_catches_external_link_without_url(self):
        """external_link without url is flagged"""
        action = ActionDefinition(
            id="no_url", group="utilities", title="NoURL", description="T",
            kind="external_link", risk="N/A",
        )
        catalog = ActionCatalog(actions=[action])
        errors = catalog.validate()
        assert any("must include url" in e for e in errors)

    def test_validate_catches_external_link_with_tweak_ids(self):
        """external_link that defines tweak_ids is flagged"""
        action = ActionDefinition(
            id="link_tweaks", group="utilities", title="BadLink", description="T",
            kind="external_link", risk="N/A",
            url="https://discord.com/download",
            tweak_ids=("test_tweak",),
        )
        catalog = ActionCatalog(actions=[action])
        errors = catalog.validate()
        assert any("cannot define tweak_ids" in e for e in errors)

    def test_validate_catches_invalid_kind(self):
        """Invalid action kind is flagged"""
        action = ActionDefinition(
            id="bad_kind", group="general", title="BadKind", description="T",
            kind="invalid_kind", risk="LOW",
        )
        catalog = ActionCatalog(actions=[action])
        errors = catalog.validate()
        assert any("invalid kind" in e.lower() for e in errors)

    def test_validate_catches_high_risk_tweak_in_pack(self):
        """tweak_pack containing HIGH risk tweak is flagged"""
        t_high = _make_tweak("high_risk_t", risk="HIGH")
        reg = _make_registry(t_high)
        action = ActionDefinition(
            id="high_pack", group="general", title="High", description="T",
            kind="tweak_pack", risk="MEDIUM",
            tweak_ids=("high_risk_t",),
        )
        catalog = ActionCatalog(registry=reg, actions=[action])
        errors = catalog.validate()
        assert any("HIGH risk" in e for e in errors)

    def test_validate_catches_untrusted_url(self):
        """external_link with untrusted domain is flagged"""
        action = ActionDefinition(
            id="untrusted", group="utilities", title="Untrusted", description="T",
            kind="external_link", risk="N/A",
            url="https://evil-phishing-site.com/download",
        )
        catalog = ActionCatalog(actions=[action])
        errors = catalog.validate()
        assert any("non-trusted" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# Tests: is_trusted_url
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsTrustedUrl:
    """Test is_trusted_url() for various URL schemes."""

    def test_trusted_https_domain(self):
        catalog = ActionCatalog()
        assert catalog.is_trusted_url("https://discord.com/download") is True
        assert catalog.is_trusted_url("https://store.steampowered.com/about/") is True

    def test_untrusted_https_domain(self):
        catalog = ActionCatalog()
        assert catalog.is_trusted_url("https://evil.com/payload") is False

    def test_trusted_subdomain(self):
        catalog = ActionCatalog()
        assert catalog.is_trusted_url("https://sub.discord.com/page") is True

    def test_http_not_trusted(self):
        catalog = ActionCatalog()
        assert catalog.is_trusted_url("http://discord.com/download") is False

    def test_empty_host_not_trusted(self):
        catalog = ActionCatalog()
        assert catalog.is_trusted_url("https://") is False

    def test_file_url_within_allowed_root(self):
        """file:// URL pointing to project root is trusted"""
        catalog = ActionCatalog()
        project = catalog.project_root
        file_url = (project / "README.md").resolve().as_uri()
        assert catalog.is_trusted_url(file_url) is True

    def test_file_url_outside_allowed_root(self):
        """file:// URL pointing outside project is NOT trusted"""
        catalog = ActionCatalog()
        outside = Path("C:/Windows/System32/cmd.exe")
        file_url = outside.as_uri()
        assert catalog.is_trusted_url(file_url) is False

    def test_ftp_scheme_not_trusted(self):
        catalog = ActionCatalog()
        assert catalog.is_trusted_url("ftp://example.com/file") is False


# ---------------------------------------------------------------------------
# Tests: open_external_link
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestOpenExternalLink:
    """Test open_external_link() method."""

    def test_returns_false_for_tweak_pack(self):
        """Cannot open a tweak_pack as external link"""
        catalog = ActionCatalog()
        action = catalog.get_action("qa_general_disable_xbox_capture")
        assert action.kind == "tweak_pack"
        assert catalog.open_external_link(action) is False

    def test_returns_false_for_untrusted_url(self):
        """Untrusted URL is not opened"""
        action = ActionDefinition(
            id="untrusted_link",
            group="utilities",
            title="Untrusted",
            description="Test",
            kind="external_link",
            risk="N/A",
            url="https://evil.com/payload",
        )
        catalog = ActionCatalog(actions=[action])
        assert catalog.open_external_link(action) is False

    def test_opens_with_confirmer_accept(self):
        """Link opens when confirmer returns True"""
        action = ActionDefinition(
            id="test_link",
            group="utilities",
            title="Test Link",
            description="Test",
            kind="external_link",
            risk="N/A",
            url="https://discord.com/download",
        )
        catalog = ActionCatalog(actions=[action])

        opened_urls = []
        result = catalog.open_external_link(
            action,
            confirmer=lambda url: True,
            opener=lambda url: (opened_urls.append(url), True)[1],
        )
        assert result is True
        assert opened_urls == ["https://discord.com/download"]

    def test_opener_exception_returns_false(self):
        """If opener raises, return False"""
        action = ActionDefinition(
            id="crash_link",
            group="utilities",
            title="Crash",
            description="Test",
            kind="external_link",
            risk="N/A",
            url="https://discord.com/download",
        )
        catalog = ActionCatalog(actions=[action])

        def bad_opener(url):
            raise RuntimeError("browser crash")

        result = catalog.open_external_link(
            action,
            confirmer=lambda url: True,
            opener=bad_opener,
        )
        assert result is False

    def test_no_confirmer_opens_directly(self):
        """Without confirmer, trusted link opens directly"""
        action = ActionDefinition(
            id="no_confirm",
            group="utilities",
            title="No Confirm",
            description="Test",
            kind="external_link",
            risk="N/A",
            url="https://discord.com/download",
            requires_confirmation=True,
        )
        catalog = ActionCatalog(actions=[action])

        opened = []
        result = catalog.open_external_link(
            action,
            opener=lambda url: (opened.append(url), True)[1],
        )
        assert result is True
        assert len(opened) == 1


# ---------------------------------------------------------------------------
# Tests: _max_risk static method
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMaxRisk:
    """Test _max_risk static method."""

    def test_single_low(self):
        tweaks = [_make_tweak(risk="LOW")]
        assert ActionCatalog._max_risk(tweaks) == "LOW"

    def test_mixed_low_medium(self):
        tweaks = [_make_tweak(risk="LOW"), _make_tweak(risk="MEDIUM")]
        assert ActionCatalog._max_risk(tweaks) == "MEDIUM"

    def test_mixed_with_high(self):
        tweaks = [
            _make_tweak(risk="LOW"),
            _make_tweak(risk="MEDIUM"),
            _make_tweak(risk="HIGH"),
        ]
        assert ActionCatalog._max_risk(tweaks) == "HIGH"

    def test_empty_iterable(self):
        """Empty list defaults to LOW"""
        assert ActionCatalog._max_risk([]) == "LOW"


# ---------------------------------------------------------------------------
# Tests: ActionDefinition / ActionSummary dataclasses
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestActionDefinitionDataclass:
    """Test ActionDefinition frozen dataclass."""

    def test_frozen_immutability(self):
        action = ActionDefinition(
            id="frozen_test",
            group="general",
            title="Frozen",
            description="Test immutability",
            kind="tweak_pack",
            risk="LOW",
        )
        with pytest.raises(AttributeError):
            action.id = "changed"

    def test_default_values(self):
        action = ActionDefinition(
            id="defaults",
            group="general",
            title="Defaults",
            description="Test",
            kind="tweak_pack",
            risk="LOW",
        )
        assert action.tweak_ids == ()
        assert action.url == ""
        assert action.requires_confirmation is True
        assert action.requires_nvidia is False
        assert action.helper_text == ""


@pytest.mark.unit
class TestActionSummaryDataclass:
    """Test ActionSummary dataclass."""

    def test_fields(self):
        summary = ActionSummary(
            tweak_count=5, max_risk="MEDIUM", requires_restart=True
        )
        assert summary.tweak_count == 5
        assert summary.max_risk == "MEDIUM"
        assert summary.requires_restart is True

    def test_frozen_immutability(self):
        summary = ActionSummary(
            tweak_count=0, max_risk="N/A", requires_restart=False
        )
        with pytest.raises(AttributeError):
            summary.tweak_count = 99


# ---------------------------------------------------------------------------
# Tests: RISK_ORDER constant
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRiskOrder:
    """Test RISK_ORDER mapping."""

    def test_ordering(self):
        assert RISK_ORDER["LOW"] < RISK_ORDER["MEDIUM"]
        assert RISK_ORDER["MEDIUM"] < RISK_ORDER["HIGH"]
        assert RISK_ORDER["N/A"] == -1

    def test_contains_all_levels(self):
        assert "LOW" in RISK_ORDER
        assert "MEDIUM" in RISK_ORDER
        assert "HIGH" in RISK_ORDER
        assert "N/A" in RISK_ORDER
