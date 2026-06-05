# LATS P3
# Memory Logger V2
#
# Purpose:
# - Central logging helper for Memory Brain
# - Separate decision / candidate / update / error logs
# - Support Error Registry
#
# Scope:
# - TEST only
# - Memory Brain only

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

sys.path.insert(
    0,
    str(ROOT / "shared")
)

from error_registry import get_error


LOG_DIR = (
    ROOT
    / "logs"
    / "memory_brain"
)

DECISION_LOG = LOG_DIR / "memory_decision.log"
CANDIDATE_LOG = LOG_DIR / "candidate.log"
UPDATE_LOG = LOG_DIR / "memory_update.log"
ERROR_LOG = LOG_DIR / "memory_error.log"


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_log_dir():
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def safe_json(data):
    try:
        return json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
        )
    except Exception:
        return str(data)


def write_line(path, event, payload=None):
    ensure_log_dir()

    record = {
        "time": now_text(),
        "event": event,
        "payload": payload or {},
    }

    with path.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(safe_json(record) + "\n")

    return record


def log_decision(payload):
    return write_line(
        DECISION_LOG,
        "MEMORY_DECISION",
        payload,
    )


def log_candidate(event, payload):
    return write_line(
        CANDIDATE_LOG,
        event,
        payload,
    )


def log_update(payload):
    return write_line(
        UPDATE_LOG,
        "MEMORY_UPDATE",
        payload,
    )


def log_error(event, error, payload=None):
    data = {
        "error": str(error),
        "context": payload or {},
    }

    return write_line(
        ERROR_LOG,
        event,
        data,
    )


def log_error_code(
    code,
    error,
    payload=None,
):
    meta = get_error(code)

    data = {
        "code": code,
        "name": meta.get("name"),
        "level": meta.get("level"),
        "error": str(error),
        "payload": payload or {},
    }

    return write_line(
        ERROR_LOG,
        "ERROR",
        data,
    )


if __name__ == "__main__":

    log_decision(
        {
            "signal_id": "TEST_SIGNAL",
            "memory_id": "TEST_MEMORY",
            "memory_score": 100,
            "decision": "TEST_DECISION",
        }
    )

    log_candidate(
        "CREATE_CANDIDATE",
        {
            "candidate_id": "TEST_CANDIDATE",
            "status": "waiting_confirm",
        }
    )

    log_update(
        {
            "memory_id": "TEST_MEMORY",
            "hit_count_before": 1,
            "hit_count_after": 2,
        }
    )

    log_error_code(
        "MEM-301",
        "runtime loop failed",
        {
            "module": "runtime_runner",
        },
    )

    print("PASS: memory_logger.py")
