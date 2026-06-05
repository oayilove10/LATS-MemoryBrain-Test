# LATS V3
# Repository Snapshot V1

import json
from pathlib import Path
from datetime import datetime

from memory_repository import get_all_memories


BASE = Path.home() / "LATS_PRODUCTION_P3_TEST"

SNAPSHOT_DIR = (
    BASE /
    "memory_brain" /
    "data" /
    "snapshots"
)


def create_repository_snapshot():
    memories = get_all_memories()

    SNAPSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    snapshot_file = (
        SNAPSHOT_DIR /
        f"memory_index_snapshot_{timestamp}.json"
    )

    payload = {
        "created_at": datetime.now().isoformat(),
        "total_memory": len(memories),
        "memories": memories,
    }

    with snapshot_file.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return str(snapshot_file)


if __name__ == "__main__":
    print(create_repository_snapshot())
