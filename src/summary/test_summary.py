from src.summary import generate_summary

# Mock data (like Apple example)
test_data = {
    "info": {
        "pe_ratio": 35.55,
        "peg_ratio": 2.52,
        "roe": 141.47,
        "profit_margin": 27.15,
        "revenue_growth": 16.6,
        "earnings_growth": 21.8,
        "debt_to_equity": 0.795,
        "current_ratio": 1.07,
        "free_cash_flow": 101090746368,
        "dividend_yield": 0.0038,
        "payout_ratio": 12.59,
        "current_price": 293.32,
        "sector": "Technology",
    },
    "history": {
        "rsi_14": 68.94,
        "ma50": 262.8,
        "ma200": 256.75,
    },
}

scorer_output = {
    "final_score": 59.84,
    "recommendation": "Hold",
    "confidence": {"score": 81.2, "level": "High"},
}

result = generate_summary(test_data, scorer_output)

print("=" * 60)
print("SUMMARY:")
print(result["summary"])
print("\nSTRENGTHS:")
for s in result["strengths"]:
    print(f"  ✅ {s}")
print("\nRISKS:")
for r in result["risks"]:
    print(f"  ⚠️ {r}")
print("\nNEUTRALS:")
for n in result["neutrals"]:
    print(f"  ⚖️ {n}")
print("\nCONTRADICTIONS:")
for c in result["contradictions"]:
    print(f"  🔄 {c}")



# main usage
# from src.scoring.stock_scorer import StockScorer
# from src.summary import generate_summary

# # 1. Get scorer output
# scorer = StockScorer(data, stock_type="Blend Stock")
# score_result = scorer.score()   # returns dict with final_score, recommendation, etc.

# # 2. Generate summary separately
# summary_output = generate_summary(data, {
#     "final_score": score_result["final_score"],
#     "recommendation": score_result["recommendation"],
#     "confidence": score_result.get("confidence", {})
# })

# # 3. Use both independently
# print(f"Score: {score_result['final_score']} – {score_result['recommendation']}")
# print(f"Summary: {summary_output['summary']}")
# print(f"Strengths: {summary_output['strengths']}")
# print(f"Risks: {summary_output['risks']}")