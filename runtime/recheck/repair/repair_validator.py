# LATS P3
# Repair Validator V1
#
# Purpose:
# - Validate repair readiness before backfill
# - Read Recheck Report
# - Read Repair Queue
# - Read Duplicate Guard Report
#
# Rules:
# - READ ONLY
# - No Memory update
# - No hit_count update
# - No candidate confirm/promote
# - No backfill execution

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

RECHECK_REPORT = (
    ROOT
    / "runtime"
    / "recheck"
    / "reports"
    / "latest_recheck_report.json"
)

REPAIR_QUEUE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "repair_queue.json"
)

DUPLICATE_REPORT = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "duplicate_reports"
    / "latest_duplicate_guard_report.json"
)

VALIDATION_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "validation_reports"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    VALIDATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def load_json(path):
    if not path.exists():
        return None

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_json(path, data):
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def build_validation():
    recheck = load_json(RECHECK_REPORT)
    queue = load_json(REPAIR_QUEUE)
    duplicate = load_json(DUPLICATE_REPORT)

    blockers = []
    warnings = []

    if not recheck:
        blockers.append("RECHECK_REPORT_MISSING")

    if not queue:
        blockers.append("REPAIR_QUEUE_MISSING")

    if not duplicate:
        blockers.append("DUPLICATE_GUARD_REPORT_MISSING")

    if blockers:
        return {
            "schema": "lats_p3_repair_validation_v1",
            "created_at": now_text(),
            "status": "NOT_READY",
            "ready_for_backfill": False,
            "blockers": blockers,
            "warnings": warnings,
            "rules": {
                "read_only": True,
                "memory_update": False,
                "backfill_execution": False,
            },
        }

    recheck_status = recheck.get("final_status")
    recheck_next_action = recheck.get("next_action")
    queue_jobs = queue.get("total_jobs", 0)
    waiting_backfill = queue.get("waiting_backfill", 0)
    duplicate_status = duplicate.get("status")

    if recheck_status != "FAIL":
        warnings.append("RECHECK_NOT_FAIL_STATE")

    if recheck_next_action != "RUN_BLOCKED_BACKFILL_REQUIRED":
        warnings.append("RECHECK_NEXT_ACTION_NOT_BACKFILL_REQUIRED")

    if queue_jobs <= 0:
        blockers.append("NO_REPAIR_JOBS")

    if waiting_backfill <= 0:
        blockers.append("NO_WAIT_BACKFILL_JOBS")

    if duplicate_status != "OK":
        blockers.append("DUPLICATE_GUARD_NOT_OK")

    for job in duplicate.get("checked_jobs", []):
        if not job.get("duplicate_guard"):
            blockers.append(
                f"DUPLICATE_GUARD_DISABLED:{job.get('job_id')}"
            )

        if job.get("memory_update"):
            blockers.append(
                f"MEMORY_UPDATE_TRUE:{job.get('job_id')}"
            )

        if job.get("candidate_update"):
            blockers.append(
                f"CANDIDATE_UPDATE_TRUE:{job.get('job_id')}"
            )

    ready = len(blockers) == 0

    return {
        "schema": "lats_p3_repair_validation_v1",
        "created_at": now_text(),
        "status": (
            "READY_FOR_BACKFILL"
            if ready
            else "NOT_READY"
        ),
        "ready_for_backfill": ready,
        "blockers": blockers,
        "warnings": warnings,
        "summary": {
            "recheck_status": recheck_status,
            "recheck_next_action": recheck_next_action,
            "repair_jobs": queue_jobs,
            "waiting_backfill": waiting_backfill,
            "duplicate_guard_status": duplicate_status,
        },
        "rules": {
            "read_only": True,
            "memory_update": False,
            "hit_count_update": False,
            "candidate_confirm": False,
            "candidate_promote": False,
            "backfill_execution": False,
        },
    }


def save_validation(report):
    ensure_dir()

    latest = VALIDATION_DIR / "latest_repair_validation.json"
    stamped = VALIDATION_DIR / f"repair_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(
        latest,
        report,
    )

    save_json(
        stamped,
        report,
    )

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 REPAIR VALIDATOR V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("ready_for_backfill:", report.get("ready_for_backfill"))
    print("blockers:", report.get("blockers"))
    print("warnings:", report.get("warnings"))

    summary = report.get("summary", {})

    print("\n[SUMMARY]")
    print("recheck_status:", summary.get("recheck_status"))
    print("recheck_next_action:", summary.get("recheck_next_action"))
    print("repair_jobs:", summary.get("repair_jobs"))
    print("waiting_backfill:", summary.get("waiting_backfill"))
    print("duplicate_guard_status:", summary.get("duplicate_guard_status"))

    print("\n[RULE]")
    print("Repair Validator is read-only")
    print("Backfill execution is not enabled in V1")


def main():
    report = build_validation()
    latest, stamped = save_validation(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if not report.get("ready_for_backfill"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
