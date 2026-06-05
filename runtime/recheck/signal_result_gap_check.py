# LATS P3
# Signal / Result Gap Check V1
#
# READ ONLY
# - Check signal_data.csv
# - Check result_data.csv
# - Detect duplicate signal_id
# - Detect missing result for signal
# - Detect timestamp gaps
# - Do not update Memory

import csv
import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

SIGNAL_FILE = ROOT / "data" / "signal_data.csv"
RESULT_FILE = ROOT / "data" / "result_data.csv"
REPORT_DIR = ROOT / "runtime" / "recheck" / "reports"

EXPECTED_INTERVAL_MS = 15 * 60 * 1000
GAP_MULTIPLIER = 2


def ensure_report_dir():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def read_csv(path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_int(value):
    try:
        return int(float(value))
    except Exception:
        return None


def is_test_row(row):
    text = json.dumps(row, ensure_ascii=False)
    markers = [
        "TEST_SIGNAL",
        "DUP_TEST",
        "SMOKE_",
        "TEST_",
    ]
    return any(m in text for m in markers)


def analyze_rows(rows, label):
    clean = [
        r for r in rows
        if not is_test_row(r)
    ]

    ids = {}
    duplicate_ids = []

    for r in clean:
        sid = r.get("signal_id", "")
        if not sid:
            continue

        ids[sid] = ids.get(sid, 0) + 1

    duplicate_ids = [
        sid for sid, count in ids.items()
        if count > 1
    ]

    timed = []

    for r in clean:
        ts = to_int(r.get("signal_time_ms"))
        if ts is None:
            continue

        timed.append(
            {
                "signal_id": r.get("signal_id", ""),
                "symbol": r.get("symbol", ""),
                "signal_time_ms": ts,
                "signal_time_text": r.get("signal_time_text", ""),
                "status": r.get("status", ""),
            }
        )

    timed = sorted(
        timed,
        key=lambda x: x["signal_time_ms"],
    )

    gaps = []

    for prev, cur in zip(timed, timed[1:]):
        diff = cur["signal_time_ms"] - prev["signal_time_ms"]

        if diff > EXPECTED_INTERVAL_MS * GAP_MULTIPLIER:
            gaps.append(
                {
                    "from_signal_id": prev.get("signal_id"),
                    "to_signal_id": cur.get("signal_id"),
                    "from_time_ms": prev.get("signal_time_ms"),
                    "to_time_ms": cur.get("signal_time_ms"),
                    "from_time_text": prev.get("signal_time_text"),
                    "to_time_text": cur.get("signal_time_text"),
                    "gap_minutes": round(diff / 1000 / 60, 2),
                    "expected_minutes": 15,
                }
            )

    first = timed[0] if timed else {}
    last = timed[-1] if timed else {}

    return {
        "label": label,
        "total_rows": len(rows),
        "clean_rows": len(clean),
        "test_rows": len(rows) - len(clean),
        "timed_rows": len(timed),
        "duplicate_signal_id_count": len(duplicate_ids),
        "duplicate_signal_ids": duplicate_ids[:20],
        "gap_count": len(gaps),
        "largest_gap_minutes": max(
            [g["gap_minutes"] for g in gaps],
            default=0,
        ),
        "first_time_text": first.get("signal_time_text"),
        "last_time_text": last.get("signal_time_text"),
        "first_time_ms": first.get("signal_time_ms"),
        "last_time_ms": last.get("signal_time_ms"),
        "gaps": gaps[:50],
    }


def analyze_signal_result_link(signal_rows, result_rows):
    signal_ids = set(
        r.get("signal_id", "")
        for r in signal_rows
        if r.get("signal_id") and not is_test_row(r)
    )

    result_ids = set(
        r.get("signal_id", "")
        for r in result_rows
        if r.get("signal_id") and not is_test_row(r)
    )

    missing_result = sorted(signal_ids - result_ids)
    result_without_signal = sorted(result_ids - signal_ids)

    return {
        "signal_count": len(signal_ids),
        "result_count": len(result_ids),
        "missing_result_count": len(missing_result),
        "result_without_signal_count": len(result_without_signal),
        "missing_result_sample": missing_result[:50],
        "result_without_signal_sample": result_without_signal[:50],
    }


def build_report():
    signal_rows = read_csv(SIGNAL_FILE)
    result_rows = read_csv(RESULT_FILE)

    signal_report = analyze_rows(
        signal_rows,
        "signal_data",
    )

    result_report = analyze_rows(
        result_rows,
        "result_data",
    )

    link_report = analyze_signal_result_link(
        signal_rows,
        result_rows,
    )

    status = "PASS"

    if signal_report["gap_count"] > 0:
        status = "WARN"

    if result_report["gap_count"] > 0:
        status = "WARN"

    if link_report["missing_result_count"] > 0:
        status = "WARN"

    report = {
        "schema": "lats_p3_signal_result_gap_check_v1",
        "created_at": now_text(),
        "status": status,
        "read_only": True,
        "files": {
            "signal_file": str(SIGNAL_FILE),
            "result_file": str(RESULT_FILE),
        },
        "signal_report": signal_report,
        "result_report": result_report,
        "link_report": link_report,
        "rules": {
            "expected_interval_minutes": 15,
            "gap_detect_over_minutes": 30,
            "exclude_test_rows": True,
            "memory_update": False,
        },
    }

    return report


def save_report(report):
    ensure_report_dir()

    latest = REPORT_DIR / "latest_signal_result_gap_report.json"
    stamped = REPORT_DIR / f"signal_result_gap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    text = json.dumps(
        report,
        ensure_ascii=False,
        indent=2,
    )

    latest.write_text(text, encoding="utf-8")
    stamped.write_text(text, encoding="utf-8")

    return latest, stamped


def print_summary(report):
    print("=" * 80)
    print("LATS P3 SIGNAL / RESULT GAP CHECK V1")
    print("=" * 80)

    print("status:", report.get("status"))
    print("read_only:", report.get("read_only"))

    s = report["signal_report"]
    r = report["result_report"]
    l = report["link_report"]

    print("\n[SIGNAL]")
    print("rows:", s["total_rows"])
    print("clean_rows:", s["clean_rows"])
    print("test_rows:", s["test_rows"])
    print("first:", s["first_time_text"])
    print("last:", s["last_time_text"])
    print("gap_count:", s["gap_count"])
    print("largest_gap_minutes:", s["largest_gap_minutes"])
    print("duplicate_count:", s["duplicate_signal_id_count"])

    print("\n[RESULT]")
    print("rows:", r["total_rows"])
    print("clean_rows:", r["clean_rows"])
    print("test_rows:", r["test_rows"])
    print("first:", r["first_time_text"])
    print("last:", r["last_time_text"])
    print("gap_count:", r["gap_count"])
    print("largest_gap_minutes:", r["largest_gap_minutes"])
    print("duplicate_count:", r["duplicate_signal_id_count"])

    print("\n[LINK]")
    print("signal_count:", l["signal_count"])
    print("result_count:", l["result_count"])
    print("missing_result_count:", l["missing_result_count"])
    print("result_without_signal_count:", l["result_without_signal_count"])

    if s["gaps"]:
        print("\n[SIGNAL GAP SAMPLE]")
        for gap in s["gaps"][:5]:
            print(gap)

    if r["gaps"]:
        print("\n[RESULT GAP SAMPLE]")
        for gap in r["gaps"][:5]:
            print(gap)


def main():
    report = build_report()
    latest, stamped = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest)
    print("stamped:", stamped)


if __name__ == "__main__":
    main()
