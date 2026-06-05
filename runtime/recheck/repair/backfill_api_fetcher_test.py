# LATS P3
# Backfill API Fetcher TEST V1
#
# Purpose:
# - Read validated fetch plan
# - Fetch Binance Futures klines
# - Save fetched rows to report only
#
# Rules:
# - API fetch enabled
# - No write to signal_data/result_data
# - No Memory update
# - No candidate confirm/promote

import json
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

VALIDATION_FILE = (
    ROOT
    / "runtime"
    / "recheck"
    / "repair"
    / "backfill_fetch_validation"
    / "latest_backfill_fetch_validation.json"
)

FETCH_PLAN_FILE = (
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
    / "backfill_api_fetch_reports"
)

BINANCE_FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"


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


def fetch_klines(symbol, interval, start_ms, end_ms, limit=1500):
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": int(start_ms),
        "endTime": int(end_ms),
        "limit": limit,
    }

    url = BINANCE_FUTURES_KLINES + "?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url, timeout=20) as response:
        raw = response.read().decode("utf-8")

    return json.loads(raw), url


def normalize_kline(row):
    return {
        "open_time_ms": row[0],
        "open": row[1],
        "high": row[2],
        "low": row[3],
        "close": row[4],
        "volume": row[5],
        "close_time_ms": row[6],
        "quote_volume": row[7],
        "trade_count": row[8],
        "taker_buy_base_volume": row[9],
        "taker_buy_quote_volume": row[10],
    }


def build_report():
    validation = load_json(VALIDATION_FILE, {})
    plan = load_json(FETCH_PLAN_FILE, {})

    blockers = []

    if not validation:
        blockers.append("FETCH_VALIDATION_MISSING")

    if validation and validation.get("status") != "READY_FOR_API_FETCH":
        blockers.append("FETCH_VALIDATION_NOT_READY")

    if not plan:
        blockers.append("FETCH_PLAN_MISSING")

    fetch_results = []

    if blockers:
        return {
            "schema": "lats_p3_backfill_api_fetcher_test_v1",
            "created_at": now_text(),
            "status": "BLOCKED",
            "blockers": blockers,
            "api_fetch_enabled": True,
            "write_enabled": False,
            "memory_update": False,
            "fetch_results": [],
        }

    for task in plan.get("fetch_tasks", []):
        try:
            rows, url = fetch_klines(
                task.get("symbol"),
                task.get("timeframe"),
                task.get("start_time_ms"),
                task.get("end_time_ms"),
            )

            normalized = [
                normalize_kline(row)
                for row in rows
            ]

            fetch_results.append(
                {
                    "job_id": task.get("job_id"),
                    "job_type": task.get("job_type"),
                    "symbol": task.get("symbol"),
                    "timeframe": task.get("timeframe"),
                    "status": "FETCH_OK",
                    "expected_candidate_rows": task.get("candidate_rows"),
                    "fetched_rows": len(normalized),
                    "url": url,
                    "rows": normalized,
                }
            )

        except Exception as e:
            fetch_results.append(
                {
                    "job_id": task.get("job_id"),
                    "job_type": task.get("job_type"),
                    "symbol": task.get("symbol"),
                    "timeframe": task.get("timeframe"),
                    "status": "FETCH_ERROR",
                    "error": str(e),
                    "expected_candidate_rows": task.get("candidate_rows"),
                    "fetched_rows": 0,
                    "rows": [],
                }
            )

    failed = [
        r for r in fetch_results
        if r.get("status") != "FETCH_OK"
    ]

    status = "FETCH_TEST_OK"

    if failed:
        status = "FETCH_TEST_WARN"

    return {
        "schema": "lats_p3_backfill_api_fetcher_test_v1",
        "created_at": now_text(),
        "status": status,
        "blockers": [],
        "api_fetch_enabled": True,
        "write_enabled": False,
        "memory_update": False,
        "summary": {
            "fetch_tasks": len(fetch_results),
            "fetch_ok": len(fetch_results) - len(failed),
            "fetch_error": len(failed),
            "total_fetched_rows": sum(
                r.get("fetched_rows", 0)
                for r in fetch_results
            ),
        },
        "rules": {
            "write_signal_result_enabled": False,
            "memory_update": False,
            "candidate_update": False,
            "insert_enabled": False,
        },
        "fetch_results": fetch_results,
    }


def save_report(report):
    ensure_dir()

    latest = REPORT_DIR / "latest_backfill_api_fetch_test.json"
    stamped = REPORT_DIR / f"backfill_api_fetch_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    save_json(latest, report)
    save_json(stamped, report)

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 BACKFILL API FETCHER TEST V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("blockers:", report.get("blockers"))
    print("api_fetch_enabled:", report.get("api_fetch_enabled"))
    print("write_enabled:", report.get("write_enabled"))
    print("memory_update:", report.get("memory_update"))

    s = report.get("summary", {})

    print("\n[SUMMARY]")
    print("fetch_tasks:", s.get("fetch_tasks"))
    print("fetch_ok:", s.get("fetch_ok"))
    print("fetch_error:", s.get("fetch_error"))
    print("total_fetched_rows:", s.get("total_fetched_rows"))

    print("\n[TASKS]")
    for r in report.get("fetch_results", []):
        print(
            r.get("job_id"),
            "|",
            r.get("job_type"),
            "|",
            r.get("symbol"),
            "|",
            r.get("status"),
            "| expected:",
            r.get("expected_candidate_rows"),
            "| fetched:",
            r.get("fetched_rows"),
        )

    print("\n[RULE]")
    print("API fetch only")
    print("No write to signal/result")
    print("No Memory update")


def main():
    report = build_report()
    latest, stamped = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)

    if report.get("status") == "BLOCKED":
        raise SystemExit(1)

    if report.get("status") == "FETCH_TEST_WARN":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
