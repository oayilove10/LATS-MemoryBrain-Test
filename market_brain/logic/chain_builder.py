# LATS V3 V1
# Market Brain - Chain Builder
#
# EVENT -> CHAIN

def build_chain_record(events):
    if not events:
        return {
            "chain_id": "",
            "symbol": "",
            "start_event": "",
            "end_event": "",
            "event_count": 0,
            "trend": "unknown",
            "cycle": "unknown",
            "result": "",
            "status": "empty",
        }

    first = events[0]
    last = events[-1]

    symbol = first.get("symbol", "")

    chain_id = (
        f"CHAIN_{symbol}_"
        f"{first.get('event_type', 'START')}_"
        f"{last.get('event_type', 'END')}"
    )

    return {
        "chain_id": chain_id,
        "symbol": symbol,
        "start_event": first.get("event_type", ""),
        "end_event": last.get("event_type", ""),
        "event_count": len(events),
        "trend": "unknown",
        "cycle": "unknown",
        "result": "",
        "status": "waiting_result",
    }


if __name__ == "__main__":
    events = [
        {
            "symbol": "BTCUSDT",
            "timeframe": "4H",
            "event_type": "4H_BULL_CLOSE",
            "event_time": "2026-06-03 08:00:00",
        },
        {
            "symbol": "BTCUSDT",
            "timeframe": "1H",
            "event_type": "1H_BULL_CLOSE",
            "event_time": "2026-06-03 09:00:00",
        },
        {
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "event_type": "15m_LONG_SIGNAL",
            "event_time": "2026-06-03 09:15:00",
        },
    ]

    print(build_chain_record(events))
