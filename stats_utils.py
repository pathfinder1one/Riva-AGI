import statistics
from typing import List, Dict, Union


def get_summary_statistics(data: List[Union[int, float]]) -> Dict[str, float]:
    """Computes summary statistics for a given list of numerical data.

    Args:
        data: A list of integers or floats.

    Returns:
        A dictionary containing the count, mean, median, variance,
        standard deviation, minimum, and maximum of the data.

    Raises:
        ValueError: If the data list is empty.
        TypeError: If the data contains non-numerical values.
    """
    if not data:
        raise ValueError("The data list cannot be empty.")

    if not all(isinstance(x, (int, float)) for x in data):
        raise TypeError("All elements in the data list must be numbers.")

    n = len(data)

    if n == 1:
        return {
            "count": float(n),
            "mean": float(data[0]),
            "median": float(data[0]),
            "variance": 0.0,
            "standard_deviation": 0.0,
            "min": float(data[0]),
            "max": float(data[0]),
        }

    return {
        "count": float(n),
        "mean": float(statistics.mean(data)),
        "median": float(statistics.median(data)),
        "variance": float(statistics.variance(data)),
        "standard_deviation": float(statistics.stdev(data)),
        "min": float(min(data)),
        "max": float(max(data)),
    }