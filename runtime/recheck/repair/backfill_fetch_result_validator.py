# LATS P3
# Backfill Fetch Result Validator V1
#
# Purpose:
# - Compare expected candidate timestamps with fetched API rows
# - Detect missing/extra fetched timestamps
# - Block write if mismatch
#
# Rules:
# - READ ONLY
# - No write to signal/result
# - No Memory update

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

CANDIDATE_CHECK_FILE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_candidate_checks"
    / "latest_backfill_candidate_duplicate_check.json"
)

API_FETCH_FILE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_api_fetch_reports"
    / "latest_backfill_api_fetch_test.json"
)

REPORT_DIR = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_fetch_result_validation"
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


def group_expected_candidates(candidates):
    groups = {}

    for row in candidates:
        if row.get("decision") != "INSERT_ALLOWED":
            continue

        key = (
            row.get("job_id"),
            row.get("job_type"),
        )

        groups.setdefault(key, set()).add(
            int(row.get("signal_time_ms"))
        )

    return groups


def group_fetched_rows(fetch_results):
    groups = {}

    for result in fetch_results:
        key = (
            result.get("job_id"),
            result.get("job_type"),
        )

        rows = result.get("rows", [])

        groups[key] = set(
            int(row.get("open_time_ms"))
            for row in rows
            if row.get("open_time_ms") is not None
        )

    return groups


def validate_group(key, expected_set, fetched_set):
    missing = sorted(expected_set - fetched_set)
    extra = sorted(fetched_set - expected_set)

    status = "PASS"

    if missing or extra:
        status = "FAIL"

    return {
        "job_id": key[0],
        "job_type": key[1],
        "status": status,
        "expected_rows": len(expected_set),
        "fetched_rows": len(fetched_set),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing_timestamps": missing[:20],
        "extra_timestamps": extra[:20],
        "write_allowed": status == "PASS",
    }


def build_report():
    candidate_check = load_json(CANDIDATE_CHECK_FILE, {})
    api_fetch = load_json(API_FETCH_FILE, {})

    blockers = []

    if not candidate_check:
        blockers.append("CANDIDATE_CHECK_MISSING")

    if not api_fetch:
        blockers.append("API_FETCH_REPORT_MISSING")

    if api_fetch and api_fetch.get("status") not in [
        "FETCH_TEST_OK",
        "FETCH_TEST_WARN",
    ]:
        blockers.append("API_FETCH_STATUS_NOT_OK")

    expected_groups = group_expected_candidates(
        candidate_check.get("checked_candidates", [])
    )

    fetched_groups = group_fetched_rows(
        api_fetch.get("fetch_results", [])
    )

    results = []

    all_keys = sorted(
        set(expected_groups.keys()) | set(fetched_groups.keys())
    )

    for key in all_keys:
        results.append(
            validate_group(
                key,
                expected_groups.get(key, set()),
                fetched_groups.get(key, set()),
            )
        )

    failed = [
        r for r in results
        if r.get("status") != "PASS"
    ]

    status = "READY_FOR_WRITE_TEST"

    if blockers or failed:
        status = "BLOCK_WRITE_MISMATCH"

    return {
        "schema": "lats_p3_backfill_fetch_result_validator_v1",
        "created_at": now_text(),
        "status": status,
        "blockers": blockers,
        "read_only": True,
        "write_enabled": False,
        "memory_update": False,
        "summary": {
            "validated_groups": len(results),
            "failed_groups": len(failed),
            "total_expected_rows": sum(
                r.get("expected_rows", 0)
                for r in results
            ),
            "total_fetched_rows": sum(
                r.get("fetched_rows", 0)
                for r in results
            ),
            "total_missing": sum(
                r.get("missing_count", 0)
                for r in results
            ),
            "total_extra": sum(
                r.get("extra_count", 0)
                for r in results
            ),
        },
        "results": results,
        "rules": {
            "write_signal_result_enabled": False,
            "memory_update": False,
            "block_write_on_mismatch": True,
        },
    }


def save_report(report):
    ensure_dir()

    latest = REPORT_DIR / "latest_backfill_fetch_result_validation.json"
    stamped = REPORT_DIR / f"backfill_fetch_result_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(latest, report)
    save_json(stamped, report)

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 BACKFILL FETCH RESULT VALIDATOR V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("blockers:", report.get("blockers"))
    print("read_only:", report.get("read_only"))

    s = report.get("summary", {})

    print("\n[SUMMARY]")
    print("validated_groups:", s.get("validated_groups"))
    print("failed_groups:", s.get("failed_groups"))
    print("total_expected_rows:", s.get("total_expected_rows"))
    print("total_fetched_rows:", s.get("total_fetched_rows"))
    print("total_missing:", s.get("total_missing"))
    print("total_extra:", s.get("total_extra"))

    print("\n[RESULTS]")
    for r in report.get("results", []):
        print(
            r.get("job_id"),
            "|",
            r.get("job_type"),
            "|",
            r.get("status"),
            "| expected:",
            r.get("expected_rows"),
            "| fetched:",
            r.get("fetched_rows"),
            "| missing:",
            r.get("missing_count"),
            "| extra:",
            r.get("extra_count"),
            "| write_allowed:",
            r.get("write_allowed"),
        )

        if r.get("missing_count"):
            print("  missing_sample:", r.get("missing_timestamps"))

        if r.get("extra_count"):
            print("  extra_sample:", r.get("extra_timestamps"))

    print("\n[RULE]")
    print("No write")
    print("No Memory update")
    print("Block write on mismatch")


def main():
    report = build_report()
    latest, stamped = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if report.get("status") == "BLOCK_WRITE_MISMATCH":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
