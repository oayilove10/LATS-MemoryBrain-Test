# LATS V3 V1
# Trading Brain - Play / Skip Engine


def classify_play_skip(decision: str) -> str:
    decision = str(decision or "").upper()

    if decision in ["ULTRA_STRONG_MATCH", "STRONG_MATCH"]:
        return "PLAY"

    if decision == "GOOD_MATCH":
        return "PLAY_REDUCED_RISK"

    if decision == "PARTIAL_MATCH":
        return "WAIT_MORE_DATA"

    return "SKIP"


if __name__ == "__main__":
    print(classify_play_skip("ULTRA_STRONG_MATCH"))
    print(classify_play_skip("GOOD_MATCH"))
    print(classify_play_skip("WEAK_MATCH"))
