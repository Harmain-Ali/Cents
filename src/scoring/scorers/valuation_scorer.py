from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_inverse


class ValuationScorer(BaseScorer):
    """
    Calculate a valuation score based on common multiples (lower is better).

    The score uses inverse normalisation (higher score = cheaper valuation):
        - 30% P/E ratio – normalised from 5 to 60 (below 5 → 100, above 60 → 0)
        - 25% PEG ratio – normalised from 0.5 to 3
        - 20% Price/Book – normalised from 0.5 to 10
        - 15% Price/Sales – normalised from 0.5 to 15
        - 10% EV/EBITDA – normalised from 3 to 30

    Returns:
        dict: Contains 'score' (0–100) and 'details' with individual component scores.
    """

    def calculate(self):
        # Access data using schema keys (lowercase)
        info = self.data["info"]

        # --- Extract values with safe conversion ---
        pe = safe_float(info.get("pe_ratio"))
        peg = safe_float(info.get("peg_ratio"))
        pb = safe_float(info.get("price_to_book"))
        ps = safe_float(info.get("price_to_sales"))
        ev = safe_float(info.get("ev_to_ebitda"))

        # --- Inverse normalisation (lower multiple = higher score) ---
        pe_score = normalize_inverse(pe, 5, 60)
        peg_score = normalize_inverse(peg, 0.5, 3)
        pb_score = normalize_inverse(pb, 0.5, 10)
        ps_score = normalize_inverse(ps, 0.5, 15)
        ev_score = normalize_inverse(ev, 3, 30)

        # --- Weighted final score ---
        raw_score = (
            pe_score * 0.30 +
            peg_score * 0.25 +
            pb_score * 0.20 +
            ps_score * 0.15 +
            ev_score * 0.10
        )

        return {
            "score": round(raw_score, 2),
            "details": {
                "pe_score": round(pe_score, 2),
                "peg_score": round(peg_score, 2),
                "pb_score": round(pb_score, 2),
                "ps_score": round(ps_score, 2),
                "ev_score": round(ev_score, 2),
            },
        }