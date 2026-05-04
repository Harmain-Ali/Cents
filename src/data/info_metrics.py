# info_metrics.py

from typing import Dict, Any


def compute_info_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adds EPS growth inside INFO section
    """

    info = data.get("info", {})

    if not info:
        return data

    trailing_eps = info.get("trailing_eps")
    forward_eps = info.get("forward_eps")

    if (
        trailing_eps is not None
        and forward_eps is not None
        and trailing_eps != 0
    ):
        eps_growth = ((forward_eps - trailing_eps) / abs(trailing_eps)) * 100
    else:
        eps_growth = None

    # Inject into INFO
    info["eps_growth"] = eps_growth

    return data