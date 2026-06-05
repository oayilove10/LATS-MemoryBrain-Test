# LATS P3
# Memory Loop V4
#
# Purpose:
# - Core memory decision loop
# - Search existing memory
# - Promote/update memory if found
# - Check raw data fallback
# - Create waiting_confirm candidate if not found
#
# Scope:
# - Memory Brain only
# - No AI Chief
# - No Risk Brain
# - No Execution Brain

from memory_search import search_memory
from memory_matcher import match_memory
from memory_promoter import promote_memory
from memory_rawdata_validator import check_raw_data
from memory_statistics_v2 import update_memory_stats
from example_manager import add_example
from candidate_repository import upsert_candidate


def build_query(memory_record):
    return {
        "symbol": memory_record.get("symbol"),
        "trend": memory_record.get("trend"),
        "cycle": memory_record.get("cycle"),
    }


def get_example_id(memory_record):
    return memory_record.get(
        "chain_id",
        memory_record.get(
            "event_id",
            memory_record.get(
                "memory_id",
                "",
            ),
        ),
    )


def run_memory_loop(memory_record):
    query = build_query(memory_record)

    memories = search_memory(
        query,
        status_filter="confirmed",
        min_score=100,
    )

    example_id = get_example_id(memory_record)

    # CASE 1: FOUND IN MEMORY
    if memories:
        match_result = match_memory(
            query,
            memories,
        )

        best_memory = match_result.get("best_memory")

        final_memory = promote_memory(
            memory_record,
            best_memory,
        )

        final_memory["match_score"] = match_result.get("score", 0)
        final_memory["memory_source"] = "memory"
        final_memory["status"] = "confirmed"

        final_memory = update_memory_stats(final_memory)
        final_memory = add_example(final_memory, example_id)

        return final_memory

    # CASE 2: NOT FOUND IN MEMORY → CHECK RAW DATA
    raw_result = check_raw_data(memory_record)

    if raw_result.get("found"):
        memory_record["status"] = "confirmed"
        memory_record["memory_source"] = "raw_data"
        memory_record["evidence_id"] = raw_result.get("evidence_id", "")
        memory_record["match_score"] = raw_result.get("similarity", 0)

        memory_record = update_memory_stats(memory_record)
        memory_record = add_example(memory_record, example_id)

        return memory_record

    # CASE 3: NOT FOUND ANYWHERE → CANDIDATE
    memory_record["status"] = "waiting_confirm"
    memory_record["memory_source"] = "candidate"
    memory_record["match_score"] = 0

    memory_record = update_memory_stats(memory_record)
    memory_record = add_example(memory_record, example_id)

    upsert_candidate(memory_record)

    return memory_record


if __name__ == "__main__":
    memory_record = {
        "memory_id": "MEM_LOOP_TEST",
        "symbol": "BTCUSDT",
        "chain_id": "CHAIN_LOOP_TEST",
        "trend": "up",
        "cycle": "continue_up",
    }

    print(run_memory_loop(memory_record))
