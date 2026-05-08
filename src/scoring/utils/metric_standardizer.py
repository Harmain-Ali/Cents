from copy import deepcopy
from typing import Dict, Any

from src.scoring.utils.safe_math import safe_float


class MetricStandardizer:
    """
    Standardizes raw Yahoo Finance metrics into internally consistent formats.
    ...

    STANDARD INTERNAL FORMATS:
    --------------------------
    Percent‑based metrics (except dividend yield):
        Stored as real percentages (e.g., profit_margin = 25 means 25%)
    Ratios:
        Stored as raw ratios (e.g., debt_to_equity = 0.8)
    Dividend yield:
        Stored as **decimal** (e.g., 0.0038 for 0.38%) – because DividendScorer expects 0–0.10 range.
    """

    # ------------------------------------------------------------
    # Metrics that come as decimals (e.g., 0.25) and should become percentages (25)
    # ------------------------------------------------------------
    DECIMAL_TO_PERCENT_METRICS = [
        # profitability
        "profit_margin",
        "operating_margin",
        "gross_margin",
        "roe",
        "roa",
        # growth
        "revenue_growth",
        "earnings_growth",
        "quarterly_earnings_growth",
        "eps_growth",
        # payout ratio (stays as percentage)
        "payout_ratio"
    ]

    DEBT_TO_EQUITY_METRIC = "debt_to_equity"

    @classmethod
    def standardize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        standardized = deepcopy(data)
        info = standardized.get("info", {})

        # ----------------------------------------------------
        # 1. Decimal -> Percent conversion (except dividend_yield)
        # ----------------------------------------------------
        for metric in cls.DECIMAL_TO_PERCENT_METRICS:
            value = safe_float(info.get(metric))
            if value is None:
                continue
            info[metric] = value * 100

        # ----------------------------------------------------
        # 2. Debt-to-equity: from Yahoo's scaled number (e.g., 79 → 0.79)
        # ----------------------------------------------------
        debt_to_equity = safe_float(info.get(cls.DEBT_TO_EQUITY_METRIC))
        if debt_to_equity is not None:
            info[cls.DEBT_TO_EQUITY_METRIC] = debt_to_equity / 100

        # ----------------------------------------------------
        # 3. Dividend yield: FROM percentage TO decimal
        #    (Yahoo gives 0.38 for 0.38% → convert to 0.0038)
        # ----------------------------------------------------
        dividend_yield = safe_float(info.get("dividend_yield"))
        if dividend_yield is not None:
            # Convert from percent to decimal (e.g., 0.38 → 0.0038)
            info["dividend_yield"] = dividend_yield / 100

        # ----------------------------------------------------
        # 4. Payout ratio safety (unchanged)
        # ----------------------------------------------------
        payout_ratio = safe_float(info.get("payout_ratio"))
        if payout_ratio is not None:
            if payout_ratio > 1000:
                info["payout_ratio"] = None

        return standardized