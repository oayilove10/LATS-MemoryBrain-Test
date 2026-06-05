# LATS P3
# Duplicate Guard V1
#
# Purpose:
# - Protect repair/backfill path from duplicate inserts
# - Check existing signal_id/result signal_id before backfill
#
# Rules:
# - READ ONLY
# - No Memory update
# - No hit_count update
# - No candidate confirm/promote
# - No write to signal/result data

import csv
import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

SIGNAL_FILE = ROOT / "data" / "signal_data.csv"
RESULT_FILE = ROOT / "data" / "result_data.csv"

REPAIR_DIR = ROOT / "runtime" / "recheck" / "repair"
QUEUE_FILE = REPAIR_DIR / "repair_queue.json"
REPORT_DIR = REPAIR_DIR / "duplicate_reports"


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_report_dir():
    REPORT_DIR.mkdir(
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


def read_csv_ids(path):
    ids = set()

    if not path.exists():
        return ids

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            signal_id = row.get("signal_id", "")

            if signal_id:
                ids.add(signal_id)

    return ids


def collect_existing_ids():
    signal_ids = read_csv_ids(SIGNAL_FILE)
    result_ids = read_csv_ids(RESULT_FILE)

    return {
        "signal_ids": signal_ids,
        "result_ids": result_ids,
    }


def check_repair_jobs(queue, existing):
    jobs = queue.get("jobs", [])

    checked_jobs = []

    for job in jobs:
        from_signal_id = job.get("from_signal_id")
        to_signal_id = job.get("to_signal_id")
        job_type = job.get("job_type")

        existing_pool = existing["signal_ids"]

        if job_type == "RESULT_GAP_BACKFILL":
            existing_pool = existing["result_ids"]

        boundary_ids = [
            from_signal_id,
            to_signal_id,
        ]

        duplicate_boundary_ids = [
            sid for sid in boundary_ids
            if sid and sid in existing_pool
        ]

        checked_jobs.append(
            {
                "job_id": job.get("job_id"),
                "job_type": job_type,
                "status": job.get("status"),
                "source": job.get("source"),
                "gap_minutes": job.get("gap_minutes"),
                "from_signal_id": from_signal_id,
                "to_signal_id": to_signal_id,
                "duplicate_boundary_count": len(
                    duplicate_boundary_ids
                ),
                "duplicate_boundary_ids": duplicate_boundary_ids,
                "duplicate_guard": True,
                "memory_update": False,
                "candidate_update": False,
                "decision": "SAFE_TO_BACKFILL_WITH_ROW_LEVEL_CHECK",
                "note": (
                    "Boundary ids exist because they mark gap edges. "
                    "Actual backfill rows must be checked one by one before insert."
                ),
            }
        )

    return checked_jobs


def build_report():
    queue = load_json(QUEUE_FILE)

    if not queue:
        return {
            "schema": "lats_p3_duplicate_guard_report_v1",
            "created_at": now_text(),
            "status": "FAIL",
            "reason": "repair_queue.json not found",
            "read_only": True,
        }

    existing = collect_existing_ids()

    checked_jobs = check_repair_jobs(
        queue,
        existing,
    )

    return {
        "schema": "lats_p3_duplicate_guard_report_v1",
        "created_at": now_text(),
        "status": "OK",
        "read_only": True,
        "files": {
            "signal_file": str(SIGNAL_FILE),
            "result_file": str(RESULT_FILE),
            "repair_queue": str(QUEUE_FILE),
        },
        "existing_counts": {
            "signal_ids": len(existing["signal_ids"]),
            "result_ids": len(existing["result_ids"]),
        },
        "queue": {
            "total_jobs": queue.get("total_jobs"),
            "waiting_backfill": queue.get("waiting_backfill"),
        },
        "jobs_checked": len(checked_jobs),
        "checked_jobs": checked_jobs,
        "rules": {
            "row_level_duplicate_check_required": True,
            "signal_id_unique": True,
            "result_signal_id_unique": True,
            "memory_update": False,
            "candidate_update": False,
            "backfill_execution_enabled": False,
        },
    }


def save_report(report):
    ensure_report_dir()

    latest = REPORT_DIR / "latest_duplicate_guard_report.json"
    stamped = REPORT_DIR / f"duplicate_guard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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
    print("LATS P3 DUPLICATE GUARD V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("read_only:", report.get("read_only"))

    counts = report.get("existing_counts", {})
    print("\n[EXISTING IDS]")
    print("signal_ids:", counts.get("signal_ids"))
    print("result_ids:", counts.get("result_ids"))

    queue = report.get("queue", {})
    print("\n[QUEUE]")
    print("total_jobs:", queue.get("total_jobs"))
    print("waiting_backfill:", queue.get("waiting_backfill"))

    print("\n[JOBS]")
    for job in report.get("checked_jobs", []):
        print(
            job.get("job_id"),
            "|",
            job.get("job_type"),
            "|",
            "duplicate_boundary:",
            job.get("duplicate_boundary_count"),
            "|",
            job.get("decision"),
        )

    print("\n[RULE]")
    print("Duplicate Guard is read-only")
    print("Backfill must check every row before insert")


def main():
    report = build_report()
    latest, stamped = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if report.get("status") != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
