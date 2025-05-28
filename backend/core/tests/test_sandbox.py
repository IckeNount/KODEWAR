import pytest
from unittest.mock import Mock, patch
from ..sandbox import SandboxManager, SandboxError, ResourceLimitError, SecurityError
from ..tasks import run_code_task, prepare_execution_command, process_execution_result

@pytest.fixture
def sandbox_manager():
    return SandboxManager()

@pytest.fixture
def mock_docker_client():
    with patch('docker.from_env') as mock:
        yield mock

def test_create_container(sandbox_manager, mock_docker_client):
    # Mock container creation
    mock_container = Mock()
    mock_container.id = 'test-container-id'
    mock_docker_client.containers.create.return_value = mock_container
    
    # Test container creation
    result = sandbox_manager.create_container(
        image='test-image',
        command='test-command'
    )
    
    assert result['container_id'] == 'test-container-id'
    mock_docker_client.containers.create.assert_called_once()

def test_run_container(sandbox_manager, mock_docker_client):
    # Mock container operations
    mock_container = Mock()
    mock_container.wait.return_value = {'StatusCode': 0}
    mock_container.logs.return_value = b'test output'
    mock_docker_client.containers.get.return_value = mock_container
    
    # Test container execution
    result = sandbox_manager.run_container('test-container-id')
    
    assert result['exit_code'] == 0
    assert result['logs'] == 'test output'
    mock_container.start.assert_called_once()
    mock_container.wait.assert_called_once()
    mock_container.remove.assert_called_once()

def test_cleanup(sandbox_manager, mock_docker_client):
    # Mock container operations
    mock_container = Mock()
    mock_docker_client.containers.get.return_value = mock_container
    
    # Test cleanup
    sandbox_manager.cleanup('test-container-id')
    
    mock_container.remove.assert_called_once_with(force=True)

def test_resource_limit_error(sandbox_manager, mock_docker_client):
    # Mock container creation to raise resource limit error
    mock_docker_client.containers.create.side_effect = ResourceLimitError('Memory limit exceeded')
    
    with pytest.raises(ResourceLimitError):
        sandbox_manager.create_container('test-image', 'test-command')

def test_security_error(sandbox_manager, mock_docker_client):
    # Mock container creation to raise security error
    mock_docker_client.containers.create.side_effect = SecurityError('Security violation')
    
    with pytest.raises(SecurityError):
        sandbox_manager.create_container('test-image', 'test-command')

def test_prepare_execution_command():
    # Test Python command preparation
    code = 'print("Hello, World!")'
    command = prepare_execution_command(code, 'python')
    assert 'python -c' in command
    assert code in command
    
    # Test JavaScript command preparation
    code = 'console.log("Hello, World!");'
    command = prepare_execution_command(code, 'javascript')
    assert 'node -e' in command
    assert code in command
    
    # Test unsupported language
    with pytest.raises(ValueError):
        prepare_execution_command('code', 'unsupported')

def test_process_execution_result():
    # Test successful execution
    result = {
        'exit_code': 0,
        'logs': 'test output',
        'error': None
    }
    processed = process_execution_result(result, 'python')
    assert processed['status'] == 'success'
    assert processed['output'] == 'test output'
    
    # Test failed execution
    result = {
        'exit_code': 1,
        'logs': 'error output',
        'error': 'Execution failed'
    }
    processed = process_execution_result(result, 'python')
    assert processed['status'] == 'error'
    assert processed['error'] == 'Execution failed'
    assert processed['output'] == 'error output'

@pytest.mark.django_db
def test_run_code_task():
    # Test successful code execution
    with patch('core.tasks.SandboxManager') as mock_sandbox:
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation and execution
        mock_sandbox_instance.create_container.return_value = {'container_id': 'test-container'}
        mock_sandbox_instance.run_container.return_value = {
            'exit_code': 0,
            'logs': 'test output',
            'error': None
        }
        
        result = run_code_task('print("Hello")', 'python')
        assert result['status'] == 'success'
        assert result['output'] == 'test output'
        
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.run_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once()
    
    # Test resource limit error with retry
    with patch('core.tasks.SandboxManager') as mock_sandbox:
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation to raise resource limit error
        mock_sandbox_instance.create_container.side_effect = ResourceLimitError('Memory limit exceeded')
        
        with pytest.raises(ResourceLimitError):
            run_code_task('print("Hello")', 'python')
        
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once() 