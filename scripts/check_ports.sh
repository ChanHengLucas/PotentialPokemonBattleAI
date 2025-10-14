#!/bin/bash
# PokéAI Port Checker Script
# Checks if required ports are available and provides clear instructions if occupied

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
    print_warning ".env file not found, using default ports"
fi

# Default ports if not set in .env
CALC_PORT=${CALC_SERVICE_URL##*:}
CALC_PORT=${CALC_PORT:-8787}
POLICY_PORT=${POLICY_SERVICE_URL##*:}
POLICY_PORT=${POLICY_PORT:-8001}
TEAMBUILDER_PORT=${TEAMBUILDER_SERVICE_URL##*:}
TEAMBUILDER_PORT=${TEAMBUILDER_PORT:-8002}
CLIENT_PORT=${CLIENT_URL##*:}
CLIENT_PORT=${CLIENT_PORT:-3000}

print_status "Checking required ports..."

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        local process=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
        print_error "Port $port is occupied by $service (PID: $pid, Process: $process)"
        echo "  To free this port:"
        echo "    kill $pid"
        echo "    or find and stop the process using: lsof -ti:$port | xargs kill"
        return 1
    else
        print_success "Port $port is available for $service"
        return 0
    fi
}

# Check all required ports
failed=0

print_status "Checking Calc Service port ($CALC_PORT)..."
if ! check_port $CALC_PORT "Calc Service"; then
    failed=1
fi

print_status "Checking Policy Service port ($POLICY_PORT)..."
if ! check_port $POLICY_PORT "Policy Service"; then
    failed=1
fi

print_status "Checking Teambuilder Service port ($TEAMBUILDER_PORT)..."
if ! check_port $TEAMBUILDER_PORT "Teambuilder Service"; then
    failed=1
fi

print_status "Checking Client port ($CLIENT_PORT)..."
if ! check_port $CLIENT_PORT "Client"; then
    failed=1
fi

if [ $failed -eq 1 ]; then
    print_error "One or more required ports are occupied."
    print_status "Please free the occupied ports and try again."
    print_status "You can also modify the ports in .env file if needed."
    exit 1
else
    print_success "All required ports are available!"
    print_status "Port configuration:"
    print_status "  Calc Service: $CALC_PORT"
    print_status "  Policy Service: $POLICY_PORT"
    print_status "  Teambuilder Service: $TEAMBUILDER_PORT"
    print_status "  Client: $CLIENT_PORT"
fi
