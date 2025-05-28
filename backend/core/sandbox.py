import docker
import logging
import os
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class SandboxError(Exception):
    """Base exception for sandbox-related errors."""
    pass

class ResourceLimitError(SandboxError):
    """Raised when resource limits are exceeded."""
    pass

class SecurityError(SandboxError):
    """Raised when security constraints are violated."""
    pass

class SandboxManager:
    def __init__(self):
        self.client = docker.from_env()
        self.config = settings.SANDBOX_CONFIG

    def create_container(self, image: str, command: str, **kwargs) -> Dict[str, Any]:
        """
        Create a sandboxed container with the specified configuration.
        
        Args:
            image: Docker image to use
            command: Command to run in the container
            **kwargs: Additional container configuration options
            
        Returns:
            Dict containing container configuration
        """
        try:
            container_config = {
                'image': image,
                'command': command,
                'detach': True,
                'mem_limit': self.config['default_memory_limit'],
                'cpu_period': 100000,
                'cpu_quota': int(float(self.config['default_cpu_limit']) * 100000),
                'read_only': self.config['read_only'],
                'network_disabled': self.config['network_disabled'],
                'security_opt': self.config['security_opts'],
                'ulimits': [
                    docker.types.Ulimit(name=k, soft=v, hard=v)
                    for k, v in self.config['ulimits'].items()
                ],
                **kwargs
            }
            
            container = self.client.containers.create(**container_config)
            logger.info(f"Created sandbox container {container.id}")
            return {'container_id': container.id, 'config': container_config}
            
        except docker.errors.APIError as e:
            logger.error(f"Failed to create sandbox container: {str(e)}")
            raise SandboxError(f"Container creation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating sandbox container: {str(e)}")
            raise SandboxError(f"Unexpected error: {str(e)}")

    def run_container(self, container_id: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Run a sandboxed container and wait for completion.
        
        Args:
            container_id: ID of the container to run
            timeout: Optional timeout in seconds
            
        Returns:
            Dict containing execution results
        """
        try:
            container = self.client.containers.get(container_id)
            container.start()
            
            timeout = timeout or self.config['default_timeout']
            result = container.wait(timeout=timeout)
            
            logs = container.logs().decode('utf-8')
            container.remove()
            
            return {
                'exit_code': result['StatusCode'],
                'logs': logs,
                'error': result.get('Error')
            }
            
        except docker.errors.APIError as e:
            logger.error(f"Failed to run sandbox container {container_id}: {str(e)}")
            raise SandboxError(f"Container execution failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error running sandbox container {container_id}: {str(e)}")
            raise SandboxError(f"Unexpected error: {str(e)}")

    def cleanup(self, container_id: str):
        """
        Clean up a sandbox container.
        
        Args:
            container_id: ID of the container to clean up
        """
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
            logger.info(f"Cleaned up sandbox container {container_id}")
        except docker.errors.NotFound:
            logger.warning(f"Container {container_id} not found during cleanup")
        except Exception as e:
            logger.error(f"Error cleaning up container {container_id}: {str(e)}")
            raise SandboxError(f"Cleanup failed: {str(e)}") 