import os
import time
import json
import pytest
import requests
from typing import Dict, Any, Generator
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestCase:
    name: str
    code: str
    expected_status: str
    expected_tests_passed: int
    timeout: int = 30
    memory_limit: int = 512

class TestSubmissionSystem:
    """Test suite for the code submission system."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.auth_token = os.getenv("AUTH_TOKEN", "your-auth-token")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
    @pytest.fixture
    def test_cases(self) -> Generator[list[TestCase], None, None]:
        """Provide test cases for the submission system."""
        yield [
            TestCase(
                name="Basic Hello World",
                code="""
def hello_world(name: str = "World") -> str:
    return f"Hello, {name}!"
""",
                expected_status="success",
                expected_tests_passed=5
            ),
            TestCase(
                name="Timeout Test",
                code="""
def hello_world(name: str = "World") -> str:
    import time
    time.sleep(40)  # Should timeout
    return f"Hello, {name}!"
""",
                expected_status="error",
                expected_tests_passed=0,
                timeout=5
            ),
            TestCase(
                name="Memory Limit Test",
                code="""
def hello_world(name: str = "World") -> str:
    # Create a large list to exceed memory limit
    big_list = [0] * (1024 * 1024 * 1024)  # 1GB of memory
    return f"Hello, {name}!"
""",
                expected_status="error",
                expected_tests_passed=0,
                memory_limit=128
            ),
            TestCase(
                name="Syntax Error Test",
                code="""
def hello_world(name: str = "World") -> str:
    return f"Hello, {name}!"  # Missing closing quote
""",
                expected_status="error",
                expected_tests_passed=0
            )
        ]
    
    def submit_code(self, test_case: TestCase) -> Dict[str, Any]:
        """Submit code to the API."""
        payload = {
            "code": test_case.code,
            "test_file": "test_hello.py",
            "timeout": test_case.timeout,
            "memory_limit": test_case.memory_limit,
            "metadata": {
                "test_type": "automated_test",
                "test_case": test_case.name,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/submit/",
            headers=self.headers,
            json=payload
        )
        
        assert response.status_code == 202, f"Submission failed: {response.text}"
        return response.json()
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task."""
        response = requests.get(
            f"{self.base_url}/api/task/{task_id}/",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Status check failed: {response.text}"
        return response.json()
    
    def wait_for_task_completion(self, task_id: str, max_attempts: int = 10) -> Dict[str, Any]:
        """Wait for a task to complete."""
        for _ in range(max_attempts):
            status_data = self.get_task_status(task_id)
            if status_data["status"] in ["completed", "failed"]:
                return status_data
            time.sleep(2)
        
        raise TimeoutError(f"Task {task_id} did not complete in time")
    
    @pytest.mark.parametrize("test_case", [
        pytest.param(0, id="basic_hello_world"),
        pytest.param(1, id="timeout_test"),
        pytest.param(2, id="memory_limit_test"),
        pytest.param(3, id="syntax_error_test")
    ])
    def test_submission(self, test_case: int, test_cases: list[TestCase]):
        """Test code submission and execution."""
        case = test_cases[test_case]
        print(f"\n🧪 Running test case: {case.name}")
        
        try:
            # Submit code
            submission = self.submit_code(case)
            task_id = submission["task_id"]
            print(f"📤 Code submitted. Task ID: {task_id}")
            
            # Wait for completion
            print("⏳ Waiting for task completion...")
            result = self.wait_for_task_completion(task_id)
            
            # Verify results
            if case.expected_status == "success":
                assert result["status"] == "completed", f"Task failed: {result}"
                test_results = result["result"]
                assert test_results["status"] == "success", f"Tests failed: {test_results}"
                assert test_results["details"]["passed"] == case.expected_tests_passed, \
                    f"Expected {case.expected_tests_passed} tests to pass, got {test_results['details']['passed']}"
                print(f"✅ Test passed: {test_results['details']['passed']} tests passed")
            else:
                assert result["status"] == "failed" or result["result"]["status"] == "error", \
                    f"Expected error but got success: {result}"
                print(f"✅ Test passed: Error detected as expected")
                
        except Exception as e:
            pytest.fail(f"Test case '{case.name}' failed: {str(e)}")
            
    def test_invalid_submission(self):
        """Test submission with invalid data."""
        invalid_payloads = [
            {
                "code": "",  # Empty code
                "test_file": "test_hello.py"
            },
            {
                "code": "def hello_world(): pass",
                "test_file": ""  # Empty test file
            },
            {
                "code": "def hello_world(): pass",
                "test_file": "test_hello.py",
                "timeout": 0  # Invalid timeout
            },
            {
                "code": "def hello_world(): pass",
                "test_file": "test_hello.py",
                "memory_limit": 0  # Invalid memory limit
            }
        ]
        
        for i, payload in enumerate(invalid_payloads):
            try:
                response = requests.post(
                    f"{self.base_url}/api/submit/",
                    headers=self.headers,
                    json=payload
                )
                assert response.status_code == 400, \
                    f"Invalid payload {i} was accepted: {response.text}"
                print(f"✅ Invalid payload {i} rejected as expected")
            except Exception as e:
                pytest.fail(f"Test invalid submission {i} failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 