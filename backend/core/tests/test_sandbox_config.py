import pytest
from django.test import TestCase
from django.conf import settings

class SandboxConfigTest(TestCase):
    def test_sandbox_config_exists(self):
        """Test that sandbox configuration exists in settings."""
        self.assertTrue(hasattr(settings, 'SANDBOX_CONFIG'))
        
    def test_sandbox_config_values(self):
        """Test that sandbox configuration has all required values."""
        config = settings.SANDBOX_CONFIG
        
        # Test required configuration values
        self.assertIn('default_timeout', config)
        self.assertIn('default_memory_limit', config)
        self.assertIn('default_cpu_limit', config)
        self.assertIn('max_file_size', config)
        self.assertIn('max_processes', config)
        self.assertIn('read_only', config)
        self.assertIn('network_disabled', config)
        self.assertIn('security_opts', config)
        self.assertIn('ulimits', config)
        
    def test_sandbox_config_types(self):
        """Test that sandbox configuration values have correct types."""
        config = settings.SANDBOX_CONFIG
        
        # Test value types
        self.assertIsInstance(config['default_timeout'], int)
        self.assertIsInstance(config['default_memory_limit'], str)
        self.assertIsInstance(config['default_cpu_limit'], str)
        self.assertIsInstance(config['max_file_size'], str)
        self.assertIsInstance(config['max_processes'], int)
        self.assertIsInstance(config['read_only'], bool)
        self.assertIsInstance(config['network_disabled'], bool)
        self.assertIsInstance(config['security_opts'], list)
        self.assertIsInstance(config['ulimits'], dict)
        
    def test_sandbox_config_limits(self):
        """Test that sandbox configuration limits are reasonable."""
        config = settings.SANDBOX_CONFIG
        
        # Test timeout limit
        self.assertGreater(config['default_timeout'], 0)
        self.assertLess(config['default_timeout'], 300)  # 5 minutes max
        
        # Test memory limit format
        self.assertTrue(config['default_memory_limit'].endswith('m'))
        memory_value = int(config['default_memory_limit'][:-1])
        self.assertGreater(memory_value, 0)
        self.assertLess(memory_value, 2048)  # 2GB max
        
        # Test CPU limit format
        self.assertTrue(config['default_cpu_limit'].endswith('0'))
        cpu_value = float(config['default_cpu_limit'])
        self.assertGreater(cpu_value, 0)
        self.assertLess(cpu_value, 4.0)  # 4 cores max
        
        # Test file size limit format
        self.assertTrue(config['max_file_size'].endswith('mb'))
        file_size_value = int(config['max_file_size'][:-2])
        self.assertGreater(file_size_value, 0)
        self.assertLess(file_size_value, 10)  # 10MB max
        
        # Test process limit
        self.assertGreater(config['max_processes'], 0)
        self.assertLess(config['max_processes'], 10)  # 10 processes max
        
    def test_sandbox_config_security(self):
        """Test that sandbox security configuration is properly set."""
        config = settings.SANDBOX_CONFIG
        
        # Test security options
        self.assertTrue(config['read_only'])
        self.assertTrue(config['network_disabled'])
        self.assertIn('no-new-privileges', config['security_opts'])
        
        # Test ulimits
        ulimits = config['ulimits']
        self.assertIn('nofile', ulimits)
        self.assertIn('nproc', ulimits)
        self.assertIn('memlock', ulimits)
        self.assertIn('as', ulimits)
        
        # Test ulimit values
        self.assertGreater(ulimits['nofile'], 0)
        self.assertLess(ulimits['nofile'], 4096)
        self.assertGreater(ulimits['nproc'], 0)
        self.assertLess(ulimits['nproc'], 1024)
        self.assertGreater(ulimits['memlock'], 0)
        self.assertLess(ulimits['memlock'], 1048576)
        self.assertGreater(ulimits['as'], 0)
        self.assertLess(ulimits['as'], 1048576) 