import os
from celery import Celery
from kombu import Queue

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('kodewar')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure task queues
app.conf.task_queues = (
    Queue('default', routing_key='default'),
    Queue('code_execution', routing_key='code_execution'),
    Queue('test_execution', routing_key='test_execution'),
    Queue('result_processing', routing_key='result_processing'),
)

# Configure task routes
app.conf.task_routes = {
    'core.tasks.run_code_task': {
        'queue': 'code_execution',
        'routing_key': 'code_execution',
    },
    'core.tasks.run_test_task': {
        'queue': 'test_execution',
        'routing_key': 'test_execution',
    },
    'core.tasks.process_result_task': {
        'queue': 'result_processing',
        'routing_key': 'result_processing',
    },
}

# Configure task defaults
app.conf.task_defaults = {
    'time_limit': 300,  # 5 minutes
    'soft_time_limit': 240,  # 4 minutes
    'rate_limit': '100/m',  # 100 tasks per minute
}

# Configure worker settings
app.conf.worker_concurrency = 4  # Number of worker processes
app.conf.worker_prefetch_multiplier = 1  # Number of tasks prefetched per worker
app.conf.worker_max_tasks_per_child = 1000  # Restart worker after 1000 tasks

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 