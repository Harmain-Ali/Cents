from src.scoring.utils.safe_math import (
    safe_float
)


class RiskAdjustments:

    @staticmethod
    def apply(data, score):

        info = data["INFO"]
        history = data["HISTORY"]

        adjusted = score

        market_cap = safe_float(
            info.get("MARKET CAP")
        )

        beta = safe_float(
            info.get("BETA")
        )

        sector = info.get("SECTOR")

        pe = safe_float(
            info.get("PE RATIO")
        )

        earnings_growth = safe_float(
            info.get("EARNINGS GROWTH")
        )

        free_cashflow = safe_float(
            info.get("FREE CASH FLOW")
        )

        payout_ratio = safe_float(
            info.get("PAYOUT RATIO")
        )

        ma50 = safe_float(
            history.get("MA50")
        )

        ma200 = safe_float(
            history.get("MA200")
        )

        # ------------------------------------------------
        # MARKET CAP ADJUSTMENT
        # ------------------------------------------------

        if market_cap:

            # Small Cap Risk
            if market_cap < 2_000_000_000:
                adjusted -= 5

            # Mega Cap Stability
            elif market_cap > 200_000_000_000:
                adjusted += 2

        # ------------------------------------------------
        # BETA ADJUSTMENT
        # ------------------------------------------------

        if beta:

            if beta > 1.5:
                adjusted -= 3

            elif beta < 0.5:
                adjusted += 2

        # ------------------------------------------------
        # SECTOR RISK
        # ------------------------------------------------

        risky_sectors = [
            "Biotechnology",
            "Crypto",
            "Cannabis"
        ]

        if sector in risky_sectors:
            adjusted -= 3

        # ------------------------------------------------
        # DIVIDEND SAFETY
        # ------------------------------------------------

        if payout_ratio is not None and free_cashflow is not None:

            if payout_ratio > 1 and free_cashflow < 0:
                adjusted -= 4

        # ------------------------------------------------
        # VALUE TRAP DETECTION
        # ------------------------------------------------

        if pe is not None and earnings_growth is not None:

            if pe < 10 and earnings_growth < 0:
                adjusted -= 5

        # ------------------------------------------------
        # WEAK MOMENTUM
        # ------------------------------------------------

        if ma50 and ma200:

            if ma50 < ma200:
                adjusted -= 2

        # ------------------------------------------------
        # NEGATIVE FREE CASH FLOW
        # ------------------------------------------------

        if free_cashflow is not None:

            if free_cashflow < 0:
                adjusted -= 3

        return adjusted