# LATS V3
# Repository Statistics V1
#
# Analyze full memory repository.
# This is logic layer, not monitor layer.

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


def normalize_memory(memory):
    item = memory.copy()

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
            len(get_examples(memory)),
        )
    )

    return item


def build_repository_statistics(top_n=5):
    memories = [
        normalize_memory(memory)
        for memory in get_all_memories()
    ]

    confirmed = [
        memory for memory in memories
        if memory.get("status") == "confirmed"
    ]

    candidate = [
        memory for memory in memories
        if memory.get("status") == "waiting_confirm"
    ]

    rejected = [
        memory for memory in memories
        if memory.get("status") == "rejected"
    ]

    total_examples = sum(
        memory.get("example_count", 0)
        for memory in memories
    )

    avg_examples = (
        round(total_examples / len(memories), 2)
        if memories
        else 0
    )

    top_hit = sorted(
        memories,
        key=lambda x: (
            x.get("hit_count", 0),
            x.get("confirmed_count", 0),
            x.get("example_count", 0),
        ),
        reverse=True,
    )[:top_n]

    top_confirmed = sorted(
        memories,
        key=lambda x: (
            x.get("confirmed_count", 0),
            x.get("hit_count", 0),
            x.get("example_count", 0),
        ),
        reverse=True,
    )[:top_n]

    low_usage = [
        memory for memory in memories
        if memory.get("hit_count", 0) <= 1
    ]

    no_examples = [
        memory for memory in memories
        if memory.get("example_count", 0) == 0
    ]

    return {
        "total_memory": len(memories),
        "confirmed_memory": len(confirmed),
        "candidate_memory": len(candidate),
        "rejected_memory": len(rejected),
        "avg_examples": avg_examples,
        "low_usage_count": len(low_usage),
        "no_examples_count": len(no_examples),

        "top_hit_memory": [
            {
                "memory_id": memory.get("memory_id"),
                "hit_count": memory.get("hit_count", 0),
                "confirmed_count": memory.get("confirmed_count", 0),
                "example_count": memory.get("example_count", 0),
            }
            for memory in top_hit
        ],

        "top_confirmed_memory": [
            {
                "memory_id": memory.get("memory_id"),
                "confirmed_count": memory.get("confirmed_count", 0),
                "hit_count": memory.get("hit_count", 0),
                "example_count": memory.get("example_count", 0),
            }
            for memory in top_confirmed
        ],
    }


if __name__ == "__main__":
    print(build_repository_statistics())
