from typing import Union

Number = Union[int, float]

def multiply(a: Number, b: Number) -> float:
    """Returns product of two numbers."""
    return float(a * b)

def add(*loads: Number) -> float:
    """Sum multiple loads (kN, kN/m², etc.)."""
    return float(sum(loads))

def subtract(a: Number, b: Number) -> float:
    """Subtract one load from another."""
    return float(a - b)

def divide(total: Number, divisor: Number) -> float:
    """Divide total load by area or span length."""
    if divisor == 0:
        raise ValueError("Divisor cannot be zero.")
    return float(total / divisor)