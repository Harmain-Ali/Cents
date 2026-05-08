def clamp(value, min_val, max_val):

    return max(min_val, min(value, max_val))


def normalize_linear(value, min_val, max_val):

    if value is None:
        return 50.0

    value = clamp(value, min_val, max_val)

    return (
        (value - min_val) /
        (max_val - min_val)
    ) * 100


def normalize_inverse(value, min_val, max_val):

    if value is None:
        return 50.0

    value = clamp(value, min_val, max_val)

    return 100 - (
        ((value - min_val) /
        (max_val - min_val)) * 100
    )