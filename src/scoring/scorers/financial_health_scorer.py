from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear, normalize_inverse


class FinancialHealthScorer(BaseScorer):
    """
    Calculate a financial health score based on leverage, liquidity, and free cash flow yield.

    The score is a weighted combination:
        - 30% debt-to-equity (inverse normalisation, 0–3 range, lower is better)
        - 30% current ratio (linear normalisation, 0.5–4 range)
        - 20% quick ratio (linear normalisation, 0.2–3 range)
        - 20% free cash flow yield (linear normalisation, -5% to +15% FCF / market cap)

    Returns:
        dict: Contains 'score' (0–100) and 'details' with individual component scores.
    """

    def calculate(self):
        # Access data using schema keys (lowercase)
        info = self.data["info"]

        # --- Extract values with safe conversion ---
        debt_to_equity = safe_float(info.get("debt_to_equity"))
        current_ratio = safe_float(info.get("current_ratio"))
        quick_ratio = safe_float(info.get("quick_ratio"))
        free_cash_flow = safe_float(info.get("free_cash_flow"))  # note underscore
        market_cap = safe_float(info.get("market_cap"))

        # --- 1. Debt-to-equity score (lower is better) ---
        de_score = normalize_inverse(debt_to_equity, 0, 3)  # 0 → 100, 3 → 0

        # --- 2. Current ratio score (higher is better up to 4) ---
        cr_score = normalize_linear(current_ratio, 0.5, 4)  # 0.5 → 0, 4 → 100

        # --- 3. Quick ratio score (higher is better up to 3) ---
        qr_score = normalize_linear(quick_ratio, 0.2, 3)    # 0.2 → 0, 3 → 100

        # --- 4. Free cash flow yield score ---
        if free_cash_flow is not None and market_cap is not None and market_cap != 0:
            fcf_yield = free_cash_flow / market_cap
        else:
            fcf_yield = None

        fcf_score = normalize_linear(fcf_yield, -0.05, 0.15)  # -5% → 0, +15% → 100

        # --- Weighted final score ---
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
                "fcf_score": round(fcf_score, 2),
            },
        }