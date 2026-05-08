# info_metrics.py

from typing import Dict, Any


def compute_info_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute EPS growth from trailing and forward EPS values.

    This function reads `trailing_eps` and `forward_eps` from `data["info"]`
    and calculates the percentage growth:
        eps_growth = ((forward_eps - trailing_eps) / abs(trailing_eps)) * 100.

    The result is stored in `data["info"]["eps_growth"]`. If either value is
    missing or trailing EPS is zero, `eps_growth` is set to None.

    Args:
        data (Dict[str, Any]): Stock data dictionary containing an "info" key.
            The "info" dict should optionally have "trailing_eps" and "forward_eps".

    Returns:
        Dict[str, Any]: The same data dictionary with `info["eps_growth"]` added
        (float or None).
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