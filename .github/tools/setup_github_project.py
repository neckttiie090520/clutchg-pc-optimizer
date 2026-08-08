#!/usr/bin/env python3
"""Create or reconcile the ClutchG defense-readiness GitHub Project.

The command is dry-run by default. Pass ``--apply`` only after granting the
GitHub CLI token the ``project`` scope.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Callable, Sequence

OWNER = "neckttiie090520"
REPOSITORY = "neckttiie090520/clutchg-pc-optimizer"
PROJECT_TITLE = "ClutchG Defense Readiness"
ITEM_URLS = tuple(
    [f"https://github.com/{REPOSITORY}/issues/{number}" for number in range(5, 12)]
    + [f"https://github.com/{REPOSITORY}/pull/12"]
)

FIELD_SPECS = (
    ("Workflow state", "Triage,Ready,In Progress,Review,External Gate,Done"),
    ("Priority", "P0,P1,P2,P3"),
    (
        "Evidence state",
        "Planned,Automated,Historical,External Required,Human Sign-off,Accepted",
    ),
    (
        "SDLC phase",
        "Requirements,Design,Implementation,Integration,Testing,Deployment,Maintenance",
    ),
    (
        "ISO work product",
        "Project Plan,SRS,SDD,Test Plan,Test Record,Traceability,Change Request,Progress,Configuration,User Manual,Research Protocol",
    ),
    (
        "Owner role",
        "Researcher,Reviewer,Advisor,Statistician,Ethics Authority,CI,VM Operator",
    ),
)

Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class ProjectRef:
    number: int
    project_id: str
    title: str


def run_command(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Run one GitHub CLI command without invoking a shell."""
    return subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def decode_json(result: subprocess.CompletedProcess[str], action: str) -> Any:
    """Decode successful JSON output or raise an actionable error."""
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        if "project" in detail.lower() and "scope" in detail.lower():
            detail += (
                "\nAuthorize once with: gh auth refresh -h github.com "
                "-s read:project,project"
            )
        raise RuntimeError(f"{action} failed: {detail}")
    try:
        return json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{action} returned invalid JSON") from exc


def project_entries(payload: Any) -> list[dict[str, Any]]:
    """Normalize the payload returned by ``gh project list``."""
    if isinstance(payload, list):
        return [entry for entry in payload if isinstance(entry, dict)]
    if isinstance(payload, dict):
        for key in ("projects", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [entry for entry in value if isinstance(entry, dict)]
    return []


def find_project(payload: Any, title: str = PROJECT_TITLE) -> ProjectRef | None:
    """Return the existing named project, if present."""
    for entry in project_entries(payload):
        if entry.get("title") != title:
            continue
        number = entry.get("number")
        project_id = entry.get("id", "")
        if isinstance(number, int):
            return ProjectRef(number, str(project_id), title)
    return None


def field_names(payload: Any) -> set[str]:
    """Extract existing field names from ``gh project field-list`` output."""
    entries = payload.get("fields", []) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return set()
    return {
        str(entry["name"])
        for entry in entries
        if isinstance(entry, dict) and entry.get("name")
    }


def item_urls(payload: Any) -> set[str]:
    """Extract issue/PR URLs from ``gh project item-list`` output."""
    entries = payload.get("items", []) if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        return set()
    urls: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        content = entry.get("content", entry)
        if isinstance(content, dict) and content.get("url"):
            urls.add(str(content["url"]))
    return urls


def dry_run_plan() -> dict[str, Any]:
    """Return the deterministic desired state without network access."""
    return {
        "mode": "dry-run",
        "owner": OWNER,
        "repository": REPOSITORY,
        "project": PROJECT_TITLE,
        "fields": [
            {"name": name, "type": "SINGLE_SELECT", "options": options.split(",")}
            for name, options in FIELD_SPECS
        ],
        "items": list(ITEM_URLS),
        "next": (
            "Authorize project scope, then rerun with --apply: "
            "gh auth refresh -h github.com -s read:project,project"
        ),
    }


def ensure_project(runner: Runner = run_command) -> dict[str, Any]:
    """Create missing Project resources and return a reconciliation report."""
    payload = decode_json(
        runner(["gh", "project", "list", "--owner", OWNER, "--format", "json"]),
        "list projects",
    )
    project = find_project(payload)
    created_project = False
    if project is None:
        created = decode_json(
            runner(
                [
                    "gh",
                    "project",
                    "create",
                    "--owner",
                    OWNER,
                    "--title",
                    PROJECT_TITLE,
                    "--format",
                    "json",
                ]
            ),
            "create project",
        )
        number = created.get("number")
        if not isinstance(number, int):
            raise RuntimeError("create project did not return a numeric project number")
        project = ProjectRef(number, str(created.get("id", "")), PROJECT_TITLE)
        created_project = True

    number = str(project.number)
    link_result = runner(
        ["gh", "project", "link", number, "--owner", OWNER, "--repo", REPOSITORY]
    )
    if link_result.returncode != 0:
        detail = (link_result.stderr or link_result.stdout).lower()
        if "already" not in detail:
            raise RuntimeError(f"link repository failed: {detail.strip()}")

    fields_payload = decode_json(
        runner(
            [
                "gh",
                "project",
                "field-list",
                number,
                "--owner",
                OWNER,
                "--format",
                "json",
            ]
        ),
        "list project fields",
    )
    existing_fields = field_names(fields_payload)
    created_fields: list[str] = []
    for name, options in FIELD_SPECS:
        if name in existing_fields:
            continue
        decode_json(
            runner(
                [
                    "gh",
                    "project",
                    "field-create",
                    number,
                    "--owner",
                    OWNER,
                    "--name",
                    name,
                    "--data-type",
                    "SINGLE_SELECT",
                    "--single-select-options",
                    options,
                    "--format",
                    "json",
                ]
            ),
            f"create field {name}",
        )
        created_fields.append(name)

    items_payload = decode_json(
        runner(
            [
                "gh",
                "project",
                "item-list",
                number,
                "--owner",
                OWNER,
                "--format",
                "json",
                "--limit",
                "100",
            ]
        ),
        "list project items",
    )
    existing_urls = item_urls(items_payload)
    added_items: list[str] = []
    for url in ITEM_URLS:
        if url in existing_urls:
            continue
        decode_json(
            runner(
                [
                    "gh",
                    "project",
                    "item-add",
                    number,
                    "--owner",
                    OWNER,
                    "--url",
                    url,
                    "--format",
                    "json",
                ]
            ),
            f"add project item {url}",
        )
        added_items.append(url)

    return {
        "mode": "apply",
        "project_number": project.number,
        "project_url": f"https://github.com/users/{OWNER}/projects/{project.number}",
        "project_created": created_project,
        "fields_created": created_fields,
        "items_added": added_items,
        "unchanged_fields": sorted(
            existing_fields.intersection(name for name, _ in FIELD_SPECS)
        ),
        "unchanged_items": sorted(existing_urls.intersection(ITEM_URLS)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan or apply the ClutchG defense-readiness GitHub Project"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create/reconcile the Project. Without this flag, print a dry-run plan.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = ensure_project() if args.apply else dry_run_plan()
    except (OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
