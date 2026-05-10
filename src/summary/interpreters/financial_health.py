from src.summary.thresholds import get_thresholds

def interpret_debt(debt, sector):
    if debt is None:
        return None
    th = get_thresholds(sector, "debt_to_equity")
    low = th.get("low", 0.5)
    high = th.get("high", 1.5)

    if debt < low:
        return {"impact": "positive", "text": "Low debt reduces financial risk", "importance": 5}
    elif debt > high:
        return {
            "impact": "negative",
            "text": f"High debt level ({debt:.2f}x equity)",
            "importance": min(10, debt / 2)
        }
    return None

def interpret_current_ratio(cr):
    if cr is None:
        return None
    if cr > 1.5:
        return {"impact": "positive", "text": "Strong short-term liquidity", "importance": 3}
    elif cr < 1.0:
        return {"impact": "negative", "text": "Low liquidity (current ratio below 1)", "importance": 5}
    return None

def interpret_fcf(fcf):
    if fcf is None:
        return None
    if fcf > 0:
        return {"impact": "positive", "text": "Company generates positive free cash flow", "importance": 4}
    else:
        return {"impact": "negative", "text": "Negative free cash flow", "importance": 7}