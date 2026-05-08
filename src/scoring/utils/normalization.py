def clamp(value, min_val, max_val):
    """
    Restrict a value to a specified range.

    Args:
        value (float or None): The value to clamp.
        min_val (float): Minimum allowed value.
        max_val (float): Maximum allowed value.

    Returns:
        float: The clamped value. If value is None, returns None.
    """
    if value is None:
        return None
    return max(min_val, min(value, max_val))


def normalize_linear(value, min_val, max_val):
    """
    Normalize a value to a 0–100 scale using linear mapping.

    Values below min_val are clamped to min_val (score 0).
    Values above max_val are clamped to max_val (score 100).

    Args:
        value (float or None): The input value to normalize.
        min_val (float): Minimum reference value (maps to 0).
        max_val (float): Maximum reference value (maps to 100).

    Returns:
        float: Normalized score from 0 to 100. If value is None, returns 50.0 (neutral).
    """
    if value is None:
        return 50.0

    value = clamp(value, min_val, max_val)

    return ((value - min_val) / (max_val - min_val)) * 100


def normalize_inverse(value, min_val, max_val):
    """
    Normalize a value to a 0–100 scale with inverse relationship.

    Higher input values produce lower scores (inverse linear mapping).
    Values below min_val map to 100, above max_val map to 0.

    Args:
        value (float or None): The input value to normalize (lower is better).
        min_val (float): Minimum reference value (maps to 100).
        max_val (float): Maximum reference value (maps to 0).

    Returns:
        float: Normalized score from 0 to 100. If value is None, returns 50.0 (neutral).
    """
    if value is None:
        return 50.0

    value = clamp(value, min_val, max_val)

    return 100 - (((value - min_val) / (max_val - min_val)) * 100)