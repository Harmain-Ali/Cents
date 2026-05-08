# technical_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_technical_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute common technical indicators from price/volume history.

    The function expects a `history` key with a `data` field containing a DataFrame
    of daily OHLCV data. It calculates:
        - 50‑day and 200‑day simple moving averages (ma50, ma200)
        - 14‑day Relative Strength Index (RSI)
        - MACD line and signal line (12, 26, 9)
        - 20‑day average volume (avg_volume_20d)

    Only the latest values of these indicators are stored back into `data["history"]`
    as top‑level keys for easy access by scorers.

    Args:
        data (Dict[str, Any]): Stock data dictionary. Must contain `history.data`,
            a pandas DataFrame with at least `close` and `volume` columns.

    Returns:
        Dict[str, Any]: The same data dictionary, enriched with the following
        keys under `history`:
            - ma50 (float or None)
            - ma200 (float or None)
            - rsi_14 (float or None)
            - macd (float or None)
            - signal (float or None)
            - avg_volume_20d (float or None)

        If the price history is missing or empty, the function returns unmodified data.
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