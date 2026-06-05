# LATS P3
# Memory Continuous Runtime Runner V2
#
# Purpose:
# - Run Memory Brain runtime repeatedly
# - Use runtime_v2.run() which already uses MemoryAPI
# - Write runtime log
# - Write Memory Brain decision/error logs
#
# Scope:
# - TEST only
# - Memory Brain only
# - No AI Chief
# - No Risk Brain
# - No Execution Brain

import sys
import time
import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"
LOGIC = ROOT / "memory_brain" / "logic"

sys.path.insert(0, str(LOGIC))

from runtime_v2 import run
from memory_logger import (
    log_decision,
    log_error,
)


LOG_DIR = (
    ROOT
    / "logs"
    / "memory_runtime"
)

LATEST_FILE = (
    LOG_DIR
    / "latest_memory_runtime.json"
)

LOG_FILE = (
    LOG_DIR
    / "memory_runtime.log"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_log_dir():
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def write_log(message):
    ensure_log_dir()

    line = f"[{now_text()}] {message}\n"

    with LOG_FILE.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(line)

    print(line, end="")


def save_latest(payload):
    ensure_log_dir()

    with LATEST_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )


def build_decision_payload(result, loop_id):
    return {
        "loop_id": loop_id,
        "signal_id": result.get("signal_id"),
        "symbol": result.get("symbol"),
        "chain_id": result.get("chain_id"),
        "trend": result.get("trend"),
        "cycle": result.get("cycle"),
        "memory_source": result.get("memory_source"),
        "memory_status": result.get("memory_status"),
        "memory_score": result.get("memory_score"),
        "trade_decision": result.get("trade_decision"),
        "play_action": result.get("play_action"),
        "execution_mode": result.get("execution_mode"),
        "top_memory_results": result.get("top_memory_results", []),
    }


def run_once(loop_id=1):
    write_log(f"LOOP_START loop_id={loop_id}")

    try:
        result = run()

        payload = {
            "status": "OK",
            "loop_id": loop_id,
            "updated_at": now_text(),
            "result": result,
        }

        save_latest(payload)

        decision_payload = build_decision_payload(
            result,
            loop_id,
        )

        log_decision(decision_payload)

        write_log(
            "LOOP_OK "
            f"loop_id={loop_id} "
            f"symbol={result.get('symbol')} "
            f"memory_score={result.get('memory_score')} "
            f"decision={result.get('trade_decision')}"
        )

        return payload

    except Exception as exc:
        payload = {
            "status": "ERROR",
            "loop_id": loop_id,
            "updated_at": now_text(),
            "error": str(exc),
        }

        save_latest(payload)

        log_error(
            "MEMORY_RUNTIME_LOOP_ERROR",
            exc,
            {
                "loop_id": loop_id,
            },
        )

        write_log(
            f"LOOP_ERROR loop_id={loop_id} error={exc}"
        )

        return payload


def run_loop(
    max_loops=3,
    sleep_seconds=5,
):
    write_log(
        "MEMORY_RUNTIME_RUNNER_START "
        f"max_loops={max_loops} "
        f"sleep_seconds={sleep_seconds}"
    )

    results = []

    for loop_id in range(1, max_loops + 1):
        payload = run_once(loop_id=loop_id)
        results.append(payload)

        if loop_id < max_loops:
            write_log(
                f"SLEEP loop_id={loop_id} seconds={sleep_seconds}"
            )
            time.sleep(sleep_seconds)

    write_log("MEMORY_RUNTIME_RUNNER_END")

    return results


if __name__ == "__main__":
    run_loop(
        max_loops=3,
        sleep_seconds=2,
    )
