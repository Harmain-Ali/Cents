from src.scoring.scorers.base_scorer import BaseScorer

from src.scoring.utils.safe_math import safe_float

from src.scoring.utils.normalization import (
    normalize_linear
)


class GrowthScorer(BaseScorer):

    def calculate(self):

        info = self.data["INFO"]
        financials = self.data["FINANCIALS"]

        revenue_growth = safe_float(
            info.get("REVENUE GROWTH")
        )

        earnings_growth = safe_float(
            info.get("EARNINGS GROWTH")
        )

        eps_growth = safe_float(
            info.get("EPS GROWTH")
        )

        positive_quarters = safe_float(
            financials.get("POSITIVE QUARTERS")
        )

        rg_score = normalize_linear(
            revenue_growth,
            -0.20,
            0.40
        )

        eg_score = normalize_linear(
            earnings_growth,
            -0.20,
            0.40
        )

        eps_score = normalize_linear(
            eps_growth,
            -0.20,
            0.40
        )

        consistency_score = normalize_linear(
            positive_quarters,
            0,
            8
        )

        raw_score = (
            rg_score * 0.30 +
            eg_score * 0.30 +
            eps_score * 0.20 +
            consistency_score * 0.20
        )

        return {
            "score": round(raw_score, 2),

            "details": {
                "revenue_growth_score": round(rg_score, 2),
                "earnings_growth_score": round(eg_score, 2),
                "eps_growth_score": round(eps_score, 2),
                "consistency_score": round(consistency_score, 2)
            }
        }