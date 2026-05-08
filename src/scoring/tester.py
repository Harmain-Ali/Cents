from pprint import pprint

from src.data.fetcher import DataFetcher

from src.classification.stock_type_classifier import (
    StockTypeClassifier
)

from src.scoring.stock_scorer import StockScorer


ticker = "AAPL"

# ------------------------------------------------
# FETCH DATA
# ------------------------------------------------

fetcher = DataFetcher()

data = fetcher.fetch(ticker)

# ------------------------------------------------
# CLASSIFY STOCK TYPE
# ------------------------------------------------

info = data["INFO"]

classifier_metrics = {

    "eps_growth": info.get("EPS GROWTH"),

    "revenue_growth": info.get("REVENUE GROWTH"),

    "earnings_growth": info.get("EARNINGS GROWTH"),

    "quarterly_earnings_growth":
        info.get("QUARTERLY EARNING GROWTH"),

    "pe_ratio": info.get("PE RATIO"),

    "peg_ratio": info.get("PEG RATIO"),

    "roe": info.get("ROE"),

    "profit_margin": info.get("PROFIT MARGIN"),
}

classifier = StockTypeClassifier()

classification = classifier.classify(
    classifier_metrics
)

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