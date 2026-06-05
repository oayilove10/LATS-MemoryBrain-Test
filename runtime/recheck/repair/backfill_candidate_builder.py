# LATS P3
# Backfill Candidate Builder V1
#
# Purpose:
# - Read Repair Execution Plan
# - Generate missing timestamp candidates
# - No API fetch
# - No write to signal/result
# - No Memory update

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

REPAIR_DIR = ROOT / "runtime" / "recheck" / "repair"

EXECUTION_PLAN = (
    REPAIR_DIR
    / "execution_plans"
    / "latest_repair_execution_plan.json"
)

CANDIDATE_DIR = (
    REPAIR_DIR
    / "backfill_candidates"
)

INTERVAL_MS = 15 * 60 * 1000


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)


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


def normalize_to_next_open_time(ms):
    """
    Convert close-time style xxx999 to next candle open-time style xxx000.
    Example:
    1779728399999 -> next 15m open -> 1779729300000
    """
    ms = int(ms or 0)
    return ((ms // INTERVAL_MS) + 1) * INTERVAL_MS


def normalize_to_open_time(ms):
    """
    Convert any timestamp to its candle open-time boundary.
    """
    ms = int(ms or 0)
    return (ms // INTERVAL_MS) * INTERVAL_MS


def build_missing_timestamps(task):
    start = int(task.get("from_time_ms") or 0)
    end = int(task.get("to_time_ms") or 0)

    timestamps = []

    current = normalize_to_next_open_time(start)
    end_open = normalize_to_open_time(end)

    while current < end_open:
        timestamps.append(current)
        current += INTERVAL_MS

    return timestamps


def build_candidate_rows(task):
    timestamps = build_missing_timestamps(task)

    rows = []

    symbol = task.get("symbol", "UNKNOWN")
    timeframe = task.get("timeframe", "15m")

    for ts in timestamps:
        rows.append(
            {
                "candidate_id": f"{symbol}_{timeframe}_{ts}",
                "job_id": task.get("job_id"),
                "job_type": task.get("job_type"),
                "symbol": symbol,
                "timeframe": timeframe,
                "signal_time_ms": ts,
                "status": "WAIT_API_FETCH",
                "api_fetch_enabled": False,
                "write_enabled": False,
                "memory_update": False,
            }
        )

    return rows


def build_report():
    plan = load_json(EXECUTION_PLAN, {})

    blockers = []

    if not plan:
        blockers.append("EXECUTION_PLAN_MISSING")

    if plan and plan.get("status") == "NOT_READY":
        blockers.append("EXECUTION_PLAN_NOT_READY")

    tasks = plan.get("tasks", [])

    candidates = []

    for task in tasks:
        candidates.extend(
            build_candidate_rows(task)
        )

    status = "READY_FOR_API_FETCH_TEST"

    if blockers:
        status = "NOT_READY"

    return {
        "schema": "lats_p3_backfill_candidate_builder_v1",
        "created_at": now_text(),
        "status": status,
        "blockers": blockers,
        "dry_run": True,
        "summary": {
            "tasks": len(tasks),
            "candidate_rows": len(candidates),
        },
        "rules": {
            "api_fetch_enabled": False,
            "write_signal_result_enabled": False,
            "memory_update": False,
            "duplicate_guard_required": True,
        },
        "candidates": candidates,
    }


def save_report(report):
    ensure_dir()

    latest = CANDIDATE_DIR / "latest_backfill_candidates.json"
    stamped = CANDIDATE_DIR / f"backfill_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(latest, report)
    save_json(stamped, report)

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 BACKFILL CANDIDATE BUILDER V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("dry_run:", report.get("dry_run"))
    print("blockers:", report.get("blockers"))

    summary = report.get("summary", {})

    print("\n[SUMMARY]")
    print("tasks:", summary.get("tasks"))
    print("candidate_rows:", summary.get("candidate_rows"))

    print("\n[SAMPLE]")
    for row in report.get("candidates", [])[:5]:
        print(
            row.get("candidate_id"),
            "|",
            row.get("job_type"),
            "|",
            row.get("status"),
        )

    print("\n[RULE]")
    print("No API fetch")
    print("No write to signal/result")
    print("No Memory update")


def main():
    report = build_report()
    latest, stamped = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if report.get("status") == "NOT_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
