"""
Forward‑looking adjustments to supplement the trailing‑only scoring.

Uses analyst estimates, forward valuation, and momentum to adjust the
final score (positive or negative) before clipping to 0–100.
"""

from src.scoring.utils.safe_math import safe_float


class ForwardAdjustments:
    """
    Apply bonuses/penalties based on forward‑looking estimates.
    """

    @staticmethod
    def apply(data, score):
        """
        Args:
            data (dict): Full stock data dictionary (with 'info' key).
            score (float): Score after risk adjustments (0–100).

        Returns:
            float: Adjusted score (may be outside 0–100; caller will clip).
        """
        if score is None:
            score = 50.0
        info = data.get("info", {})
        adjusted = score

        # ------------------------------------------------
        # 1. Forward PEG (P/E divided by earnings growth)
        #    Cheap future growth = bonus
        # ------------------------------------------------
        forward_pe = safe_float(info.get("forward_pe"))
        eps_growth = safe_float(info.get("eps_growth"))  # our computed forward growth

        if forward_pe is not None and eps_growth is not None and eps_growth > 0:
            forward_peg = forward_pe / eps_growth
            if forward_peg < 1.0:
                adjusted += 5
            elif forward_peg > 3.0:
                adjusted -= 3

        # ------------------------------------------------
        # 2. Analyst recommendation (from Yahoo)
        # ------------------------------------------------
        rec = info.get("recommendation_key", "").lower()
        bonus_map = {
            "strong_buy": 7,
            "buy": 5,
            "hold": 0,
            "sell": -5,
            "strong_sell": -7
        }
        adjusted += bonus_map.get(rec, 0)

        # ------------------------------------------------
        # 3. Recovery bonus: forward growth strongly positive
        #    while trailing growth was negative
        # ------------------------------------------------
        forward_eps_abs = safe_float(info.get("forward_eps"))
        trailing_eps = safe_float(info.get("trailing_eps"))
        if forward_eps_abs and trailing_eps and trailing_eps != 0:
            forward_growth = (forward_eps_abs - trailing_eps) / abs(trailing_eps) * 100
            # If forward growth >20% and trailing growth was negative (eps_growth < 0)
            if forward_growth > 20 and eps_growth and eps_growth < 0:
                adjusted += 4

        # ------------------------------------------------
        # 4. Price target upside (requires target_mean_price)
        # ------------------------------------------------
        target_price = safe_float(info.get("target_mean_price"))
        current_price = safe_float(info.get("current_price"))
        if target_price and current_price and current_price > 0:
            upside = (target_price - current_price) / current_price
            if upside > 0.2:          # >20% upside
                adjusted += 3
            elif upside < -0.1:       # >10% downside
                adjusted -= 2
