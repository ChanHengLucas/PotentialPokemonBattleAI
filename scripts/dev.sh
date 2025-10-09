#!/bin/bash

# PokéAI Development Script

set -e

echo "Starting PokéAI development environment..."

# Check if services are already running
if pgrep -f "calc.*dev" > /dev/null; then
    echo "Calc service already running"
else
    echo "Starting calc service..."
    cd services/calc && npm run dev &
    CALC_PID=$!
    echo "Calc service started (PID: $CALC_PID)"
fi

if pgrep -f "policy.*main.py" > /dev/null; then
    echo "Policy service already running"
else
    echo "Starting policy service..."
    cd services/policy && python main.py &
    POLICY_PID=$!
    echo "Policy service started (PID: $POLICY_PID)"
fi

if pgrep -f "teambuilder.*main.py" > /dev/null; then
    echo "Team builder service already running"
else
    echo "Starting team builder service..."
    cd services/teambuilder && python main.py &
    TEAMBUILDER_PID=$!
    echo "Team builder service started (PID: $TEAMBUILDER_PID)"
fi

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check service health
echo "Checking service health..."

# Check calc service
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✓ Calc service is healthy"
else
    echo "✗ Calc service is not responding"
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

echo ""
echo "Development environment ready!"
echo "Services running on:"
echo "  Calc Service: http://localhost:3001"
echo "  Policy Service: http://localhost:8000"
echo "  Team Builder Service: http://localhost:8001"
echo ""
echo "To start the client:"
echo "  cd client && npm run dev"
echo ""
echo "To build a team:"
echo "  ./scripts/build-team.sh"
echo ""
echo "To run ladder battles:"
echo "  node client/src/ladder.ts --format gen9ou --maxGames 3"
echo ""
echo "To run self-play:"
echo "  python sims/selfplay/run.py --games 50"
echo ""
echo "To evaluate teams:"
echo "  python sims/selfplay/eval_teamset.py --candidates 8 --games 20"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    pkill -f "calc.*dev" 2>/dev/null || true
    pkill -f "policy.*main.py" 2>/dev/null || true
    pkill -f "teambuilder.*main.py" 2>/dev/null || true
    echo "Services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for user interrupt
wait
