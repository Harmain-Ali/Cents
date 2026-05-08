from src.scoring.scorers.base_scorer import BaseScorer

from src.scoring.utils.safe_math import safe_float

from src.scoring.utils.normalization import (
    normalize_linear
)


class ProfitabilityScorer(BaseScorer):

    def calculate(self):

        info = self.data["INFO"]

        roe = safe_float(info.get("ROE"))
        roa = safe_float(info.get("ROA"))

        profit_margin = safe_float(
            info.get("PROFIT MARGIN")
        )

        operating_margin = safe_float(
            info.get("OPERATING MARGIN")
        )

        gross_margin = safe_float(
            info.get("GROSS MARGIN")
        )

        roe_score = normalize_linear(roe, 0, 30)
        roa_score = normalize_linear(roa, 0, 20)

        pm_score = normalize_linear(
            profit_margin,
            0,
            0.30
        )

        om_score = normalize_linear(
            operating_margin,
            0,
            0.30
        )

        gm_score = normalize_linear(
            gross_margin,
            0,
            0.60
        )

        raw_score = (
            roe_score * 0.30 +
            roa_score * 0.20 +
            pm_score * 0.25 +
            om_score * 0.15 +
            gm_score * 0.10
        )

        return {
            "score": round(raw_score, 2),

            "details": {
                "roe_score": round(roe_score, 2),
                "roa_score": round(roa_score, 2),
                "profit_margin_score": round(pm_score, 2),
                "operating_margin_score": round(om_score, 2),
                "gross_margin_score": round(gm_score, 2)
            }
        }