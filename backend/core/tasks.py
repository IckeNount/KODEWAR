import os
import json
import tempfile
import shutil
from typing import Dict, Any, Optional
from celery import shared_task
import docker
from docker.errors import DockerException
from django.conf import settings

@shared_task(bind=True, max_retries=3)
def run_code_task(self, code: str, test_file: str, timeout: int = 30, memory_limit: int = 512) -> Dict[str, Any]:
    """
    Celery task to run user code in a sandboxed Docker container.
    
    Args:
        code: The user's code to run
        test_file: Path to the test file
        timeout: Test execution timeout in seconds
        memory_limit: Memory limit in MB
        
    Returns:
        Dictionary containing test results
    """
    container = None
    temp_dir = None
    
    try:
        # Initialize Docker client
        client = docker.from_env()
        
        # Create temporary directory for code
        temp_dir = tempfile.mkdtemp()
        code_path = os.path.join(temp_dir, 'solution.py')
        
        # Write user code to file
        with open(code_path, 'w') as f:
            f.write(code)
            
        # Build sandbox image if not exists
        try:
            client.images.get('code-sandbox')
        except docker.errors.ImageNotFound:
            client.images.build(
                path=os.path.join(settings.BASE_DIR, 'sandbox'),
                tag='code-sandbox',
                dockerfile='Dockerfile.sandbox'
            )
        
        # Create and start container
        container = client.containers.create(
            image='code-sandbox',
            environment={
                'TEST_FILE': test_file,
                'TEST_TIMEOUT': str(timeout),
                'MEMORY_LIMIT': str(memory_limit)
            },
            mem_limit=f'{memory_limit}m',
            network_disabled=True,  # Disable network access
            read_only=True,  # Make container filesystem read-only
            volumes={
                temp_dir: {'bind': '/app/user_code', 'mode': 'ro'}
            }
        )
        
        # Start container
        container.start()
        
        # Wait for container to finish
        exit_code = container.wait(timeout=timeout + 5)  # Add 5 seconds buffer
        
        # Get container logs
        logs = container.logs(stdout=True, stderr=True).decode('utf-8')
        
        # Parse results
        try:
            results = json.loads(logs)
        except json.JSONDecodeError:
            results = {
                'status': 'error',
                'message': 'Failed to parse test results',
                'details': {
                    'raw_output': logs,
                    'exit_code': exit_code['StatusCode']
                }
            }
            
        return results
        
    except DockerException as e:
        # Retry on Docker-related errors
        self.retry(exc=e, countdown=5)
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'details': {
                'error_type': type(e).__name__
            }
        }
        
    finally:
        # Cleanup
        if container:
            try:
                container.stop(timeout=1)
                container.remove()
            except:
                pass
                
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass 