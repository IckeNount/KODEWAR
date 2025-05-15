# Code Testing Sandbox

This is a sandbox environment for running and testing code submissions in a secure, isolated container.

## Setup

1. Build the Docker image:

```bash
docker build -t code-sandbox .
```

2. Run tests:

```bash
docker run -v $(pwd):/app code-sandbox python test_runner.py <test_file> <submission_file>
```

## Features

- Isolated Python environment
- Secure execution with non-root user
- Comprehensive test reporting
- Timeout protection
- Code coverage reporting

## Dependencies

- Python 3.11
- pytest
- pytest-timeout
- pytest-cov
- pytest-mock

## Security

The sandbox runs code in an isolated container with a non-root user to prevent system access and resource abuse.
