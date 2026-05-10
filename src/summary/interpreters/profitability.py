from src.summary.thresholds import get_thresholds

def interpret_roe(roe, debt_to_equity, sector):
    if roe is None:
        return None
    th = get_thresholds(sector, "roe")
    weak = th.get("weak", 8)
    avg = th.get("average", 15)
    strong = th.get("strong", 20)

    if roe > strong:
        if debt_to_equity and debt_to_equity > 1.0:
            return {
                "impact": "neutral",
                "text": f"Good ROE ({roe:.1f}%) but supported by high debt",
                "importance": 5
            }
        else:
            return {
                "impact": "positive",
                "text": f"Excellent profitability (ROE {roe:.1f}%)",
                "importance": min(10, roe / 10)
            }
    elif roe > avg:
        return {"impact": "positive", "text": f"Good profitability (ROE {roe:.1f}%)", "importance": 5}
    elif roe < weak:
        return {
            "impact": "negative",
            "text": f"Weak profitability (ROE {roe:.1f}%)",
            "importance": min(10, (weak - roe) / 2)
        }
    return None

def interpret_profit_margin(margin):
    if margin is None:
        return None
    if margin > 15:
        return {
            "impact": "positive",
            "text": f"Healthy profit margin ({margin:.1f}%)",
            "importance": min(10, margin / 5)
        }
    elif margin < 5:
        return {
            "impact": "negative",
            "text": f"Thin profit margin ({margin:.1f}%)",
            "importance": min(10, (5 - margin) / 2)
        }
    return None