from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear, normalize_inverse
from src.scoring.config.sector_config import get_range

class FinancialHealthScorer(BaseScorer):
    """
    Financial health score with sector‑aware liquidity ranges.
    """

    def calculate(self):
        info = self.data["info"]
        sector = info.get("sector")

        debt_to_equity = safe_float(info.get("debt_to_equity"))
        current_ratio = safe_float(info.get("current_ratio"))
        quick_ratio = safe_float(info.get("quick_ratio"))
        free_cash_flow = safe_float(info.get("free_cash_flow"))
        market_cap = safe_float(info.get("market_cap"))

        # D/E uses inverse normalisation – can keep default 0–3 for all
        de_score = normalize_inverse(debt_to_equity, 0, 3)

        # Liquidity ranges from config
        cr_min, cr_max = get_range(sector, "current_ratio", 0.5, 4)
        qr_min, qr_max = get_range(sector, "quick_ratio", 0.2, 3)

        if cr_min is None:
            cr_score = 50
        else:
            cr_score = normalize_linear(current_ratio, cr_min, cr_max)

        if qr_min is None:
            qr_score = 50
        else:
            qr_score = normalize_linear(quick_ratio, qr_min, qr_max)

        # FCF yield
        if free_cash_flow is not None and market_cap is not None and market_cap != 0:
            fcf_yield = (free_cash_flow / market_cap) * 100
        else:
            fcf_yield = None
        fcf_score = normalize_linear(fcf_yield, -5, 15)

        raw_score = (
            de_score * 0.30 +
            cr_score * 0.30 +
            qr_score * 0.20 +
            fcf_score * 0.20
        )

        return {
            "score": round(raw_score, 2),
            "details": {
                "debt_to_equity_score": round(de_score, 2),
                "current_ratio_score": round(cr_score, 2),
                "quick_ratio_score": round(qr_score, 2),
                "fcf_score": round(fcf_score, 2),
            },
        }