from src.scoring.scorers.base_scorer import BaseScorer
from src.scoring.utils.safe_math import safe_float
from src.scoring.utils.normalization import normalize_linear
from src.scoring.config.sector_config import get_range

class ProfitabilityScorer(BaseScorer):
    """
    Profitability score with sector‑aware ROE/ROA ranges.
    """

    def calculate(self):
        info = self.data["info"]
        sector = info.get("sector")

        roe = safe_float(info.get("roe"))
        roa = safe_float(info.get("roa"))
        profit_margin = safe_float(info.get("profit_margin"))
        operating_margin = safe_float(info.get("operating_margin"))
        gross_margin = safe_float(info.get("gross_margin"))

        # Get ranges (defaults from config)
        roe_min, roe_max = get_range(sector, "roe", 0, 30)
        roa_min, roa_max = get_range(sector, "roa", 0, 20)
        pm_min, pm_max = get_range(sector, "profit_margin", 0, 30)
        om_min, om_max = get_range(sector, "operating_margin", 0, 35)
        gm_min, gm_max = get_range(sector, "gross_margin", 0, 60)

        roe_score = normalize_linear(roe, roe_min, roe_max) if roe_min is not None else 50
        roa_score = normalize_linear(roa, roa_min, roa_max) if roa_min is not None else 50
        pm_score = normalize_linear(profit_margin, pm_min, pm_max) if pm_min is not None else 50
        om_score = normalize_linear(operating_margin, om_min, om_max) if om_min is not None else 50
        gm_score = normalize_linear(gross_margin, gm_min, gm_max) if gm_min is not None else 50

        raw_score = (
            roe_score * 0.30 +
            roa_score * 0.20 +
            pm_score * 0.25 +
            om_score * 0.15 +
            gm_score * 0.10
        )

        return {
            "score": round(raw_score, 2),
            "details": {
                "roe_score": round(roe_score, 2),
                "roa_score": round(roa_score, 2),
                "profit_margin_score": round(pm_score, 2),
                "operating_margin_score": round(om_score, 2),
                "gross_margin_score": round(gm_score, 2),
            },
        }