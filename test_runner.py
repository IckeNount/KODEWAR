#!/usr/bin/env python3
import os
import sys
import pytest
import json
from typing import Dict, Any

def run_tests(test_file: str, submission_file: str) -> Dict[str, Any]:
    """
    Run tests for a given submission file.
    
    Args:
        test_file: Path to the test file
        submission_file: Path to the submission file
        
    Returns:
        Dictionary containing test results
    """
    try:
        # Set the submission file path as an environment variable
        os.environ['SUBMISSION_FILE'] = submission_file
        
        # Run pytest and capture results
        result = pytest.main([
            test_file,
            '-v'
        ])
        
        return {
            'success': result == 0,
            'exit_code': result,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'exit_code': 1,
            'error': str(e)
        }

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_runner.py <test_file> <submission_file>")
        sys.exit(1)
        
    test_file = sys.argv[1]
    submission_file = sys.argv[2]
    
    if not os.path.exists(test_file):
        print(f"Error: Test file {test_file} not found")
        sys.exit(1)
        
    if not os.path.exists(submission_file):
        print(f"Error: Submission file {submission_file} not found")
        sys.exit(1)
    
    results = run_tests(test_file, submission_file)
    print(json.dumps(results, indent=2))
    
    sys.exit(0 if results['success'] else 1)

if __name__ == '__main__':
    main() 