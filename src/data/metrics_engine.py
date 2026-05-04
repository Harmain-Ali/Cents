
# metrics_engine.py

from typing import Dict, Any

from .info_metrics import compute_info_metrics
from .technical_metrics import compute_technical_metrics
from .dividend_metrics import compute_dividend_metrics
from .growth_metrics import compute_growth_metrics


def get_final_stock_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs all metric modules and enriches original data
    """

    data = compute_info_metrics(data)
    data = compute_technical_metrics(data)
    data = compute_dividend_metrics(data)
    data = compute_growth_metrics(data)

    return data




    


    