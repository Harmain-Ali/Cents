# growth_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_growth_metrics(
    data: Dict[str, Any],
    num_quarters: int = 8
) -> Dict[str, Any]:
    """
    Compute quarterly growth and profitability metrics.

    Metrics
    -------
    1. positive_quarters
        Average number of quarters with positive YoY
        revenue and earnings growth. (Rounded integer)

    2. profitable_quarters
        Number of quarters with positive net income.

    Parameters
    ----------
    data : Dict[str, Any]
        Stock data dictionary.

    num_quarters : int, default=8
        Number of recent quarters to analyze.

    Returns
    -------
    Dict[str, Any]
        Updated stock data dictionary with keys:
        - positive_quarters (int or None)
        - profitable_quarters (int or None)
    """

    financials = data.get("financials", {})
    df = financials.get("data")

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        financials["positive_quarters"] = None
        financials["profitable_quarters"] = None
        return data

    # ---------------------------------------------------------
    # FETCH ROWS (case‑insensitive)
    # ---------------------------------------------------------

    revenue = _get_row(
        df,
        [
            "total_revenue",
            "revenue",
            "totalRevenue"
        ]
    )

    earnings = _get_row(
        df,
        [
            "net_income",
            "net_profit",
            "netIncome"
        ]
    )

    if revenue is None or earnings is None:
        financials["positive_quarters"] = None
        financials["profitable_quarters"] = None
        return data

    # ---------------------------------------------------------
    # CLEAN + SORT
    # ---------------------------------------------------------

    revenue = revenue.dropna().sort_index()
    earnings = earnings.dropna().sort_index()

    # ---------------------------------------------------------
    # KEEP MOST RECENT QUARTERS (+4 for YoY calculation)
    # ---------------------------------------------------------

    revenue = revenue.tail(num_quarters + 4)
    earnings = earnings.tail(num_quarters + 4)

    # ---------------------------------------------------------
    # YOY GROWTH
    # ---------------------------------------------------------

    rev_growth = _yoy_growth(revenue)
    earn_growth = _yoy_growth(earnings)

    # ---------------------------------------------------------
    # POSITIVE GROWTH QUARTERS
    # ---------------------------------------------------------

    rev_positive = sum(g > 0 for g in rev_growth)
    earn_positive = sum(g > 0 for g in earn_growth)

    positive_quarters = round(
        (rev_positive + earn_positive) / 2
    )

    # ---------------------------------------------------------
    # PROFITABLE QUARTERS
    # ---------------------------------------------------------

    recent_earnings = earnings.tail(num_quarters)

    profitable_quarters = int(
        sum(v > 0 for v in recent_earnings)
    )

    # ---------------------------------------------------------
    # SAVE RESULTS
    # ---------------------------------------------------------

    financials["positive_quarters"] = positive_quarters
    financials["profitable_quarters"] = profitable_quarters

    return data


# =========================================================
# HELPERS
# =========================================================

def _get_row(df: pd.DataFrame, names: list):
    """
    Retrieve first matching row from dataframe (case‑insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with metrics as index.
    names : list
        List of possible index names (strings).

    Returns
    -------
    pd.Series or None
        The row (Series) corresponding to the first matching name,
        or None if none found.
    """
    normalized_index = {
        str(idx).lower(): idx
        for idx in df.index
    }

    for name in names:
        key = name.lower()
        if key in normalized_index:
            return df.loc[normalized_index[key]]

    return None


def _yoy_growth(series: pd.Series):
    """
    Calculate quarterly year‑over‑year growth percentages.

    Formula:
    Growth = ((Current - PreviousYearQuarter) / abs(Previous)) * 100

    Returns a list of growth values for each quarter where a complete
    4‑quarter lag exists.
    """
    growth = []
    values = series.values

    for i in range(4, len(values)):
        current = values[i]
        previous = values[i - 4]

        if (
            pd.notna(current)
            and pd.notna(previous)
            and previous != 0
        ):
            g = ((current - previous) / abs(previous)) * 100
            growth.append(float(g))

    return growth