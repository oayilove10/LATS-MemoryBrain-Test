# LATS V3
# Memory Health V2
#
# Check Memory Index health via Repository

from memory_repository import get_all_memories


def check_memory_health():
    memories = get_all_memories()

    total = len(memories)
    confirmed = 0
    candidate = 0
    missing_examples = 0
    duplicate_ids = 0

    seen_ids = set()

    for m in memories:
        memory_id = m.get("memory_id", "")

        if memory_id in seen_ids:
            duplicate_ids += 1
        else:
            seen_ids.add(memory_id)

        if m.get("status") == "confirmed":
            confirmed += 1

        if m.get("status") == "waiting_confirm":
            candidate += 1

        if not m.get("examples"):
            missing_examples += 1

    return {
        "total_memory": total,
        "confirmed": confirmed,
        "candidate": candidate,
        "missing_examples": missing_examples,
        "duplicate_ids": duplicate_ids,
        "status": "OK" if duplicate_ids == 0 else "WARN",
    }


if __name__ == "__main__":
    print(check_memory_health())
