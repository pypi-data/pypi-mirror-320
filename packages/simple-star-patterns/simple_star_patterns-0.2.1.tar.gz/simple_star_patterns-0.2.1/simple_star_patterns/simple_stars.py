# simple_stars.py

"""Module for generating various star patterns."""

def print_triangle(size: int, symbol: str = '*') -> None:
    """Print a right-angled triangle pattern.
    
    Args:
        size: Number of rows in the triangle
        symbol: Character to use for the pattern
    """
    for i in range(1, size + 1):
        print(symbol * i)

def print_inverted_triangle(size: int, symbol: str = '*') -> None:
    """Print an inverted triangle pattern.
    
    Args:
        size: Number of rows in the triangle
        symbol: Character to use for the pattern
    """
    for i in range(size, 0, -1):
        print(symbol * i)

def print_pyramid(size: int, symbol: str = '*') -> None:
    """Print a pyramid pattern.
    
    Args:
        size: Number of rows in the pyramid
        symbol: Character to use for the pattern
    """
    for i in range(size):
        spaces = ' ' * (size - i - 1)
        stars = symbol * (2 * i + 1)
        print(f"{spaces}{stars}")

def print_pattern(pattern: str, size: int, symbol: str = '*') -> None:
    """Print the specified pattern.
    
    Args:
        pattern: Type of pattern ('triangle', 'inverted_triangle', 'pyramid')
        size: Number of rows in the pattern
        symbol: Character to use for the pattern
    """
    if size <= 0:
        print("Size must be a positive number.")
        return

    if len(symbol) != 1:
        print("Symbol must be a single character.")
        return

    patterns = {
        'triangle': print_triangle,
        'inverted_triangle': print_inverted_triangle,
        'pyramid': print_pyramid
    }

    if pattern not in patterns:
        print(f"Unknown pattern: {pattern}")
        print(f"Available patterns: {', '.join(patterns.keys())}")
        return

    patterns[pattern](size, symbol)