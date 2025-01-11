# mathlib/operations.py

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def multi(a, b):
    return a * b

def div(a, b):
    if b != 0:
        return a / b
    else:
        raise ValueError("Division by zero is not allowed.")
