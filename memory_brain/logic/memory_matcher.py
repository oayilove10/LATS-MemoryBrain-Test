# LATS V3 V1
# Memory Matcher


def match_memory(
    current_context,
    memories
):

    if not memories:
        return None

    best_memory = None
    best_score = -1

    for m in memories:

        score = 0

        if (
            current_context.get("symbol")
            ==
            m.get("symbol")
        ):
            score += 40

        if (
            current_context.get("trend")
            ==
            m.get("trend")
        ):
            score += 30

        if (
            current_context.get("cycle")
            ==
            m.get("cycle")
        ):
            score += 30

        if score > best_score:

            best_score = score
            best_memory = m

    return {

        "best_memory":
            best_memory,

        "score":
            best_score,
    }


if __name__ == "__main__":

    context = {

        "symbol":
        "BTCUSDT",

        "trend":
        "up",

        "cycle":
        "continue_up",
    }

    memories = [

        {
            "memory_id":
            "MEM001",

            "symbol":
            "BTCUSDT",

            "trend":
            "up",

            "cycle":
            "continue_up",
        },

        {
            "memory_id":
            "MEM002",

            "symbol":
            "BTCUSDT",

            "trend":
            "down",

            "cycle":
            "continue_down",
        }
    ]

    print(
        match_memory(
            context,
            memories
        )
    )
