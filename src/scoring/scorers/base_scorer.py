from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseScorer(ABC):
    """
    Abstract base class for all scoring modules.

    Subclasses must implement the `calculate` method to compute a score
    based on the stock data provided at initialization.

    Attributes:
        data (Dict[str, Any]): The enriched stock data dictionary following
            the standard schema (with keys: info, history, dividends, financials).
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the scorer with stock data.

        Args:
            data (Dict[str, Any]): Stock data dictionary containing at least
                the fields required by the specific scorer implementation.
        """
        self.data = data

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Compute the score for the stock.

        Subclasses must override this method to implement their specific
        scoring logic.

        Returns:
            Dict[str, Any]: A dictionary containing at least:
                - "score": float (0–100)
                - "details": dict with component scores or additional info.
        """
        pass