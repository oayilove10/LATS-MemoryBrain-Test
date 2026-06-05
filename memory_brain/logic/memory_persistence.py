# LATS P3
# Memory Persistence V2

import json
from pathlib import Path

from memory_logger import log_error_code


BASE = Path.home() / "LATS_PRODUCTION_P3_TEST"

MEMORY_DIR = (
    BASE /
    "memory_brain" /
    "data"
)

MEMORY_FILE = (
    MEMORY_DIR /
    "memory_index.json"
)


def load_memory_index():

    if not MEMORY_FILE.exists():
        return []

    try:

        with MEMORY_FILE.open(
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception as exc:

        log_error_code(
            "MEM-001",
            exc,
            {
                "module": "memory_persistence",
                "action": "load_memory_index",
                "file": str(MEMORY_FILE),
            },
        )

        return []


def save_memory_index(memory_list):

    MEMORY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        with MEMORY_FILE.open(
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory_list,
                f,
                ensure_ascii=False,
                indent=2
            )

        return str(MEMORY_FILE)

    except Exception as exc:

        log_error_code(
            "MEM-002",
            exc,
            {
                "module": "memory_persistence",
                "action": "save_memory_index",
                "file": str(MEMORY_FILE),
            },
        )

        raise


if __name__ == "__main__":

    memories = [
        {
            "memory_id": "MEM_TEST_001",
            "symbol": "BTCUSDT",
            "trend": "up",
            "cycle": "continue_up",
            "hit_count": 1,
            "examples": ["CHAIN_TEST_001"],
        }
    ]

    path = save_memory_index(memories)

    print(path)
    print(load_memory_index())
