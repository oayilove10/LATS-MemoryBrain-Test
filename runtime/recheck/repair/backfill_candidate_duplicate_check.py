# LATS P3
# Backfill Candidate Duplicate Check V1
#
# Purpose:
# - Read backfill candidates
# - Compare with signal_data.csv and result_data.csv
# - Mark candidates as INSERT_ALLOWED or DUPLICATE_SKIP
#
# Rules:
# - READ ONLY
# - No API fetch
# - No write to signal/result
# - No Memory update

import csv
import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

SIGNAL_FILE = ROOT / "data" / "signal_data.csv"
RESULT_FILE = ROOT / "data" / "result_data.csv"

CANDIDATE_FILE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_candidates"
    / "latest_backfill_candidates.json"
)

REPORT_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_candidate_checks"
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


def read_existing_ids(path):
    ids = set()

    if not path.exists():
        return ids

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            signal_id = row.get("signal_id", "")
            if signal_id:
                ids.add(signal_id)

    return ids


def build_report():
    payload = load_json(CANDIDATE_FILE, {})

    blockers = []

    if not payload:
        blockers.append("BACKFILL_CANDIDATES_MISSING")

    signal_ids = read_existing_ids(SIGNAL_FILE)
    result_ids = read_existing_ids(RESULT_FILE)

    checked = []

    duplicate_count = 0
    insert_allowed_count = 0

    for row in payload.get("candidates", []):
        candidate_id = row.get("candidate_id")
        job_type = row.get("job_type")

        existing_pool = signal_ids

        if job_type == "RESULT_GAP_BACKFILL":
            existing_pool = result_ids

        decision = "INSERT_ALLOWED"

        if candidate_id in existing_pool:
            decision = "DUPLICATE_SKIP"
            duplicate_count += 1
        else:
            insert_allowed_count += 1

        checked.append(
            {
                "candidate_id": candidate_id,
                "job_id": row.get("job_id"),
                "job_type": job_type,
                "symbol": row.get("symbol"),
                "timeframe": row.get("timeframe"),
                "signal_time_ms": row.get("signal_time_ms"),
                "decision": decision,
                "api_fetch_enabled": False,
                "write_enabled": False,
                "memory_update": False,
            }
        )

    status = "OK"

    if blockers:
        status = "NOT_READY"

    return {
        "schema": "lats_p3_backfill_candidate_duplicate_check_v1",
        "created_at": now_text(),
        "status": status,
        "blockers": blockers,
        "read_only": True,
        "summary": {
            "candidate_rows": len(checked),
            "insert_allowed": insert_allowed_count,
            "duplicate_skip": duplicate_count,
            "existing_signal_ids": len(signal_ids),
            "existing_result_ids": len(result_ids),
        },
        "rules": {
            "api_fetch_enabled": False,
            "write_signal_result_enabled": False,
            "memory_update": False,
            "row_level_duplicate_check": True,
        },
        "checked_candidates": checked,
    }


def save_report(report):
    ensure_dir()

    latest = REPORT_DIR / "latest_backfill_candidate_duplicate_check.json"
    stamped = REPORT_DIR / f"backfill_candidate_duplicate_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(latest, report)
    save_json(stamped, report)

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 BACKFILL CANDIDATE DUPLICATE CHECK V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("read_only:", report.get("read_only"))
    print("blockers:", report.get("blockers"))

    s = report.get("summary", {})

    print("\n[SUMMARY]")
    print("candidate_rows:", s.get("candidate_rows"))
    print("insert_allowed:", s.get("insert_allowed"))
    print("duplicate_skip:", s.get("duplicate_skip"))
    print("existing_signal_ids:", s.get("existing_signal_ids"))
    print("existing_result_ids:", s.get("existing_result_ids"))

    print("\n[SAMPLE]")
    for row in report.get("checked_candidates", [])[:5]:
        print(
            row.get("candidate_id"),
            "|",
            row.get("job_type"),
            "|",
            row.get("decision"),
        )

    print("\n[RULE]")
    print("Read only")
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

    if report.get("status") == "NOT_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
