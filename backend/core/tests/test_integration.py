import pytest
import json
import time
import requests
from pathlib import Path
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import CodeSubmission
from ..tasks import run_code_task
from ..sandbox import SandboxManager

class IntegrationTest(TestCase):
    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        self.sandbox = SandboxManager()
        self.submission_url = reverse('code-submission')
        self.status_url = reverse('submission-status')
        
    def test_full_submission_flow(self):
        """Test the complete flow from submission to result."""
        # Prepare test code
        code = 'print("Hello, World!")'
        data = {
            'code': code,
            'language': 'python',
            'test_cases': []
        }
        
        # Submit code
        response = self.client.post(self.submission_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        submission_id = response.data['submission_id']
        
        # Wait for task completion
        max_retries = 10
        for _ in range(max_retries):
            response = self.client.get(f"{self.status_url}?submission_id={submission_id}")
            if response.data['status'] != 'pending':
                break
            time.sleep(1)
            
        # Verify result
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['output'].strip(), 'Hello, World!')
        
    def test_security_breakout_attempts(self):
        """Test various security breakout attempts."""
        breakout_tests = [
            {
                'name': 'file_system_access',
                'code': 'open("/etc/passwd").read()',
                'expected_error': 'Permission denied'
            },
            {
                'name': 'network_access',
                'code': 'import socket; socket.socket().connect(("google.com", 80))',
                'expected_error': 'Network is disabled'
            },
            {
                'name': 'process_creation',
                'code': 'import os; os.system("ls")',
                'expected_error': 'Operation not permitted'
            },
            {
                'name': 'memory_exhaustion',
                'code': 'a = "x" * (1024 * 1024 * 1024)',  # 1GB string
                'expected_error': 'Memory limit exceeded'
            }
        ]
        
        for test in breakout_tests:
            with self.subTest(test['name']):
                data = {
                    'code': test['code'],
                    'language': 'python',
                    'test_cases': []
                }
                
                response = self.client.post(self.submission_url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
                submission_id = response.data['submission_id']
                
                # Wait for task completion
                max_retries = 10
                for _ in range(max_retries):
                    response = self.client.get(f"{self.status_url}?submission_id={submission_id}")
                    if response.data['status'] != 'pending':
                        break
                    time.sleep(1)
                    
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['status'], 'error')
                self.assertIn(test['expected_error'], response.data['error'])
                
    def test_resource_limits(self):
        """Test resource limit enforcement."""
        # Test CPU limit
        cpu_test = '''
import time
while True:
    pass
'''
        data = {
            'code': cpu_test,
            'language': 'python',
            'test_cases': []
        }
        
        response = self.client.post(self.submission_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        submission_id = response.data['submission_id']
        
        # Wait for task completion
        max_retries = 10
        for _ in range(max_retries):
            response = self.client.get(f"{self.status_url}?submission_id={submission_id}")
            if response.data['status'] != 'pending':
                break
            time.sleep(1)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('CPU time limit exceeded', response.data['error'])
        
    def test_concurrent_submissions(self):
        """Test handling of concurrent submissions."""
        # Submit multiple tasks simultaneously
        submissions = []
        for i in range(5):
            code = f'print("Task {i}")'
            data = {
                'code': code,
                'language': 'python',
                'test_cases': []
            }
            response = self.client.post(self.submission_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
            submissions.append(response.data['submission_id'])
            
        # Wait for all tasks to complete
        results = []
        for submission_id in submissions:
            max_retries = 10
            for _ in range(max_retries):
                response = self.client.get(f"{self.status_url}?submission_id={submission_id}")
                if response.data['status'] != 'pending':
                    results.append(response.data)
                    break
                time.sleep(1)
                
        # Verify all tasks completed successfully
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertEqual(result['status'], 'success')
            
    def test_error_handling(self):
        """Test error handling in the submission flow."""
        error_tests = [
            {
                'name': 'syntax_error',
                'code': 'print("Hello"',
                'expected_error': 'SyntaxError'
            },
            {
                'name': 'runtime_error',
                'code': '1/0',
                'expected_error': 'ZeroDivisionError'
            },
            {
                'name': 'invalid_language',
                'code': 'print("Hello")',
                'language': 'invalid',
                'expected_error': 'Unsupported language'
            }
        ]
        
        for test in error_tests:
            with self.subTest(test['name']):
                data = {
                    'code': test['code'],
                    'language': test.get('language', 'python'),
                    'test_cases': []
                }
                
                response = self.client.post(self.submission_url, data, format='json')
                if 'expected_error' in test:
                    self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
                    submission_id = response.data['submission_id']
                    
                    # Wait for task completion
                    max_retries = 10
                    for _ in range(max_retries):
                        response = self.client.get(f"{self.status_url}?submission_id={submission_id}")
                        if response.data['status'] != 'pending':
                            break
                        time.sleep(1)
                        
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertEqual(response.data['status'], 'error')
                    self.assertIn(test['expected_error'], response.data['error'])
                else:
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    
    def test_test_case_execution(self):
        """Test execution of code with test cases."""
        code = '''
def add(a, b):
    return a + b
'''
        test_cases = [
            {
                'input': {'a': 1, 'b': 2},
                'expected': 3
            },
            {
                'input': {'a': -1, 'b': 1},
                'expected': 0
            }
        ]
        
        data = {
            'code': code,
            'language': 'python',
            'test_cases': test_cases
        }
        
        response = self.client.post(self.submission_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        submission_id = response.data['submission_id']
        
        # Wait for task completion
        max_retries = 10
        for _ in range(max_retries):
            response = self.client.get(f"{self.status_url}?submission_id={submission_id}")
            if response.data['status'] != 'pending':
                break
            time.sleep(1)
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['test_results']), 2)
        for result in response.data['test_results']:
            self.assertTrue(result['passed']) 