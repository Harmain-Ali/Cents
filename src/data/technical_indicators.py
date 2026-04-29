# technical_indicators.py

import yfinance as yf
import pandas as pd


class TechnicalIndicators:
    def __init__(self, ticker: str, period: str = "1y"):
        self.ticker_symbol = ticker
        self.period = period

        # Create ticker object
        self.stock = yf.Ticker(self.ticker_symbol)

        # Load historical data
        self.data = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        data = self.stock.history(period=self.period)

        if data.empty:
            raise ValueError("Invalid ticker or no data found.")

        return data

    # =============================
    # MOVING AVERAGES
    # =============================
    def moving_averages(self):
        df = self.data.copy()

        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()

        return {
            "price": df["Close"].iloc[-1],
            "ma50": df["MA50"].iloc[-1],
            "ma200": df["MA200"].iloc[-1]
        }

    # =============================
    # RSI
    # =============================
    def rsi(self, window: int = 14):
        df = self.data.copy()

        delta = df["Close"].diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window).mean()
        avg_loss = loss.rolling(window).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return {
            "rsi": rsi.iloc[-1]
        }

    # =============================
    # MACD
    # =============================
    def macd(self):
        df = self.data.copy()

        df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()

        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        return {
            "macd": df["MACD"].iloc[-1],
            "signal": df["Signal"].iloc[-1]
        }

    # =============================
    # VOLUME
    # =============================
    def volume(self):
        df = self.data.copy()

        avg_volume = df["Volume"].rolling(20).mean()

        return {
            "current_volume": df["Volume"].iloc[-1],
            "avg_volume": avg_volume.iloc[-1]
        }

    # =============================
    # ALL INDICATORS (COMBINED)
    # =============================
    def get_all_indicators(self):
        return {
            "ticker": self.ticker_symbol,
            "moving_averages": self.moving_averages(),
            "rsi": self.rsi(),
            "macd": self.macd(),
            "volume": self.volume()
        }
