import yfinance as yf
import pandas as pd


def get_growth_consistency_score(ticker: str, num_quarters: int = 8) -> dict:
    """
    Returns:
    - positive_quarters
    - consistency_score
    """

    try:
        stock = yf.Ticker(ticker.upper())
        df = stock.quarterly_income_stmt

        if df is None or df.empty:
            return {"error": "No quarterly data available"}

        # Get revenue & net income
        revenue = _get_row(df, ["Total Revenue", "Revenue"])
        earnings = _get_row(df, ["Net Income", "Net Profit"])

        if revenue is None or earnings is None:
            return {"error": "Required financial data not found"}

        # Sort oldest → newest
        revenue = revenue.sort_index()
        earnings = earnings.sort_index()

        # Calculate YoY growth
        rev_growth = _calculate_yoy_growth(revenue, num_quarters)
        earn_growth = _calculate_yoy_growth(earnings, num_quarters)

        # Count positives
        rev_pos = sum(g > 0 for g in rev_growth)
        earn_pos = sum(g > 0 for g in earn_growth)

        avg_positive = round((rev_pos + earn_pos) / 2)

        # Score
        score = _calculate_score(avg_positive, num_quarters)

        return {
            "positive_quarters": avg_positive,
            "consistency_score": score
        }

    except Exception as e:
        return {"error": str(e)}


# ------------------ HELPERS ------------------

def _get_row(df, possible_names):
    for name in possible_names:
        if name in df.index:
            return df.loc[name]
    return None


def _calculate_yoy_growth(series, num_quarters):
    series = series.head(num_quarters + 4)  # need extra for YoY
    growth = []

    for i in range(4, len(series)):
        curr = series.iloc[i]
        prev = series.iloc[i - 4]

        if pd.notna(curr) and pd.notna(prev) and prev != 0:
            growth.append(((curr - prev) / abs(prev)) * 100)

    return growth[:num_quarters]


def _calculate_score(positive, total):
    if total == 0:
        return 0

    pct = (positive / total) * 100

    if pct >= 87.5:
        return 20
    elif pct >= 62.5:
        return 15
    elif pct >= 37.5:
        return 10
    else:
        return 5