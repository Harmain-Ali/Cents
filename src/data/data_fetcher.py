import yfinance as yf
import pandas as pd
from numbers import Real
from typing import Dict, Any, Union
import warnings


class DataFetcher:
    """
    A comprehensive stock data fetcher using Yahoo Finance API.
    
    This class provides methods to fetch historical prices, company information,
    quarterly income statements, dividend data, and combines them into a single
    data structure.
    
    Attributes:
        ticker_symbol (str): The stock ticker symbol (upper case)
        period (str): Time period for historical data (e.g., '1y', '5y', 'max')
        interval (str): Data interval (e.g., '1d', '1wk', '1mo')
        stock (yf.Ticker): The yfinance Ticker object for the specified stock
        is_valid (bool): Whether the ticker is valid (set during initialization)
    """
    
    def __init__(self, ticker: str, period: str = "1y", interval: str = "1d"):
        """
        Initialize the DataFetcher with a stock ticker and data parameters.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
            period (str, optional): Historical data period. Defaults to "1y".
                Valid values: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
            interval (str, optional): Data interval/frequency. Defaults to "1d".
                Valid values: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
        
        Note:
            The ticker is validated during initialization. If invalid, the stock object
            is still created but all fetch methods will return errors.
            Use the is_valid attribute or validate_ticker() method to check validity.
        """
        self.ticker_symbol = ticker.upper()
        self.period = period
        self.interval = interval

        # Create ticker object (reused for all data fetches to minimize API calls)
        self.stock = yf.Ticker(self.ticker_symbol)
        
        # Validate the ticker during initialization
        self.is_valid = self.validate_ticker()
    
    @classmethod
    def validate_ticker_static(cls, ticker: str) -> bool:
        """
        Static method to validate a ticker without creating a class instance.
        
        Args:
            ticker (str): Stock ticker symbol to validate
            
        Returns:
            bool: True if ticker is valid and has data, False otherwise
            
        Examples:
            >>> # Use without creating an instance
            >>> is_valid = DataFetcher.validate_ticker_static("AAPL")
            >>> if is_valid:
            >>>     fetcher = DataFetcher("AAPL")
            
            >>> # Check multiple tickers
            >>> tickers = ["AAPL", "INVALID", "MSFT"]
            >>> valid_tickers = [t for t in tickers if DataFetcher.validate_ticker_static(t)]
            >>> print(f"Valid tickers: {valid_tickers}")
        """
        try:
            stock = yf.Ticker(ticker.upper())
            # Try to fetch a small amount of data to verify the ticker exists
            hist = stock.history(period="1d")
            return not hist.empty
        except Exception:
            return False
    
    def validate_ticker(self) -> bool:
        """
        Validate if the current ticker exists and has data.
        
        This method checks whether the ticker symbol provided during initialization
        corresponds to a valid stock with available data on Yahoo Finance.
        
        Returns:
            bool: True if ticker is valid and has data, False otherwise
            
        Examples:
            >>> fetcher = DataFetcher("AAPL")
            >>> if fetcher.validate_ticker():
            >>>     print("Valid ticker!")
            >>> else:
            >>>     print("Invalid ticker!")
            
            >>> # Check validity without fetching full data
            >>> fetcher = DataFetcher("INVALID_TICKER")
            >>> if not fetcher.is_valid:
            >>>     print("Please provide a valid ticker symbol")
        """
        try:
            # Try to fetch a small amount of data to verify the ticker exists
            hist = self.stock.history(period="1d")
            return not hist.empty
        except Exception:
            return False
    
    def fetch_historical(self) -> Dict[str, Any]:
        """
        Fetch historical price data for the initialized ticker.
        
        Retrieves OHLCV (Open, High, Low, Close, Volume) data for the specified
        period and interval. The data is cleaned by standardizing column names
        and removing timezone information from the index.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'data': pandas DataFrame with historical price data, or None if error
                    Columns include: open, high, low, close, volume, dividends, stock splits
                - 'error': Error message string if an error occurred, otherwise None
        
        Examples:
            >>> fetcher = DataFetcher('AAPL')
            >>> result = fetcher.fetch_historical()
            >>> if result['error'] is None:
            >>>     print(result['data'].head())
        
        Note:
            The returned DataFrame index is datetime with timezone removed (naive).
            Column names are standardized to lowercase with underscores.
        """
        # Check if ticker is valid first
        if not self.is_valid:
            return {"data": None, "error": f"Invalid ticker symbol: {self.ticker_symbol}"}
        
        try:
            df = self.stock.history(period=self.period, interval=self.interval)

            if df.empty:
                return {"data": None, "error": f"No historical data found for {self.ticker_symbol}"}

            # Clean column names (handle non-string columns safely)
            df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]

            # Remove timezone from index if present
            if hasattr(df.index, "tz") and df.index.tz is not None:
                df.index = df.index.tz_localize(None)

            return {"data": df, "error": None}

        except Exception as e:
            warnings.warn(f"Error fetching historical data: {e}")
            return {"data": None, "error": str(e)}

    def fetch_info(self) -> Dict[str, Any]:
        """
        Fetch comprehensive company information and fundamental metrics.
        
        Extracts key financial metrics, valuation ratios, growth indicators,
        and market data from Yahoo Finance. The data is structured for
        machine learning and quantitative analysis.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'data': Dictionary of fundamental metrics (see structure below), or None if error
                - 'error': Error message string if an error occurred, otherwise None
        
        The returned 'data' dictionary includes:
            Basic Info: symbol, long_name, short_name, sector, industry
            Price Info: current_price, previous_close
            Valuation: pe_ratio, forward_pe, peg_ratio, price_to_book, ev_to_ebitda, price_to_sales
            Profitability: profit_margin, operating_margin, gross_margin, roe, roa
            EPS: trailing_eps, forward_eps
            Growth: revenue_growth, earnings_growth, quarterly_earnings_growth
            Financial Health: debt_to_equity, current_ratio, quick_ratio
            Cash Flow: free_cash_flow, operating_cash_flow
            Market: beta, market_cap, volume, avg_volume
            Dividends: dividend_yield, payout_ratio
        
        Examples:
            >>> fetcher = DataFetcher('MSFT')
            >>> result = fetcher.fetch_info()
            >>> if result['error'] is None:
            >>>     print(f"P/E Ratio: {result['data']['pe_ratio']}")
            >>>     print(f"Market Cap: {result['data']['market_cap']}")
        
        Note:
            Numeric fields may be None if the data is not available for the stock.
            String fields may be None if the information is missing.
        """
        # Check if ticker is valid first
        if not self.is_valid:
            return {"data": None, "error": f"Invalid ticker symbol: {self.ticker_symbol}"}
        
        try:
            info = self.stock.info
            
            if not info:
                return {"data": None, "error": f"No info data found for {self.ticker_symbol}"}
            
            def _get_num(key):
                val = info.get(key)

                if val is None or pd.isna(val):
                    return None

                if isinstance(val, Real):
                    return float(val)

                return None

            def _get_str(key):
                val = info.get(key)

                if val is None or pd.isna(val):
                    return None

                return str(val)
            
            features = {
                # Basic Info
                "symbol": _get_str("symbol"),
                "long_name": _get_str("longName"),
                "short_name": _get_str("shortName"),
                "sector": _get_str("sector"),
                "industry": _get_str("industry"),
                
                # Price Info
                "current_price": _get_num("currentPrice"),
                "previous_close": _get_num("previousClose"),
                
                # Valuation
                "pe_ratio": _get_num("trailingPE"),
                "forward_pe": _get_num("forwardPE"),
                "peg_ratio": _get_num("pegRatio"),
                "price_to_book": _get_num("priceToBook"),
                "ev_to_ebitda": _get_num("enterpriseToEbitda"),
                "price_to_sales": _get_num("priceToSalesTrailing12Months"),
                
                # Profitability & EPS
                "profit_margin": _get_num("profitMargins"),
                "operating_margin": _get_num("operatingMargins"),
                "gross_margin": _get_num("grossMargins"),
                "roe": _get_num("returnOnEquity"),
                "roa": _get_num("returnOnAssets"),
                "trailing_eps": _get_num("trailingEps"),
                "forward_eps": _get_num("forwardEps"),
                
                # Growth
                "revenue_growth": _get_num("revenueGrowth"),
                "earnings_growth": _get_num("earningsGrowth"),
                "quarterly_earnings_growth": _get_num("earningsQuarterlyGrowth"),
                
                # Financial Health
                "debt_to_equity": _get_num("debtToEquity"),
                "current_ratio": _get_num("currentRatio"),
                "quick_ratio": _get_num("quickRatio"),
                
                # Cash Flow
                "free_cash_flow": _get_num("freeCashflow"),
                "operating_cash_flow": _get_num("operatingCashflow"),
                
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

    def fetch_quarterly_income(self) -> Dict[str, Any]:
        """
        Fetch quarterly income statement data.
        
        Retrieves the quarterly income statement including revenue, cost of goods sold,
        operating expenses, net income, and other financial metrics.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'data': pandas DataFrame with quarterly income statement data, or None if error
                    Rows represent financial metrics, columns represent fiscal quarters
                - 'error': Error message string if an error occurred, otherwise None
        
        Examples:
            >>> fetcher = DataFetcher('AAPL')
            >>> result = fetcher.fetch_quarterly_income()
            >>> if result['error'] is None:
            >>>     # Display the most recent quarter's data
            >>>     print(result['data'].iloc[:, 0])
        
        Note:
            The DataFrame structure: metrics as rows (e.g., 'Total Revenue', 'Net Income'),
            quarters as columns. Returns None for stocks with no income statement data.
        """
        # Check if ticker is valid first
        if not self.is_valid:
            return {"data": None, "error": f"Invalid ticker symbol: {self.ticker_symbol}"}
        
        try:
            quarterly_income_sheet = self.stock.quarterly_income_stmt
            
            if quarterly_income_sheet is None or quarterly_income_sheet.empty:
                return {"data": None, "error": f"No quarterly income data found for {self.ticker_symbol}"}

            # Normalize row/index names
            quarterly_income_sheet.index = (
                quarterly_income_sheet.index
                .astype(str)
                .str.lower()
                .str.replace(" ", "_")
            )
            
            return {"data": quarterly_income_sheet, "error": None}
            
        except Exception as e:
            warnings.warn(f"Error fetching quarterly income: {e}")
            return {"data": None, "error": str(e)}

    def fetch_dividends(self) -> Dict[str, Any]:
        """
        Fetch dividend history for the initialized ticker.
        
        Retrieves historical dividend payments including payment dates and amounts.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'data': pandas Series with dividend data, or None if error
                    Index contains dividend payment dates, values are dividend amounts
                - 'error': Error message string if an error occurred, otherwise None
        
        Examples:
            >>> fetcher = DataFetcher('AAPL')
            >>> result = fetcher.fetch_dividends()
            >>> if result['error'] is None:
            >>>     print(f"Total dividends paid: {result['data'].sum()}")
            >>>     print(f"Last dividend: {result['data'].iloc[-1]} on {result['data'].index[-1]}")
        
        Note:
            Returns None for stocks that do not pay dividends.
            Dividend amounts are typically in raw currency units (not adjusted for splits).
        """
        # Check if ticker is valid first
        if not self.is_valid:
            return {"data": None, "error": f"Invalid ticker symbol: {self.ticker_symbol}"}
        
        try:
            dividends = self.stock.dividends
            
            if dividends is None or dividends.empty:
                return {"data": None, "error": f"No dividends data found for {self.ticker_symbol}"}
            
            return {"data": dividends, "error": None}
            
        except Exception as e:
            warnings.warn(f"Error fetching dividends: {e}")
            return {"data": None, "error": str(e)}

    def get_full_stock_data(self) -> Dict[str, Any]:
        """
        Fetch and combine all available stock data into a single dictionary.
        
        This method aggregates information from all individual fetch methods:
        - Company information and fundamental metrics
        - Historical price data
        - Quarterly income statements
        - Dividend history
        
        Each component is fetched independently, and errors are tracked separately
        to allow partial data retrieval even if some components fail.
        
        Returns:
            Dict[str, Any]: A comprehensive dictionary containing:
                - 'ticker' (str): The stock ticker symbol
                - 'info' (dict): Fundamental metrics from fetch_info(), or None if error
                - 'history' (DataFrame): Historical prices from fetch_historical(), or None if error
                - 'financials' (DataFrame): Quarterly income from fetch_quarterly_income(), or None if error
                - 'dividends' (Series): Dividend history from fetch_dividends(), or None if error
                - 'errors' (dict): Dictionary of error messages keyed by component name
                - 'success' (bool): True if all components fetched successfully, False otherwise
        
        Examples:
            >>> fetcher = DataFetcher('AAPL')
            >>> data = fetcher.get_full_stock_data()
            >>> 
            >>> # Check if all data was fetched successfully
            >>> if data['success']:
            >>>     print(f"Company: {data['info']['short_name']}")
            >>>     print(f"Current Price: ${data['info']['current_price']}")
            >>>     print(f"Historical Data Shape: {data['history'].shape}")
            >>>     print(f"Dividends Count: {len(data['dividends'])}")
            >>> else:
            >>>     print(f"Partial errors: {data['errors']}")
            >>>     # Still access successfully fetched components
            >>>     if data['info']:
            >>>         print(f"Info available: {data['info']['symbol']}")
        
        Note:
            This method does not prevent you from accessing individual components
            even if others failed. Check the 'errors' dictionary or individual
            component values (None indicates fetch failure).
            All fetch methods reuse the same Ticker object to minimize API calls.
        """
        # Fetch each component once
        info_result = self.fetch_info()
        history_result = self.fetch_historical()
        financials_result = self.fetch_quarterly_income()
        dividends_result = self.fetch_dividends()
        
        # Build result with safe data extraction
        result = {
        "ticker": self.ticker_symbol,

        "info": info_result.get("data") if info_result.get("error") is None else {},

        "history": {
            "data": history_result.get("data") if history_result.get("error") is None else None
        },

        "dividends": {
            "data": dividends_result.get("data") if dividends_result.get("error") is None else None
        },

        "financials": {
            "data": financials_result.get("data") if financials_result.get("error") is None else None
        },

        "errors": {},
        "success": self.is_valid
    }
        
        # Collect non-null errors
        if info_result.get("error"):
            result['errors']['info'] = info_result["error"]
            result['success'] = False

        if history_result.get("error"):
            result['errors']['history'] = history_result["error"]
            result['success'] = False

        if financials_result.get("error"):
            result['errors']['financials'] = financials_result["error"]
            result['success'] = False

        if dividends_result.get("error"):
            result['errors']['dividends'] = dividends_result["error"]
            result['success'] = False
        
        return result


# ============================================================================
# Helper function for quick validation without creating a class instance
# ============================================================================

def is_valid_ticker(ticker: str) -> bool:
    """
    Quick utility function to check if a ticker symbol is valid.
    
    Args:
        ticker (str): Stock ticker symbol to validate
        
    Returns:
        bool: True if ticker is valid, False otherwise
        
    Examples:
        >>> if is_valid_ticker("AAPL"):
        >>>     print("AAPL is a valid ticker")
        >>> 
        >>> # Filter a list of tickers
        >>> tickers = ["AAPL", "INVALID", "MSFT", "GOOGL"]
        >>> valid = [t for t in tickers if is_valid_ticker(t)]
        >>> print(f"Valid tickers: {valid}")
    """
    return DataFetcher.validate_ticker_static(ticker)


# Example usage (commented out)
# fetcher = DataFetcher("AAPL")
# data = fetcher.get_full_stock_data()
# 
# # Check if all data was fetched successfully
# if data['success']:
#     print(f"Info: {data['info']['short_name']}")
#     print(f"History shape: {data['history'].shape}")
#     print(f"Dividends count: {len(data['dividends'])}")
# else:
#     print(f"Partial errors: {data['errors']}")