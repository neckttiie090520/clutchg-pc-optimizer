"""
Unit tests for execution dialog generic job title resolution.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gui.components.execution_dialog import ExecutionDialog


@pytest.mark.unit
class TestExecutionDialog:

    def test_resolve_job_title_from_profile_like_object(self):
        class ProfileLike:
            display_name = "Safe Mode"

        assert ExecutionDialog.resolve_job_title(ProfileLike()) == "Safe Mode"

    def test_resolve_job_title_from_name_object(self):
        class NamedJob:
            name = "Quick Action"

        assert ExecutionDialog.resolve_job_title(NamedJob()) == "Quick Action"

    def test_resolve_job_title_from_string(self):
        assert ExecutionDialog.resolve_job_title("Custom (4 tweaks)") == "Custom (4 tweaks)"
