# technical_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_technical_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds MA, RSI, MACD, Volume metrics inside HISTORY
    """

    history = data.get("history", {})
    df = history.get("data")

    if df is None or df.empty:
        return data

    df = df.copy()

    # Moving averages
    df["ma50"] = df["close"].rolling(50).mean()
    df["ma200"] = df["close"].rolling(200).mean()

    # RSI (14)
    delta = df["close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()

    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # Volume
    df["avg_volume_20"] = df["volume"].rolling(20).mean()

    latest = df.iloc[-1]

    # Inject into HISTORY
    history.update({
        "ma50": latest["ma50"],
        "ma200": latest["ma200"],
        "rsi_14": latest["rsi"],
        "macd": latest["macd"],
        "signal": latest["signal"],
        "avg_volume_20d": latest["avg_volume_20"]
    })

    return data