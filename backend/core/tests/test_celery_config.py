import pytest
from django.test import TestCase
from django.conf import settings
from celery import current_app

class CeleryConfigTest(TestCase):
    def test_celery_config_exists(self):
        """Test that Celery configuration exists in settings."""
        self.assertTrue(hasattr(settings, 'CELERY_BROKER_URL'))
        self.assertTrue(hasattr(settings, 'CELERY_RESULT_BACKEND'))
        self.assertTrue(hasattr(settings, 'CELERY_ACCEPT_CONTENT'))
        self.assertTrue(hasattr(settings, 'CELERY_TASK_SERIALIZER'))
        self.assertTrue(hasattr(settings, 'CELERY_RESULT_SERIALIZER'))
        
    def test_celery_config_values(self):
        """Test that Celery configuration has correct values."""
        # Test broker URL
        self.assertTrue(settings.CELERY_BROKER_URL.startswith('redis://'))
        
        # Test result backend
        self.assertTrue(settings.CELERY_RESULT_BACKEND.startswith('redis://'))
        
        # Test content types
        self.assertIn('json', settings.CELERY_ACCEPT_CONTENT)
        
        # Test serializers
        self.assertEqual(settings.CELERY_TASK_SERIALIZER, 'json')
        self.assertEqual(settings.CELERY_RESULT_SERIALIZER, 'json')
        
    def test_celery_app_config(self):
        """Test that Celery app is properly configured."""
        # Test broker URL
        self.assertEqual(current_app.conf.broker_url, settings.CELERY_BROKER_URL)
        
        # Test result backend
        self.assertEqual(current_app.conf.result_backend, settings.CELERY_RESULT_BACKEND)
        
        # Test content types
        self.assertEqual(current_app.conf.accept_content, settings.CELERY_ACCEPT_CONTENT)
        
        # Test serializers
        self.assertEqual(current_app.conf.task_serializer, settings.CELERY_TASK_SERIALIZER)
        self.assertEqual(current_app.conf.result_serializer, settings.CELERY_RESULT_SERIALIZER)
        
    def test_celery_task_config(self):
        """Test that Celery tasks are properly configured."""
        # Test run_code_task configuration
        task = current_app.tasks['core.tasks.run_code_task']
        
        # Test task name
        self.assertEqual(task.name, 'core.tasks.run_code_task')
        
        # Test task options
        self.assertTrue(task.max_retries, 3)
        self.assertTrue(hasattr(task, 'bind'))
        
    def test_celery_worker_config(self):
        """Test that Celery worker configuration is properly set."""
        # Test worker concurrency
        self.assertTrue(hasattr(current_app.conf, 'worker_concurrency'))
        self.assertGreater(current_app.conf.worker_concurrency, 0)
        
        # Test worker prefetch multiplier
        self.assertTrue(hasattr(current_app.conf, 'worker_prefetch_multiplier'))
        self.assertGreater(current_app.conf.worker_prefetch_multiplier, 0)
        
        # Test worker max tasks per child
        self.assertTrue(hasattr(current_app.conf, 'worker_max_tasks_per_child'))
        self.assertGreater(current_app.conf.worker_max_tasks_per_child, 0)
        
    def test_celery_task_routes(self):
        """Test that Celery task routes are properly configured."""
        # Test task routes
        self.assertTrue(hasattr(current_app.conf, 'task_routes'))
        
        # Test run_code_task route
        routes = current_app.conf.task_routes
        self.assertIn('core.tasks.run_code_task', routes)
        self.assertIn('queue', routes['core.tasks.run_code_task'])
        
    def test_celery_task_queues(self):
        """Test that Celery task queues are properly configured."""
        # Test task queues
        self.assertTrue(hasattr(current_app.conf, 'task_queues'))
        
        # Test default queue
        queues = current_app.conf.task_queues
        self.assertIn('default', queues)
        
        # Test code execution queue
        self.assertIn('code_execution', queues)
        
    def test_celery_task_defaults(self):
        """Test that Celery task defaults are properly configured."""
        # Test task defaults
        self.assertTrue(hasattr(current_app.conf, 'task_defaults'))
        
        # Test task time limit
        self.assertTrue(hasattr(current_app.conf.task_defaults, 'time_limit'))
        self.assertGreater(current_app.conf.task_defaults.time_limit, 0)
        
        # Test task soft time limit
        self.assertTrue(hasattr(current_app.conf.task_defaults, 'soft_time_limit'))
        self.assertGreater(current_app.conf.task_defaults.soft_time_limit, 0)
        
        # Test task rate limit
        self.assertTrue(hasattr(current_app.conf.task_defaults, 'rate_limit'))
        self.assertIsNotNone(current_app.conf.task_defaults.rate_limit) 