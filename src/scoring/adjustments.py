from src.scoring.utils.safe_math import safe_float


class RiskAdjustments:
    """
    Apply risk‑based penalties or bonuses to a base score.

    Adjustments are made for:
        - Market cap (small cap penalty, mega cap bonus)
        - Beta (high volatility penalty, low volatility bonus)
        - Sector (high‑risk sectors like Biotech, Crypto, Cannabis)
        - Dividend safety (high payout with negative FCF)
        - Value trap (low P/E but negative earnings growth)
        - Weak momentum (50‑day MA below 200‑day MA)
        - Negative free cash flow

    Args:
        data (dict): Full stock data dictionary following the standard schema.
        score (float): The base score to adjust (typically 0–100).

    Returns:
        float: Adjusted score.
    """

    @staticmethod
    def apply(data, score):
        # Access data using schema keys (lowercase)
        info = data["info"]
        history = data["history"]

        adjusted = score

        # --- Extract values with safe conversion ---
        market_cap = safe_float(info.get("market_cap"))
        beta = safe_float(info.get("beta"))
        sector = info.get("sector")  # string, may be None
        pe = safe_float(info.get("pe_ratio"))
        earnings_growth = safe_float(info.get("earnings_growth"))
        free_cash_flow = safe_float(info.get("free_cash_flow"))
        payout_ratio = safe_float(info.get("payout_ratio"))
        ma50 = safe_float(history.get("ma50"))
        ma200 = safe_float(history.get("ma200"))

        # ------------------------------------------------
        # MARKET CAP ADJUSTMENT
        # ------------------------------------------------
        if market_cap is not None:
            # Small Cap Risk (under $2B)
            if market_cap < 2_000_000_000:
                adjusted -= 5
            # Mega Cap Stability (over $200B)
            elif market_cap > 200_000_000_000:
                adjusted += 2

        # ------------------------------------------------
        # BETA ADJUSTMENT
        # ------------------------------------------------
        if beta is not None:
            if beta > 1.5:
                adjusted -= 3
            elif beta < 0.5:
                adjusted += 2

        # ------------------------------------------------
        # SECTOR RISK
        # ------------------------------------------------
        risky_sectors = ["Biotechnology", "Crypto", "Cannabis"]
        if sector in risky_sectors:
            adjusted -= 3

        # ------------------------------------------------
        # DIVIDEND SAFETY
        # ------------------------------------------------
        if payout_ratio is not None and free_cash_flow is not None:
            if payout_ratio > 1 and free_cash_flow < 0:
                adjusted -= 4

        # ------------------------------------------------
        # VALUE TRAP DETECTION
        # ------------------------------------------------
        if pe is not None and earnings_growth is not None:
            if pe < 10 and earnings_growth < 0:
                adjusted -= 5

        # ------------------------------------------------
        # WEAK MOMENTUM
        # ------------------------------------------------
        if ma50 is not None and ma200 is not None:
            if ma50 < ma200:
                adjusted -= 2

        # ------------------------------------------------
        # NEGATIVE FREE CASH FLOW
        # ------------------------------------------------
        if free_cash_flow is not None and free_cash_flow < 0:
            adjusted -= 3

        return adjusted