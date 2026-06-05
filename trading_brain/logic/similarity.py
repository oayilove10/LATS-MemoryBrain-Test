# LATS V3
# Trading Brain - Similarity Engine V2


def score_similarity(signal, memory):
    score, detail = score_similarity_detail(signal, memory)
    return score


def score_similarity_detail(signal, memory):
    score = 0
    detail = {}

    detail["symbol"] = 20 if signal.get("symbol") == memory.get("symbol") else 0
    detail["cycle"] = 20 if signal.get("cycle") == memory.get("cycle") else 0
    detail["trend"] = 20 if signal.get("trend") == memory.get("trend") else 0
    detail["pattern"] = 20 if signal.get("pattern") == memory.get("pattern") else 0
    detail["direction"] = 20 if signal.get("direction") == memory.get("direction") else 0

    score = sum(detail.values())

    return score, detail


if __name__ == "__main__":
    signal = {
        "symbol": "BTCUSDT",
        "cycle": "continue_up",
        "trend": "up",
        "pattern": "pullback",
        "direction": "long",
    }

    memory = {
        "symbol": "BTCUSDT",
        "cycle": "continue_down",
        "trend": "down",
        "pattern": "breakout_continue_short",
        "direction": "short",
    }

    score, detail = score_similarity_detail(signal, memory)

    print(score)
    print(detail)
