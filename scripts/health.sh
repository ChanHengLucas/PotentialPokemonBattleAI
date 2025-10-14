#!/bin/bash
# PokéAI Health Check Script
# Pings /health on all services and exits non-zero if any fail

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    print_warning ".env file not found, using default URLs"
fi

# Default URLs if not set in .env
CALC_URL=${CALC_SERVICE_URL:-http://localhost:8787}
POLICY_URL=${POLICY_SERVICE_URL:-http://localhost:8001}
TEAMBUILDER_URL=${TEAMBUILDER_SERVICE_URL:-http://localhost:8002}
CLIENT_URL=${CLIENT_URL:-http://localhost:3000}

print_status "Checking service health..."

# Function to check service health
check_service() {
    local url=$1
    local service=$2
    local timeout=${3:-5}
    
    print_status "Checking $service at $url..."
    
    if curl -s --max-time $timeout "$url/health" > /dev/null 2>&1; then
        print_success "$service is healthy"
        return 0
    else
        print_error "$service is not responding"
        echo "  URL: $url/health"
        echo "  Timeout: ${timeout}s"
        echo "  Check if the service is running and accessible"
        return 1
    fi
}

# Check all services
failed=0

# Check Calc Service
if ! check_service "$CALC_URL" "Calc Service" 5; then
    failed=1
fi

# Check Policy Service
if ! check_service "$POLICY_URL" "Policy Service" 5; then
    failed=1
fi

# Check Teambuilder Service
if ! check_service "$TEAMBUILDER_URL" "Teambuilder Service" 5; then
    failed=1
fi

# Check Client (optional, may not be running in all scenarios)
if ! check_service "$CLIENT_URL" "Client" 3; then
    print_warning "Client is not responding (this may be expected)"
fi

if [ $failed -eq 1 ]; then
    print_error "One or more services are not healthy."
    print_status "Please check the service logs and ensure all services are running."
    print_status "You can start services with: ./scripts/dev.sh"
    exit 1
else
    print_success "All required services are healthy!"
    print_status "Service URLs:"
    print_status "  Calc Service: $CALC_URL"
    print_status "  Policy Service: $POLICY_URL"
    print_status "  Teambuilder Service: $TEAMBUILDER_URL"
fi
