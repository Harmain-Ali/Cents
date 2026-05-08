from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear, normalize_inverse


class DividendScorer(BaseScorer):
    """
    Calculate a dividend attractiveness score based on yield, payout ratio, and dividend growth.

    The score is a weighted combination:
        - 30% dividend yield (linear normalisation from 0% to 10% yield)
        - 30% payout ratio (inverse normalisation, lower is better, range 0 to 150%)
        - 40% dividend CAGR (linear normalisation from -10% to +20% growth)

    If the dividend history has any cuts, the growth score is penalised by 50%.

    Returns:
        dict: Contains 'score' (0–100) and 'details' with individual component scores.
    """

    def calculate(self):
        # Access data using schema keys (lowercase)
        info = self.data["info"]
        dividends = self.data["dividends"]

        # --- Extract values with safe conversion ---
        dividend_yield = safe_float(info.get("dividend_yield"))
        payout_ratio = safe_float(info.get("payout_ratio"))
        dividend_cagr = safe_float(dividends.get("dividend_cagr"))
        has_cuts = dividends.get("has_cuts")  # boolean

        # --- 1. Dividend yield score (higher is better, typical range 0–10%) ---
        dy_score = normalize_linear(dividend_yield, 0, 0.10)  # 0% → 0, 10% → 100

        # --- 2. Payout ratio score (lower is better, 0–150% range) ---
        pr_score = normalize_inverse(payout_ratio, 0, 1.5)   # 0% → 100, 150% → 0

        # --- 3. Dividend growth score (CAGR, range -10% to +20%) ---
        dg_score = normalize_linear(dividend_cagr, -0.10, 0.20)  # -10% → 0, +20% → 100

        # Penalise if there were any dividend cuts
        if has_cuts:
            dg_score *= 0.5

        # --- Weighted final score ---
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
                "dividend_growth_score": round(dg_score, 2),
            },
        }