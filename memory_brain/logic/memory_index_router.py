# LATS V3
# Memory Index Router V5
#
# Flow:
# 1. Search confirmed memory
# 2. If found -> confirmed / matched repository
# 3. If not found -> search candidate memory
# 4. If candidate found -> promote if count reaches threshold
# 5. If no candidate -> waiting_confirm
# 6. Upsert final memory into repository

from memory_search import (
    search_confirmed_memory,
    search_candidate_memory,
)
from memory_promoter import promote_memory
from memory_statistics_v2 import update_memory_stats
from memory_repository import (
    get_all_memories,
    save_all_memories,
    find_by_id,
)
from memory_upsert import upsert_memory


def build_query(memory_record):
    return {
        "symbol": memory_record.get("symbol"),
        "trend": memory_record.get("trend"),
        "cycle": memory_record.get("cycle"),
    }


def get_best_match(matches):
    if not matches:
        return None
    return matches[0]


def save_final_memory(final_memory):
    memories = get_all_memories()

    memories = upsert_memory(
        memories,
        final_memory,
    )

    save_all_memories(memories)

    return (
        find_by_id(final_memory.get("memory_id"))
        or final_memory
    )


def ensure_examples(memory_record):
    if memory_record.get("examples"):
        return memory_record

    chain_id = memory_record.get("chain_id")
    if chain_id:
        memory_record["examples"] = [chain_id]
        memory_record["example_count"] = 1

    return memory_record


def route_memory(memory_record):
    memory_record = ensure_examples(memory_record.copy())

    query = build_query(memory_record)

    confirmed_matches = search_confirmed_memory(query)
    matched_memory = get_best_match(confirmed_matches)

    candidate_matches = []
    candidate_memory = None

    if not matched_memory:
        candidate_matches = search_candidate_memory(query)
        candidate_memory = get_best_match(candidate_matches)

    promoted = promote_memory(
        memory_record.copy(),
        matched_memory=matched_memory,
        candidate_memory=candidate_memory,
        confirm_threshold=2,
    )

    updated = update_memory_stats(promoted)

    saved = save_final_memory(updated)

    saved["router_stage"] = "memory_index_router_v5"
    saved["matched_confirmed_count"] = len(confirmed_matches)
    saved["matched_candidate_count"] = len(candidate_matches)

    return saved


if __name__ == "__main__":
    tests = [
        {
            "memory_id": "MEM_ROUTER_V5_TEST",
            "symbol": "TESTCOIN",
            "chain_id": "CHAIN_ROUTER_V5_TEST",
            "trend": "up",
            "cycle": "continue_up",
        }
    ]

    for item in tests:
        print(route_memory(item))
