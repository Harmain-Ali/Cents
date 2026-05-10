def interpret_rsi(rsi):
    if rsi is None:
        return None
    if rsi > 70:
        return {
            "impact": "negative",
            "text": f"Overbought – potential pullback (RSI {rsi:.0f})",
            "importance": min(10, (rsi - 70) / 3)
        }
    elif rsi < 30:
        return {
            "impact": "positive",
            "text": f"Oversold – possible bounce (RSI {rsi:.0f})",
            "importance": min(10, (30 - rsi) / 3)
        }
    return None

def interpret_trend(price, ma50, ma200):
    if price is None or ma50 is None or ma200 is None:
        return None
    if price > ma50 > ma200:
        return {"impact": "positive", "text": "Strong upward price trend", "importance": 8}
    elif price > ma200:
        return {"impact": "positive", "text": "Price above long‑term average (bullish)", "importance": 5}
    elif price < ma200:
        return {"impact": "negative", "text": "Price below long‑term average (bearish)", "importance": 6}
    return None