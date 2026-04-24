"""
Data Fetching Module

Provides a simple interface for fetching stock data using yfinance.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
import warnings


class StockDataFetcher:
    """
    Simple stock data fetcher for Yahoo Finance.
    
    Provides methods to validate tickers, fetch historical data,
    get company info, extract ML features, and access financial statements.
    """

    def validate_ticker(self, ticker: str) -> bool:
        """
        Check if a ticker symbol is valid.

        Args:
            ticker: Stock symbol (e.g., 'AAPL')

        Returns:
            True if valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period="1d")
            return not hist.empty
        except Exception:
            return False

    def fetch_historical(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
        ) -> Dict[str, Any]:
        """
        Fetch historical price data.

        Args:
            ticker: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)

        Returns:
            Dictionary with 'data' (DataFrame) and 'error' keys
        """
        try:
            stock = yf.Ticker(ticker.upper())
            df = stock.history(period=period, interval=interval)

            if df.empty:
                return {"data": None, "error": "No historical data found"}

            # Clean column names
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]

            # Remove timezone from index
            if hasattr(df.index, "tz") and df.index.tz is not None:
                df.index = df.index.tz_localize(None)

            return {"data": df, "error": None}

        except Exception as e:
            warnings.warn(f"Error fetching historical data: {e}")
            return {"data": None, "error": str(e)}

    def fetch_info(self, ticker: str) -> Dict[str, Any]:
        """
        Extract ML-ready numeric features for stock analysis.

        Returns only the most important numeric metrics suitable for
        machine learning models and quantitative scoring.

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with 'data' (features dict) and 'error' keys
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info

            if not info:
                return {"data": None, "error": f"No data found for {ticker}"}

            def _get_num(key):
                """Helper to safely get numeric values."""
                val = info.get(key)
                return float(val) if isinstance(val, (int, float)) else None

            features = {
                "symbol": ticker.upper(),
                
                # Valuation
                "pe_ratio": _get_num("trailingPE"),
                "forward_pe": _get_num("forwardPE"),
                "peg_ratio": _get_num("pegRatio"),
                "price_to_book": _get_num("priceToBook"),
                "ev_to_ebitda": _get_num("enterpriseToEbitda"),
                "price_to_sales": _get_num("priceToSalesTrailing12Months"),
                
                # Profitability
                "profit_margin": _get_num("profitMargins"),
                "operating_margin": _get_num("operatingMargins"),
                "roe": _get_num("returnOnEquity"),
                "roa": _get_num("returnOnAssets"),
                
                # Growth
                "revenue_growth": _get_num("revenueGrowth"),
                "earnings_growth": _get_num("earningsGrowth"),
                "quarterly_earnings_growth": _get_num("earningsQuarterlyGrowth"),
                
                # Financial Health
                "debt_to_equity": _get_num("debtToEquity"),
                "current_ratio": _get_num("currentRatio"),
                "quick_ratio": _get_num("quickRatio"),
                
                # Cash Flow
                "free_cashflow": _get_num("freeCashflow"),
                "operating_cashflow": _get_num("operatingCashflow"),
                
                # Market
                "beta": _get_num("beta"),
                "market_cap": _get_num("marketCap"),
                "volume": _get_num("volume"),
                "avg_volume": _get_num("averageVolume"),
                
                # Dividends
                "dividend_yield": _get_num("dividendYield"),
                "payout_ratio": _get_num("payoutRatio"),
            }
            
            return {"data": features, "error": None}

        except Exception as e:
            return {"data": None, "error": str(e)}

    def fetch_financials(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch financial statements.

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with income statement, balance sheet, and cash flow
        """
        try:
            stock = yf.Ticker(ticker.upper())

            financials = {
                'income_stmt': None,
                'balance_sheet': None,
                'cash_flow': None,
                'quarterly_income': None,
                'quarterly_balance': None,
                'quarterly_cash_flow': None,
                'error': None
            }

            # Fetch each statement individually (silently fail if not available)
            try:
                financials['income_stmt'] = stock.income_stmt
            except Exception:
                pass

            try:
                financials['balance_sheet'] = stock.balance_sheet
            except Exception:
                pass

            try:
                financials['cash_flow'] = stock.cashflow
            except Exception:
                pass

            try:
                financials['quarterly_income'] = stock.quarterly_income_stmt
            except Exception:
                pass

            try:
                financials['quarterly_balance'] = stock.quarterly_balance_sheet
            except Exception:
                pass

            try:
                financials['quarterly_cash_flow'] = stock.quarterly_cashflow
            except Exception:
                pass

            return financials

        except Exception as e:
            warnings.warn(f"Error fetching financials: {e}")
            return {'error': str(e)}

    def get_full_stock_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get complete stock data (info, historical prices, financials).

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with all stock data
        """
        ticker = ticker.upper()
        
        return {
            'ticker': ticker,
            'info': self.fetch_info(ticker),
            'history_1y': self.fetch_historical(ticker, period="1y"),
            'history_5y': self.fetch_historical(ticker, period="5y"),
            'financials': self.fetch_financials(ticker)
        }

    def get_batch_features(self, tickers: list) -> Dict[str, Any]:
        """
        Get features for multiple tickers at once.

        Args:
            tickers: List of stock symbols

        Returns:
            Dictionary with ticker as key and features as value
        """
        results = {}
        for ticker in tickers:
            results[ticker] = self.get_features(ticker)
        return results


# ============================================================================
# Simple helper functions for quick access
# ============================================================================

def quick_info(ticker: str) -> Optional[Dict]:
    """Quickly get company info for a ticker."""
    fetcher = StockDataFetcher()
    result = fetcher.fetch_info(ticker)
    return result if result.get('error') is None else None

