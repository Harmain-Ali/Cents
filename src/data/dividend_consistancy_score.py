import yfinance as yf
import pandas as pd
import numpy as np


def get_dividend_score(ticker: str, years: int = 5) -> dict:
    """
    Returns:
    - dividend_score
    - dividend_cagr
    - has_cuts
    - years_of_data
    """

    try:
        stock = yf.Ticker(ticker.upper())
        dividends = stock.dividends

        if dividends is None or dividends.empty:
            return {"dividend_score": 0, "error": "No dividend data"}

        # Convert to yearly dividends
        yearly_div = dividends.resample('YE').sum()

        # Keep last N years
        yearly_div = yearly_div.tail(years)

        # Remove years with 0 dividend
        yearly_div = yearly_div[yearly_div > 0]

        num_years = len(yearly_div)

        # -------- CASE 1: No dividends --------
        if num_years == 0:
            return {
                "dividend_score": 0,
                "years_of_data": 0,
                "dividend_cagr": 0,
                "has_cuts": True
            }

        # -------- CASE 2: Short history --------
        if num_years < 3:
            return {
                "dividend_score": 15,
                "years_of_data": num_years,
                "dividend_cagr": 0,
                "has_cuts": False
            }

        # -------- CHECK CUTS --------
        has_cuts = _check_dividend_cuts(yearly_div)

        # -------- CAGR --------
        cagr = _calculate_cagr(yearly_div)

        # -------- SCORING --------
        if has_cuts:
            score = 10
        elif cagr < 0:
            score = 15
        elif 0 <= cagr < 3:
            score = 25
        elif 3 <= cagr < 8:
            score = 35
        else:
            score = 40

        return {
            "dividend_score": score,
            "years_of_data": num_years,
            "dividend_cagr": round(cagr, 2),
            "has_cuts": has_cuts
        }

    except Exception as e:
        return {"error": str(e)}


# ------------------ HELPERS ------------------

def _check_dividend_cuts(series: pd.Series) -> bool:
    """
    Returns True if any year has lower dividend than previous year
    """
    values = series.values

    for i in range(1, len(values)):
        if values[i] < values[i - 1]:
            return True

    return False


def _calculate_cagr(series: pd.Series) -> float:
    """
    CAGR = (Ending / Beginning)^(1/n) - 1
    """
    values = series.values

    start = values[0]
    end = values[-1]
    n = len(values) - 1

    if start == 0 or n <= 0:
        return 0

    return ((end / start) ** (1 / n) - 1) * 100