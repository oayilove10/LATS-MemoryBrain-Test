# LATS V3 V1
# Trading Brain - Pattern Engine


def build_pattern(signal: dict) -> str:

    pattern = (
        f"{signal.get('cycle', 'unknown')}>"
        f"{signal.get('trend', 'unknown')}>"
        f"{signal.get('zone', 'unknown')}>"
        f"{signal.get('direction', 'unknown')}"
    )

    return pattern


if __name__ == "__main__":

    signal = {
        "cycle": "continue_up",
        "trend": "up",
        "zone": "support",
        "direction": "long",
    }

    print(build_pattern(signal))
