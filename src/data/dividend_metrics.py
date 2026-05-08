# dividend_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_dividend_metrics(data: Dict[str, Any], years: int = 5) -> Dict[str, Any]:
    """
    Compute dividend metrics including years of payments, cuts, and CAGR.

    The function extracts a pandas Series of dividend payments from `data["dividends"]["data"]`,
    resamples it to annual sums, and calculates the number of dividend‑paying years,
    whether any cuts occurred, and the compound annual growth rate (CAGR) over the
    last `years` (or fewer if insufficient data).

    If no dividend data exists or the series is empty, default values are inserted.

    Args:
        data (Dict[str, Any]): Stock data dictionary. Must contain a "dividends" key
            with a "data" field that is a pandas Series (datetime index, dividend amounts).
        years (int, optional): Number of trailing years to consider. Defaults to 5.

    Returns:
        Dict[str, Any]: The same data dictionary with the following keys added/updated
        under "dividends":
            - dividend_years (int): Number of years with positive dividends.
            - has_cuts (bool or None): True if any cut occurred in the period,
              False if no cuts, None if insufficient data.
            - dividend_cagr (float or None): CAGR percentage (annualised growth rate)
              rounded to 2 decimal places, or 0 if not calculable.
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
    """
    Detect if a dividend series contains any year‑over‑year cuts.

    Args:
        series (pd.Series): Annual dividend amounts indexed by year.

    Returns:
        bool: True if any year's dividend is strictly less than the previous year,
              otherwise False.
    """
    values = series.values
    return any(values[i] < values[i - 1] for i in range(1, len(values)))


def _calculate_cagr(series: pd.Series) -> float:
    """
    Calculate the compound annual growth rate (CAGR) of a dividend series.

    CAGR = (end_value / start_value) ^ (1 / (n-1)) - 1, expressed as a percentage.
    Assumes `series` contains at least 2 positive values and is sorted chronologically.

    Args:
        series (pd.Series): Annual dividend amounts indexed by year,
                            with at least 2 elements.

    Returns:
        float: CAGR as a percentage (e.g., 8.5 for 8.5%).
               Returns 0 if the starting value is zero or the length is insufficient.
    """
    values = series.values
    start, end = values[0], values[-1]
    n = len(values) - 1

    if start == 0 or n <= 0:
        return 0

    return ((end / start) ** (1 / n) - 1) * 100