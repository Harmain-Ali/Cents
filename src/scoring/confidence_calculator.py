"""
Confidence Calculation Module

Produces a score (0–100) indicating how reliable the final stock score is.
High confidence = complete data, stable fundamentals, scorer agreement, deep history.
"""

import numpy as np
from src.scoring.utils.safe_math import safe_float


class ConfidenceCalculator:
    """
    Calculate confidence based on data completeness, stability,
    scorer agreement, and history depth. No analyst coverage.
    """

    # Expected info fields (critical for core scoring)
    CORE_INFO_FIELDS = [
        "pe_ratio", "price_to_book", "price_to_sales", "ev_to_ebitda", "peg_ratio",
        "roe", "roa", "profit_margin", "operating_margin", "gross_margin",
        "revenue_growth", "earnings_growth", "eps_growth",
        "debt_to_equity", "current_ratio", "quick_ratio",
        "free_cash_flow", "market_cap", "beta"
    ]

    @classmethod
    def calculate(cls, data, category_scores):
        """
        Compute confidence score and details.

        Args:
            data (dict): Full stock data (info, history, financials, dividends)
            category_scores (dict): Output from StockScorer (each contains "score")

        Returns:
            dict: {"score": float (0–100), "level": str, "details": {...}}
        """
        info = data.get("info", {})
        history = data.get("history", {})
        dividends = data.get("dividends", {})
        financials = data.get("financials", {})

        # 1. Data completeness (45%)
        completeness = cls._data_completeness(info, history, dividends, financials)

        # 2. Historical stability (25%)
        stability = cls._stability(info, financials)

        # 3. Scorer agreement (15%)
        agreement = cls._scorer_agreement(category_scores)

        # 4. History depth (15%)
        depth = cls._history_depth(history)

        # Weighted sum (total 100%)
        total = (
            completeness * 0.45 +
            stability * 0.25 +
            agreement * 0.15 +
            depth * 0.15
        )

        # Qualitative level based on score
        level = cls._get_confidence_level(total)

        return {
            "score": round(total, 2),
            "level": level,
            "details": {
                "data_completeness": round(completeness, 2),
                "stability": round(stability, 2),
                "scorer_agreement": round(agreement, 2),
                "history_depth": round(depth, 2),
            },
        }

    @classmethod
    def _get_confidence_level(cls, score):
        """Convert numeric confidence score to qualitative label."""
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Moderate"
        elif score >= 40:
            return "Low"
        else:
            return "Very Low"

    # ------------------------------------------------------------
    # Factor calculations (each returns 0–100)
    # ------------------------------------------------------------

    @classmethod
    def _data_completeness(cls, info, history, dividends, financials):
        """Percentage of expected fields present."""
        present = 0
        for field in cls.CORE_INFO_FIELDS:
            if info.get(field) is not None:
                present += 1
        info_score = (present / len(cls.CORE_INFO_FIELDS)) * 100

        # Bonus: history has data? (10% bonus)
        hist_data = history.get("data")
        history_bonus = 10 if hist_data is not None and not hist_data.empty else 0

        # Bonus: dividends have at least 5 years? (10% bonus)
        dividend_years = dividends.get("dividend_years", 0)
        dividend_bonus = 10 if dividend_years >= 5 else 0

        # Bonus: financials have positive_quarters? (5% bonus)
        pos_q = safe_float(financials.get("positive_quarters"))
        fin_bonus = 5 if pos_q is not None else 0

        total = min(100, info_score + history_bonus + dividend_bonus + fin_bonus)
        return total

    @classmethod
    def _stability(cls, info, financials):
        """Lower volatility = higher stability. Uses beta and EPS consistency."""
        beta = safe_float(info.get("beta"))
        if beta is None:
            beta_score = 50
        elif beta <= 0.8:
            beta_score = 100
        elif beta >= 2.0:
            beta_score = 0
        else:
            # linear: 0.8->100, 2.0->0
            beta_score = (2.0 - beta) / 1.2 * 100

        eps_consistency = cls._eps_consistency(financials)
        return (beta_score * 0.6 + eps_consistency * 0.4)

    @classmethod
    def _eps_consistency(cls, financials):
        """Lower coefficient of variation (CV) of quarterly EPS = higher score."""
        df = financials.get("data")
        if df is None or df.empty:
            return 50
        eps_row = None
        for name in ["diluted_eps", "eps", "net_income_per_share"]:
            if name in df.index:
                eps_row = df.loc[name]
                break
        if eps_row is None:
            return 50
        eps_vals = eps_row.dropna().values
        if len(eps_vals) < 4:
            return 50
        mean = np.mean(eps_vals)
        std = np.std(eps_vals)
        if mean == 0:
            cv = 1.0
        else:
            cv = abs(std / mean)
        # cv 0 -> 100, cv >= 1 -> 0
        return max(0, min(100, (1 - cv) * 100))

    @classmethod
    def _scorer_agreement(cls, category_scores):
        """Low variance among the six category scores = high agreement."""
        scores = [cat["score"] for cat in category_scores.values()]
        if not scores:
            return 50
        variance = np.var(scores)
        # Max variance when half at 0, half at 100 -> variance ~2500
        # Map: variance 0 -> 100, variance 2500 -> 0
        max_var = 2500
        agreement = max(0, min(100, (1 - variance / max_var) * 100))
        return agreement

    @classmethod
    def _history_depth(cls, history):
        """Enough data for technical indicators."""
        df = history.get("data")
        if df is None or df.empty:
            return 0
        n_days = len(df)
        # Need at least 200 days for MA200
        if n_days >= 200:
            return 100
        elif n_days >= 50:
            return 50
        else:
            return 20