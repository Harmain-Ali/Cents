# dividend_metrics.py

import pandas as pd
from typing import Dict, Any


def compute_dividend_metrics(
    data: Dict[str, Any],
    years: int = 5
) -> Dict[str, Any]:
    """
    Compute dividend-related metrics.

    Metrics:
    --------
    1. dividend_years
        Number of years with dividend payments.

    2. has_cuts
        True if annual dividend decreased in any year.

    3. dividend_cagr
        Compound Annual Growth Rate of annual dividends.

    Parameters
    ----------
    data : Dict[str, Any]
        Stock data dictionary.

    years : int, default=5
        Number of recent completed years to analyze.

    Returns
    -------
    Dict[str, Any]
        Updated stock data dictionary.
    """

    dividends = data.get("dividends", {})
    series = dividends.get("data")

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if series is None or not isinstance(series, pd.Series) or series.empty:

        dividends.update({
            "dividend_years": 0,
            "has_cuts": None,
            "dividend_cagr": None
        })

        return data

    # ---------------------------------------------------------
    # CLEAN SERIES
    # ---------------------------------------------------------

    series = series.dropna()

    if series.empty:

        dividends.update({
            "dividend_years": 0,
            "has_cuts": None,
            "dividend_cagr": None
        })

        return data

    # ---------------------------------------------------------
    # ENSURE DATETIME INDEX
    # ---------------------------------------------------------

    series.index = pd.to_datetime(series.index)

    # ---------------------------------------------------------
    # SORT CHRONOLOGICALLY
    # ---------------------------------------------------------

    series = series.sort_index()

    # ---------------------------------------------------------
    # CONVERT QUARTERLY DIVIDENDS -> YEARLY TOTALS
    # ---------------------------------------------------------

    yearly = series.groupby(series.index.year).sum()

    # ---------------------------------------------------------
    # REMOVE CURRENT INCOMPLETE YEAR
    # Prevents fake negative CAGR
    # ---------------------------------------------------------

    current_year = pd.Timestamp.now().year

    yearly = yearly[yearly.index < current_year]

    # ---------------------------------------------------------
    # KEEP ONLY POSITIVE DIVIDEND YEARS
    # ---------------------------------------------------------

    yearly = yearly[yearly > 0]

    # ---------------------------------------------------------
    # KEEP RECENT YEARS
    # ---------------------------------------------------------

    yearly = yearly.tail(years)

    # ---------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------

    n = len(yearly)

    if n == 0:

        result = {
            "dividend_years": 0,
            "has_cuts": None,
            "dividend_cagr": None
        }

    elif n == 1:

        result = {
            "dividend_years": 1,
            "has_cuts": None,
            "dividend_cagr": None
        }

    else:

        result = {
            "dividend_years": n,
            "has_cuts": _has_cuts(yearly),
            "dividend_cagr": _calculate_cagr(yearly)
        }

    dividends.update(result)

    return data


# =========================================================
# HELPERS
# =========================================================

def _has_cuts(series: pd.Series) -> bool:
    """
    Detect dividend cuts in annual dividend totals.

    Parameters
    ----------
    series : pd.Series
        Annual dividend totals sorted chronologically.

    Returns
    -------
    bool
        True if any year has lower dividends than previous year.
    """

    values = series.values

    for i in range(1, len(values)):

        if values[i] < values[i - 1]:
            return True

    return False


def _calculate_cagr(series: pd.Series) -> float | None:
    """
    Calculate dividend CAGR.

    Formula:
    CAGR = ((Ending / Beginning) ** (1 / Years)) - 1

    Parameters
    ----------
    series : pd.Series
        Annual dividend totals sorted chronologically.

    Returns
    -------
    float | None
        CAGR percentage rounded to 2 decimals.
    """

    values = series.values

    start = values[0]
    end = values[-1]

    years = len(values) - 1

    # ---------------------------------------------------------
    # SAFETY CHECKS
    # ---------------------------------------------------------

    if start <= 0 or end <= 0 or years <= 0:
        return None

    try:

        cagr = ((end / start) ** (1 / years) - 1) * 100

        return round(float(cagr), 2)

    except (ZeroDivisionError, ValueError, OverflowError):

        return None