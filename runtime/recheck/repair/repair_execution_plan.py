# LATS P3
# Repair Execution Plan V1
#
# Purpose:
# - Convert repair queue into executable backfill plan
# - Estimate missing rows from gap_minutes
# - Classify gap severity
#
# Rules:
# - READ ONLY
# - No API fetch
# - No write to signal/result
# - No Memory update

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

REPAIR_DIR = ROOT / "runtime" / "recheck" / "repair"

QUEUE_FILE = REPAIR_DIR / "repair_queue.json"

VALIDATION_FILE = (
    REPAIR_DIR
    / "validation_reports"
    / "latest_repair_validation.json"
)

PLAN_DIR = REPAIR_DIR / "execution_plans"


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    PLAN_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
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


def classify_gap(minutes):
    try:
        minutes = float(minutes or 0)
    except Exception:
        minutes = 0

    if minutes < 60:
        return "GAP_SMALL"

    if minutes < 360:
        return "GAP_MEDIUM"

    if minutes < 1440:
        return "GAP_LARGE"

    return "GAP_CRITICAL"


def estimate_rows(gap_minutes, interval_minutes=15):
    try:
        gap_minutes = float(gap_minutes or 0)
    except Exception:
        return 0

    rows = int(gap_minutes // interval_minutes) - 1

    if rows < 0:
        return 0

    return rows


def extract_symbol(job):
    for key in ["from_signal_id", "to_signal_id"]:
        value = job.get(key) or ""

        if "_" in value:
            return value.split("_")[0]

    return "UNKNOWN"


def build_task(job):
    gap_minutes = job.get("gap_minutes")
    severity = classify_gap(gap_minutes)
    expected_rows = estimate_rows(gap_minutes)

    return {
        "job_id": job.get("job_id"),
        "job_type": job.get("job_type"),
        "status": "READY_FOR_FETCH_DRY_RUN",
        "symbol": extract_symbol(job),
        "timeframe": "15m",
        "from_time_ms": job.get("from_time_ms"),
        "to_time_ms": job.get("to_time_ms"),
        "from_time_text": job.get("from_time_text"),
        "to_time_text": job.get("to_time_text"),
        "gap_minutes": gap_minutes,
        "gap_severity": severity,
        "expected_missing_rows": expected_rows,
        "priority": job.get("priority", "HIGH"),
        "duplicate_guard_required": True,
        "row_level_duplicate_check_required": True,
        "api_fetch_enabled": False,
        "write_enabled": False,
        "memory_update": False,
        "candidate_update": False,
        "next_step": "WAIT_REAL_BACKFILL_ENGINE",
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
            "schema": "lats_p3_repair_execution_plan_v1",
            "created_at": now_text(),
            "status": "NOT_READY",
            "blockers": blockers,
            "tasks": [],
        }

    if not validation.get("ready_for_backfill"):
        blockers.append("VALIDATION_NOT_READY")

    tasks = [
        build_task(job)
        for job in queue.get("jobs", [])
        if job.get("status") == "WAIT_BACKFILL"
    ]

    status = "READY_FOR_BACKFILL_DRY_RUN"

    if blockers:
        status = "NOT_READY"

    return {
        "schema": "lats_p3_repair_execution_plan_v1",
        "created_at": now_text(),
        "status": status,
        "dry_run": True,
        "blockers": blockers,
        "summary": {
            "total_tasks": len(tasks),
            "total_expected_missing_rows": sum(
                t.get("expected_missing_rows", 0)
                for t in tasks
            ),
            "critical_tasks": len(
                [
                    t for t in tasks
                    if t.get("gap_severity") == "GAP_CRITICAL"
                ]
            ),
            "large_tasks": len(
                [
                    t for t in tasks
                    if t.get("gap_severity") == "GAP_LARGE"
                ]
            ),
        },
        "rules": {
            "read_only": True,
            "api_fetch_enabled": False,
            "write_signal_result_enabled": False,
            "memory_update": False,
            "hit_count_update": False,
            "candidate_confirm": False,
            "candidate_promote": False,
            "duplicate_guard_required": True,
        },
        "tasks": tasks,
    }


def save_plan(plan):
    ensure_dir()

    latest = PLAN_DIR / "latest_repair_execution_plan.json"
    stamped = PLAN_DIR / f"repair_execution_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(latest, plan)
    save_json(stamped, plan)

    return latest, stamped


def print_summary(plan):
    print("=" * 80)
    print("LATS P3 REPAIR EXECUTION PLAN V1")
    print("=" * 80)

    print("status:", plan.get("status"))
    print("dry_run:", plan.get("dry_run"))
    print("blockers:", plan.get("blockers"))

    summary = plan.get("summary", {})

    print("\n[SUMMARY]")
    print("total_tasks:", summary.get("total_tasks"))
    print("total_expected_missing_rows:", summary.get("total_expected_missing_rows"))
    print("large_tasks:", summary.get("large_tasks"))
    print("critical_tasks:", summary.get("critical_tasks"))

    print("\n[TASKS]")
    for task in plan.get("tasks", []):
        print(
            task.get("job_id"),
            "|",
            task.get("job_type"),
            "|",
            task.get("symbol"),
            "|",
            task.get("gap_severity"),
            "| expected_rows:",
            task.get("expected_missing_rows"),
        )

    print("\n[RULE]")
    print("Execution Plan is read-only")
    print("No API fetch / No write / No Memory update")


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
