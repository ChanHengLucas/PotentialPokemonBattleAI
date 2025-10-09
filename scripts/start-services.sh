#!/bin/bash

# PokéAI Service Startup Script

echo "Starting PokéAI services..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install
cd services/calc && npm install && cd ../..
cd services/policy && pip install -r requirements.txt && cd ../..
cd services/teambuilder && pip install -r requirements.txt && cd ../..

# Start services in background
echo "Starting calculation service..."
cd services/calc && npm run dev &
CALC_PID=$!

echo "Starting policy service..."
cd services/policy && python main.py &
POLICY_PID=$!

echo "Starting team builder service..."
cd services/teambuilder && python main.py &
TEAMBUILDER_PID=$!

# Wait a moment for services to start
sleep 5

# Check if services are running
echo "Checking service health..."

# Check calc service
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✓ Calculation service is healthy"
else
    echo "✗ Calculation service is not responding"
fi

# Check policy service
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Policy service is healthy"
else
    echo "✗ Policy service is not responding"
fi

# Check team builder service
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✓ Team builder service is healthy"
else
    echo "✗ Team builder service is not responding"
fi

echo "All services started!"
echo "Process IDs:"
echo "  Calc Service: $CALC_PID"
echo "  Policy Service: $POLICY_PID"
echo "  Team Builder Service: $TEAMBUILDER_PID"

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $CALC_PID $POLICY_PID $TEAMBUILDER_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for services
wait
