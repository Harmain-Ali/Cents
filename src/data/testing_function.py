# test_pipeline.py

import pprint

from src.data.data_fetcher import DataFetcher
from src.data.metrics_engine import get_final_stock_data


def run_test(ticker: str):
    print(f"\n=== Testing for ticker: {ticker} ===\n")

    # -----------------------------------
    # STEP 1: VALIDATE TICKER
    # -----------------------------------
    is_valid = DataFetcher.validate_ticker_static(ticker)

    if not is_valid:
        print(f"❌ Invalid ticker: {ticker}")
        return

    print("✅ Ticker is valid\n")

    # -----------------------------------
    # STEP 2: FETCH DATA
    # -----------------------------------
    fetcher = DataFetcher(ticker)
    data = fetcher.get_full_stock_data()

    if not data.get("success"):
        print("⚠️ Partial errors during fetch:")
        pprint.pprint(data.get("errors"))
        print()

    print("✅ Data fetched successfully\n")

    # -----------------------------------
    # STEP 3: COMPUTE METRICS
    # -----------------------------------
    enriched_data = get_final_stock_data(data)

    print("✅ Metrics computed successfully\n")

    # -----------------------------------
    # STEP 4: PRINT FINAL STRUCTURE
    # -----------------------------------
    print("========== FINAL DATA STRUCTURE ==========\n")

    _print_structure(enriched_data)

    print("\n========== FULL DATA (VALUES) ==========\n")

    pprint.pprint(enriched_data, depth=3, compact=False)


# -----------------------------------
# HELPER: PRINT STRUCTURE ONLY
# -----------------------------------

def _print_structure(data, indent=0):
    spacing = " " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{spacing}{key}:")
            _print_structure(value, indent + 4)

    elif hasattr(data, "shape"):  # pandas DataFrame / Series
        print(f"{spacing}<{type(data).__name__} shape={data.shape}>")

    else:
        print(f"{spacing}{type(data).__name__}")


# -----------------------------------
# RUN TEST
# -----------------------------------

if __name__ == "__main__":
    run_test("AAPL")   # change ticker here