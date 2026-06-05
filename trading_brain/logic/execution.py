# LATS V3 V1
# Trading Brain - Execution Mode


def classify_execution(play_action: str) -> str:

    play_action = str(play_action or "").upper()

    if play_action == "PLAY":
        return "NORMAL_EXECUTION"

    if play_action == "PLAY_REDUCED_RISK":
        return "REDUCED_RISK"

    if play_action == "WAIT_MORE_DATA":
        return "MONITOR"

    return "NO_TRADE"


if __name__ == "__main__":

    print(classify_execution("PLAY"))
    print(classify_execution("PLAY_REDUCED_RISK"))
    print(classify_execution("SKIP"))
