# dividend_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_dividend_metrics(data: Dict[str, Any], years: int = 5) -> Dict[str, Any]:
    """
    Adds dividend years, cuts, CAGR inside DIVIDENDS
    """

    dividends = data.get("dividends", {})
    series = dividends.get("data")

    if series is None or series.empty:
        dividends.update({
            "dividend_years": 0,
            "has_cuts": None,
            "dividend_cagr": None
        })
        return data

    yearly = series.resample("YE").sum()
    yearly = yearly.tail(years)
    yearly = yearly[yearly > 0]

    n = len(yearly)

    if n == 0:
        result = {
            "dividend_years": 0,
            "has_cuts": True,
            "dividend_cagr": 0
        }
    elif n < 3:
        result = {
            "dividend_years": n,
            "has_cuts": False,
            "dividend_cagr": 0
        }
    else:
        result = {
            "dividend_years": n,
            "has_cuts": _has_cuts(yearly),
            "dividend_cagr": round(_calculate_cagr(yearly), 2)
        }

    dividends.update(result)

    return data


# -------- HELPERS --------

def _has_cuts(series: pd.Series) -> bool:
    values = series.values
    return any(values[i] < values[i - 1] for i in range(1, len(values)))


def _calculate_cagr(series: pd.Series) -> float:
    values = series.values
    start, end = values[0], values[-1]
    n = len(values) - 1

    if start == 0 or n <= 0:
        return 0

    return ((end / start) ** (1 / n) - 1) * 100