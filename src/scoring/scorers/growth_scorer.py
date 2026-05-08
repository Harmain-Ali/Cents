from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear


class GrowthScorer(BaseScorer):
    """
    Calculate a growth score based on revenue, earnings, EPS growth, and consistency.

    The score is a weighted combination:
        - 30% revenue growth (linear normalisation from -20% to +40% CAGR)
        - 30% earnings growth (linear normalisation from -20% to +40%)
        - 20% EPS growth (linear normalisation from -20% to +40%)
        - 20% consistency (number of positive quarters in recent history, 0–8)

    Returns:
        dict: Contains 'score' (0–100) and 'details' with individual component scores.
    """

    def calculate(self):
        # Access data using schema keys (lowercase)
        info = self.data["info"]
        financials = self.data["financials"]

        # --- Extract values with safe conversion ---
        revenue_growth = safe_float(info.get("revenue_growth"))
        earnings_growth = safe_float(info.get("earnings_growth"))
        eps_growth = safe_float(info.get("eps_growth"))
        positive_quarters = safe_float(financials.get("positive_quarters"))

        # --- 1. Revenue growth score ---
        rg_score = normalize_linear(revenue_growth, -20, 40)

        # --- 2. Earnings growth score ---
        eg_score = normalize_linear(earnings_growth, -20, 40)

        # --- 3. EPS growth score ---
        eps_score = normalize_linear(eps_growth, -20, 40)

        # --- 4. Consistency score (number of quarters with positive growth, 0 to 8) ---
        consistency_score = normalize_linear(positive_quarters, 0, 8)

        # --- Weighted final score ---
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
                "consistency_score": round(consistency_score, 2),
            },
        }