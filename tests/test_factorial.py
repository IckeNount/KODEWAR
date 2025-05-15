import pytest
import importlib.util
import sys
import os
from pathlib import Path

def load_submission():
    """Load the submission file as a module."""
    submission_path = os.environ.get('SUBMISSION_FILE')
    if not submission_path:
        pytest.fail("SUBMISSION_FILE environment variable not set")
    
    spec = importlib.util.spec_from_file_location("submission", submission_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["submission"] = module
    spec.loader.exec_module(module)
    return module

def test_factorial_implementation():
    """Test the factorial function implementation."""
    submission = load_submission()
    
    # Test cases
    test_cases = [
        (0, 1),      # factorial(0) should be 1
        (1, 1),      # factorial(1) should be 1
        (5, 120),    # factorial(5) should be 120
        (10, 3628800) # factorial(10) should be 3628800
    ]
    
    for input_num, expected in test_cases:
        result = submission.factorial(input_num)
        assert result == expected, f"factorial({input_num}) should be {expected}, but got {result}"

def test_factorial_negative():
    """Test that factorial raises ValueError for negative numbers."""
    submission = load_submission()
    
    with pytest.raises(ValueError):
        submission.factorial(-1)

def test_factorial_large_number():
    """Test factorial with a large number."""
    submission = load_submission()
    
    result = submission.factorial(20)
    expected = 2432902008176640000
    assert result == expected, f"factorial(20) should be {expected}, but got {result}" 