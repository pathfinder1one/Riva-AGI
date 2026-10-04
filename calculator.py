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