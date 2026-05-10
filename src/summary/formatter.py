"""
Formats the final summary text using templates.
Contradictions are handled separately and never duplicated as risks.
"""

import random

SUMMARY_TEMPLATES = {
    "positive_negative": [
        "This stock shows {pos}. However, {neg}. Overall, it is a {rec} recommendation with {conf} confidence.",
        "On the positive side, {pos}. But {neg}. The verdict: {rec} with {conf} confidence.",
        "{pos} is encouraging, yet {neg} are concerns. Therefore, the recommendation is {rec} ({conf} confidence).",
    ],
    "positive_only": [
        "This stock shows {pos}. Overall, it is a {rec} recommendation with {conf} confidence.",
        "Key strengths include {pos}. Hence, the stock is rated {rec} with {conf} confidence.",
    ],
    "negative_only": [
        "This stock faces challenges: {neg}. As a result, it is a {rec} recommendation with {conf} confidence.",
        "Risks outweigh positives: {neg}. Consequently, the rating is {rec} ({conf} confidence).",
    ],
}


def format_summary(strengths, risks, neutrals, contradictions, recommendation, conf_level):
    """Returns a clean, non‑duplicated summary string."""

    # Map recommendation to a word (no leading "a")
    rec_map = {
        "Strong Buy": "strong buy",
        "Buy": "buy",
        "Hold": "hold",
        "Weak Hold": "weak hold (consider waiting)",
        "Sell": "sell",
    }
    rec_phrase = rec_map.get(recommendation, "hold")

    # --- Handle contradictions (highest priority) ---
    if contradictions:
        main_issue = contradictions[0]["text"]
        summary = f"Key contradiction: {main_issue}. "
        pos_text = ", ".join([s["text"] for s in strengths[:2]]) if strengths else ""
        neg_text = ", ".join([r["text"] for r in risks[:2]]) if risks else ""
        if pos_text and neg_text:
            summary += f"On the positive side, {pos_text}. But also {neg_text}. "
        elif pos_text:
            summary += f"On the positive side, {pos_text}. "
        elif neg_text:
            summary += f"Risks include {neg_text}. "
        summary += f"Overall, it is a {rec_phrase} recommendation with {conf_level} confidence."
        if neutrals and "Notably" not in summary:
            summary += f" Notably, {neutrals[0]['text']}."
        if conf_level in ["Low", "Very Low"]:
            summary += " (Limited data – use caution.)"
        return summary

    # --- No contradictions: use standard templates ---
    pos_text = ", ".join([s["text"] for s in strengths[:2]]) if strengths else ""
    neg_text = ", ".join([r["text"] for r in risks[:2]]) if risks else ""

    if strengths and risks:
        template = random.choice(SUMMARY_TEMPLATES["positive_negative"])
        summary = template.format(pos=pos_text, neg=neg_text, rec=rec_phrase, conf=conf_level)
    elif strengths:
        template = random.choice(SUMMARY_TEMPLATES["positive_only"])
        summary = template.format(pos=pos_text, rec=rec_phrase, conf=conf_level)
    elif risks:
        template = random.choice(SUMMARY_TEMPLATES["negative_only"])
        summary = template.format(neg=neg_text, rec=rec_phrase, conf=conf_level)
    else:
        summary = f"This stock has mixed signals. The recommendation is a {rec_phrase} recommendation with {conf_level} confidence."

    # Append neutral insight if available
    if neutrals and "Notably" not in summary:
        summary += f" Notably, {neutrals[0]['text']}."

    if conf_level in ["Low", "Very Low"]:
        summary += " (Limited data – use caution.)"

    return summary