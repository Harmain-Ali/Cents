"""
Complete stock analysis pipeline: fetch → enrich → classify → score → summarize.
Run with: python test_stock.py
"""

import sys
from pprint import pprint

from src.data.data_fetcher import DataFetcher
from src.data.metrics_engine import get_final_stock_data
from src.processes.stock_type_classifier import StockTypeClassifier
from src.scoring.stock_scorer import StockScorer
from src.summary import generate_summary   # new summary module


def analyze_ticker(ticker: str):
    """
    Run full analysis on a single ticker and print results.
    """
    print(f"\n{'='*60}")
    print(f"  ANALYZING: {ticker.upper()}")
    print(f"{'='*60}\n")

    # -------------------------------------------
    # 1. Validate ticker
    # -------------------------------------------
    is_valid = DataFetcher.validate_ticker_static(ticker)
    if not is_valid:
        print(f"❌ Invalid ticker: {ticker}")
        return None
    print("✅ Ticker is valid\n")

    # -------------------------------------------
    # 2. Fetch raw data
    # -------------------------------------------
    fetcher = DataFetcher(ticker)
    data = fetcher.get_full_stock_data()
    if not data.get("success"):
        print("⚠️ Partial errors during fetch:")
        pprint(data.get("errors", {}))
        print()
    print("✅ Data fetched successfully\n")

    # -------------------------------------------
    # 3. Compute extra metrics (technical, dividends, growth)
    # -------------------------------------------
    data = get_final_stock_data(data)
    print("✅ Metrics computed successfully\n")

    # -------------------------------------------
    # 4. Classify stock type (Growth / Value / Blend)
    # -------------------------------------------
    classifier = StockTypeClassifier(metrics=data["info"])
    classification = classifier.classify()
    stock_type = classification["classification"]
    print(f"📊 Stock type: {stock_type}\n")

    # -------------------------------------------
    # 5. Score the stock
    # -------------------------------------------
    scorer = StockScorer(data=data, stock_type=stock_type)
    score_result = scorer.score()
    print("✅ Scoring complete\n")

    # -------------------------------------------
    # 6. Generate human summary (NEW)
    # -------------------------------------------
    summary_output = generate_summary(
        data,
        {
            "final_score": score_result["final_score"],
            "recommendation": score_result["recommendation"],
            "confidence": score_result.get("confidence", {}),
        }
    )

    # -------------------------------------------
    # 7. Display results
    # -------------------------------------------
    print("\n" + "="*60)
    print("  NUMERIC SCORE & DETAILS")
    print("="*60)
    pprint(score_result)

    print("\n" + "="*60)
    print("  HUMAN READABLE SUMMARY")
    print("="*60)
    print(f"\n📈 {summary_output['summary']}\n")

    print("✅ STRENGTHS:")
    for s in summary_output["strengths"]:
        print(f"   • {s}")

    print("\n⚠️ RISKS:")
    for r in summary_output["risks"]:
        print(f"   • {r}")

    if summary_output["neutrals"]:
        print("\n⚖️ NEUTRAL OBSERVATIONS:")
        for n in summary_output["neutrals"]:
            print(f"   • {n}")

    if summary_output["contradictions"]:
        print("\n🔄 CONTRADICTIONS (key tensions):")
        for c in summary_output["contradictions"]:
            print(f"   • {c}")

    print(f"\n🔒 Confidence: {summary_output['confidence_label']} ({summary_output['confidence_score']:.1f}%)\n")

    return {
        "score": score_result,
        "summary": summary_output,
    }


if __name__ == "__main__":
    # You can change the ticker or pass as command line argument
    ticker = sys.argv[1] if len(sys.argv) > 1 else "Asti"
    analyze_ticker(ticker)