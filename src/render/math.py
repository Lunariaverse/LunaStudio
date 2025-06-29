import math
from typing import Tuple


def clipValue(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value so it stays within the range [min_value, max_value].

    :param value: The input value to clamp.
    :param min_value: Lower bound.
    :param max_value: Upper bound.
    :return: Clamped value.
    """
    return max(min_value, min(max_value, value))


def linearScale01(value: float, min_value: float, max_value: float) -> float:
    """
    Linearly scale a value from [min_value, max_value] to [0.0, 1.0].

    :param value: Input value.
    :param min_value: Minimum expected input value.
    :param max_value: Maximum expected input value.
    :return: Scaled value in [0.0, 1.0].
    """
    if max_value == min_value:
        return 0.0  # avoid division by zero
    value = clipValue(value, min_value, max_value)
    return (value - min_value) / (max_value - min_value)


def linearScale_11(value: float, min_value: float, max_value: float) -> float:
    """
    Linearly scale a value from [min_value, max_value] to [-1.0, 1.0].

    :param value: Input value.
    :param min_value: Minimum expected input value.
    :param max_value: Maximum expected input value.
    :return: Scaled value in [-1.0, 1.0].
    """
    if max_value == min_value:
        return 0.0  # avoid division by zero
    middle = (max_value + min_value) / 2
    value = clipValue(value, min_value, max_value)
    return (value - middle) / (max_value - middle)


def euclideanDistance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate the Euclidean distance between two 2D points.

    :param p1: First point as (x, y).
    :param p2: Second point as (x, y).
    :return: Distance as float.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
