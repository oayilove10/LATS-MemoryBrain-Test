# LATS V3
# Memory Statistics


def update_stats(memory):

    memory["hit_count"] = (
        memory.get("hit_count", 0)
        + 1
    )

    memory["confirmed_count"] = (
        memory.get(
            "confirmed_count",
            0
        )
    )

    if (
        memory.get("status")
        ==
        "confirmed"
    ):
        memory["confirmed_count"] += 1

    return memory


if __name__ == "__main__":

    memory = {

        "memory_id":
        "MEM_TEST",

        "status":
        "confirmed"
    }

    print(
        update_stats(
            memory
        )
    )
