from src.summary.thresholds import get_thresholds

def interpret_growth(metric_name, growth, sector):
    """
    metric_name: "Revenue" or "Earnings"
    growth: percentage (e.g., 12.5 for 12.5%)
    """
    if growth is None:
        return None
    th = get_thresholds(sector, f"{metric_name.lower()}_growth")
    if not th:
        th = get_thresholds(sector, "revenue_growth")
    declining = th.get("declining", 0)
    moderate = th.get("moderate", 10)
    strong = th.get("strong", 20)

    if growth > strong:
        return {
            "impact": "positive",
            "text": f"Very strong {metric_name.lower()} growth ({growth:.1f}%)",
            "importance": min(10, growth / 5)
        }
    elif growth > moderate:
        return {
            "impact": "positive",
            "text": f"Solid {metric_name.lower()} growth ({growth:.1f}%)",
            "importance": 5
        }
    elif growth < declining:
        return {
            "impact": "negative",
            "text": f"{metric_name} is declining ({growth:.1f}%)",
            "importance": min(10, abs(growth) / 5)
        }
    return None