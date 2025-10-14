#!/bin/bash
# PokéAI Environment Setup Script
# Creates virtual environments and installs dependencies

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

print_status "Setting up PokéAI development environment..."

# Check Node.js version
print_status "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js version: $NODE_VERSION"

# Check Python version
print_status "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Python version: $PYTHON_VERSION"

# Create virtual environments
print_status "Creating virtual environments..."

# Policy service venv
if [ ! -d ".venv-policy" ]; then
    print_status "Creating .venv-policy..."
    python3 -m venv .venv-policy
    print_success "Created .venv-policy"
else
    print_status "Using existing .venv-policy"
fi

# Teambuilder service venv
if [ ! -d ".venv-teambuilder" ]; then
    print_status "Creating .venv-teambuilder..."
    python3 -m venv .venv-teambuilder
    print_success "Created .venv-teambuilder"
else
    print_status "Using existing .venv-teambuilder"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."

# Policy service
print_status "Installing policy service dependencies..."
source .venv-policy/bin/activate
pip install --upgrade pip
pip install -r services/policy/requirements.txt
deactivate
print_success "Policy service dependencies installed"

# Teambuilder service
print_status "Installing teambuilder service dependencies..."
source .venv-teambuilder/bin/activate
pip install --upgrade pip
pip install -r services/teambuilder/requirements.txt
deactivate
print_success "Teambuilder service dependencies installed"

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."

# Root dependencies
print_status "Installing root dependencies..."
npm install
print_success "Root dependencies installed"

# Calc service
print_status "Installing calc service dependencies..."
cd services/calc
npm install
cd ../..
print_success "Calc service dependencies installed"

# Client
print_status "Installing client dependencies..."
cd client
npm install
cd ..
print_success "Client dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# PokéAI Service Configuration
CALC_SERVICE_URL=http://localhost:8787
POLICY_SERVICE_URL=http://localhost:8001
TEAMBUILDER_SERVICE_URL=http://localhost:8002
CLIENT_URL=http://localhost:3000

# Training Configuration
TRAINING_LOG_DIR=data/logs/train
CHECKPOINT_DIR=models/checkpoints
REPORTS_DIR=data/reports

# Format Configuration
DEFAULT_FORMAT=gen9ou
FORMAT_VERSION=1.0.0
DEX_VERSION=1.0.0
EOF
    print_success "Created .env file"
else
    print_status "Using existing .env file"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/logs/train
mkdir -p data/reports
mkdir -p data/debug
mkdir -p models/checkpoints
mkdir -p tests/wiring
print_success "Created necessary directories"

print_success "Environment setup complete!"
print_status "To activate environments:"
print_status "  Policy: source .venv-policy/bin/activate"
print_status "  Teambuilder: source .venv-teambuilder/bin/activate"
