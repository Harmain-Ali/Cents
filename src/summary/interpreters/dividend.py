from src.summary.thresholds import get_thresholds

def interpret_dividend(yield_pct, payout, sector):
    if yield_pct is None or yield_pct <= 0:
        return None

    # Cross-check: high yield + high payout ratio is risky
    if yield_pct > 3 and payout and payout > 80:
        return {
            "impact": "negative",
            "text": f"High dividend yield ({yield_pct:.2f}%) but payout ratio ({payout:.0f}%) suggests unsustainability",
            "importance": 6
        }

    th = get_thresholds(sector, "dividend_yield")
    low = th.get("low", 1)
    attractive = th.get("attractive", 3)
    high = th.get("high", 5)

    if yield_pct > attractive:
        return {
            "impact": "positive",
            "text": f"Attractive dividend yield ({yield_pct:.2f}%)",
            "importance": min(10, yield_pct)
        }
    elif yield_pct > low:
        return {"impact": "neutral", "text": f"Modest dividend yield ({yield_pct:.2f}%)", "importance": 2}
    return None