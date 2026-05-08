from src.scoring.utils.safe_math import safe_float
from src.scoring.config.sector_config import HIGH_RISK_SECTORS

class RiskAdjustments:
    # ... (same docstring) ...

    @staticmethod
    def apply(data, score):
        info = data["info"]
        history = data["history"]

        adjusted = score

        market_cap = safe_float(info.get("market_cap"))
        beta = safe_float(info.get("beta"))
        sector = info.get("sector")
        pe = safe_float(info.get("pe_ratio"))
        earnings_growth = safe_float(info.get("earnings_growth"))
        free_cash_flow = safe_float(info.get("free_cash_flow"))
        payout_ratio = safe_float(info.get("payout_ratio"))
        ma50 = safe_float(history.get("ma50"))
        ma200 = safe_float(history.get("ma200"))

        # Market cap
        if market_cap is not None:
            if market_cap < 2_000_000_000:
                adjusted -= 5
            elif market_cap > 200_000_000_000:
                adjusted += 2

        # Beta
        if beta is not None:
            if beta > 1.5:
                adjusted -= 3
            elif beta < 0.5:
                adjusted += 2

        # Sector risk – using config list
        if sector and sector in HIGH_RISK_SECTORS:
            adjusted -= 3

        # Dividend safety
        if payout_ratio is not None and free_cash_flow is not None:
            if payout_ratio > 1 and free_cash_flow < 0:
                adjusted -= 4

        # Value trap
        if pe is not None and earnings_growth is not None:
            if pe < 10 and earnings_growth < 0:
                adjusted -= 5

        # Weak momentum
        if ma50 is not None and ma200 is not None:
            if ma50 < ma200:
                adjusted -= 2

        # Negative FCF
        if free_cash_flow is not None and free_cash_flow < 0:
            adjusted -= 3

        return adjusted