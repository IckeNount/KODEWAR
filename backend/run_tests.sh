#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Starting automated tests for code submission system..."

# Check if required environment variables are set
if [ -z "$AUTH_TOKEN" ]; then
    echo -e "${RED}Error: AUTH_TOKEN environment variable is not set${NC}"
    exit 1
fi

# Set default API URL if not provided
export API_BASE_URL=${API_BASE_URL:-"http://localhost:8000"}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if Celery worker is running
if ! pgrep -f "celery worker" > /dev/null; then
    echo -e "${YELLOW}Warning: Celery worker process not found${NC}"
    echo "Make sure the Celery worker is running before continuing"
    read -p "Press Enter to continue or Ctrl+C to abort..."
fi

# Run the test suites
echo "🧪 Running test suites..."

echo -e "\n${YELLOW}Running submission system tests...${NC}"
python -m pytest tests/test_submission_system.py -v

echo -e "\n${YELLOW}Running worker integration tests...${NC}"
python -m pytest tests/test_worker_integration.py -v

# Check if tests passed
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    exit 1
fi 