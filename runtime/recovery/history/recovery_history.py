# LATS P3
# Recovery History V1
#
# Purpose:
# - Store recovery history from latest Recheck / Repair pipeline
# - Keep gap history
# - Keep repair history
# - Keep runtime stop history placeholder
#
# Rules:
# - READ ONLY to Memory Brain
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

EXECUTION_PLAN = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "execution_plans"
    / "latest_repair_execution_plan.json"
)

HISTORY_DIR = (
    ROOT
    / "runtime"
    / "recovery"
    / "history"
)

GAP_HISTORY = HISTORY_DIR / "gap_history.json"
REPAIR_HISTORY = HISTORY_DIR / "repair_history.json"
RUNTIME_STOP_HISTORY = HISTORY_DIR / "runtime_stop_history.json"


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)
    except Exception:
        return default


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


def append_unique(history, item, key_fields):
    for old in history:
        matched = True

        for key in key_fields:
            if old.get(key) != item.get(key):
                matched = False
                break

        if matched:
            return history, False

    history.append(item)
    return history, True


def build_gap_entries(recheck):
    entries = []

    sr = recheck.get("signal_result_gap_check", {})
    signal_report = sr.get("signal_report", {})
    result_report = sr.get("result_report", {})

    for gap in signal_report.get("gaps", []):
        entries.append(
            {
                "history_type": "GAP_HISTORY",
                "source": "signal_data",
                "gap_type": "SIGNAL_GAP",
                "from_signal_id": gap.get("from_signal_id"),
                "to_signal_id": gap.get("to_signal_id"),
                "from_time_ms": gap.get("from_time_ms"),
                "to_time_ms": gap.get("to_time_ms"),
                "from_time_text": gap.get("from_time_text"),
                "to_time_text": gap.get("to_time_text"),
                "gap_minutes": gap.get("gap_minutes"),
                "severity": classify_gap(gap.get("gap_minutes")),
                "detected_at": now_text(),
                "status": "WAIT_BACKFILL",
                "reason": "UNKNOWN",
                "memory_update": False,
            }
        )

    for gap in result_report.get("gaps", []):
        entries.append(
            {
                "history_type": "GAP_HISTORY",
                "source": "result_data",
                "gap_type": "RESULT_GAP",
                "from_signal_id": gap.get("from_signal_id"),
                "to_signal_id": gap.get("to_signal_id"),
                "from_time_ms": gap.get("from_time_ms"),
                "to_time_ms": gap.get("to_time_ms"),
                "from_time_text": gap.get("from_time_text"),
                "to_time_text": gap.get("to_time_text"),
                "gap_minutes": gap.get("gap_minutes"),
                "severity": classify_gap(gap.get("gap_minutes")),
                "detected_at": now_text(),
                "status": "WAIT_BACKFILL",
                "reason": "UNKNOWN",
                "memory_update": False,
            }
        )

    return entries


def build_repair_entries(queue, plan):
    entries = []

    tasks_by_job = {}

    for task in plan.get("tasks", []):
        tasks_by_job[task.get("job_id")] = task

    for job in queue.get("jobs", []):
        task = tasks_by_job.get(job.get("job_id"), {})

        entries.append(
            {
                "history_type": "REPAIR_HISTORY",
                "job_id": job.get("job_id"),
                "job_type": job.get("job_type"),
                "status": job.get("status"),
                "source": job.get("source"),
                "from_signal_id": job.get("from_signal_id"),
                "to_signal_id": job.get("to_signal_id"),
                "gap_minutes": job.get("gap_minutes"),
                "severity": classify_gap(job.get("gap_minutes")),
                "expected_missing_rows": task.get("expected_missing_rows"),
                "symbol": task.get("symbol", "UNKNOWN"),
                "timeframe": task.get("timeframe", "15m"),
                "created_at": job.get("created_at"),
                "history_updated_at": now_text(),
                "duplicate_guard": job.get("duplicate_guard"),
                "memory_update": False,
                "candidate_update": False,
                "backfill_status": "NOT_EXECUTED",
            }
        )

    return entries


def update_history():
    ensure_dir()

    recheck = load_json(RECHECK_REPORT, {})
    queue = load_json(REPAIR_QUEUE, {})
    plan = load_json(EXECUTION_PLAN, {})

    gap_history = load_json(GAP_HISTORY, [])
    repair_history = load_json(REPAIR_HISTORY, [])
    runtime_stop_history = load_json(RUNTIME_STOP_HISTORY, [])

    gap_entries = build_gap_entries(recheck)
    repair_entries = build_repair_entries(queue, plan)

    gap_added = 0
    repair_added = 0

    for item in gap_entries:
        gap_history, added = append_unique(
            gap_history,
            item,
            [
                "source",
                "from_signal_id",
                "to_signal_id",
                "gap_type",
            ],
        )

        if added:
            gap_added += 1

    for item in repair_entries:
        repair_history, added = append_unique(
            repair_history,
            item,
            [
                "job_id",
            ],
        )

        if added:
            repair_added += 1

    save_json(GAP_HISTORY, gap_history)
    save_json(REPAIR_HISTORY, repair_history)
    save_json(RUNTIME_STOP_HISTORY, runtime_stop_history)

    return {
        "status": "OK",
        "created_at": now_text(),
        "gap_total": len(gap_history),
        "gap_added": gap_added,
        "repair_total": len(repair_history),
        "repair_added": repair_added,
        "runtime_stop_total": len(runtime_stop_history),
        "files": {
            "gap_history": str(GAP_HISTORY),
            "repair_history": str(REPAIR_HISTORY),
            "runtime_stop_history": str(RUNTIME_STOP_HISTORY),
        },
        "rules": {
            "read_only_to_memory": True,
            "memory_update": False,
            "hit_count_update": False,
            "candidate_confirm": False,
            "candidate_promote": False,
            "backfill_execution": False,
        },
    }


def print_summary(result):
    print("=" * 80)
    print("LATS P3 RECOVERY HISTORY V1")
    print("=" * 80)

    print("status:", result.get("status"))
    print("gap_total:", result.get("gap_total"))
    print("gap_added:", result.get("gap_added"))
    print("repair_total:", result.get("repair_total"))
    print("repair_added:", result.get("repair_added"))
    print("runtime_stop_total:", result.get("runtime_stop_total"))

    print("\n[FILES]")
    for key, value in result.get("files", {}).items():
        print(key + ":", value)

    print("\n[RULE]")
    print("Recovery History does not update Memory Brain")
    print("Backfill execution is not enabled")


def main():
    result = update_history()
    print_summary(result)

    if result.get("status") != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
