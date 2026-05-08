def get_recommendation(score):
    """
    Convert a numerical score into a textual investment recommendation.

    The score ranges from 0 to 100 (though any value is accepted). Higher
    scores indicate stronger investment merit.

    Recommendation thresholds:
        - 85–100: "Strong Buy"
        - 70–84:  "Buy"
        - 55–69:  "Hold"
        - 40–54:  "Weak Hold"
        - 0–39:   "Sell"

    Args:
        score (float or int): Numerical score, typically after risk adjustments.

    Returns:
        str: One of "Strong Buy", "Buy", "Hold", "Weak Hold", or "Sell".
    """
    if score >= 85:
        return "Strong Buy"
    elif score >= 70:
        return "Buy"
    elif score >= 55:
        return "Hold"
    elif score >= 40:
        return "Weak Hold"
    return "Sell"