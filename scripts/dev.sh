#!/bin/bash
# PokéAI Development Startup Script
# Starts all services with proper supervision and graceful shutdown

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

# Default URLs if not set in .env
CALC_URL=${CALC_SERVICE_URL:-http://localhost:3001}
POLICY_URL=${POLICY_SERVICE_URL:-http://localhost:8000}
TEAMBUILDER_URL=${TEAMBUILDER_SERVICE_URL:-http://localhost:8001}
CLIENT_URL=${CLIENT_URL:-http://localhost:3000}

# Extract ports from URLs
CALC_PORT=${CALC_URL##*:}
POLICY_PORT=${POLICY_URL##*:}
TEAMBUILDER_PORT=${TEAMBUILDER_URL##*:}
CLIENT_PORT=${CLIENT_URL##*:}

# Check if we're in the project root
if [ ! -f "package.json" ] || [ ! -d "services" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environments exist
if [ ! -d ".venv-policy" ] || [ ! -d ".venv-teambuilder" ]; then
    print_error "Virtual environments not found. Please run ./scripts/setup_env.sh first"
    exit 1
fi

# Function to start a service with retry logic
start_service() {
    local service_name=$1
    local start_command=$2
    local health_url=$3
    local max_retries=5
    local retry_count=0
    
    print_status "Starting $service_name..."
    
    while [ $retry_count -lt $max_retries ]; do
        # Start the service in background
        eval "$start_command" &
        local pid=$!
        
        # Wait a moment for startup
        sleep 3
        
        # Check if service is healthy
        if curl -s --max-time 5 "$health_url/health" > /dev/null 2>&1; then
            print_success "$service_name started successfully (PID: $pid)"
            echo $pid
            return 0
        else
            print_warning "$service_name not responding, retrying... ($((retry_count + 1))/$max_retries)"
            kill $pid 2>/dev/null || true
            retry_count=$((retry_count + 1))
            sleep 2
        fi
    done
    
    print_error "$service_name failed to start after $max_retries attempts"
    return 1
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    
    # Kill all background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    # Wait for processes to exit
    sleep 2
    
    # Force kill if still running
    jobs -p | xargs -r kill -9 2>/dev/null || true
    
    print_success "All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

print_status "Starting PokéAI Development Environment..."
print_status "Service URLs:"
print_status "  Calc Service: $CALC_URL"
print_status "  Policy Service: $POLICY_URL"
print_status "  Teambuilder Service: $TEAMBUILDER_URL"
print_status "  Client: $CLIENT_URL"

# Start Calc Service
CALC_PID=$(start_service "Calc Service" "cd services/calc && npm run dev" "$CALC_URL")
if [ $? -ne 0 ]; then
    print_error "Failed to start Calc Service"
    exit 1
fi

# Start Policy Service
POLICY_PID=$(start_service "Policy Service" "source .venv-policy/bin/activate && cd services/policy && python main.py" "$POLICY_URL")
if [ $? -ne 0 ]; then
    print_error "Failed to start Policy Service"
    kill $CALC_PID 2>/dev/null || true
    exit 1
fi

# Start Teambuilder Service
TEAMBUILDER_PID=$(start_service "Teambuilder Service" "source .venv-teambuilder/bin/activate && cd services/teambuilder && python main.py" "$TEAMBUILDER_URL")
if [ $? -ne 0 ]; then
    print_error "Failed to start Teambuilder Service"
    kill $CALC_PID $POLICY_PID 2>/dev/null || true
    exit 1
fi

# Start Client (optional)
print_status "Starting Client..."
cd client
npm run dev &
CLIENT_PID=$!
cd ..

# Wait a moment for client startup
sleep 3

# Check client health (optional)
if curl -s --max-time 5 "$CLIENT_URL" > /dev/null 2>&1; then
    print_success "Client started successfully (PID: $CLIENT_PID)"
else
    print_warning "Client may not be ready yet"
fi

print_success "All services started successfully!"
print_status "Service PIDs:"
print_status "  Calc Service: $CALC_PID"
print_status "  Policy Service: $POLICY_PID"
print_status "  Teambuilder Service: $TEAMBUILDER_PID"
print_status "  Client: $CLIENT_PID"

print_status "Press Ctrl+C to stop all services"

# Monitor services and show minimal logs
while true; do
    # Check if any service died
    if ! kill -0 $CALC_PID 2>/dev/null; then
        print_error "Calc Service died unexpectedly"
        cleanup
    fi
    
    if ! kill -0 $POLICY_PID 2>/dev/null; then
        print_error "Policy Service died unexpectedly"
        cleanup
    fi
    
    if ! kill -0 $TEAMBUILDER_PID 2>/dev/null; then
        print_error "Teambuilder Service died unexpectedly"
        cleanup
    fi
    
    sleep 5
done