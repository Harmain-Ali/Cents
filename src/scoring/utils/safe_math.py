import math


def safe_float(value):

    try:
        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return None

        return value

    except:
        return None