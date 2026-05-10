def get_recommendation(score):
    """
    Convert a numerical score into a textual investment recommendation.

    The score ranges from 0 to 100 (though any value is accepted). Higher
    scores indicate stronger investment merit.

    Recommendation thresholds (3‑tier system):
        - 70–100: "Buy"
        - 40–69:  "Hold"
        - 0–39:   "Sell"

    Args:
        score (float or int): Numerical score, typically after risk adjustments.

    Returns:
        str: One of "Buy", "Hold", or "Sell".
    """
    if score >= 70:
        return "Buy"
    elif score >= 40:
        return "Hold"
    else:
        return "Sell"