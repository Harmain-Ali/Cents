def get_recommendation(score):

    if score >= 85:
        return "Strong Buy"

    elif score >= 70:
        return "Buy"

    elif score >= 55:
        return "Hold"

    elif score >= 40:
        return "Weak Hold"

    return "Sell"