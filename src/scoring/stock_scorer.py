from src.scoring.weights import WEIGHTS

from src.scoring.recommendation import (
    get_recommendation
)

from src.scoring.adjustments import (
    RiskAdjustments
)

from src.scoring.scorers.valuation_scorer import (
    ValuationScorer
)

from src.scoring.scorers.profitability_scorer import (
    ProfitabilityScorer
)

from src.scoring.scorers.growth_scorer import (
    GrowthScorer
)

from src.scoring.scorers.financial_health_scorer import (
    FinancialHealthScorer
)

from src.scoring.scorers.dividend_scorer import (
    DividendScorer
)

from src.scoring.scorers.technical_scorer import (
    TechnicalScorer
)


class StockScorer:

    def __init__(self, data, stock_type):

        self.data = data
        self.stock_type = stock_type

        self.weights = WEIGHTS[stock_type]

    def score(self):

        valuation = ValuationScorer(
            self.data
        ).calculate()

        profitability = ProfitabilityScorer(
            self.data
        ).calculate()

        growth = GrowthScorer(
            self.data
        ).calculate()

        health = FinancialHealthScorer(
            self.data
        ).calculate()

        dividend = DividendScorer(
            self.data
        ).calculate()

        technical = TechnicalScorer(
            self.data
        ).calculate()

        category_scores = {

            "valuation": valuation,

            "profitability": profitability,

            "growth": growth,

            "financial_health": health,

            "dividend": dividend,

            "technical": technical
        }

        final_score = 0

        for category, result in category_scores.items():

            weighted = (
                result["score"] *
                self.weights[category]
            )

            result["weight"] = (
                self.weights[category]
            )

            result["weighted_score"] = round(
                weighted,
                2
            )

            final_score += weighted

        adjusted_score = RiskAdjustments.apply(
            self.data,
            final_score
        )

        adjusted_score = round(
            max(0, min(100, adjusted_score)),
            2
        )

        recommendation = get_recommendation(
            adjusted_score
        )

        return {

            "stock_type": self.stock_type,

            "category_scores": category_scores,

            "raw_score": round(
                final_score,
                2
            ),

            "final_score": adjusted_score,

            "recommendation": recommendation
        }