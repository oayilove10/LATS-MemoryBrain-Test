# LATS P3
# Backfill Fetch Planner V1
#
# Purpose:
# - Read candidate duplicate check
# - Group INSERT_ALLOWED candidates by job/symbol/timeframe/job_type
# - Build API fetch plan
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

CHECK_FILE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_candidate_checks"
    / "latest_backfill_candidate_duplicate_check.json"
)

FETCH_PLAN_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_fetch_plans"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    FETCH_PLAN_DIR.mkdir(parents=True, exist_ok=True)


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


def group_candidates(candidates):
    groups = {}

    for row in candidates:
        if row.get("decision") != "INSERT_ALLOWED":
            continue

        key = (
            row.get("job_id"),
            row.get("job_type"),
            row.get("symbol"),
            row.get("timeframe"),
        )

        groups.setdefault(key, []).append(row)

    return groups


def build_fetch_task(key, rows):
    job_id, job_type, symbol, timeframe = key

    timestamps = sorted(
        int(r.get("signal_time_ms"))
        for r in rows
        if r.get("signal_time_ms") is not None
    )

    return {
        "job_id": job_id,
        "job_type": job_type,
        "symbol": symbol,
        "timeframe": timeframe,
        "status": "READY_FOR_API_FETCH_TEST",
        "candidate_rows": len(rows),
        "start_time_ms": timestamps[0] if timestamps else None,
        "end_time_ms": timestamps[-1] if timestamps else None,
        "api": {
            "provider": "BINANCE",
            "market": "FUTURES",
            "endpoint_type": "KLINES",
            "interval": timeframe,
            "api_fetch_enabled": False,
        },
        "rules": {
            "write_enabled": False,
            "memory_update": False,
            "duplicate_guard_required": True,
            "validate_after_fetch": True,
        },
    }


def build_plan():
    check = load_json(CHECK_FILE, {})

    blockers = []

    if not check:
        blockers.append("CANDIDATE_DUPLICATE_CHECK_MISSING")

    if check and check.get("status") != "OK":
        blockers.append("CANDIDATE_DUPLICATE_CHECK_NOT_OK")

    candidates = check.get("checked_candidates", [])

    groups = group_candidates(candidates)

    fetch_tasks = [
        build_fetch_task(key, rows)
        for key, rows in groups.items()
    ]

    status = "READY_FOR_API_FETCH_TEST"

    if blockers:
        status = "NOT_READY"

    return {
        "schema": "lats_p3_backfill_fetch_planner_v1",
        "created_at": now_text(),
        "status": status,
        "blockers": blockers,
        "dry_run": True,
        "summary": {
            "insert_allowed_candidates": check.get("summary", {}).get("insert_allowed", 0),
            "duplicate_skip": check.get("summary", {}).get("duplicate_skip", 0),
            "fetch_tasks": len(fetch_tasks),
            "total_candidate_rows": sum(
                t.get("candidate_rows", 0)
                for t in fetch_tasks
            ),
        },
        "rules": {
            "api_fetch_enabled": False,
            "write_signal_result_enabled": False,
            "memory_update": False,
            "duplicate_guard_required": True,
        },
        "fetch_tasks": fetch_tasks,
    }


def save_plan(plan):
    ensure_dir()

    latest = FETCH_PLAN_DIR / "latest_backfill_fetch_plan.json"
    stamped = FETCH_PLAN_DIR / f"backfill_fetch_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(latest, plan)
    save_json(stamped, plan)

    return latest, stamped


def print_summary(plan):
    print("=" * 80)
    print("LATS P3 BACKFILL FETCH PLANNER V1")
    print("=" * 80)

    print("status:", plan.get("status"))
    print("dry_run:", plan.get("dry_run"))
    print("blockers:", plan.get("blockers"))

    s = plan.get("summary", {})

    print("\n[SUMMARY]")
    print("insert_allowed_candidates:", s.get("insert_allowed_candidates"))
    print("duplicate_skip:", s.get("duplicate_skip"))
    print("fetch_tasks:", s.get("fetch_tasks"))
    print("total_candidate_rows:", s.get("total_candidate_rows"))

    print("\n[TASKS]")
    for task in plan.get("fetch_tasks", []):
        print(
            task.get("job_id"),
            "|",
            task.get("job_type"),
            "|",
            task.get("symbol"),
            "|",
            task.get("timeframe"),
            "| rows:",
            task.get("candidate_rows"),
            "|",
            task.get("status"),
        )

    print("\n[RULE]")
    print("No API fetch")
    print("No write")
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
