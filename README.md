# KodeWar

A secure code execution platform for programming challenges.

## Architecture

### Code Execution Flow

1. **Code Submission**

   - User submits code via `/api/submit/` endpoint
   - System validates input and generates submission ID
   - Code is queued for execution

2. **Task Processing**

   - Celery worker picks up the task
   - Sandbox container is created with security policies
   - Code is executed in isolated environment
   - Results are captured and processed

3. **Result Retrieval**
   - User checks status via `/api/status/` endpoint
   - System returns execution results or error messages
   - Test results are included if test cases were provided

### Security

- Docker container isolation
- Resource limits (CPU, memory, I/O)
- System call restrictions
- Non-root user execution
- Regular security scanning

## Quick Start

### Prerequisites

- Docker
- Python 3.11
- Redis
- Celery

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the sandbox image:
   ```bash
   docker build -t kodewar-sandbox -f backend/sandbox/Dockerfile.sandbox .
   ```
4. Start the services:
   ```bash
   docker-compose up -d
   ```

### Running Tests

```bash
pytest backend/core/tests/
```

## Development Guide

### Adding New Features

1. Create feature branch
2. Write tests
3. Implement feature
4. Run security scan
5. Submit pull request

### Code Submission

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

# Check status
status = requests.get(
    f'http://localhost:8000/api/status/?submission_id={submission_id}',
    headers={'Authorization': 'Bearer your-token'}
)
```

### Troubleshooting

1. Check container logs:
   ```bash
   docker logs kodewar-sandbox
   ```
2. View application logs:
   ```bash
   tail -f backend/logs/app.log
   ```
3. Monitor Celery tasks:
   ```bash
   celery -A backend inspect active
   ```

## Security

### Regular Maintenance

1. Update dependencies
2. Run security scans
3. Review security profiles
4. Monitor resource usage

### Security Scanning

```bash
trivy image kodewar-sandbox --severity HIGH,CRITICAL
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Write tests
4. Implement changes
5. Submit pull request

## License

MIT License
