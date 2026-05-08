from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_inverse
from src.scoring.config.sector_config import get_range

class ValuationScorer(BaseScorer):
    """
    Calculate valuation score with sector‑aware ranges.
    """

    def calculate(self):
        info = self.data["info"]
        sector = info.get("sector")

        pe = safe_float(info.get("pe_ratio"))
        peg = safe_float(info.get("peg_ratio"))
        pb = safe_float(info.get("price_to_book"))
        ps = safe_float(info.get("price_to_sales"))
        ev = safe_float(info.get("ev_to_ebitda"))

        # Get sector-aware ranges
        pe_min, pe_max = get_range(sector, "pe_ratio", 5, 60)
        peg_min, peg_max = get_range(sector, "peg_ratio", 0.5, 3)
        pb_min, pb_max = get_range(sector, "price_to_book", 0.5, 10)
        ps_min, ps_max = get_range(sector, "price_to_sales", 0.5, 15)
        ev_min, ev_max = get_range(sector, "ev_to_ebitda", 3, 30)

        pe_score = normalize_inverse(pe, pe_min, pe_max) if pe_min is not None else 50
        peg_score = normalize_inverse(peg, peg_min, peg_max) if peg_min is not None else 50
        pb_score = normalize_inverse(pb, pb_min, pb_max) if pb_min is not None else 50
        ps_score = normalize_inverse(ps, ps_min, ps_max) if ps_min is not None else 50
        ev_score = normalize_inverse(ev, ev_min, ev_max) if ev_min is not None else 50

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