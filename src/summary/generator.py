"""
Main summary generator. Collects all insights, detects contradictions separately,
and builds final output without duplication.
"""

from src.summary.types import SummaryOutput
from src.summary.interpreters import (
    interpret_pe, interpret_peg,
    interpret_roe, interpret_profit_margin,
    interpret_growth,
    interpret_debt, interpret_current_ratio, interpret_fcf,
    interpret_dividend,
    interpret_rsi, interpret_trend,
)
from src.summary.contradictions import detect_contradictions
from src.summary.formatter import format_summary
from src.scoring.utils.safe_math import safe_float


def generate_summary(data: dict, scorer_output: dict) -> SummaryOutput:
    """
    data: raw stock data (info, history, etc.)
    scorer_output: output from StockScorer.score() (final_score, recommendation, confidence)
    """
    info = data.get("info", {})
    history = data.get("history", {})
    sector = info.get("sector")

    # Extract key metrics
    pe = safe_float(info.get("pe_ratio"))
    peg = safe_float(info.get("peg_ratio"))
    roe = safe_float(info.get("roe"))
    profit_margin = safe_float(info.get("profit_margin"))
    rev_growth = safe_float(info.get("revenue_growth"))
    earn_growth = safe_float(info.get("earnings_growth"))
    debt = safe_float(info.get("debt_to_equity"))
    cr = safe_float(info.get("current_ratio"))
    fcf = safe_float(info.get("free_cash_flow"))
    div_yield = safe_float(info.get("dividend_yield"))
    payout = safe_float(info.get("payout_ratio"))
    rsi = safe_float(history.get("rsi_14"))
    price = safe_float(info.get("current_price"))
    ma50 = safe_float(history.get("ma50"))
    ma200 = safe_float(history.get("ma200"))

    # Collect all *non‑contradiction* insights
    insights = []

    # Valuation
    if pe:
        insight = interpret_pe(pe, sector)
        if insight:
            insights.append(insight)
    if peg:
        insight = interpret_peg(peg, sector)
        if insight:
            insights.append(insight)

    # Profitability
    if roe is not None:
        insight = interpret_roe(roe, debt, sector)
        if insight:
            insights.append(insight)
    if profit_margin is not None:
        insight = interpret_profit_margin(profit_margin)
        if insight:
            insights.append(insight)

    # Growth
    if rev_growth is not None:
        insight = interpret_growth("Revenue", rev_growth, sector)
        if insight:
            insights.append(insight)
    if earn_growth is not None:
        insight = interpret_growth("Earnings", earn_growth, sector)
        if insight:
            insights.append(insight)

    # Financial Health
    if debt is not None:
        insight = interpret_debt(debt, sector)
        if insight:
            insights.append(insight)
    if cr is not None:
        insight = interpret_current_ratio(cr)
        if insight:
            insights.append(insight)
    if fcf is not None:
        insight = interpret_fcf(fcf)
        if insight:
            insights.append(insight)

    # Dividend
    if div_yield is not None and div_yield > 0:
        insight = interpret_dividend(div_yield, payout, sector)
        if insight:
            insights.append(insight)

    # Technical
    if rsi is not None:
        insight = interpret_rsi(rsi)
        if insight:
            insights.append(insight)
    if price and ma50 and ma200:
        insight = interpret_trend(price, ma50, ma200)
        if insight:
            insights.append(insight)

    # Detect contradictions separately – do NOT add to insights
    contradictions = detect_contradictions(
        rev_growth, fcf, debt, roe, pe, earn_growth, profit_margin, rsi, price, ma200
    )

    # Separate standard insights by impact
    strengths = [i for i in insights if i["impact"] == "positive"]
    risks = [i for i in insights if i["impact"] == "negative"]
    neutrals = [i for i in insights if i["impact"] == "neutral"]

    # Sort by importance (descending)
    strengths.sort(key=lambda x: x["importance"], reverse=True)
    risks.sort(key=lambda x: x["importance"], reverse=True)
    neutrals.sort(key=lambda x: x["importance"], reverse=True)

    # Build final summary text (contradictions are passed separately)
    summary_text = format_summary(
        strengths[:3],
        risks[:3],
        neutrals[:1],
        contradictions,   # only used for the main summary block, not as risks
        scorer_output.get("recommendation", "Hold"),
        scorer_output.get("confidence", {}).get("level", "Moderate"),
    )

    return {
        "summary": summary_text,
        "strengths": [s["text"] for s in strengths[:3]],
        "risks": [r["text"] for r in risks[:3]],
        "neutrals": [n["text"] for n in neutrals[:1]],
        "contradictions": [c["text"] for c in contradictions],
        "recommendation": scorer_output.get("recommendation", "Hold"),
        "confidence_label": scorer_output.get("confidence", {}).get("level", "Moderate"),
        "confidence_score": scorer_output.get("confidence", {}).get("score", 50),
    }