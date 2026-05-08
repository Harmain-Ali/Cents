from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear


class TechnicalScorer(BaseScorer):
    """
    Calculate a technical score based on moving averages, RSI, MACD, and volume.

    The score is a weighted combination:
        - 40% moving average alignment (price vs MA50 vs MA200)
        - 30% RSI proximity to neutral (50)
        - 20% MACD line vs signal line
        - 10% volume ratio relative to 20‑day average

    Returns:
        dict: Contains 'score' (0–100) and 'details' with individual component scores.
    """

    def calculate(self):
        # Access data using the schema keys (lowercase)
        info = self.data["info"]
        history = self.data["history"]

        # --- Extract values with safe conversion ---
        current_price = safe_float(info.get("current_price"))

        ma50 = safe_float(history.get("ma50"))
        ma200 = safe_float(history.get("ma200"))

        rsi = safe_float(history.get("rsi_14"))

        macd = safe_float(history.get("macd"))
        signal = safe_float(history.get("signal"))

        volume = safe_float(info.get("volume"))
        avg_volume = safe_float(history.get("avg_volume_20d"))

        # --- 1. Moving Average Score ---
        ma_score = 50  # default neutral

        if current_price is not None and ma50 is not None and ma200 is not None:
            if current_price > ma50 > ma200:
                ma_score = 100
            elif current_price > ma200:
                ma_score = 70
            else:
                ma_score = 30

        # --- 2. RSI Score (distance from 50) ---
        if rsi is not None:
            # Maximum distance 50 → score from 0 to 100, scaled linearly
            rsi_score = 100 - abs(rsi - 50) * 2
            # Clamp to [0, 100] for safety
            rsi_score = max(0, min(100, rsi_score))
        else:
            rsi_score = 50

        # --- 3. MACD Score ---
        if macd is not None and signal is not None:
            macd_score = 100 if macd > signal else 40
        else:
            macd_score = 50

        # --- 4. Volume Score ---
        if volume is not None and avg_volume is not None and avg_volume > 0:
            volume_ratio = volume / avg_volume
            volume_score = normalize_linear(volume_ratio, 0.5, 2)
            # Clamp to [0, 100] as normalize_linear may produce values beyond
            volume_score = max(0, min(100, volume_score))
        else:
            volume_score = 50

        # --- Weighted final score ---
        raw_score = (
            ma_score * 0.40 +
            rsi_score * 0.30 +
            macd_score * 0.20 +
            volume_score * 0.10
        )

        return {
            "score": round(raw_score, 2),
            "details": {
                "ma_score": round(ma_score, 2),
                "rsi_score": round(rsi_score, 2),
                "macd_score": round(macd_score, 2),
                "volume_score": round(volume_score, 2),
            },
        }