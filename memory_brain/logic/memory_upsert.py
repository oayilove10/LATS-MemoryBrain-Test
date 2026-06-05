# LATS V3
# Memory Upsert V3
#
# If memory_id exists -> update existing memory
# Merge examples without duplicates
# Accumulate counters
# Keep max 10 examples

MAX_EXAMPLES = 10


def merge_examples(old_memory, new_memory):
    old_examples = old_memory.get("examples", [])
    new_examples = new_memory.get("examples", [])

    merged = []

    for item in old_examples + new_examples:
        if item not in merged:
            merged.append(item)

    if len(merged) > MAX_EXAMPLES:
        merged = merged[-MAX_EXAMPLES:]

    return merged


def accumulate_count(old_memory, new_memory, key):
    return (
        int(old_memory.get(key, 0) or 0)
        +
        int(new_memory.get(key, 0) or 0)
    )


def upsert_memory(memory_index, new_memory):
    new_id = new_memory.get("memory_id", "")

    if not new_id:
        memory_index.append(new_memory)
        return memory_index

    for i, old_memory in enumerate(memory_index):
        if old_memory.get("memory_id") == new_id:
            merged = old_memory.copy()
            merged.update(new_memory)

            merged["hit_count"] = accumulate_count(
                old_memory,
                new_memory,
                "hit_count",
            )

            merged["confirmed_count"] = accumulate_count(
                old_memory,
                new_memory,
                "confirmed_count",
            )

            examples = merge_examples(
                old_memory,
                new_memory,
            )

            merged["examples"] = examples
            merged["example_count"] = len(examples)

            if old_memory.get("first_seen"):
                merged["first_seen"] = old_memory.get("first_seen")

            memory_index[i] = merged
            return memory_index

    memory_index.append(new_memory)
    return memory_index


if __name__ == "__main__":
    memory_index = [
        {
            "memory_id": "MEM001",
            "hit_count": 3,
            "confirmed_count": 2,
            "examples": ["CHAIN_001"],
            "example_count": 1,
            "first_seen": "OLD_TIME",
        }
    ]

    new_memory = {
        "memory_id": "MEM001",
        "hit_count": 1,
        "confirmed_count": 1,
        "examples": ["CHAIN_002"],
        "example_count": 1,
        "first_seen": "NEW_TIME",
        "last_seen": "NEW_TIME",
    }

    print(upsert_memory(memory_index, new_memory))
