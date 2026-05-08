from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear


class ProfitabilityScorer(BaseScorer):
    """
    Calculate a profitability score based on return ratios and margins.

    The score is a weighted combination:
        - 30% Return on Equity (ROE) – linear normalisation from 0% to 30%
        - 20% Return on Assets (ROA) – linear normalisation from 0% to 20%
        - 25% Profit margin – linear normalisation from 0% to 30%
        - 15% Operating margin – linear normalisation from 0% to 30%
        - 10% Gross margin – linear normalisation from 0% to 60%

    Returns:
        dict: Contains 'score' (0–100) and 'details' with individual component scores.
    """

    def calculate(self):
        # Access data using schema keys (lowercase)
        info = self.data["info"]

        # --- Extract values with safe conversion ---
        roe = safe_float(info.get("roe"))
        roa = safe_float(info.get("roa"))
        profit_margin = safe_float(info.get("profit_margin"))
        operating_margin = safe_float(info.get("operating_margin"))
        gross_margin = safe_float(info.get("gross_margin"))

        # --- 1. ROE score (0–30% range) ---
        roe_score = normalize_linear(roe, 0, 30)

        # --- 2. ROA score (0–20% range) ---
        roa_score = normalize_linear(roa, 0, 20)

        # --- 3. Profit margin score (0–30% range) ---
        pm_score = normalize_linear(profit_margin, 0, 0.30)

        # --- 4. Operating margin score (0–30% range) ---
        om_score = normalize_linear(operating_margin, 0, 0.30)

        # --- 5. Gross margin score (0–60% range) ---
        gm_score = normalize_linear(gross_margin, 0, 0.60)

        # --- Weighted final score ---
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
                "gross_margin_score": round(gm_score, 2),
            },
        }