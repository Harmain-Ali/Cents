"""
Sector‑aware thresholds for human interpretation.
Wraps the existing sector_config (assuming it's in src.scoring.config).
"""

from src.scoring.config.sector_config import get_interpretation as _get_interpretation

def get_thresholds(sector: str, metric: str) -> dict:
    """
    Returns thresholds dict for a metric, sector‑aware.
    Example: {"cheap": 12, "fair": 20, "expensive": 25}
    """
    return _get_interpretation(sector, metric)