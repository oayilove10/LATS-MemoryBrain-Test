# LATS P3
# Backfill Fetch Validator V1
#
# Purpose:
# - Validate fetch plan before API fetch
#
# Rules:
# - READ ONLY
# - No API fetch
# - No write
# - No Memory update

import json
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

PLAN_FILE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_fetch_plans"
    / "latest_backfill_fetch_plan.json"
)

REPORT_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_fetch_validation"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_task(task):
    errors = []

    if not task.get("symbol"):
        errors.append("SYMBOL_MISSING")

    if not task.get("timeframe"):
        errors.append("TIMEFRAME_MISSING")

    start_ms = task.get("start_time_ms")
    end_ms = task.get("end_time_ms")

    if start_ms is None:
        errors.append("START_TIME_MISSING")

    if end_ms is None:
        errors.append("END_TIME_MISSING")

    if (
        start_ms is not None
        and end_ms is not None
        and start_ms >= end_ms
    ):
        errors.append("INVALID_TIME_RANGE")

    if task.get("candidate_rows", 0) <= 0:
        errors.append("NO_CANDIDATE_ROWS")

    return {
        "job_id": task.get("job_id"),
        "job_type": task.get("job_type"),
        "symbol": task.get("symbol"),
        "timeframe": task.get("timeframe"),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def build_report():
    plan = load_json(PLAN_FILE, {})

    blockers = []

    if not plan:
        blockers.append("FETCH_PLAN_MISSING")

    results = []

    for task in plan.get("fetch_tasks", []):
        results.append(validate_task(task))

    failed = [
        r for r in results
        if r["status"] == "FAIL"
    ]

    status = "READY_FOR_API_FETCH"

    if blockers or failed:
        status = "BLOCK_API_FETCH"

    return {
        "schema": "lats_p3_backfill_fetch_validator_v1",
        "created_at": now_text(),
        "status": status,
        "blockers": blockers,
        "failed_tasks": len(failed),
        "validated_tasks": len(results),
        "api_fetch_enabled": False,
        "memory_update": False,
        "results": results,
    }


def save_report(report):
    ensure_dir()

    latest = REPORT_DIR / "latest_backfill_fetch_validation.json"
    stamped = REPORT_DIR / (
        f"backfill_fetch_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    save_json(latest, report)
    save_json(stamped, report)

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 BACKFILL FETCH VALIDATOR V1")
    print("=" * 80)

    print("status:", report["status"])
    print("blockers:", report["blockers"])
    print("validated_tasks:", report["validated_tasks"])
    print("failed_tasks:", report["failed_tasks"])

    print("\n[TASKS]")
    for r in report["results"]:
        print(
            r["job_id"],
            "|",
            r["job_type"],
            "|",
            r["status"],
            "|",
            r["errors"],
        )

    print("\n[RULE]")
    print("No API fetch")
    print("No write")
    print("No Memory update")


def main():
    report = build_report()
    latest, stamped = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if report["status"] == "BLOCK_API_FETCH":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
