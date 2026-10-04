"""Tests for calculator.py"""

import pytest
from calculator import Calculator, calculate


def test_calculator_chaining():
    calc = Calculator(10)
    res = calc.add(5).subtract(3).multiply(2).divide(4).power(2).result()
    # ((10 + 5 - 3) * 2 / 4) ** 2 = (12 * 2 / 4) ** 2 = 6 ** 2 = 36.0
    assert res == 36.0


def test_calculator_division_by_zero():
    calc = Calculator(10)
    with pytest.raises(ValueError, match="Division by zero"):
        calc.divide(0)


def test_calculate_expression_basic():
    assert calculate("2 + 2") == 4
    assert calculate("10 - 3 * 2") == 4
    assert calculate("(10 - 3) * 2") == 14
    assert calculate("2 ^ 3") == 8
    assert calculate("5 / 2") == 2.5


def test_calculate_unary_operations():
    assert calculate("-5 + 3") == -2
    assert calculate("+5 - 3") == 2


def test_calculate_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("10 / 0")


def test_calculate_invalid_expression():
    with pytest.raises(ValueError):
        calculate("invalid_expr()")
