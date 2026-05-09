from pprint import pprint

from src.data.data_fetcher import DataFetcher
from src.data.metrics_engine import get_final_stock_data


from src.processes.stock_type_classifier import (
    StockTypeClassifier
)

from src.scoring.stock_scorer import StockScorer


ticker = "aapl"

print(f"\n=== Testing for ticker: {ticker} ===\n")

    # -----------------------------------
    # STEP 1: VALIDATE TICKER
    # -----------------------------------
is_valid = DataFetcher.validate_ticker_static(ticker)

if not is_valid:
    print(f"❌ Invalid ticker: {ticker}")
    

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
data = get_final_stock_data(data)

print("✅ Metrics computed successfully\n")


# ------------------------------------------------
# CLASSIFY STOCK TYPE
# ------------------------------------------------

classifier = StockTypeClassifier(metrics=data["info"])
classification = classifier.classify() 

stock_type = classification["classification"]

# ------------------------------------------------
# SCORE STOCK
# ------------------------------------------------

scorer = StockScorer(
    data=data,
    stock_type=stock_type
)

result = scorer.score()

# ------------------------------------------------
# PRINT RESULTS
# ------------------------------------------------

pprint(result)