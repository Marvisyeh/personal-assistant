from langchain.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers together"""
    return a - b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@tool
def divide(a: int, b: int) -> float:
    """Divide two numbers together"""
    return a / b
