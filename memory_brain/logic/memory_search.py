# LATS V3
# Memory Search V2
#
# Search memory from Memory Repository.
# Supports confirmed memory and candidate/waiting memory.

from memory_repository import get_all_memories


def get_status(memory):
    return memory.get("status", "confirmed")


def basic_score(query, memory):
    score = 0

    if query.get("symbol") == memory.get("symbol"):
        score += 40

    if query.get("trend") == memory.get("trend"):
        score += 30

    if query.get("cycle") == memory.get("cycle"):
        score += 30

    return score


def search_memory(query, status_filter=None, min_score=100):
    memories = get_all_memories()

    matches = []

    for memory in memories:
        status = get_status(memory)

        if status_filter and status != status_filter:
            continue

        score = basic_score(query, memory)

        if score >= min_score:
            item = memory.copy()
            item["search_score"] = score
            item["status"] = status
            matches.append(item)

    matches = sorted(
        matches,
        key=lambda x: (
            x.get("search_score", 0),
            x.get("hit_count", 0),
            x.get("confirmed_count", 0),
        ),
        reverse=True,
    )

    return matches


def search_confirmed_memory(query):
    return search_memory(
        query,
        status_filter="confirmed",
        min_score=100,
    )


def search_candidate_memory(query):
    return search_memory(
        query,
        status_filter="waiting_confirm",
        min_score=100,
    )


if __name__ == "__main__":
    query = {
        "symbol": "BTCUSDT",
        "trend": "up",
        "cycle": "continue_up",
    }

    print("CONFIRMED")
    print(search_confirmed_memory(query))

    print("CANDIDATE")
    print(search_candidate_memory(query))
