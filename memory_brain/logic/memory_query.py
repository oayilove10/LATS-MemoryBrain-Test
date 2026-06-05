# LATS V3
# Memory Query V4
#
# Search Memory Index via Repository
# Safe for old/simple memory records

from memory_repository import get_all_memories


def safe_int(value, default=0):
    try:
        return int(value or default)
    except Exception:
        return default


def get_status(memory):
    return memory.get("status", "confirmed")


def get_examples(memory):
    return memory.get("examples", [])


def score_memory(query, memory):
    score = 0
    reasons = []

    if query.get("symbol") == memory.get("symbol"):
        score += 40
        reasons.append("symbol_match")

    if query.get("trend") == memory.get("trend"):
        score += 30
        reasons.append("trend_match")

    if query.get("cycle") == memory.get("cycle"):
        score += 30
        reasons.append("cycle_match")

    return score, reasons


def is_usable_memory(memory):
    return get_status(memory) == "confirmed"


def enrich_result(memory, score, reasons):
    item = memory.copy()

    examples = get_examples(memory)

    item["query_score"] = score
    item["query_reasons"] = reasons
    item["status"] = get_status(memory)
    item["hit_count"] = safe_int(memory.get("hit_count", 0))
    item["confirmed_count"] = safe_int(
        memory.get(
            "confirmed_count",
            1 if get_status(memory) == "confirmed" else 0,
        )
    )
    item["example_count"] = safe_int(
        memory.get(
            "example_count",
            len(examples),
        )
    )

    return item


def query_memory_index(query, top_n=5, confirmed_only=True):
    memories = get_all_memories()

    results = []

    for memory in memories:
        if confirmed_only and not is_usable_memory(memory):
            continue

        score, reasons = score_memory(query, memory)

        if score > 0:
            results.append(
                enrich_result(
                    memory,
                    score,
                    reasons,
                )
            )

    results = sorted(
        results,
        key=lambda x: (
            x.get("query_score", 0),
            x.get("hit_count", 0),
            x.get("confirmed_count", 0),
            x.get("example_count", 0),
        ),
        reverse=True,
    )

    return results[:top_n]


if __name__ == "__main__":
    query = {
        "symbol": "BTCUSDT",
        "trend": "up",
        "cycle": "continue_up",
    }

    print(query_memory_index(query))
