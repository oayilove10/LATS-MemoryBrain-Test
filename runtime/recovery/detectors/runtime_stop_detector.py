# LATS P3
# Runtime Stop Detector V1
#
# Purpose:
# - Detect runtime stop / downtime before start
# - Save runtime stop history
#
# Rules:
# - READ ONLY to Memory Brain
# - No Memory update
# - No backfill execution

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

RUNTIME_LATEST = (
    ROOT
    / "logs"
    / "memory_runtime"
    / "latest_memory_runtime.json"
)

HISTORY_DIR = (
    ROOT
    / "runtime"
    / "recovery"
    / "history"
)

RUNTIME_STOP_HISTORY = (
    HISTORY_DIR
    / "runtime_stop_history.json"
)

STOP_WARN_MINUTES = 60


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def classify_downtime(minutes):
    try:
        minutes = float(minutes or 0)
    except Exception:
        minutes = 0

    if minutes < 60:
        return "DOWNTIME_SMALL"

    if minutes < 360:
        return "DOWNTIME_MEDIUM"

    if minutes < 1440:
        return "DOWNTIME_LARGE"

    return "DOWNTIME_CRITICAL"


def build_event():
    payload = load_json(RUNTIME_LATEST, {})

    if not payload:
        return {
            "event_type": "RUNTIME_STOP_CHECK",
            "status": "WARN",
            "reason": "LATEST_RUNTIME_FILE_MISSING",
            "last_runtime_time": None,
            "downtime_minutes": None,
            "severity": "UNKNOWN",
            "detected_at": now_text(),
            "memory_update": False,
        }

    last_time_text = payload.get("updated_at")
    last_time = parse_time(last_time_text)

    if not last_time:
        return {
            "event_type": "RUNTIME_STOP_CHECK",
            "status": "WARN",
            "reason": "LATEST_RUNTIME_TIME_INVALID",
            "last_runtime_time": last_time_text,
            "downtime_minutes": None,
            "severity": "UNKNOWN",
            "detected_at": now_text(),
            "memory_update": False,
        }

    now = datetime.now()
    downtime = round((now - last_time).total_seconds() / 60, 2)

    status = "OK"
    reason = "RUNTIME_GAP_WITHIN_LIMIT"

    if downtime >= STOP_WARN_MINUTES:
        status = "WARN"
        reason = "RUNTIME_STOP_DETECTED"

    return {
        "event_type": "RUNTIME_STOP_CHECK",
        "status": status,
        "reason": reason,
        "last_runtime_time": last_time_text,
        "downtime_minutes": downtime,
        "severity": classify_downtime(downtime),
        "detected_at": now_text(),
        "memory_update": False,
    }


def append_history(event):
    ensure_dir()

    history = load_json(RUNTIME_STOP_HISTORY, [])

    key = (
        event.get("event_type"),
        event.get("last_runtime_time"),
        event.get("reason"),
    )

    for old in history:
        old_key = (
            old.get("event_type"),
            old.get("last_runtime_time"),
            old.get("reason"),
        )

        if old_key == key:
            old["last_seen_at"] = now_text()
            old["seen_count"] = int(old.get("seen_count", 1) or 1) + 1
            save_json(RUNTIME_STOP_HISTORY, history)
            return False, old

    event["seen_count"] = 1
    event["last_seen_at"] = now_text()

    history.append(event)
    save_json(RUNTIME_STOP_HISTORY, history)

    return True, event


def print_summary(event, added):
    print("=" * 80)
    print("LATS P3 RUNTIME STOP DETECTOR V1")
    print("=" * 80)

    print("status:", event.get("status"))
    print("reason:", event.get("reason"))
    print("last_runtime_time:", event.get("last_runtime_time"))
    print("downtime_minutes:", event.get("downtime_minutes"))
    print("severity:", event.get("severity"))
    print("history_added:", added)
    print("seen_count:", event.get("seen_count"))

    print("\n[FILE]")
    print(RUNTIME_STOP_HISTORY)

    print("\n[RULE]")
    print("Runtime Stop Detector does not update Memory Brain")


def main():
    event = build_event()
    added, saved_event = append_history(event)

    print_summary(saved_event, added)

    if event.get("status") == "WARN":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
