# growth_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_growth_metrics(data: Dict[str, Any], num_quarters: int = 8) -> Dict[str, Any]:
    """
    Compute the number of quarters with positive year-over-year growth for revenue and earnings.

    The function extracts quarterly financial data from `data["financials"]["data"]`, identifies
    revenue and earnings rows, calculates YoY growth for up to `num_quarters` recent quarters,
    and stores the average number of positive growth quarters under `financials["positive_quarters"]`.

    Args:
        data (Dict[str, Any]): Stock data dictionary. Must contain a "financials" key
            with a "data" field that is a pandas DataFrame (index: metric names, columns: quarters).
        num_quarters (int, optional): Number of trailing quarters to evaluate. Defaults to 8.

    Returns:
        Dict[str, Any]: The same data dictionary with `financials["positive_quarters"]` updated:
            - int: Average of positive YoY growth counts for revenue and earnings (rounded).
            - None: If required data is missing.
    """
    financials = data.get("financials", {})
    df = financials.get("data")

    if df is None or df.empty:
        financials["positive_quarters"] = None
        return data

    revenue = _get_row(df, ["total_revenue", "revenue"])
    earnings = _get_row(df, ["net_income", "net_profit"])

    if revenue is None or earnings is None:
        financials["positive_quarters"] = None
        return data

    revenue = revenue.sort_index()
    earnings = earnings.sort_index()

    rev_growth = _yoy_growth(revenue, num_quarters)
    earn_growth = _yoy_growth(earnings, num_quarters)

    rev_pos = sum(g > 0 for g in rev_growth)
    earn_pos = sum(g > 0 for g in earn_growth)

    financials["positive_quarters"] = round((rev_pos + earn_pos) / 2)

    return data


# -------- HELPERS --------

def _get_row(df: pd.DataFrame, names: list):
    """
    Retrieve a row from a DataFrame by trying multiple possible index names.

    Args:
        df (pd.DataFrame): DataFrame with metrics as index.
        names (list): List of string index names to try, in order of preference.

    Returns:
        pandas.Series or None: The row (Series) corresponding to the first matching name,
        or None if none of the names are found in the index.
    """
    for name in names:
        if name in df.index:
            return df.loc[name]
    return None


def _yoy_growth(series: pd.Series, n: int):
    """
    Calculate year-over-year growth percentages for a quarterly time series.

    For each quarter beyond the first four, computes (current - previous_year) / previous_year * 100.
    Returns up to `n` most recent growth values (the last `n` valid quarters).

    Args:
        series (pd.Series): Quarterly time series indexed by date (sorted ascending).
        n (int): Number of growth values to return (from the most recent end).

    Returns:
        list: List of growth percentages (float) for up to `n` quarters.
              Empty list if fewer than 5 data points or insufficient previous values.
    """
    series = series.head(n + 4)
    growth = []

    for i in range(4, len(series)):
        curr = series.iloc[i]
        prev = series.iloc[i - 4]

        if pd.notna(curr) and pd.notna(prev) and prev != 0:
            growth.append(((curr - prev) / abs(prev)) * 100)

    return growth[:n]