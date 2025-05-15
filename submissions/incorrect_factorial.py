def factorial(n):
    """
    An incorrect implementation of factorial that will fail some tests.
    """
    if n < 0:
        return 0  # Incorrect: should raise ValueError
    
    if n == 0:
        return 0  # Incorrect: should return 1
    
    result = 1
    for i in range(1, n + 1):  # Incorrect: starts from 1 instead of 2
        result *= i
    return result 