from src.summary.thresholds import get_thresholds

def interpret_pe(pe, sector):
    if not pe or pe <= 0:
        return None
    th = get_thresholds(sector, "pe_ratio")
    cheap = th.get("cheap", 12)
    fair = th.get("fair", 20)
    expensive = th.get("expensive", 25)

    if pe < cheap:
        return {
            "impact": "positive",
            "text": f"Very attractive valuation (P/E {pe:.1f})",
            "importance": min(10, (cheap - pe) / cheap * 10)
        }
    elif pe < fair:
        return {"impact": "neutral", "text": f"Reasonable valuation (P/E {pe:.1f})", "importance": 3}
    elif pe < expensive:
        return {"impact": "neutral", "text": f"Moderately high valuation (P/E {pe:.1f})", "importance": 4}
    else:
        return {
            "impact": "negative",
            "text": f"Expensive valuation (P/E {pe:.1f})",
            "importance": min(10, (pe - expensive) / 5)
        }

def interpret_peg(peg, sector):
    if not peg or peg <= 0:
        return None
    th = get_thresholds(sector, "peg_ratio")
    good = th.get("good", 0.8)
    warning = th.get("warning", 2.0)

    if peg < good:
        return {
            "impact": "positive",
            "text": f"Growth is undervalued (PEG {peg:.2f})",
            "importance": min(10, (good - peg) * 5)
        }
    elif peg > warning:
        return {
            "impact": "negative",
            "text": f"Growth may be overpriced (PEG {peg:.2f})",
            "importance": min(10, (peg - warning) * 2)
        }
    return None