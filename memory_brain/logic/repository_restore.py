# LATS V3
# Repository Restore V1

import json
from pathlib import Path

from memory_persistence import save_memory_index


BASE = Path.home() / "LATS_PRODUCTION_P3_TEST"

SNAPSHOT_DIR = (
    BASE /
    "memory_brain" /
    "data" /
    "snapshots"
)


def list_snapshots():
    if not SNAPSHOT_DIR.exists():
        return []

    return sorted(
        SNAPSHOT_DIR.glob("memory_index_snapshot_*.json")
    )


def restore_latest_snapshot():
    snapshots = list_snapshots()

    if not snapshots:
        return {
            "status": "ERROR",
            "message": "No snapshot found",
        }

    latest = snapshots[-1]

    with latest.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    memories = payload.get("memories", [])

    save_memory_index(memories)

    return {
        "status": "OK",
        "restored_from": str(latest),
        "total_memory": len(memories),
    }


if __name__ == "__main__":
    print(restore_latest_snapshot())
