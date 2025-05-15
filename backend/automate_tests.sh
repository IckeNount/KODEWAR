#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
export API_BASE_URL="http://localhost:8000"
export AUTH_TOKEN="test-token-123"  # For testing purposes
CELERY_WORKER_PID=""
DJANGO_SERVER_PID=""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
    
    # Kill Django server if running
    if [ ! -z "$DJANGO_SERVER_PID" ]; then
        echo "Stopping Django server..."
        kill $DJANGO_SERVER_PID 2>/dev/null || true
    fi
    
    # Kill Celery worker if running
    if [ ! -z "$CELERY_WORKER_PID" ]; then
        echo "Stopping Celery worker..."
        kill $CELERY_WORKER_PID 2>/dev/null || true
    fi
    
    # Stop any running containers
    echo "Cleaning up Docker containers..."
    docker ps -q | xargs -r docker stop
    docker ps -aq | xargs -r docker rm
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Register cleanup function
trap cleanup EXIT

# Function to check if a port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
    return $?
}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}⏳ Waiting for $service to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://$host:$port" >/dev/null; then
            echo -e "${GREEN}✅ $service is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "\n${RED}❌ $service failed to start${NC}"
    return 1
}

# Start Django server
start_django() {
    echo -e "\n${BLUE}🚀 Starting Django server...${NC}"
    if check_port 8000; then
        echo -e "${YELLOW}⚠️ Port 8000 is already in use${NC}"
        return 1
    fi
    
    python3 manage.py runserver > django.log 2>&1 &
    DJANGO_SERVER_PID=$!
    
    # Wait for Django to start
    wait_for_service localhost 8000 "Django server"
    return $?
}

# Start Celery worker
start_celery() {
    echo -e "\n${BLUE}🚀 Starting Celery worker...${NC}"
    python3 -m celery -A core worker --loglevel=info > celery.log 2>&1 &
    CELERY_WORKER_PID=$!
    
    # Wait for Celery to start
    sleep 5  # Give Celery time to initialize
    if ps -p $CELERY_WORKER_PID > /dev/null; then
        echo -e "${GREEN}✅ Celery worker started${NC}"
        return 0
    else
        echo -e "${RED}❌ Celery worker failed to start${NC}"
        return 1
    fi
}

# Run the tests
run_tests() {
    echo -e "\n${BLUE}🧪 Running tests...${NC}"
    
    # Run the test script
    ./run_tests.sh
    
    # Check the result
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✅ All tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ Tests failed${NC}"
        return 1
    fi
}

# Main execution
echo -e "${BLUE}🚀 Starting automated test process...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Start services
start_django || exit 1
start_celery || exit 1

# Run tests
run_tests

# The cleanup function will be called automatically on exit 