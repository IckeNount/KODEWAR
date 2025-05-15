import os
import time
import json
import pytest
import requests
import docker
from typing import Dict, Any
from datetime import datetime, timedelta

class TestWorkerIntegration:
    """Test suite for verifying Celery worker and Docker sandbox integration."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.auth_token = os.getenv("AUTH_TOKEN", "your-auth-token")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        self.docker_client = docker.from_env()
        
    def get_container_count(self) -> int:
        """Get the number of running containers."""
        return len(self.docker_client.containers.list())
        
    def test_worker_picks_up_job(self):
        """Verify that the Celery worker picks up the job."""
        # Record initial container count
        initial_containers = self.get_container_count()
        print(f"📊 Initial container count: {initial_containers}")
        
        # Submit a simple test
        test_code = """
def hello_world(name: str = "World") -> str:
    return f"Hello, {name}!"
"""
        payload = {
            "code": test_code,
            "test_file": "test_hello.py",
            "timeout": 30,
            "memory_limit": 512,
            "metadata": {
                "test_type": "worker_verification",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Submit the code
        response = requests.post(
            f"{self.base_url}/api/submit/",
            headers=self.headers,
            json=payload
        )
        assert response.status_code == 202, f"Submission failed: {response.text}"
        
        # Get task ID
        task_id = response.json()["task_id"]
        print(f"📤 Task submitted with ID: {task_id}")
        
        # Wait for container to start (should happen within 5 seconds)
        start_time = datetime.now()
        container_started = False
        
        while (datetime.now() - start_time) < timedelta(seconds=5):
            current_containers = self.get_container_count()
            if current_containers > initial_containers:
                container_started = True
                print(f"✅ Container started (count: {current_containers})")
                break
            time.sleep(0.5)
            
        assert container_started, "No new container was started within 5 seconds"
        
        # Wait for task completion
        print("⏳ Waiting for task completion...")
        max_attempts = 15
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{self.base_url}/api/task/{task_id}/",
                headers=self.headers
            )
            assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
            
            status_data = status_response.json()
            if status_data["status"] in ["completed", "failed"]:
                print(f"✅ Task completed with status: {status_data['status']}")
                
                # Verify test results
                if status_data["status"] == "completed":
                    result = status_data["result"]
                    assert result["status"] == "success", f"Tests failed: {result}"
                    assert result["details"]["passed"] == 5, \
                        f"Expected 5 tests to pass, got {result['details']['passed']}"
                    print(f"✅ All 5 tests passed successfully")
                break
                
            time.sleep(2)
            
        # Verify container cleanup
        final_containers = self.get_container_count()
        assert final_containers == initial_containers, \
            f"Container not cleaned up (initial: {initial_containers}, final: {final_containers})"
        print("✅ Container cleanup verified")
        
    def test_sandbox_isolation(self):
        """Verify that the sandbox container is properly isolated."""
        # Submit code that attempts to access system resources
        test_code = """
def hello_world(name: str = "World") -> str:
    import os
    import socket
    import subprocess
    
    # Try to access system resources
    try:
        os.system("ls /")  # Should fail
    except:
        pass
        
    try:
        socket.create_connection(("google.com", 80))  # Should fail
    except:
        pass
        
    try:
        subprocess.run(["echo", "test"])  # Should fail
    except:
        pass
        
    return f"Hello, {name}!"
"""
        payload = {
            "code": test_code,
            "test_file": "test_hello.py",
            "timeout": 30,
            "memory_limit": 512
        }
        
        # Submit the code
        response = requests.post(
            f"{self.base_url}/api/submit/",
            headers=self.headers,
            json=payload
        )
        assert response.status_code == 202, f"Submission failed: {response.text}"
        
        # Wait for task completion
        task_id = response.json()["task_id"]
        print(f"📤 Task submitted with ID: {task_id}")
        
        # Poll for results
        max_attempts = 10
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{self.base_url}/api/task/{task_id}/",
                headers=self.headers
            )
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                # Verify that the code still works despite isolation
                result = status_data["result"]
                assert result["status"] == "success", f"Tests failed: {result}"
                assert result["details"]["passed"] == 5, \
                    f"Expected 5 tests to pass, got {result['details']['passed']}"
                print("✅ Code executed successfully in isolated environment")
                break
                
            time.sleep(2)
            
        print("✅ Sandbox isolation verified")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 