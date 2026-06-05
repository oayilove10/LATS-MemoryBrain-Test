# LATS P3
# Memory Repository V2
#
# Purpose:
# - Public repository access for Memory Brain
# - Load / save / upsert / find memory
# - Write memory_update.log via memory_logger
#
# Scope:
# - TEST only
# - Memory Brain only

from memory_persistence import (
    load_memory_index,
    save_memory_index,
)

from memory_upsert import upsert_memory

from memory_logger import (
    log_update,
)


def get_all_memories():
    return load_memory_index()


def save_all_memories(memories):
    return save_memory_index(memories)


def upsert(memory):
    memories = load_memory_index()

    memories = upsert_memory(
        memories,
        memory,
    )

    save_memory_index(memories)

    return memory


def find_by_id(memory_id):
    memories = load_memory_index()

    for memory in memories:

        if memory.get("memory_id") == memory_id:
            return memory

    return None


if __name__ == "__main__":

    test_memory = {
        "memory_id": "MEM_REPO_TEST",
        "symbol": "BTCUSDT",
        "trend": "up",
        "cycle": "continue_up",
        "status": "confirmed",
        "hit_count": 1,
        "confirmed_count": 1,
        "examples": [
            "CHAIN_REPO_TEST"
        ],
    }

    upsert(test_memory)

    print(
        find_by_id(
            "MEM_REPO_TEST"
        )
    )
