# LATS P3
# Repair Job Builder V2
#
# Purpose:
# - Read latest Recheck Report
# - Detect Signal/Result gaps
# - Create repair jobs
# - Reuse existing job if same gap already exists
# - Save repair queue
#
# Rules:
# - READ ONLY to Memory Brain
# - No hit_count update
# - No candidate confirm/promote
# - No backfill execution yet
# - Create/Update repair plan only

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


def load_json(path, default=None):
    if default is None:
        default = {}

    if not path.exists():
        return default

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


def gap_key(job):
    return "|".join(
        [
            str(job.get("job_type", "")),
            str(job.get("source", "")),
            str(job.get("from_signal_id", "")),
            str(job.get("to_signal_id", "")),
            str(job.get("from_time_ms", "")),
            str(job.get("to_time_ms", "")),
        ]
    )


def load_existing_jobs():
    queue = load_json(
        QUEUE_FILE,
        default={
            "jobs": [],
        },
    )

    jobs = queue.get(
        "jobs",
        [],
    )

    by_key = {}

    for job in jobs:
        by_key[gap_key(job)] = job

    return jobs, by_key


def base_job_from_gap(gap, job_type, source, reason):
    return {
        "job_id": "",
        "job_type": job_type,
        "status": "WAIT_BACKFILL",
        "source": source,
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
        "updated_at": now_text(),
        "seen_count": 1,
        "reason": reason,
    }


def upsert_job(candidate, existing_by_key, next_index):
    key = gap_key(candidate)
    old = existing_by_key.get(key)

    if old:
        updated = dict(old)
        updated["updated_at"] = now_text()
        updated["seen_count"] = int(
            updated.get("seen_count", 1) or 1
        ) + 1
        updated["status"] = updated.get(
            "status",
            "WAIT_BACKFILL",
        )
        updated["dedup_action"] = "REUSED_EXISTING_JOB"
        return updated, False, next_index

    candidate["job_id"] = make_job_id(next_index)
    candidate["dedup_action"] = "CREATED_NEW_JOB"

    return candidate, True, next_index + 1


def build_gap_jobs(report):
    existing_jobs, existing_by_key = load_existing_jobs()

    candidates = []

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

    for gap in signal_report.get("gaps", []):
        candidates.append(
            base_job_from_gap(
                gap,
                "SIGNAL_GAP_BACKFILL",
                "signal_data",
                "signal gap detected by recheck path",
            )
        )

    for gap in result_report.get("gaps", []):
        candidates.append(
            base_job_from_gap(
                gap,
                "RESULT_GAP_BACKFILL",
                "result_data",
                "result gap detected by recheck path",
            )
        )

    next_index = 1
    final_by_key = {
        gap_key(job): job
        for job in existing_jobs
    }

    created_count = 0
    reused_count = 0

    for candidate in candidates:
        job, created, next_index = upsert_job(
            candidate,
            final_by_key,
            next_index,
        )

        final_by_key[gap_key(job)] = job

        if created:
            created_count += 1
        else:
            reused_count += 1

    jobs = list(final_by_key.values())

    jobs = sorted(
        jobs,
        key=lambda x: (
            x.get("status", ""),
            x.get("created_at", ""),
            x.get("job_id", ""),
        ),
    )

    return jobs, created_count, reused_count


def build_queue(report, jobs, created_count, reused_count):
    waiting = [
        j for j in jobs
        if j.get("status") == "WAIT_BACKFILL"
    ]

    return {
        "schema": "lats_p3_repair_queue_v2",
        "created_at": now_text(),
        "updated_at": now_text(),
        "source_report": str(RECHECK_REPORT),
        "recheck_status": report.get("final_status"),
        "next_action": report.get("next_action"),
        "total_jobs": len(jobs),
        "waiting_backfill": len(waiting),
        "created_count": created_count,
        "reused_count": reused_count,
        "rules": {
            "memory_read_only": True,
            "no_hit_count_update": True,
            "no_candidate_confirm": True,
            "no_candidate_promote": True,
            "duplicate_guard_required": True,
            "job_dedup_enabled": True,
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
    print("LATS P3 REPAIR JOB BUILDER V2")
    print("=" * 80)

    print("recheck_status:", queue.get("recheck_status"))
    print("next_action:", queue.get("next_action"))
    print("total_jobs:", queue.get("total_jobs"))
    print("waiting_backfill:", queue.get("waiting_backfill"))
    print("created_count:", queue.get("created_count"))
    print("reused_count:", queue.get("reused_count"))

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
            "| seen:",
            job.get("seen_count"),
            "|",
            job.get("dedup_action"),
        )

    print("\n[RULE]")
    print("Repair Job Builder does not update Memory Brain")
    print("Job dedup is enabled")
    print("Backfill execution is not enabled in V2")


def main():
    report = load_json(RECHECK_REPORT)

    if not report:
        print("FAIL: latest_recheck_report.json not found")
        raise SystemExit(1)

    jobs, created_count, reused_count = build_gap_jobs(report)
    queue = build_queue(
        report,
        jobs,
        created_count,
        reused_count,
    )

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
        print("\nWARN: repair jobs ready, backfill required")


if __name__ == "__main__":
    main()
