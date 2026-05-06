"""
stock_type_classifier.py

Enhanced stock classification module that categorizes stocks into Growth, Value, or Blend
based on historical growth metrics, valuation ratios (P/E, PEG), and quality indicators
(ROE, profit margin).

The classification pipeline:
1. Score four growth metrics (EPS, revenue, earnings, quarterly earnings growth).
2. Determine a base growth classification using total growth score.
3. Adjust classification based on quality metrics (ROE, profit margin).
4. Apply valuation overrides using P/E and PEG ratios.

Final Output: "Growth Stock", "Value Stock", or "Blend Stock"

Usage:
    metrics = {
        "eps_growth": 25,
        "revenue_growth": 18,
        "earnings_growth": 22,
        "quarterly_earnings_growth": 12,      # original key, no renaming
        "pe_ratio": 30,
        "peg_ratio": 1.2,
        "roe": 18,
        "profit_margin": 12,
    }
    classifier = StockTypeClassifier(metrics=metrics)
    result = classifier.classify()
"""

from typing import Dict, Any, Optional
import math


class StockTypeClassifier:
    """
    Classifies a stock's type (Growth/Value/Blend) based on fundamental data.

    The classifier uses a scoring system for growth metrics, then refines the
    result with quality and valuation checks.

    Args:
        metrics: Optional flat dictionary containing the stock's fundamental metrics.
                 Expected keys: eps_growth, revenue_growth, earnings_growth,
                 quarterly_earnings_growth, pe_ratio, peg_ratio, roe, profit_margin.
                 If provided, it is stored and used by classify().
    """

    def __init__(self, metrics: Optional[Dict[str, Any]] = None):
        """Initialize classifier with optional flat metrics dictionary."""
        self.metrics = metrics
        self.thresholds = {
            "eps_growth": {"high": 20, "mid": 10},
            "revenue_growth": {"high": 15, "mid": 5},
            "earnings_growth": {"high": 20, "mid": 10},
            "quarterly_earnings_growth": {"high": 15, "mid": 5},   # original key
        }

    # ---------------------------------------------------
    # SAFE VALUE HANDLING
    # ---------------------------------------------------
    def _safe_float(self, value: Optional[float]) -> Optional[float]:
        """
        Convert a value to float safely, handling None, NaN, and inf.

        Args:
            value: Input value (int, float, str, or None).

        Returns:
            Float representation if conversion succeeds and value is finite,
            otherwise None.
        """
        if value is None:
            return None
        try:
            value = float(value)
            if math.isnan(value) or math.isinf(value):
                return None
            return value
        except (ValueError, TypeError):
            return None

    # ---------------------------------------------------
    # SCORING FUNCTION
    # ---------------------------------------------------
    def _score_metric(self, value: Optional[float], high: float, mid: float) -> int:
        """
        Convert a growth metric value into a discrete score.

        Scoring rules:
            - 3: value > high threshold (strong growth)
            - 2: mid < value <= high (moderate growth)
            - 1: 0 < value <= mid (weak positive growth)
            - 0: value <= 0 or missing (negative/no growth)

        Args:
            value: The growth percentage (e.g., 15 for 15%).
            high: High threshold for score 3.
            mid: Mid threshold for score 2.

        Returns:
            Integer score from 0 to 3.
        """
        value = self._safe_float(value)

        if value is None:
            return 0

        # Cap extreme values to avoid distortion from outliers
        value = min(value, 200)

        if value > high:
            return 3
        elif value > mid:
            return 2
        elif value > 0:
            return 1
        else:
            return 0

    # ---------------------------------------------------
    # GROWTH SCORE 
    # ---------------------------------------------------
    def _compute_growth_score(self, metrics: Dict[str, Any]) -> Dict[str, int]:
        """
        Compute individual and total growth scores from a metrics dictionary.

        Args:
            metrics: Flat dictionary with keys: eps_growth, revenue_growth,
                     earnings_growth, quarterly_earnings_growth.

        Returns:
            Dictionary with individual scores and total_score (max 12).
        """
        scores = {
            "eps_score": self._score_metric(
                metrics.get("eps_growth"),
                self.thresholds["eps_growth"]["high"],
                self.thresholds["eps_growth"]["mid"],
            ),
            "revenue_score": self._score_metric(
                metrics.get("revenue_growth"),
                self.thresholds["revenue_growth"]["high"],
                self.thresholds["revenue_growth"]["mid"],
            ),
            "earnings_score": self._score_metric(
                metrics.get("earnings_growth"),
                self.thresholds["earnings_growth"]["high"],
                self.thresholds["earnings_growth"]["mid"],
            ),
            "quarterly_score": self._score_metric(
                metrics.get("quarterly_earnings_growth"),
                self.thresholds["quarterly_earnings_growth"]["high"],
                self.thresholds["quarterly_earnings_growth"]["mid"],
            ),
        }
        scores["total_score"] = sum(scores.values())
        return scores

    # ---------------------------------------------------
    # BASE CLASSIFICATION (PURE GROWTH)
    # ---------------------------------------------------
    def _base_classification(self, total_score: int) -> str:
        """
        Determine initial classification based solely on total growth score.

        Classification rules (max score = 12):
            - total_score >= 9 → "Growth Stock"
            - 5 <= total_score <= 8 → "Blend Stock"
            - total_score < 5 → "Value Stock"

        Args:
            total_score: Sum of individual growth metric scores (0-12).

        Returns:
            One of "Growth Stock", "Blend Stock", or "Value Stock".
        """
        if total_score >= 9:
            return "Growth Stock"
        elif total_score >= 5:
            return "Blend Stock"
        else:
            return "Value Stock"

    # ---------------------------------------------------
    # QUALITY CHECK
    # ---------------------------------------------------
    def _quality_score(self, metrics: Dict[str, Any]) -> int:
        """
        Compute a quality score based on ROE and profit margin.

        Scoring:
            - ROE > 15% → +2 points; ROE > 8% → +1 point
            - Profit margin > 10% → +2 points; > 5% → +1 point
        Maximum score = 4.

        Args:
            metrics: Flat dictionary containing 'roe' and 'profit_margin'.

        Returns:
            Integer quality score (0-4).
        """
        roe = self._safe_float(metrics.get("roe"))
        margin = self._safe_float(metrics.get("profit_margin"))

        score = 0
        if roe is not None:
            if roe > 15:
                score += 2
            elif roe > 8:
                score += 1
        if margin is not None:
            if margin > 10:
                score += 2
            elif margin > 5:
                score += 1
        return score

    # ---------------------------------------------------
    # VALUATION ADJUSTMENT
    # ---------------------------------------------------
    def _valuation_adjustment(self, metrics: Dict[str, Any], classification: str) -> str:
        """
        Override classification based on valuation metrics (P/E and PEG).

        Override rules:
            1. If P/E > 50 AND EPS growth is negative → downgrade to "Value Stock".
            2. If PEG > 2 and currently "Growth Stock" → downgrade to "Blend Stock".
            3. If PEG < 1 and currently "Value Stock" → upgrade to "Blend Stock".

        Args:
            metrics: Flat dictionary containing 'pe_ratio', 'peg_ratio', and 'eps_growth'.
            classification: Current classification before valuation adjustment.

        Returns:
            Possibly adjusted classification string.
        """
        pe = self._safe_float(metrics.get("pe_ratio"))
        peg = self._safe_float(metrics.get("peg_ratio"))
        growth = self._safe_float(metrics.get("eps_growth"))

        if pe is not None and growth is not None:
            if pe > 50 and growth < 0:
                return "Value Stock"
        if peg is not None:
            if peg > 2 and classification == "Growth Stock":
                return "Blend Stock"
            if peg < 1 and classification == "Value Stock":
                return "Blend Stock"
        return classification

    # ---------------------------------------------------
    # PUBLIC CLASSIFICATION METHOD
    # ---------------------------------------------------
    def classify(self, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the full classification pipeline on a stock's fundamental metrics.

        If the classifier was instantiated with metrics, you can call classify()
        without arguments. Otherwise, pass metrics as an argument.

        Args:
            metrics: Flat dictionary of stock metrics. Expected keys:
                - eps_growth (float)
                - revenue_growth (float)
                - earnings_growth (float)
                - quarterly_earnings_growth (float)
                - pe_ratio (float)
                - peg_ratio (float)
                - roe (float)
                - profit_margin (float)

        Returns:
            Dictionary with keys:
                - classification: Final stock type ("Growth Stock", "Value Stock", "Blend Stock")
                - growth_score: Total growth score (0-12)
                - quality_score: Quality score (0-4)
                - details: Individual growth metric scores

        Raises:
            ValueError: If no metrics are available.
        """
        if metrics is None:
            if self.metrics is None:
                raise ValueError("No metrics provided. Pass metrics to classify() or supply metrics in constructor.")
            metrics = self.metrics

        # Step 1: Growth scoring
        growth_scores = self._compute_growth_score(metrics)
        base_class = self._base_classification(growth_scores["total_score"])

        # Step 2: Quality influence
        quality = self._quality_score(metrics)
        if base_class == "Value Stock" and quality >= 3:
            base_class = "Blend Stock"
        if base_class == "Growth Stock" and quality <= 1:
            base_class = "Blend Stock"

        # Step 3: Valuation adjustment
        final_class = self._valuation_adjustment(metrics, base_class)

        return {
            "classification": final_class,
            "growth_score": growth_scores["total_score"],
            "quality_score": quality,
            "details": growth_scores,
        }


# -------------------------------------------------------------------
# Example usage (with flat metrics dictionary, e.g. from data["info"])
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Simulated flat metrics (as you would get from data["info"])
    flat_metrics = {
        "eps_growth": 25,
        "revenue_growth": 18,
        "earnings_growth": 22,
        "quarterly_earnings_growth": 12,   # original key, no renaming
        "pe_ratio": 30,
        "peg_ratio": 1.2,
        "roe": 18,
        "profit_margin": 12,
    }

    # Option 1: Pass metrics at initialization
    classifier = StockTypeClassifier(metrics=flat_metrics)
    result = classifier.classify()   # no argument needed
    from pprint import pprint
    pprint(result)

    # Option 2: Pass metrics directly to classify()
    classifier2 = StockTypeClassifier()
    result2 = classifier2.classify(metrics=flat_metrics)
    pprint(result2)