# LATS V3 V1
# Trend From Chain


def detect_trend(chain):

    start_event = chain.get(
        "start_event",
        ""
    )

    end_event = chain.get(
        "end_event",
        ""
    )

    text = (
        start_event +
        " " +
        end_event
    ).upper()

    if (
        "BULL" in text
        or
        "LONG" in text
    ):
        return "up"

    if (
        "BEAR" in text
        or
        "SHORT" in text
    ):
        return "down"

    return "conflict"


if __name__ == "__main__":

    chain = {
        "chain_id":
        "CHAIN_BTCUSDT_4H_BULL_CLOSE_15m_LONG_SIGNAL",

        "symbol":
        "BTCUSDT",

        "start_event":
        "4H_BULL_CLOSE",

        "end_event":
        "15m_LONG_SIGNAL",

        "event_count":
        3,
    }

    print(
        detect_trend(
            chain
        )
    )
