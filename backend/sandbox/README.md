# Code Execution Sandbox

## Overview

The sandbox system provides a secure, isolated environment for executing user-submitted code. It uses Docker containers with strict security policies and resource limits to ensure safe code execution.

## Architecture

### Components

- **Sandbox Container**: Isolated environment for code execution
- **Security Profiles**: Seccomp profile for system call restrictions
- **Resource Limits**: CPU, memory, and I/O constraints
- **Result Processing**: Output capture and validation

### Security Measures

1. **Container Isolation**

   - Non-root user execution
   - Read-only filesystem
   - Network isolation
   - Resource limits

2. **System Call Restrictions**

   - Seccomp profile limiting available syscalls
   - Kernel security options
   - Process limits

3. **Resource Constraints**
   - CPU time limit: 30 seconds
   - Memory limit: 512MB
   - File descriptor limit: 1024
   - Disk I/O limits

## I/O Contract

### Input

```json
{
  "code": "string", // The code to execute
  "language": "string", // Programming language (python/javascript)
  "test_cases": [
    // Optional test cases
    {
      "input": "string", // Test input
      "expected": "string" // Expected output
    }
  ]
}
```

### Output

```json
{
    "status": "string",         // success/error
    "output": "string",         // Program output
    "error": "string",          // Error message (if any)
    "test_results": [          // Test results (if test cases provided)
        {
            "input": "string",
            "expected": "string",
            "actual": "string",
            "passed": boolean
        }
    ]
}
```

## Dependencies

- Python 3.11
- Docker
- Redis (for task queue)
- Required Python packages (see requirements.txt)

## Usage

### Building the Sandbox

```bash
docker build -t kodewar-sandbox -f Dockerfile.sandbox .
```

### Running Tests

```bash
pytest backend/core/tests/test_sandbox.py
```

### Security Scanning

```bash
trivy image kodewar-sandbox --severity HIGH,CRITICAL
```

## Troubleshooting

### Common Issues

1. **Container Creation Fails**

   - Check Docker daemon status
   - Verify resource availability
   - Check security profile configuration

2. **Execution Timeout**

   - Verify CPU time limit
   - Check for infinite loops
   - Review resource constraints

3. **Memory Issues**
   - Check memory limit configuration
   - Review code for memory leaks
   - Verify ulimit settings

### Logging

- Container logs: `docker logs <container_id>`
- Application logs: `backend/logs/sandbox.log`
- Security logs: `backend/logs/security.log`

## Maintenance

### Regular Tasks

1. Update base image
2. Review security profiles
3. Update dependencies
4. Run security scans
5. Review resource limits

### Monitoring

- Container resource usage
- Security violations
- Execution times
- Error rates
