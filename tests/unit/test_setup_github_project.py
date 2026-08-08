"""Tests for the GitHub Project reconciliation utility.

These tests never invoke GitHub or require network access.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Sequence


SCRIPT_PATH = (
    Path(__file__).parents[2]
    / ".github"
    / "tools"
    / "setup_github_project.py"
)
SPEC = importlib.util.spec_from_file_location("setup_github_project", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def completed(payload=None, *, returncode=0, stderr=""):
    """Build a text-mode CompletedProcess matching the script runner contract."""
    stdout = "" if payload is None else json.dumps(payload)
    return subprocess.CompletedProcess([], returncode, stdout=stdout, stderr=stderr)


class FakeRunner:
    """Return queued responses and retain every argument vector."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls: list[list[str]] = []

    def __call__(self, args: Sequence[str]):
        self.calls.append(list(args))
        if not self.responses:
            raise AssertionError(f"Unexpected command: {args}")
        return self.responses.pop(0)

    def assert_consumed(self):
        self.assert_no_responses = not self.responses
        if self.responses:
            raise AssertionError(f"Unused responses: {len(self.responses)}")


class ProjectParsingTests(unittest.TestCase):
    def test_find_project_accepts_wrapped_project_list(self):
        payload = {
            "projects": [
                {"number": 2, "id": "PVT_other", "title": "Other"},
                {
                    "number": 7,
                    "id": "PVT_target",
                    "title": MODULE.PROJECT_TITLE,
                },
            ]
        }

        project = MODULE.find_project(payload)

        self.assertEqual(project.number, 7)
        self.assertEqual(project.project_id, "PVT_target")

    def test_extractors_ignore_malformed_entries(self):
        self.assertEqual(
            MODULE.field_names({"fields": [{"name": "Priority"}, {}, "bad"]}),
            {"Priority"},
        )
        self.assertEqual(
            MODULE.item_urls(
                {
                    "items": [
                        {"content": {"url": "https://example.test/1"}},
                        {"content": {}},
                        "bad",
                    ]
                }
            ),
            {"https://example.test/1"},
        )


class ProjectReconciliationTests(unittest.TestCase):
    def test_dry_run_is_deterministic_and_non_mutating(self):
        first = MODULE.dry_run_plan()
        second = MODULE.dry_run_plan()

        self.assertEqual(first, second)
        self.assertEqual(first["mode"], "dry-run")
        self.assertEqual(len(first["fields"]), len(MODULE.FIELD_SPECS))
        self.assertEqual(first["items"], list(MODULE.ITEM_URLS))

    def test_existing_complete_project_creates_nothing(self):
        fields = [{"name": name} for name, _ in MODULE.FIELD_SPECS]
        items = [{"content": {"url": url}} for url in MODULE.ITEM_URLS]
        runner = FakeRunner(
            [
                completed(
                    {
                        "projects": [
                            {
                                "number": 4,
                                "id": "PVT_existing",
                                "title": MODULE.PROJECT_TITLE,
                            }
                        ]
                    }
                ),
                completed(),
                completed({"fields": fields}),
                completed({"items": items}),
            ]
        )

        report = MODULE.ensure_project(runner)

        self.assertFalse(report["project_created"])
        self.assertEqual(report["fields_created"], [])
        self.assertEqual(report["items_added"], [])
        self.assertEqual(len(runner.calls), 4)
        self.assertFalse(any("field-create" in call for call in runner.calls))
        self.assertFalse(any("item-add" in call for call in runner.calls))
        runner.assert_consumed()

    def test_missing_project_is_created_and_reconciled(self):
        create_field_responses = [completed({"id": f"PVTF_{index}"}) for index, _ in enumerate(MODULE.FIELD_SPECS)]
        add_item_responses = [completed({"id": f"PVTI_{index}"}) for index, _ in enumerate(MODULE.ITEM_URLS)]
        runner = FakeRunner(
            [
                completed({"projects": []}),
                completed({"number": 3, "id": "PVT_new"}),
                completed(),
                completed({"fields": []}),
                *create_field_responses,
                completed({"items": []}),
                *add_item_responses,
            ]
        )

        report = MODULE.ensure_project(runner)

        self.assertTrue(report["project_created"])
        self.assertEqual(report["project_number"], 3)
        self.assertEqual(report["fields_created"], [name for name, _ in MODULE.FIELD_SPECS])
        self.assertEqual(report["items_added"], list(MODULE.ITEM_URLS))
        create_call = next(call for call in runner.calls if "create" in call)
        self.assertIn(MODULE.PROJECT_TITLE, create_call)
        runner.assert_consumed()

    def test_partial_state_only_creates_missing_resources(self):
        existing_field = MODULE.FIELD_SPECS[0][0]
        existing_item = MODULE.ITEM_URLS[0]
        missing_field_count = len(MODULE.FIELD_SPECS) - 1
        missing_item_count = len(MODULE.ITEM_URLS) - 1
        runner = FakeRunner(
            [
                completed(
                    {
                        "projects": [
                            {
                                "number": 9,
                                "id": "PVT_partial",
                                "title": MODULE.PROJECT_TITLE,
                            }
                        ]
                    }
                ),
                completed(returncode=1, stderr="repository is already linked"),
                completed({"fields": [{"name": existing_field}]}),
                *[completed({"id": f"field-{index}"}) for index in range(missing_field_count)],
                completed({"items": [{"content": {"url": existing_item}}]}),
                *[completed({"id": f"item-{index}"}) for index in range(missing_item_count)],
            ]
        )

        report = MODULE.ensure_project(runner)

        self.assertEqual(report["unchanged_fields"], [existing_field])
        self.assertEqual(report["unchanged_items"], [existing_item])
        self.assertNotIn(existing_field, report["fields_created"])
        self.assertNotIn(existing_item, report["items_added"])
        runner.assert_consumed()

    def test_missing_scope_fails_before_any_mutation(self):
        runner = FakeRunner(
            [
                completed(
                    returncode=1,
                    stderr="authentication token is missing required scopes [read:project]",
                )
            ]
        )

        with self.assertRaisesRegex(RuntimeError, "gh auth refresh"):
            MODULE.ensure_project(runner)

        self.assertEqual(len(runner.calls), 1)
        self.assertEqual(runner.calls[0][1:3], ["project", "list"])
        runner.assert_consumed()


if __name__ == "__main__":
    unittest.main()
