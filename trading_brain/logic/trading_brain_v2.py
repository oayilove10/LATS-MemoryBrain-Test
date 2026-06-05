# LATS V3 V1
# Trading Brain V2


def run_trading_brain(
    context,
    memory_match
):

    score = memory_match.get(
        "score",
        0
    )

    if score >= 90:

        return {

            "decision":
            "ULTRA_STRONG_MATCH",

            "play_action":
            "PLAY",

            "execution_mode":
            "NORMAL_EXECUTION",

            "score":
            score,
        }

    if score >= 70:

        return {

            "decision":
            "STRONG_MATCH",

            "play_action":
            "PLAY",

            "execution_mode":
            "REDUCED_RISK",

            "score":
            score,
        }

    if score >= 50:

        return {

            "decision":
            "MEDIUM_MATCH",

            "play_action":
            "CAUTION",

            "execution_mode":
            "REDUCED_RISK",

            "score":
            score,
        }

    return {

        "decision":
        "WEAK_MATCH",

        "play_action":
        "SKIP",

        "execution_mode":
        "NO_TRADE",

        "score":
        score,
    }


if __name__ == "__main__":

    context = {

        "trend":
        "up",

        "cycle":
        "continue_up",
    }

    memory_match = {

        "score":
        100
    }

    print(
        run_trading_brain(
            context,
            memory_match
        )
    )
