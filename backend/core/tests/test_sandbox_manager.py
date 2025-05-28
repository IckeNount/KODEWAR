import pytest
from unittest.mock import Mock, patch
from ..sandbox import SandboxManager, SandboxError, ResourceLimitError, SecurityError
from django.conf import settings

class TestSandboxManager:
    @pytest.fixture
    def sandbox_manager(self):
        """Create a SandboxManager instance."""
        return SandboxManager()
        
    @pytest.fixture
    def mock_docker_client(self):
        """Create a mock Docker client."""
        with patch('docker.from_env') as mock:
            yield mock
            
    @pytest.fixture
    def mock_container(self):
        """Create a mock Docker container."""
        container = Mock()
        container.id = 'test-container-id'
        container.wait.return_value = {'StatusCode': 0}
        container.logs.return_value = b'test output'
        return container
        
    def test_init(self, sandbox_manager):
        """Test SandboxManager initialization."""
        assert sandbox_manager.config == settings.SANDBOX_CONFIG
        
    def test_create_container(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container creation."""
        mock_docker_client.containers.create.return_value = mock_container
        
        result = sandbox_manager.create_container(
            image='test-image',
            command='test-command'
        )
        
        assert result['container_id'] == 'test-container-id'
        mock_docker_client.containers.create.assert_called_once()
        
        # Test container configuration
        call_args = mock_docker_client.containers.create.call_args[1]
        assert call_args['image'] == 'test-image'
        assert call_args['command'] == 'test-command'
        assert call_args['detach'] is True
        assert call_args['mem_limit'] == settings.SANDBOX_CONFIG['default_memory_limit']
        assert call_args['read_only'] == settings.SANDBOX_CONFIG['read_only']
        assert call_args['network_disabled'] == settings.SANDBOX_CONFIG['network_disabled']
        assert 'security_opt' in call_args
        assert 'ulimits' in call_args
        
    def test_create_container_error(self, sandbox_manager, mock_docker_client):
        """Test container creation error handling."""
        mock_docker_client.containers.create.side_effect = Exception('Test error')
        
        with pytest.raises(SandboxError):
            sandbox_manager.create_container('test-image', 'test-command')
            
    def test_run_container(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container execution."""
        mock_docker_client.containers.get.return_value = mock_container
        
        result = sandbox_manager.run_container('test-container-id')
        
        assert result['exit_code'] == 0
        assert result['logs'] == 'test output'
        mock_container.start.assert_called_once()
        mock_container.wait.assert_called_once()
        mock_container.remove.assert_called_once()
        
    def test_run_container_timeout(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container execution with timeout."""
        mock_docker_client.containers.get.return_value = mock_container
        mock_container.wait.side_effect = Exception('Timeout')
        
        with pytest.raises(SandboxError):
            sandbox_manager.run_container('test-container-id', timeout=5)
            
    def test_run_container_error(self, sandbox_manager, mock_docker_client):
        """Test container execution error handling."""
        mock_docker_client.containers.get.side_effect = Exception('Test error')
        
        with pytest.raises(SandboxError):
            sandbox_manager.run_container('test-container-id')
            
    def test_cleanup(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container cleanup."""
        mock_docker_client.containers.get.return_value = mock_container
        
        sandbox_manager.cleanup('test-container-id')
        
        mock_container.remove.assert_called_once_with(force=True)
        
    def test_cleanup_not_found(self, sandbox_manager, mock_docker_client):
        """Test cleanup of non-existent container."""
        mock_docker_client.containers.get.side_effect = Exception('Container not found')
        
        # Should not raise an error
        sandbox_manager.cleanup('test-container-id')
        
    def test_resource_limit_error(self, sandbox_manager, mock_docker_client):
        """Test resource limit error handling."""
        mock_docker_client.containers.create.side_effect = ResourceLimitError('Memory limit exceeded')
        
        with pytest.raises(ResourceLimitError):
            sandbox_manager.create_container('test-image', 'test-command')
            
    def test_security_error(self, sandbox_manager, mock_docker_client):
        """Test security error handling."""
        mock_docker_client.containers.create.side_effect = SecurityError('Security violation')
        
        with pytest.raises(SecurityError):
            sandbox_manager.create_container('test-image', 'test-command')
            
    def test_container_configuration(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container configuration values."""
        mock_docker_client.containers.create.return_value = mock_container
        
        sandbox_manager.create_container('test-image', 'test-command')
        
        call_args = mock_docker_client.containers.create.call_args[1]
        
        # Test CPU configuration
        assert 'cpu_period' in call_args
        assert 'cpu_quota' in call_args
        cpu_quota = int(float(settings.SANDBOX_CONFIG['default_cpu_limit']) * 100000)
        assert call_args['cpu_quota'] == cpu_quota
        
        # Test memory configuration
        assert call_args['mem_limit'] == settings.SANDBOX_CONFIG['default_memory_limit']
        
        # Test security configuration
        assert call_args['read_only'] == settings.SANDBOX_CONFIG['read_only']
        assert call_args['network_disabled'] == settings.SANDBOX_CONFIG['network_disabled']
        assert call_args['security_opt'] == settings.SANDBOX_CONFIG['security_opts']
        
        # Test ulimits configuration
        ulimits = call_args['ulimits']
        assert len(ulimits) == len(settings.SANDBOX_CONFIG['ulimits'])
        for ulimit in ulimits:
            assert ulimit.name in settings.SANDBOX_CONFIG['ulimits']
            assert ulimit.soft == settings.SANDBOX_CONFIG['ulimits'][ulimit.name]
            assert ulimit.hard == settings.SANDBOX_CONFIG['ulimits'][ulimit.name]
            
    def test_container_execution_result(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container execution result processing."""
        mock_docker_client.containers.get.return_value = mock_container
        
        # Test successful execution
        result = sandbox_manager.run_container('test-container-id')
        assert result['exit_code'] == 0
        assert result['logs'] == 'test output'
        assert 'error' not in result
        
        # Test failed execution
        mock_container.wait.return_value = {'StatusCode': 1, 'Error': 'Test error'}
        result = sandbox_manager.run_container('test-container-id')
        assert result['exit_code'] == 1
        assert result['logs'] == 'test output'
        assert result['error'] == 'Test error'
        
    def test_container_logs(self, sandbox_manager, mock_docker_client, mock_container):
        """Test container logs handling."""
        mock_docker_client.containers.get.return_value = mock_container
        
        # Test successful logs
        mock_container.logs.return_value = b'test output'
        result = sandbox_manager.run_container('test-container-id')
        assert result['logs'] == 'test output'
        
        # Test empty logs
        mock_container.logs.return_value = b''
        result = sandbox_manager.run_container('test-container-id')
        assert result['logs'] == ''
        
        # Test binary logs
        mock_container.logs.return_value = b'\x00\x01\x02\x03'
        result = sandbox_manager.run_container('test-container-id')
        assert result['logs'] == '\x00\x01\x02\x03' 