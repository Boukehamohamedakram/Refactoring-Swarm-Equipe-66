def is_within_range(value: float | int) -> bool:
    """
    Check if the given value is within the range (0, 100).

    Args:
        value: A numeric value to check against the range (0, 100).

    Returns:
        bool: True if the value is greater than 0 and less than 100, False otherwise.
    """
    return 0 < value < 100