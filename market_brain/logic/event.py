# LATS V3 V1
# Market Brain - Event Layer

def build_event(snapshot):
    timeframe = snapshot.get("timeframe", "15m")
    signal_type = str(snapshot.get("signal_type", "")).upper()

    if timeframe == "15m" and signal_type == "LONG":
        event_type = "15m_LONG_SIGNAL"
    elif timeframe == "15m" and signal_type == "SHORT":
        event_type = "15m_SHORT_SIGNAL"
    else:
        event_type = snapshot.get("event_type", "signal")

    event_time = snapshot.get(
        "event_time",
        snapshot.get("signal_time", "")
    )

    return {
        "timeframe": timeframe,
        "event_type": event_type,
        "event_time": event_time,
        "symbol": snapshot.get("symbol", ""),
    }


if __name__ == "__main__":
    sample = {
        "symbol": "BTCUSDT",
        "timeframe": "15m",
        "signal_type": "LONG",
        "event_time": "2026-06-03 09:15:00",
    }

    print(build_event(sample))
