import pytest
import yaml
import os
from pathlib import Path

class DockerComposeTest:
    @pytest.fixture
    def docker_compose(self):
        """Load docker-compose.yml file."""
        compose_path = Path(__file__).parent.parent.parent.parent / 'docker-compose.yml'
        with open(compose_path) as f:
            return yaml.safe_load(f)
            
    def test_services_exist(self, docker_compose):
        """Test that all required services exist."""
        services = docker_compose['services']
        
        # Test required services
        assert 'backend' in services
        assert 'celery_worker_code' in services
        assert 'celery_worker_test' in services
        assert 'celery_worker_result' in services
        assert 'flower' in services
        assert 'redis' in services
        assert 'postgres' in services
        
    def test_backend_service(self, docker_compose):
        """Test backend service configuration."""
        backend = docker_compose['services']['backend']
        
        # Test ports
        assert '8000:8000' in backend['ports']
        
        # Test volumes
        assert './backend:/app' in backend['volumes']
        
        # Test environment variables
        env = backend['environment']
        assert 'DJANGO_SETTINGS_MODULE=config.settings' in env
        assert 'CELERY_BROKER_URL=redis://redis:6379/0' in env
        assert 'CELERY_RESULT_BACKEND=redis://redis:6379/0' in env
        
        # Test dependencies
        assert 'redis' in backend['depends_on']
        assert 'postgres' in backend['depends_on']
        
    def test_celery_workers(self, docker_compose):
        """Test Celery worker services configuration."""
        workers = {
            'celery_worker_code': 'code_execution',
            'celery_worker_test': 'test_execution',
            'celery_worker_result': 'result_processing'
        }
        
        for worker_name, queue in workers.items():
            worker = docker_compose['services'][worker_name]
            
            # Test command
            assert f'celery -A config worker -Q {queue} -l info' in worker['command']
            
            # Test volumes
            assert './backend:/app' in worker['volumes']
            
            # Test environment variables
            env = worker['environment']
            assert 'DJANGO_SETTINGS_MODULE=config.settings' in env
            assert 'CELERY_BROKER_URL=redis://redis:6379/0' in env
            assert 'CELERY_RESULT_BACKEND=redis://redis:6379/0' in env
            
            # Test dependencies
            assert 'redis' in worker['depends_on']
            assert 'backend' in worker['depends_on']
            
    def test_flower_service(self, docker_compose):
        """Test Flower service configuration."""
        flower = docker_compose['services']['flower']
        
        # Test ports
        assert '5555:5555' in flower['ports']
        
        # Test command
        assert 'celery -A config flower --port=5555' in flower['command']
        
        # Test volumes
        assert './backend:/app' in flower['volumes']
        
        # Test environment variables
        env = flower['environment']
        assert 'DJANGO_SETTINGS_MODULE=config.settings' in env
        assert 'CELERY_BROKER_URL=redis://redis:6379/0' in env
        assert 'CELERY_RESULT_BACKEND=redis://redis:6379/0' in env
        
        # Test dependencies
        assert 'redis' in flower['depends_on']
        assert 'backend' in flower['depends_on']
        
    def test_redis_service(self, docker_compose):
        """Test Redis service configuration."""
        redis = docker_compose['services']['redis']
        
        # Test image
        assert redis['image'] == 'redis:6-alpine'
        
        # Test ports
        assert '6379:6379' in redis['ports']
        
        # Test volumes
        assert 'redis_data:/data' in redis['volumes']
        
    def test_postgres_service(self, docker_compose):
        """Test PostgreSQL service configuration."""
        postgres = docker_compose['services']['postgres']
        
        # Test image
        assert postgres['image'] == 'postgres:13-alpine'
        
        # Test ports
        assert '5432:5432' in postgres['ports']
        
        # Test environment variables
        env = postgres['environment']
        assert 'POSTGRES_DB=kodewar' in env
        assert 'POSTGRES_USER=kodewar' in env
        assert 'POSTGRES_PASSWORD=kodewar' in env
        
        # Test volumes
        assert 'postgres_data:/var/lib/postgresql/data' in postgres['volumes']
        
    def test_volumes(self, docker_compose):
        """Test volume definitions."""
        volumes = docker_compose['volumes']
        
        # Test required volumes
        assert 'redis_data' in volumes
        assert 'postgres_data' in volumes 