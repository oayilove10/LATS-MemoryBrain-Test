# LATS P3
# Recheck Path V3
#
# Purpose:
# - Mandatory gate before Runtime Test / Runtime Full
# - Check runtime gap
# - Check storage paths
# - Check signal/result gap
# - Check Memory health read-only
# - Block runtime if signal/result gap exists
#
# Rules:
# - READ ONLY to Memory Brain
# - No hit_count update
# - No candidate confirm/promote
# - No memory statistics update
# - No real backfill yet; report BACKFILL_REQUIRED only

import sys
import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"
LOGIC = ROOT / "memory_brain" / "logic"
SHARED = ROOT / "shared"
RECHECK = ROOT / "runtime" / "recheck"

sys.path.insert(0, str(LOGIC))
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(RECHECK))

from memory_api import MemoryAPI
from signal_result_gap_check import build_report as build_signal_result_gap_report


REPORT_DIR = ROOT / "runtime" / "recheck" / "reports"
RUNTIME_LATEST = ROOT / "logs" / "memory_runtime" / "latest_memory_runtime.json"

CHECK_PATHS = {
    "raw_database": ROOT / "raw_database",
    "live_data": ROOT / "data",
    "memory_data": ROOT / "memory_brain" / "data",
    "candidate_data": ROOT / "memory_brain" / "data" / "candidates",
    "runtime_logs": ROOT / "logs" / "memory_runtime",
    "memory_logs": ROOT / "logs" / "memory_brain",
}

GAP_WARN_MINUTES = 60


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def ensure_report_dir():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def count_files(path):
    if not path.exists():
        return {
            "exists": False,
            "file_count": 0,
            "latest_file": None,
            "latest_modified": None,
        }

    files = [
        p for p in path.rglob("*")
        if p.is_file()
    ]

    if not files:
        return {
            "exists": True,
            "file_count": 0,
            "latest_file": None,
            "latest_modified": None,
        }

    latest = max(
        files,
        key=lambda p: p.stat().st_mtime,
    )

    return {
        "exists": True,
        "file_count": len(files),
        "latest_file": str(latest),
        "latest_modified": datetime.fromtimestamp(
            latest.stat().st_mtime
        ).isoformat(timespec="seconds"),
    }


def check_storage_paths():
    results = {}

    for name, path in CHECK_PATHS.items():
        results[name] = count_files(path)

    return results


def check_last_runtime_gap():
    payload = load_json(RUNTIME_LATEST)

    if not payload:
        return {
            "status": "WARN",
            "code": "SYS-101",
            "name": "DATA_GAP_BEFORE_START",
            "reason": "latest runtime file not found",
            "last_runtime_time": None,
            "gap_minutes": None,
            "action": "BACKFILL_REVIEW_REQUIRED",
        }

    last_time_text = payload.get("updated_at")
    last_time = parse_time(last_time_text)

    if not last_time:
        return {
            "status": "WARN",
            "code": "SYS-101",
            "name": "DATA_GAP_BEFORE_START",
            "reason": "latest runtime time invalid",
            "last_runtime_time": last_time_text,
            "gap_minutes": None,
            "action": "BACKFILL_REVIEW_REQUIRED",
        }

    now = datetime.now()
    gap_minutes = round((now - last_time).total_seconds() / 60, 2)

    if gap_minutes >= GAP_WARN_MINUTES:
        return {
            "status": "WARN",
            "code": "SYS-101",
            "name": "DATA_GAP_BEFORE_START",
            "reason": "runtime stopped before start",
            "last_runtime_time": last_time_text,
            "gap_minutes": gap_minutes,
            "action": "BACKFILL_REQUIRED",
        }

    return {
        "status": "OK",
        "code": "",
        "name": "NO_RUNTIME_GAP",
        "reason": "runtime gap within limit",
        "last_runtime_time": last_time_text,
        "gap_minutes": gap_minutes,
        "action": "PASS",
    }


def check_memory_read_only():
    api = MemoryAPI()

    info = api.info()
    health = api.health()
    candidate_stats = api.candidate_stats()

    status = "OK"

    if health.get("status") != "OK":
        status = "FAIL"

    return {
        "status": status,
        "memory_api": info,
        "health": health,
        "candidate_stats": candidate_stats,
        "read_only": True,
    }


def build_missing_checks(storage_paths):
    checks = []

    for name, result in storage_paths.items():
        if not result.get("exists"):
            checks.append(
                {
                    "name": name,
                    "status": "WARN",
                    "reason": "path missing",
                    "action": "REVIEW_REQUIRED",
                }
            )
            continue

        if result.get("file_count", 0) == 0:
            checks.append(
                {
                    "name": name,
                    "status": "WARN",
                    "reason": "no files found",
                    "action": "REVIEW_REQUIRED",
                }
            )
            continue

        checks.append(
            {
                "name": name,
                "status": "OK",
                "reason": "files found",
                "file_count": result.get("file_count"),
                "latest_modified": result.get("latest_modified"),
                "action": "PASS",
            }
        )

    return checks


def decide_final_status(runtime_gap, memory_check, signal_result_gap):
    blockers = []

    if memory_check.get("status") != "OK":
        blockers.append("MEMORY_HEALTH_FAIL")

    if signal_result_gap.get("status") == "WARN":
        blockers.append("SIGNAL_RESULT_GAP_DETECTED")

    final_status = "PASS"

    if blockers:
        final_status = "FAIL"

    return final_status, blockers


def build_report():
    runtime_gap = check_last_runtime_gap()
    storage_paths = check_storage_paths()
    missing_checks = build_missing_checks(storage_paths)
    memory_check = check_memory_read_only()
    signal_result_gap = build_signal_result_gap_report()

    final_status, blockers = decide_final_status(
        runtime_gap,
        memory_check,
        signal_result_gap,
    )

    report = {
        "schema": "lats_p3_recheck_report_v3",
        "created_at": now_text(),
        "final_status": final_status,
        "blockers": blockers,
        "rules": {
            "memory_read_only": True,
            "no_hit_count_update": True,
            "no_candidate_confirm": True,
            "no_candidate_promote": True,
            "no_memory_statistics_update": True,
            "real_backfill_enabled": False,
            "run_blocked_on_signal_result_gap": True,
        },
        "runtime_gap_check": runtime_gap,
        "storage_paths": storage_paths,
        "missing_checks": missing_checks,
        "signal_result_gap_check": signal_result_gap,
        "memory_check": memory_check,
        "next_action": (
            "RUN_ALLOWED"
            if final_status == "PASS"
            else "RUN_BLOCKED_BACKFILL_REQUIRED"
        ),
    }

    return report


def save_report(report):
    ensure_report_dir()

    latest_file = REPORT_DIR / "latest_recheck_report.json"
    stamped_file = REPORT_DIR / f"recheck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    text = json.dumps(report, ensure_ascii=False, indent=2)

    latest_file.write_text(text, encoding="utf-8")
    stamped_file.write_text(text, encoding="utf-8")

    return latest_file, stamped_file


def print_summary(report):
    print("=" * 80)
    print("LATS P3 RECHECK PATH V3")
    print("=" * 80)

    print("final_status:", report.get("final_status"))
    print("next_action:", report.get("next_action"))
    print("blockers:", report.get("blockers"))

    gap = report.get("runtime_gap_check", {})
    print("\n[RUNTIME GAP]")
    print("status:", gap.get("status"))
    print("code:", gap.get("code"))
    print("name:", gap.get("name"))
    print("gap_minutes:", gap.get("gap_minutes"))
    print("reason:", gap.get("reason"))
    print("action:", gap.get("action"))

    print("\n[STORAGE CHECK]")
    for item in report.get("missing_checks", []):
        print(
            item.get("status"),
            "|",
            item.get("name"),
            "|",
            item.get("reason"),
            "|",
            item.get("action"),
        )

    sr = report.get("signal_result_gap_check", {})
    s = sr.get("signal_report", {})
    r = sr.get("result_report", {})
    l = sr.get("link_report", {})

    print("\n[SIGNAL / RESULT GAP]")
    print("status:", sr.get("status"))
    print("signal_rows:", s.get("clean_rows"))
    print("signal_gap_count:", s.get("gap_count"))
    print("signal_largest_gap_minutes:", s.get("largest_gap_minutes"))
    print("result_rows:", r.get("clean_rows"))
    print("result_gap_count:", r.get("gap_count"))
    print("result_largest_gap_minutes:", r.get("largest_gap_minutes"))
    print("missing_result_count:", l.get("missing_result_count"))

    mem = report.get("memory_check", {})
    health = mem.get("health", {})
    cand = mem.get("candidate_stats", {})

    print("\n[MEMORY READ ONLY CHECK]")
    print("status:", mem.get("status"))
    print("memory_total:", health.get("total_memory"))
    print("health:", health.get("status"))
    print("candidate_total:", cand.get("total_candidates"))
    print("read_only:", mem.get("read_only"))

    print("\n[RULE]")
    print("RECHECK PATH does not update Memory Brain")
    print("REAL BACKFILL is not enabled in V3")


def main():
    report = build_report()
    latest_file, stamped_file = save_report(report)

    print_summary(report)

    print("\n[REPORT]")
    print("latest:", latest_file)
    print("stamped:", stamped_file)

    if report.get("final_status") != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
