from src.scoring.scorers.base_scorer import BaseScorer

from src.scoring.utils.safe_math import safe_float

from src.scoring.utils.normalization import (
    normalize_linear,
    normalize_inverse
)


class DividendScorer(BaseScorer):

    def calculate(self):

        info = self.data["INFO"]
        dividends = self.data["DIVIDENDS"]

        dividend_yield = safe_float(
            info.get("DIVIDEND YEILD")
        )

        payout_ratio = safe_float(
            info.get("PAYOUT RATIO")
        )

        dividend_cagr = safe_float(
            dividends.get("DIVIDEND CAGR")
        )

        has_cuts = dividends.get("HAS CUTS")

        dy_score = normalize_linear(
            dividend_yield,
            0,
            0.10
        )

        pr_score = normalize_inverse(
            payout_ratio,
            0,
            1.5
        )

        dg_score = normalize_linear(
            dividend_cagr,
            -0.10,
            0.20
        )

        if has_cuts:
            dg_score *= 0.5

        raw_score = (
            dy_score * 0.30 +
            pr_score * 0.30 +
            dg_score * 0.40
        )

        return {
            "score": round(raw_score, 2),

            "details": {
                "dividend_yield_score": round(dy_score, 2),
                "payout_ratio_score": round(pr_score, 2),
                "dividend_growth_score": round(dg_score, 2)
            }
        }