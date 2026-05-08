"""
Sector‑aware configuration for scoring ranges.

Each sector can override the min/max ranges for specific metrics.
If a sector is not listed, default ranges apply.
"""

# Default ranges used when no sector override exists
DEFAULT_RANGES = {
    # Valuation metrics (inverse normalisation, lower is better)
    "pe_ratio": (5, 60),          # P/E ratio
    "peg_ratio": (0.5, 3),        # PEG ratio
    "price_to_book": (0.5, 10),   # P/B
    "price_to_sales": (0.5, 15),  # P/S
    "ev_to_ebitda": (3, 30),      # EV/EBITDA

    # Financial health (liquidity)
    "current_ratio": (0.5, 4),    # linear, higher is better
    "quick_ratio": (0.2, 3),

    # Profitability (linear, higher is better)
    "roe": (0, 30),               # ROE %
    "roa": (0, 20),               # ROA %
    "profit_margin": (0, 30),
    "operating_margin": (0, 35),
    "gross_margin": (0, 60),
}

# Sector‑specific overrides
SECTOR_RANGES = {
    "Technology": {
        "price_to_book": (0.5, 20),      # Tech can have higher P/B
        "current_ratio": (0.5, 2.5),     # Efficient, low ratios acceptable
        "quick_ratio": (0.2, 2.0),
        "roe": (0, 40),                  # Tech can have very high ROE
        "roa": (0, 25),
    },
    "Financial Services": {
        "price_to_book": (0.5, 3),       # Banks rarely exceed 3x
        "price_to_sales": (0.5, 5),
        "current_ratio": None,           # Not relevant – skip scoring
        "quick_ratio": None,
        "debt_to_equity": (0, 3),        # Use same default but maybe adjust
    },
    "Real Estate": {
        "price_to_book": (0.5, 5),
        "current_ratio": (0.5, 2),
        "quick_ratio": (0.2, 1.5),
        "roe": (0, 15),                  # REITs have lower ROE
        "roa": (0, 10),
    },
    "Energy": {
        "price_to_book": (0.5, 8),
        "pe_ratio": (5, 50),
        "current_ratio": (0.5, 3),
    },
    "Healthcare": {
        "price_to_book": (0.5, 15),
        "pe_ratio": (5, 70),
        "current_ratio": (0.5, 4),
    },
    "Consumer Cyclical": {
        "price_to_book": (0.5, 12),
        "current_ratio": (0.5, 3),
    },
    "Consumer Defensive": {
        "price_to_book": (0.5, 10),
        "current_ratio": (0.5, 3),
        "roe": (0, 35),
    },
    "Industrials": {
        "price_to_book": (0.5, 10),
        "current_ratio": (0.5, 3),
    },
    "Utilities": {
        "price_to_book": (0.5, 8),
        "pe_ratio": (5, 40),
        "current_ratio": (0.5, 2.5),
        "roe": (0, 20),
    },
    "Basic Materials": {
        "price_to_book": (0.5, 8),
        "current_ratio": (0.5, 3),
    },
    "Communication Services": {
        "price_to_book": (0.5, 15),
        "current_ratio": (0.5, 3),
    },
    "Crypto": {
        # High risk, adjust valuations
        "price_to_book": (0.5, 30),
        "pe_ratio": (5, 100),
    },
    "Biotechnology": {
        "price_to_book": (0.5, 25),
        "pe_ratio": (5, 100),
        "current_ratio": (0.5, 5),
    },
    "Cannabis": {
        "price_to_book": (0.5, 20),
        "pe_ratio": (5, 80),
    },
}

# High‑risk sectors for penalty in RiskAdjustments
HIGH_RISK_SECTORS = [
    "Biotechnology",
    "Crypto",
    "Cannabis",
    "Energy",          # volatile
    "Basic Materials", # cyclical
]

def get_range(sector: str, metric: str, default_min: float, default_max: float):
    """
    Return (min, max) for a given sector and metric.
    If sector overrides exist and metric is set to None, returns (None, None) → skip.
    """
    if sector and sector in SECTOR_RANGES:
        overrides = SECTOR_RANGES[sector]
        if metric in overrides:
            val = overrides[metric]
            if val is None:
                return (None, None)
            if isinstance(val, tuple):
                return val
    # Fallback to default if available
    if metric in DEFAULT_RANGES:
        return DEFAULT_RANGES[metric]
    return (default_min, default_max)