import os
import json
import tempfile
import shutil
from typing import Dict, Any, Optional
from celery import shared_task
import docker
from docker.errors import DockerException
from django.conf import settings
from .sandbox import SandboxManager, SandboxError, ResourceLimitError, SecurityError
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

@shared_task
def run_code_task(code, language, test_cases=None, submission_id=None):
    """Execute code in sandboxed environment."""
    sandbox = SandboxManager()
    container = None
    
    try:
        # Create container
        container = sandbox.create_container(
            code=code,
            language=language,
            test_cases=test_cases
        )
        
        # Run container
        result = sandbox.run_container(container)
        
        # Process results
        if test_cases:
            test_results = []
            for test_case, output in zip(test_cases, result['output'].split('\n')):
                test_results.append({
                    'input': test_case['input'],
                    'expected': test_case['expected'],
                    'actual': output,
                    'passed': output.strip() == test_case['expected'].strip()
                })
            
            # Store results in cache
            cache.set(
                f'submission_{submission_id}',
                {
                    'status': 'success',
                    'output': result['output'],
                    'test_results': test_results
                },
                timeout=300  # 5 minutes
            )
        else:
            # Store results in cache
            cache.set(
                f'submission_{submission_id}',
                {
                    'status': 'success',
                    'output': result['output']
                },
                timeout=300  # 5 minutes
            )
            
    except ResourceLimitError as e:
        cache.set(
            f'submission_{submission_id}',
            {
                'status': 'error',
                'error': str(e)
            },
            timeout=300  # 5 minutes
        )
        raise
    except SecurityError as e:
        cache.set(
            f'submission_{submission_id}',
            {
                'status': 'error',
                'error': str(e)
            },
            timeout=300  # 5 minutes
        )
        raise
    except SandboxError as e:
        cache.set(
            f'submission_{submission_id}',
            {
                'status': 'error',
                'error': str(e)
            },
            timeout=300  # 5 minutes
        )
        raise
    except Exception as e:
        cache.set(
            f'submission_{submission_id}',
            {
                'status': 'error',
                'error': str(e)
            },
            timeout=300  # 5 minutes
        )
        raise
    finally:
        if container:
            sandbox.cleanup(container)

def prepare_execution_command(code: str, language: str, test_cases: list = None) -> str:
    """Prepare the execution command based on language and test cases."""
    # Implementation depends on language-specific requirements
    # This is a placeholder implementation
    if language == 'python':
        return f"python -c '{code}'"
    elif language == 'javascript':
        return f"node -e '{code}'"
    # Add more language support as needed
    raise ValueError(f"Unsupported language: {language}")

def process_execution_result(result: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Process the execution result and format the response."""
    if result['exit_code'] == 0:
        return {
            'status': 'success',
            'output': result['logs'],
            'exit_code': result['exit_code']
        }
    else:
        return {
            'status': 'error',
            'error': 'Execution failed',
            'output': result['logs'],
            'exit_code': result['exit_code'],
            'details': result.get('error')
        } 