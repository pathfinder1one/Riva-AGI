#!/usr/bin/env python3
"""
Module: calculator.py
Author: Senior Coder Agent (Riva-AGI)
Description: A robust command-line calculator for basic arithmetic operations.
"""

import sys

def add(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Returns the difference between two numbers."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Returns the product of two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Returns the quotient of two numbers. Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("Error: Division by zero is not allowed.")
    return a / b

class Calculator:
    """Fluent chaining calculator."""
    def __init__(self, initial_value: float = 0.0):
        self._value = float(initial_value)

    def add(self, n: float) -> "Calculator":
        self._value += float(n)
        return self

    def subtract(self, n: float) -> "Calculator":
        self._value -= float(n)
        return self

    def multiply(self, n: float) -> "Calculator":
        self._value *= float(n)
        return self

    def divide(self, n: float) -> "Calculator":
        if n == 0:
            raise ValueError("Division by zero")
        self._value /= float(n)
        return self

    def power(self, n: float) -> "Calculator":
        self._value = self._value ** float(n)
        return self

    def result(self) -> float:
        return self._value


def calculate(expression: str) -> float:
    """Safely evaluates a basic math expression string supporting +, -, *, /, ^, parentheses."""
    import ast
    import operator

    expr = expression.replace("^", "**").strip()

    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    try:
        parsed = ast.parse(expr, mode='eval')
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}") from e

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in operators:
                if op_type is ast.Div and right == 0:
                    raise ZeroDivisionError("division by zero")
                return operators[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in operators:
                return operators[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")
        else:
            raise ValueError(f"Unsupported expression element: {type(node)}")

    return _eval(parsed)

def get_number(prompt: str) -> float:
    """Helper function to safely get a float input from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    """Main function to run the interactive calculator loop."""
    print("========================================")
    print("      Riva-AGI Python Calculator        ")
    print("========================================")
    
    while True:
        print("\nSelect operation:")
        print("1. Add (+)")
        print("2. Subtract (-)")
        print("3. Multiply (*)")
        print("4. Divide (/)")
        print("5. Exit")

        choice = input("Enter choice (1/2/3/4/5): ").strip()

        if choice == '5':
            print("Exiting calculator. Goodbye!")
            sys.exit(0)

        if choice in ('1', '2', '3', '4'):
            num1 = get_number("Enter first number: ")
            num2 = get_number("Enter second number: ")

            try:
                if choice == '1':
                    result = add(num1, num2)
                    op = '+'
                elif choice == '2':
                    result = subtract(num1, num2)
                    op = '-'
                elif choice == '3':
                    result = multiply(num1, num2)
                    op = '*'
                elif choice == '4':
                    result = divide(num1, num2)
                    op = '/'

                print(f"\nResult: {num1} {op} {num2} = {result}")

            except ValueError as e:
                print(f"\n{e}")
        else:
            print("\nInvalid choice! Please select a valid option from the menu.")

if __name__ == "__main__":
    main()