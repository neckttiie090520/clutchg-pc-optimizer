import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARTIFACTS = [
    "docs/defense-readiness/README.md",
    "docs/defense-readiness/01-current-evidence-matrix-2026-07-30.md",
    "docs/defense-readiness/02-defense-question-bank-2026-07-30.md",
    "docs/defense-readiness/03-human-validation-checklist-2026-07-30.md",
    "docs/defense-readiness/04-github-project-backlog-draft-2026-07-30.md",
    "docs/defense-readiness/05-read-only-thesis-audit-appendix-2026-07-30.md",
    "docs/defense-readiness/06-evidence-manifest-2026-07-30.json",
    "docs/defense-readiness/07-thesis-toolchain-integration-plan-2026-07-30.md",
    "docs/defense-readiness/08-de-ai-editorial-protocol-2026-07-30.md",
    "docs/defense-readiness/09-github-sdlc-governance-2026-07-30.md",
    "docs/defense-readiness/10-de-ai-scan-raw-2026-07-30.json",
    "docs/defense-readiness/10-de-ai-scan-report-2026-07-30.md",
    "docs/defense-readiness/11-human-action-register-2026-07-30.md",
    "docs/defense-readiness/12-audit-handoff-2026-08-05.md",
    "docs/defense-readiness/13-regression-validation-report-2026-08-06.md",
    "clutchg/tests/vv/verify-recovery-mechanism.bat",
    "clutchg/tests/unit/test_recovery_mechanism_contract.py",
    "clutchg/tests/unit/test_plan_mode_gating.py",
    "clutchg/tests/unit/test_iso_metric_currency.py",
    "clutchg/tests/unit/test_registry_claim_fidelity.py",
    "clutchg/tests/unit/test_traceability_record_fidelity.py",
    "src/backup/backup-registry.bat",
    "src/safety/rollback.bat",
    "clutchg/src/core/batch_executor.py",
    "clutchg/src/core/backup_manager.py",
    "clutchg/src/core/action_catalog.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


records = []
missing = []
for relative in ARTIFACTS:
    path = ROOT / relative
    if not path.is_file():
        missing.append(relative)
        continue
    records.append(
        {"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size}
    )

manifest = {
    "schema_version": "1.1",
    "generated_at": "2026-08-06T00:00:00+07:00",
    "revision": git("rev-parse", "HEAD"),
    "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
    "commits_ahead_of_main": int(git("rev-list", "--count", "main..HEAD")),
    "environment": {
        "platform": "Windows-11-10.0.22631-SP0",
        "python": "3.14.2",
        "pytest": "9.0.2",
    },
    "validation": {
        "unit": {"passed": 1055, "failed": 0},
        "integration": {"passed": 23, "failed": 0},
        "combined": {"passed": 1078, "failed": 0},
        "e2e": {"collected": 64, "run": 0, "reason": "requires a live Windows desktop session"},
        "coverage_core_percent": 81,
        "coverage_repository_percent": 40,
        "coverage_core_target_percent": 70,
        "compileall": "clean",
        "targeted_rescan": {
            "remediated_paths": {"passed": 242, "failed": 0},
            "security_and_durability": {"passed": 131, "deselected": 916, "failed": 0},
            "truthfulness_guards": {"passed": 118, "failed": 0},
        },
        "readonly_runtime_vv": {
            "harness": "clutchg/tests/vv/verify-recovery-mechanism.bat",
            "passed": 3,
            "partial": 2,
            "failed": 0,
            "cases": {
                "existing_value": "PASS",
                "absent_value": "PASS",
                "absent_key": "PASS",
                "power_scheme": "PARTIAL:export-needs-elevation",
                "service_capture": "PARTIAL:sc-config-needs-elevation",
            },
        },
        "plan_mode": {
            "backup": "rc=0 state=COMMITTED success=19 failed=0",
            "rollback": "rc=0 state=COMPLETED success=18 failed=0",
            "host_mutated": False,
        },
    },
    "residual_risks": [
        {"id": "R-01", "summary": "bcdedit /import never executed against a real boot configuration", "status": "EXTERNAL_VERIFICATION_REQUIRED"},
        {"id": "R-02", "summary": "sc config restore never executed; capture verified, restore not", "status": "EXTERNAL_VERIFICATION_REQUIRED"},
        {"id": "R-03", "summary": "64 E2E tests collected, never run", "status": "EXTERNAL_VERIFICATION_REQUIRED"},
        {"id": "R-04", "summary": "packaged installer signing and release provenance unverified", "status": "EXTERNAL_VERIFICATION_REQUIRED"},
        {"id": "R-05", "summary": "journaled batch transactions accumulate without bound", "status": "OPEN_BY_DECISION"},
        {"id": "R-06", "summary": "max_backups config key is read by nothing; negative values accepted", "status": "OPEN_LOW"},
        {"id": "R-07", "summary": "findings verified by one reviewer, not two", "status": "OPEN"},
        {"id": "R-08", "summary": "updater 66%, system_info 64%, paths 63% core coverage; privilege- and platform-bounded", "status": "EXTERNAL_VERIFICATION_REQUIRED"},
        {"id": "R-09", "summary": "working tree not frozen; PR #13 into develop mergeable but not merged", "status": "HUMAN_SIGN_OFF_REQUIRED"},
    ],
    "scope": "Closing validation of the remediation recorded in 12-audit-handoff-2026-08-05.md.",
    "source_state": "Working tree not frozen; hashes identify artifact contents at this revision, not a signed release baseline.",
    "missing_artifacts": missing,
    "artifacts": records,
}

out = ROOT / "docs/defense-readiness/14-evidence-manifest-2026-08-06.json"
out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)}: {len(records)} artifacts, {len(missing)} missing")
for name in missing:
    print(f"  MISSING {name}")
