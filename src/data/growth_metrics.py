# growth_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_growth_metrics(data: Dict[str, Any], num_quarters: int = 8) -> Dict[str, Any]:
    """
    Adds positive_quarters inside FINANCIALS
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
    for name in names:
        if name in df.index:
            return df.loc[name]
    return None


def _yoy_growth(series: pd.Series, n: int):
    series = series.head(n + 4)
    growth = []

    for i in range(4, len(series)):
        curr = series.iloc[i]
        prev = series.iloc[i - 4]

        if pd.notna(curr) and pd.notna(prev) and prev != 0:
            growth.append(((curr - prev) / abs(prev)) * 100)

    return growth[:n]