def detect_contradictions(rev_growth, fcf, debt, roe, pe, earn_growth, profit_margin, rsi, price, ma200):
    contradictions = []

    if rev_growth and rev_growth > 15 and fcf and fcf < 0 and debt and debt > 1.0:
        contradictions.append({
            "impact": "negative",
            "is_contradiction": True,
            "text": "Revenue is growing rapidly, but it's funded by debt and negative free cash flow – growth may be unsustainable.",
            "importance": 9,
        })

    if roe and roe > 20 and debt and debt > 1.2:
        contradictions.append({
            "impact": "negative",
            "is_contradiction": True,
            "text": f"High ROE ({roe:.1f}%) is partly due to high leverage – underlying profitability is weaker.",
            "importance": 7,
        })

    if pe and pe < 15 and earn_growth and earn_growth < -5:
        contradictions.append({
            "impact": "negative",
            "is_contradiction": True,
            "text": f"Low P/E ({pe:.1f}) is misleading because earnings are falling – classic value trap.",
            "importance": 8,
        })

    if rev_growth and rev_growth > 10 and profit_margin and profit_margin < 5:
        contradictions.append({
            "impact": "negative",
            "is_contradiction": True,
            "text": "Sales are growing, but profit margins are very thin – revenue growth isn't translating to profits.",
            "importance": 7,
        })

    if price and ma200 and price > ma200 and ((debt and debt > 1.5) or (fcf and fcf < 0)):
        contradictions.append({
            "impact": "negative",
            "is_contradiction": True,
            "text": "Stock price is in an uptrend, but underlying financial health is weak – market optimism may be overdone.",
            "importance": 6,
        })

    if rsi and rsi > 70 and ((fcf and fcf < 0) or (earn_growth and earn_growth < 0)):
        contradictions.append({
            "impact": "negative",
            "is_contradiction": True,
            "text": "Stock is overbought despite weak fundamentals – potential for sharp correction.",
            "importance": 8,
        })

    return contradictions