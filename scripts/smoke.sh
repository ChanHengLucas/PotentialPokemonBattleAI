#!/bin/bash
# PokéAI Smoke Test Script
# Runs comprehensive smoke tests including pretrain assertions, wiring tests, and proof run

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

# Check if we're in the project root
if [ ! -f "package.json" ] || [ ! -d "services" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting PokéAI Smoke Tests..."
print_status "=" * 60

# Step 1: Check environment
print_status "Step 1: Checking environment..."
if [ ! -d ".venv-policy" ] || [ ! -d ".venv-teambuilder" ]; then
    print_error "Virtual environments not found. Please run ./scripts/setup_env.sh first"
    exit 1
fi
print_success "Environment check passed"

# Step 2: Check ports
print_status "Step 2: Checking ports..."
if ! ./scripts/check_ports.sh; then
    print_error "Port check failed. Please free occupied ports or start services"
    exit 1
fi
print_success "Port check passed"

# Step 3: Check service health
print_status "Step 3: Checking service health..."
if ! ./scripts/health.sh; then
    print_error "Service health check failed. Please start services with ./scripts/dev.sh"
    exit 1
fi
print_success "Service health check passed"

# Step 4: Run pretrain assertions
print_status "Step 4: Running pretrain assertions..."
if ! source .venv-policy/bin/activate && python scripts/pretrain_smoke.py; then
    print_error "Pre-train assertions failed"
    exit 1
fi
print_success "Pre-train assertions passed"

# Step 5: Run wiring tests
print_status "Step 5: Running wiring tests..."
if ! source .venv-teambuilder/bin/activate && python -m pytest tests/wiring/test_real_paths.py -v; then
    print_error "Wiring tests failed"
    exit 1
fi
print_success "Wiring tests passed"

# Step 6: Run 5-game self-play with explain-update
print_status "Step 6: Running 5-game self-play with explain-update..."
if ! source .venv-policy/bin/activate && python scripts/training_orchestrator.py stage A --games 5 --explain-update; then
    print_error "Self-play test failed"
    exit 1
fi
print_success "Self-play test passed"

# Step 7: Verify artifacts were created
print_status "Step 7: Verifying proof run artifacts..."

# Check for update trace
if [ ! -f "data/reports/update_trace_stage_baseline.json" ]; then
    print_error "Update trace not found"
    exit 1
fi
print_success "Update trace found"

# Check for training diagnostics
if [ ! -f "data/reports/training_diagnostics.json" ]; then
    print_error "Training diagnostics not found"
    exit 1
fi
print_success "Training diagnostics found"

# Check for checkpoint
if [ ! -L "models/checkpoints/latest.ckpt" ]; then
    print_error "Latest checkpoint symlink not found"
    exit 1
fi
print_success "Latest checkpoint found"

print_success "All smoke tests passed! 🎉"
print_status "Artifacts created:"
print_status "  - data/reports/update_trace_stage_baseline.json"
print_status "  - data/reports/training_diagnostics.json"
print_status "  - models/checkpoints/latest.ckpt"