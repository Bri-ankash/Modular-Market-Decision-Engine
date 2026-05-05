def detect_regime(candles):
    closes = [c["close"] for c in candles]
    if len(closes) < 20:
        return "UNKNOWN"

    recent = closes[-10:]
    older = closes[-20:-10]

    recent_trend = (recent[-1] - recent[0]) / recent[0]
    older_trend = (older[-1] - older[0]) / older[0]

    volatility = sum(abs(closes[i]-closes[i-1]) for i in range(1,len(closes))) / len(closes)

    if abs(recent_trend) < 0.002:
        return "RANGE"

    if volatility > sum(closes)/len(closes)*0.003:
        return "VOLATILE"

    if recent_trend > 0:
        return "UPTREND"

    return "DOWNTREND"
