from src.scoring.scorers.base_scorer import BaseScorer

from src.scoring.utils.safe_math import safe_float

from src.scoring.utils.normalization import (
    normalize_linear
)


class TechnicalScorer(BaseScorer):

    def calculate(self):

        info = self.data["INFO"]
        history = self.data["HISTORY"]

        current_price = safe_float(
            info.get("CURRENT PRICE")
        )

        ma50 = safe_float(history.get("MA50"))
        ma200 = safe_float(history.get("MA200"))

        rsi = safe_float(
            history.get("RSI(14DAYS)")
        )

        macd = safe_float(
            history.get("MACD LINE")
        )

        signal = safe_float(
            history.get("SIGNAL LINE")
        )

        volume = safe_float(
            info.get("VOLUME")
        )

        avg_volume = safe_float(
            history.get("AVERAGE VOLUME(20 DAYS)")
        )

        ma_score = 50

        if current_price and ma50 and ma200:

            if current_price > ma50 > ma200:
                ma_score = 100

            elif current_price > ma200:
                ma_score = 70

            else:
                ma_score = 30

        rsi_score = 100 - abs(rsi - 50) * 2 \
            if rsi is not None else 50

        if macd and signal:

            macd_score = 100 if macd > signal else 40

        else:
            macd_score = 50

        if volume and avg_volume:

            volume_ratio = volume / avg_volume

        else:
            volume_ratio = None

        volume_score = normalize_linear(
            volume_ratio,
            0.5,
            2
        )

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
                "volume_score": round(volume_score, 2)
            }
        }