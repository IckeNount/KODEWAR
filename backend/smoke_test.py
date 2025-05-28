#!/usr/bin/env python3
import requests
import json
import time
import os
from typing import Dict, Any

def run_smoke_test() -> None:
    """Run a smoke test of the code submission system."""
    
    # Test configuration
    BASE_URL = "http://localhost:8000"
    API_URL = f"{BASE_URL}/api/submit/"
    AUTH_TOKEN = os.getenv("AUTH_TOKEN", "your-auth-token")  # Replace with your auth token
    
    # Test code
    test_code = """
def hello_world(name: str = "World") -> str:
    return f"Hello, {name}!"
"""
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    payload = {
        "code": test_code,
        "test_file": "test_hello.py",
        "timeout": 30,
        "memory_limit": 512,
        "metadata": {
            "test_type": "smoke_test",
            "language": "python"
        }
    }
    
    print("🚀 Starting smoke test...")
    print(f"📤 Sending request to {API_URL}")
    print(f"📝 Test code:\n{test_code}")
    
    try:
        # Send the request
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check response
        if response.status_code != 202:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        # Parse response
        result = response.json()
        task_id = result.get("task_id")
        print(f"✅ Request accepted. Task ID: {task_id}")
        
        # Poll for results
        print("⏳ Waiting for task completion...")
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            status_response = requests.get(
                f"{BASE_URL}/api/task/{task_id}/",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                
                if status == "completed":
                    print("\n✅ Task completed successfully!")
                    print("\n📊 Results:")
                    print(json.dumps(status_data.get("result", {}), indent=2))
                    return
                elif status == "failed":
                    print("\n❌ Task failed!")
                    print("\n📊 Error:")
                    print(json.dumps(status_data.get("error", {}), indent=2))
                    return
                else:
                    print(".", end="", flush=True)
            
            time.sleep(2)
            attempt += 1
            
        print("\n⚠️ Task timed out after maximum attempts")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    run_smoke_test() 