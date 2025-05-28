import pytest
import os
from pathlib import Path

class SandboxDockerfileTest:
    @pytest.fixture
    def dockerfile_path(self):
        """Get the path to the sandbox Dockerfile."""
        return Path(__file__).parent.parent.parent / 'sandbox' / 'Dockerfile.sandbox'
        
    @pytest.fixture
    def dockerfile_content(self, dockerfile_path):
        """Read the sandbox Dockerfile content."""
        with open(dockerfile_path) as f:
            return f.read()
            
    def test_dockerfile_exists(self, dockerfile_path):
        """Test that the sandbox Dockerfile exists."""
        assert dockerfile_path.exists()
        
    def test_base_image(self, dockerfile_content):
        """Test that the base image is specified."""
        assert 'FROM python:3.9-slim' in dockerfile_content
        
    def test_security_packages(self, dockerfile_content):
        """Test that security packages are installed."""
        assert 'seccomp' in dockerfile_content
        assert 'RUN apt-get update && apt-get install -y' in dockerfile_content
        
    def test_user_creation(self, dockerfile_content):
        """Test that a non-root user is created."""
        assert 'RUN useradd -m -s /bin/bash sandbox' in dockerfile_content
        assert 'USER sandbox' in dockerfile_content
        
    def test_working_directory(self, dockerfile_content):
        """Test that the working directory is set."""
        assert 'WORKDIR /app' in dockerfile_content
        
    def test_resource_limits(self, dockerfile_content):
        """Test that resource limits are set."""
        assert 'ulimit' in dockerfile_content
        assert 'nofile' in dockerfile_content
        assert 'nproc' in dockerfile_content
        assert 'memlock' in dockerfile_content
        assert 'as' in dockerfile_content
        
    def test_security_options(self, dockerfile_content):
        """Test that security options are set."""
        assert '--security-opt' in dockerfile_content
        assert 'no-new-privileges' in dockerfile_content
        assert 'seccomp' in dockerfile_content
        
    def test_volume_mounts(self, dockerfile_content):
        """Test that volume mounts are configured."""
        assert 'VOLUME' in dockerfile_content
        assert '/app/user_code' in dockerfile_content
        
    def test_environment_variables(self, dockerfile_content):
        """Test that environment variables are set."""
        assert 'ENV' in dockerfile_content
        assert 'PYTHONUNBUFFERED=1' in dockerfile_content
        
    def test_healthcheck(self, dockerfile_content):
        """Test that healthcheck is configured."""
        assert 'HEALTHCHECK' in dockerfile_content
        
    def test_entrypoint(self, dockerfile_content):
        """Test that entrypoint is configured."""
        assert 'ENTRYPOINT' in dockerfile_content
        
    def test_cmd(self, dockerfile_content):
        """Test that default command is set."""
        assert 'CMD' in dockerfile_content
        
    def test_file_permissions(self, dockerfile_content):
        """Test that file permissions are set correctly."""
        assert 'chmod' in dockerfile_content
        assert 'chown' in dockerfile_content
        
    def test_cleanup(self, dockerfile_content):
        """Test that cleanup commands are included."""
        assert 'apt-get clean' in dockerfile_content
        assert 'rm -rf /var/lib/apt/lists/*' in dockerfile_content
        
    def test_python_packages(self, dockerfile_content):
        """Test that required Python packages are installed."""
        assert 'pip install' in dockerfile_content
        assert 'requirements.txt' in dockerfile_content
        
    def test_seccomp_profile(self, dockerfile_content):
        """Test that seccomp profile is configured."""
        assert 'seccomp.json' in dockerfile_content
        
    def test_network_configuration(self, dockerfile_content):
        """Test that network configuration is set."""
        assert '--network=none' in dockerfile_content
        
    def test_read_only_filesystem(self, dockerfile_content):
        """Test that filesystem is configured as read-only."""
        assert '--read-only' in dockerfile_content
        
    def test_capabilities(self, dockerfile_content):
        """Test that capabilities are dropped."""
        assert '--cap-drop=ALL' in dockerfile_content
        
    def test_ulimit_values(self, dockerfile_content):
        """Test that ulimit values are reasonable."""
        # Extract ulimit values
        ulimit_lines = [line for line in dockerfile_content.split('\n') if 'ulimit' in line]
        
        for line in ulimit_lines:
            if 'nofile' in line:
                value = int(line.split()[-1])
                assert 0 < value <= 1024
            elif 'nproc' in line:
                value = int(line.split()[-1])
                assert 0 < value <= 1024
            elif 'memlock' in line:
                value = int(line.split()[-1])
                assert 0 < value <= 524288
            elif 'as' in line:
                value = int(line.split()[-1])
                assert 0 < value <= 524288 