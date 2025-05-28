# KodeWar Onboarding Guide

## Getting Started

### Environment Setup

1. Install prerequisites:

   ```bash
   # Install Python 3.11
   brew install python@3.11  # macOS

   # Install Docker
   brew install docker  # macOS

   # Install Redis
   brew install redis  # macOS
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/your-org/kodewar.git
   cd kodewar
   ```

3. Set up virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Build sandbox image:

   ```bash
   docker build -t kodewar-sandbox -f backend/sandbox/Dockerfile.sandbox .
   ```

5. Start services:
   ```bash
   docker-compose up -d
   ```

## Code Execution System

### Overview

The code execution system consists of:

- API endpoints for code submission and status checking
- Celery workers for task processing
- Docker containers for code execution
- Redis for task queue and result caching

### Key Components

1. **API Endpoints**

   - `/api/submit/`: Submit code for execution
   - `/api/status/`: Check execution status

2. **Task Processing**

   - Celery workers process submissions
   - Sandbox containers execute code
   - Results are cached in Redis

3. **Security Measures**
   - Container isolation
   - Resource limits
   - System call restrictions

### Common Tasks

#### Submitting Code

```python
import requests

# Submit code
response = requests.post(
    'http://localhost:8000/api/submit/',
    json={
        'code': 'def solution(x): return x * 2',
        'language': 'python',
        'test_cases': [
            {
                'input': '2',
                'expected': '4'
            }
        ]
    },
    headers={'Authorization': 'Bearer your-token'}
)

# Get submission ID
submission_id = response.json()['submission_id']
```

#### Checking Status

```python
# Check status
status = requests.get(
    f'http://localhost:8000/api/status/?submission_id={submission_id}',
    headers={'Authorization': 'Bearer your-token'}
)
print(status.json())
```

### Troubleshooting

#### Common Issues

1. **Container Creation Fails**

   ```bash
   # Check Docker daemon
   docker ps

   # Check container logs
   docker logs kodewar-sandbox
   ```

2. **Task Processing Issues**

   ```bash
   # Check Celery worker status
   celery -A backend inspect active

   # Check Redis connection
   redis-cli ping
   ```

3. **API Issues**

   ```bash
   # Check API logs
   tail -f backend/logs/app.log

   # Check Celery logs
   tail -f backend/logs/celery.log
   ```

#### Debugging Tools

1. **Container Inspection**

   ```bash
   # Inspect container
   docker inspect kodewar-sandbox

   # Check resource usage
   docker stats kodewar-sandbox
   ```

2. **Task Monitoring**

   ```bash
   # Monitor Celery tasks
   celery -A backend flower
   ```

3. **Security Scanning**
   ```bash
   # Run Trivy scan
   trivy image kodewar-sandbox --severity HIGH,CRITICAL
   ```

### Best Practices

1. **Code Submission**

   - Always include test cases
   - Set appropriate timeouts
   - Handle errors gracefully

2. **Security**

   - Review security profiles regularly
   - Monitor resource usage
   - Update dependencies

3. **Testing**
   - Write comprehensive tests
   - Run security scans
   - Test edge cases

### Resources

- [Docker Documentation](https://docs.docker.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
