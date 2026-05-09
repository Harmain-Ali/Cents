from src.scoring.weights import WEIGHTS
from src.scoring.recommendation import get_recommendation
from src.scoring.adjustments import RiskAdjustments
from src.scoring.forward_adjustments import ForwardAdjustments
from src.scoring.scorers.valuation_scorer import ValuationScorer
from src.scoring.scorers.profitability_scorer import ProfitabilityScorer
from src.scoring.scorers.growth_scorer import GrowthScorer
from src.scoring.scorers.financial_health_scorer import FinancialHealthScorer
from src.scoring.scorers.dividend_scorer import DividendScorer
from src.scoring.scorers.technical_scorer import TechnicalScorer
from src.scoring.utils.metric_standardizer import MetricStandardizer
from src.scoring.confidence_calculator import ConfidenceCalculator


class StockScorer:
    """
    Orchestrates the scoring of a stock across multiple fundamental and technical categories.

    The final score is a weighted combination of six category scores:
        - valuation
        - profitability
        - growth
        - financial_health
        - dividend
        - technical

    Weights are determined by the stock type (e.g., 'growth', 'value', 'dividend', 'blend')
    using the WEIGHTS mapping. After the weighted sum, `RiskAdjustments` apply historical
    penalties/bonuses, then `ForwardAdjustments` apply forward‑looking adjustments,
    and the final score is mapped to a textual recommendation.

    Attributes:
        data (dict): Full stock data following the standard schema.
        stock_type (str): Type of stock used to select weighting scheme.
        weights (dict): Category weights for the given stock_type.
    """

    def __init__(self, data, stock_type):
        self.data = MetricStandardizer.standardize(data)
        self.stock_type = stock_type
        self.weights = WEIGHTS[stock_type]

    def score(self):
        """
        Calculate the final stock score and recommendation.

        Returns:
            dict: Contains:
                - stock_type (str)
                - category_scores (dict with each category's score, weight, and weighted_score)
                - raw_score (float, weighted sum before adjustments)
                - final_score (float, adjusted and clipped to 0–100)
                - recommendation (str, e.g., "Buy", "Hold", "Sell")
        """
        # Calculate individual category scores
        valuation = ValuationScorer(self.data).calculate()
        profitability = ProfitabilityScorer(self.data).calculate()
        growth = GrowthScorer(self.data).calculate()
        health = FinancialHealthScorer(self.data).calculate()
        dividend = DividendScorer(self.data).calculate()
        technical = TechnicalScorer(self.data).calculate()

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
            weighted = result["score"] * self.weights[category]
            result["weight"] = self.weights[category]
            result["weighted_score"] = round(weighted, 2)
            final_score += weighted

        # Apply risk adjustments (historical / current factors)
        adjusted_score = RiskAdjustments.apply(self.data, final_score)
        if adjusted_score is None:
            adjusted_score = final_score  # fallback to raw weighted sum

        # Apply forward‑looking adjustments (analyst estimates, price targets, etc.)
        adjusted_score = ForwardAdjustments.apply(self.data, adjusted_score)
        if adjusted_score is None:
            adjusted_score = final_score  # fallback again

        # Clip to valid range [0, 100]
        adjusted_score = round(max(0, min(100, adjusted_score)), 2)

        recommendation = get_recommendation(adjusted_score)

        confidence = ConfidenceCalculator.calculate(self.data, category_scores)

        return {
            "stock_type": self.stock_type,
            "category_scores": category_scores,
            "raw_score": round(final_score, 2),
            "final_score": adjusted_score,
            "recommendation": recommendation,
            "confidence": confidence, 
        }