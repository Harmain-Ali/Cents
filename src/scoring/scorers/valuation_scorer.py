from src.scoring.scorers.base_scorer import BaseScorer

from src.scoring.utils.safe_math import safe_float

from src.scoring.utils.normalization import (
    normalize_inverse
)


class ValuationScorer(BaseScorer):

    def calculate(self):

        info = self.data["INFO"]

        pe = safe_float(info.get("PE RATIO"))
        peg = safe_float(info.get("PEG RATIO"))
        pb = safe_float(info.get("PRICE TO BOOK"))
        ps = safe_float(info.get("PRICE TO SALES"))
        ev = safe_float(info.get("EV TO EBITDA"))

        pe_score = normalize_inverse(pe, 5, 60)
        peg_score = normalize_inverse(peg, 0.5, 3)
        pb_score = normalize_inverse(pb, 0.5, 10)
        ps_score = normalize_inverse(ps, 0.5, 15)
        ev_score = normalize_inverse(ev, 3, 30)

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
                "ev_score": round(ev_score, 2)
            }
        }