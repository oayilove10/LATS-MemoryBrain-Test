# LATS V3
# Memory Statistics V2

from datetime import datetime


def update_memory_stats(memory):

    memory["hit_count"] = (
        memory.get("hit_count", 0)
        + 1
    )

    if "first_seen" not in memory:

        memory["first_seen"] = (
            datetime.now().isoformat()
        )

    memory["last_seen"] = (
        datetime.now().isoformat()
    )

    memory["example_count"] = (
        memory.get(
            "example_count",
            0
        )
    )

    if (
        memory.get("status")
        ==
        "confirmed"
    ):
        memory["confirmed_count"] = (
            memory.get(
                "confirmed_count",
                0
            )
            + 1
        )

    return memory


if __name__ == "__main__":

    memory = {

        "memory_id":
        "MEM001",

        "status":
        "confirmed"
    }

    print(
        update_memory_stats(
            memory
        )
    )
