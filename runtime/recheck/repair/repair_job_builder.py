# LATS P3
# Repair Job Builder V1
#
# Purpose:
# - Read latest Recheck Report
# - Detect Signal/Result gaps
# - Create repair jobs
# - Save repair queue
#
# Rules:
# - READ ONLY to Memory Brain
# - No hit_count update
# - No candidate confirm/promote
# - No backfill execution yet
# - Create repair plan only

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

REPAIR_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
)

JOBS_DIR = (
    REPAIR_DIR
    / "jobs"
)

QUEUE_FILE = (
    REPAIR_DIR
    / "repair_queue.json"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dirs():
    JOBS_DIR.mkdir(
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


def make_job_id(index):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"REPAIR_{stamp}_{index:03d}"


def build_gap_jobs(report):
    jobs = []

    sr = report.get(
        "signal_result_gap_check",
        {},
    )

    signal_report = sr.get(
        "signal_report",
        {},
    )

    result_report = sr.get(
        "result_report",
        {},
    )

    signal_gaps = signal_report.get(
        "gaps",
        [],
    )

    result_gaps = result_report.get(
        "gaps",
        [],
    )

    index = 1

    for gap in signal_gaps:
        jobs.append(
            {
                "job_id": make_job_id(index),
                "job_type": "SIGNAL_GAP_BACKFILL",
                "status": "WAIT_BACKFILL",
                "source": "signal_data",
                "from_signal_id": gap.get("from_signal_id"),
                "to_signal_id": gap.get("to_signal_id"),
                "from_time_ms": gap.get("from_time_ms"),
                "to_time_ms": gap.get("to_time_ms"),
                "from_time_text": gap.get("from_time_text"),
                "to_time_text": gap.get("to_time_text"),
                "gap_minutes": gap.get("gap_minutes"),
                "priority": "HIGH",
                "duplicate_guard": True,
                "memory_update": False,
                "candidate_update": False,
                "created_at": now_text(),
                "reason": "signal gap detected by recheck path",
            }
        )

        index += 1

    for gap in result_gaps:
        jobs.append(
            {
                "job_id": make_job_id(index),
                "job_type": "RESULT_GAP_BACKFILL",
                "status": "WAIT_BACKFILL",
                "source": "result_data",
                "from_signal_id": gap.get("from_signal_id"),
                "to_signal_id": gap.get("to_signal_id"),
                "from_time_ms": gap.get("from_time_ms"),
                "to_time_ms": gap.get("to_time_ms"),
                "from_time_text": gap.get("from_time_text"),
                "to_time_text": gap.get("to_time_text"),
                "gap_minutes": gap.get("gap_minutes"),
                "priority": "HIGH",
                "duplicate_guard": True,
                "memory_update": False,
                "candidate_update": False,
                "created_at": now_text(),
                "reason": "result gap detected by recheck path",
            }
        )

        index += 1

    return jobs


def build_queue(report, jobs):
    return {
        "schema": "lats_p3_repair_queue_v1",
        "created_at": now_text(),
        "source_report": str(RECHECK_REPORT),
        "recheck_status": report.get("final_status"),
        "next_action": report.get("next_action"),
        "total_jobs": len(jobs),
        "waiting_backfill": len(
            [
                j for j in jobs
                if j.get("status") == "WAIT_BACKFILL"
            ]
        ),
        "rules": {
            "memory_read_only": True,
            "no_hit_count_update": True,
            "no_candidate_confirm": True,
            "no_candidate_promote": True,
            "duplicate_guard_required": True,
            "backfill_execution_enabled": False,
        },
        "jobs": jobs,
    }


def save_jobs(jobs, queue):
    ensure_dirs()

    for job in jobs:
        job_file = (
            JOBS_DIR
            / f"{job.get('job_id')}.json"
        )

        save_json(
            job_file,
            job,
        )

    save_json(
        QUEUE_FILE,
        queue,
    )


def print_summary(queue):
    print("=" * 80)
    print("LATS P3 REPAIR JOB BUILDER V1")
    print("=" * 80)

    print("recheck_status:", queue.get("recheck_status"))
    print("next_action:", queue.get("next_action"))
    print("total_jobs:", queue.get("total_jobs"))
    print("waiting_backfill:", queue.get("waiting_backfill"))

    print("\n[JOBS]")
    for job in queue.get("jobs", []):
        print(
            job.get("job_id"),
            "|",
            job.get("job_type"),
            "|",
            job.get("status"),
            "| gap_minutes:",
            job.get("gap_minutes"),
        )

    print("\n[RULE]")
    print("Repair Job Builder does not update Memory Brain")
    print("Backfill execution is not enabled in V1")


def main():
    report = load_json(RECHECK_REPORT)

    if not report:
        print("FAIL: latest_recheck_report.json not found")
        raise SystemExit(1)

    jobs = build_gap_jobs(report)
    queue = build_queue(report, jobs)

    save_jobs(
        jobs,
        queue,
    )

    print_summary(queue)

    print("\n[QUEUE]")
    print(QUEUE_FILE)

    if not jobs:
        print("\nPASS: no repair jobs required")
    else:
        print("\nWARN: repair jobs created, backfill required")


if __name__ == "__main__":
    main()
