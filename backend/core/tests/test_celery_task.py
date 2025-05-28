import pytest
from unittest.mock import Mock, patch
from ..tasks import run_code_task, prepare_execution_command, process_execution_result
from ..sandbox import SandboxError, ResourceLimitError, SecurityError

class TestCeleryTask:
    @pytest.fixture
    def mock_sandbox(self):
        """Create a mock SandboxManager."""
        with patch('core.tasks.SandboxManager') as mock:
            yield mock
            
    def test_prepare_execution_command(self):
        """Test execution command preparation."""
        # Test Python command
        code = 'print("Hello, World!")'
        command = prepare_execution_command(code, 'python')
        assert 'python -c' in command
        assert code in command
        
        # Test JavaScript command
        code = 'console.log("Hello, World!");'
        command = prepare_execution_command(code, 'javascript')
        assert 'node -e' in command
        assert code in command
        
        # Test unsupported language
        with pytest.raises(ValueError):
            prepare_execution_command('code', 'unsupported')
            
    def test_process_execution_result(self):
        """Test execution result processing."""
        # Test successful execution
        result = {
            'exit_code': 0,
            'logs': 'test output',
            'error': None
        }
        processed = process_execution_result(result, 'python')
        assert processed['status'] == 'success'
        assert processed['output'] == 'test output'
        assert processed['exit_code'] == 0
        
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
        assert processed['exit_code'] == 1
        
    def test_run_code_task_success(self, mock_sandbox):
        """Test successful code execution."""
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
        assert result['exit_code'] == 0
        
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.run_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once()
        
    def test_run_code_task_resource_limit(self, mock_sandbox):
        """Test resource limit error handling."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation to raise resource limit error
        mock_sandbox_instance.create_container.side_effect = ResourceLimitError('Memory limit exceeded')
        
        with pytest.raises(ResourceLimitError):
            run_code_task('print("Hello")', 'python')
            
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once()
        
    def test_run_code_task_security_error(self, mock_sandbox):
        """Test security error handling."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation to raise security error
        mock_sandbox_instance.create_container.side_effect = SecurityError('Security violation')
        
        result = run_code_task('print("Hello")', 'python')
        
        assert result['status'] == 'error'
        assert result['error'] == 'Security violation'
        
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once()
        
    def test_run_code_task_sandbox_error(self, mock_sandbox):
        """Test sandbox error handling."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation to raise sandbox error
        mock_sandbox_instance.create_container.side_effect = SandboxError('Container creation failed')
        
        result = run_code_task('print("Hello")', 'python')
        
        assert result['status'] == 'error'
        assert result['error'] == 'Execution failed'
        assert 'Container creation failed' in result['details']
        
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once()
        
    def test_run_code_task_unexpected_error(self, mock_sandbox):
        """Test unexpected error handling."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation to raise unexpected error
        mock_sandbox_instance.create_container.side_effect = Exception('Unexpected error')
        
        result = run_code_task('print("Hello")', 'python')
        
        assert result['status'] == 'error'
        assert result['error'] == 'Unexpected error'
        
        mock_sandbox_instance.create_container.assert_called_once()
        mock_sandbox_instance.cleanup.assert_called_once()
        
    def test_run_code_task_cleanup(self, mock_sandbox):
        """Test cleanup in case of errors."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation to raise error
        mock_sandbox_instance.create_container.side_effect = Exception('Test error')
        
        try:
            run_code_task('print("Hello")', 'python')
        except:
            pass
            
        mock_sandbox_instance.cleanup.assert_called_once()
        
    def test_run_code_task_command_preparation(self, mock_sandbox):
        """Test command preparation for different languages."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation and execution
        mock_sandbox_instance.create_container.return_value = {'container_id': 'test-container'}
        mock_sandbox_instance.run_container.return_value = {
            'exit_code': 0,
            'logs': 'test output',
            'error': None
        }
        
        # Test Python code
        code = 'print("Hello, World!")'
        run_code_task(code, 'python')
        call_args = mock_sandbox_instance.create_container.call_args[1]
        assert 'python -c' in call_args['command']
        assert code in call_args['command']
        
        # Test JavaScript code
        code = 'console.log("Hello, World!");'
        run_code_task(code, 'javascript')
        call_args = mock_sandbox_instance.create_container.call_args[1]
        assert 'node -e' in call_args['command']
        assert code in call_args['command']
        
    def test_run_code_task_container_configuration(self, mock_sandbox):
        """Test container configuration for code execution."""
        mock_sandbox_instance = Mock()
        mock_sandbox.return_value = mock_sandbox_instance
        
        # Mock container creation and execution
        mock_sandbox_instance.create_container.return_value = {'container_id': 'test-container'}
        mock_sandbox_instance.run_container.return_value = {
            'exit_code': 0,
            'logs': 'test output',
            'error': None
        }
        
        run_code_task('print("Hello")', 'python')
        
        call_args = mock_sandbox_instance.create_container.call_args[1]
        assert call_args['image'] == 'kodewar-sandbox-python'
        assert call_args['detach'] is True 