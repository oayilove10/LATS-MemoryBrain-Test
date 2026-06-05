# LATS P3
# Backfill Runner V1 - DRY RUN
#
# Purpose:
# - Read repair queue
# - Read repair validation
# - Build backfill plan
# - DRY RUN only
#
# Rules:
# - No API fetch yet
# - No write to signal_data/result_data
# - No Memory update
# - No hit_count update
# - No candidate confirm/promote
# - Duplicate Guard required before real insert

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

REPAIR_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
)

QUEUE_FILE = (
    REPAIR_DIR
    / "repair_queue.json"
)

VALIDATION_FILE = (
    REPAIR_DIR
    / "validation_reports"
    / "latest_repair_validation.json"
)

BACKFILL_DIR = (
    REPAIR_DIR
    / "backfill_reports"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    BACKFILL_DIR.mkdir(
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


def build_backfill_task(job):
    return {
        "job_id": job.get("job_id"),
        "job_type": job.get("job_type"),
        "status": "DRY_RUN_PLANNED",
        "source": job.get("source"),
        "from_time_ms": job.get("from_time_ms"),
        "to_time_ms": job.get("to_time_ms"),
        "from_time_text": job.get("from_time_text"),
        "to_time_text": job.get("to_time_text"),
        "gap_minutes": job.get("gap_minutes"),
        "duplicate_guard_required": True,
        "row_level_duplicate_check_required": True,
        "memory_update": False,
        "candidate_update": False,
        "write_enabled": False,
        "api_fetch_enabled": False,
        "planned_action": (
            "FETCH_MISSING_ROWS_DRY_RUN_ONLY"
        ),
    }


def build_plan():
    queue = load_json(QUEUE_FILE)
    validation = load_json(VALIDATION_FILE)

    blockers = []

    if not queue:
        blockers.append("REPAIR_QUEUE_MISSING")

    if not validation:
        blockers.append("REPAIR_VALIDATION_MISSING")

    if blockers:
        return {
            "schema": "lats_p3_backfill_plan_v1",
            "created_at": now_text(),
            "status": "NOT_READY",
            "dry_run": True,
            "blockers": blockers,
            "tasks": [],
        }

    if not validation.get("ready_for_backfill"):
        blockers.append("VALIDATION_NOT_READY")

    jobs = queue.get("jobs", [])

    tasks = [
        build_backfill_task(job)
        for job in jobs
        if job.get("status") == "WAIT_BACKFILL"
    ]

    status = "READY_DRY_RUN"

    if blockers:
        status = "NOT_READY"

    if not tasks and not blockers:
        status = "NO_TASKS"

    return {
        "schema": "lats_p3_backfill_plan_v1",
        "created_at": now_text(),
        "status": status,
        "dry_run": True,
        "blockers": blockers,
        "summary": {
            "queue_jobs": queue.get("total_jobs"),
            "waiting_backfill": queue.get("waiting_backfill"),
            "planned_tasks": len(tasks),
            "validation_status": validation.get("status"),
        },
        "rules": {
            "api_fetch_enabled": False,
            "write_signal_result_enabled": False,
            "memory_update": False,
            "hit_count_update": False,
            "candidate_confirm": False,
            "candidate_promote": False,
            "duplicate_guard_required": True,
            "row_level_duplicate_check_required": True,
        },
        "tasks": tasks,
    }


def save_plan(plan):
    ensure_dir()

    latest = BACKFILL_DIR / "latest_backfill_plan.json"
    stamped = BACKFILL_DIR / f"backfill_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(
        latest,
        plan,
    )

    save_json(
        stamped,
        plan,
    )

    return latest, stamped


def print_summary(plan):
    print("=" * 80)
    print("LATS P3 BACKFILL RUNNER V1 - DRY RUN")
    print("=" * 80)

    print("status:", plan.get("status"))
    print("dry_run:", plan.get("dry_run"))
    print("blockers:", plan.get("blockers"))

    summary = plan.get("summary", {})

    print("\n[SUMMARY]")
    print("queue_jobs:", summary.get("queue_jobs"))
    print("waiting_backfill:", summary.get("waiting_backfill"))
    print("planned_tasks:", summary.get("planned_tasks"))
    print("validation_status:", summary.get("validation_status"))

    print("\n[TASKS]")
    for task in plan.get("tasks", []):
        print(
            task.get("job_id"),
            "|",
            task.get("job_type"),
            "|",
            task.get("status"),
            "| gap_minutes:",
            task.get("gap_minutes"),
        )

    print("\n[RULE]")
    print("DRY RUN only")
    print("No API fetch")
    print("No write to signal/result")
    print("No Memory update")


def main():
    plan = build_plan()
    latest, stamped = save_plan(plan)

    print_summary(plan)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if plan.get("status") == "NOT_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
