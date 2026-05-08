from src.scoring.scorers.base_scorer import BaseScorer

from src.scoring.utils.safe_math import safe_float

from src.scoring.utils.normalization import (
    normalize_linear,
    normalize_inverse
)


class FinancialHealthScorer(BaseScorer):

    def calculate(self):

        info = self.data["INFO"]

        debt_to_equity = safe_float(
            info.get("DEBT TO EQUITY")
        )

        current_ratio = safe_float(
            info.get("CURRENT RATIO")
        )

        quick_ratio = safe_float(
            info.get("QUICK RATIO")
        )

        free_cashflow = safe_float(
            info.get("FREE CASH FLOW")
        )

        market_cap = safe_float(
            info.get("MARKET CAP")
        )

        de_score = normalize_inverse(
            debt_to_equity,
            0,
            3
        )

        cr_score = normalize_linear(
            current_ratio,
            0.5,
            4
        )

        qr_score = normalize_linear(
            quick_ratio,
            0.2,
            3
        )

        if free_cashflow and market_cap:

            fcf_yield = free_cashflow / market_cap

        else:
            fcf_yield = None

        fcf_score = normalize_linear(
            fcf_yield,
            -0.05,
            0.15
        )

        raw_score = (
            de_score * 0.30 +
            cr_score * 0.30 +
            qr_score * 0.20 +
            fcf_score * 0.20
        )

        return {
            "score": round(raw_score, 2),

            "details": {
                "debt_to_equity_score": round(de_score, 2),
                "current_ratio_score": round(cr_score, 2),
                "quick_ratio_score": round(qr_score, 2),
                "fcf_score": round(fcf_score, 2)
            }
        }