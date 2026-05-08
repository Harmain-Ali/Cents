# metrics_engine.py

from typing import Dict, Any

from src.data.info_metrics import compute_info_metrics
from src.data.technical_metrics import compute_technical_metrics
from src.data.dividend_metrics import compute_dividend_metrics
from src.data.growth_metrics import compute_growth_metrics


def get_final_stock_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich raw stock data with computed fundamental, technical, dividend, and growth metrics.

    This function sequentially applies metric computation modules to the input data dictionary,
    adding derived fields under the keys "info", "history", "dividends", and "financials"
    according to the standard schema.

    Args:
        data (Dict[str, Any]): Initial stock data dictionary, typically containing at least
            the "symbol" and raw price/history information.

    Returns:
        Dict[str, Any]: The enriched data dictionary with additional metrics added/updated.
            The structure follows the schema:
            - info: fundamental and valuation metrics
            - history: technical indicators (MA, RSI, MACD, etc.)
            - dividends: dividend history, years, cuts, CAGR
            - financials: quarterly financial data and derived growth metrics

    Example:
        >>> raw_data = {"symbol": "AAPL", "history": {...}}
        >>> enriched = get_final_stock_data(raw_data)
        >>> enriched["info"]["pe_ratio"]
        28.5
    """
    data = compute_info_metrics(data)
    data = compute_technical_metrics(data)
    data = compute_dividend_metrics(data)
    data = compute_growth_metrics(data)
    return data