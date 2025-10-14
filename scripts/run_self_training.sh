#!/bin/bash

# PokéAI Self-Training Runner Script
# This script makes it easy to run the self-training process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if services are running
check_services() {
    print_status "Checking if required services are running..."
    
    local services_ok=true
    
    # Check calc service
    if ! curl -s http://localhost:3001/health > /dev/null 2>&1; then
        print_error "Calculation service is not running on port 3001"
        services_ok=false
    fi
    
    # Check policy service
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_error "Policy service is not running on port 8000"
        services_ok=false
    fi
    
    # Check team builder service
    if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_error "Team builder service is not running on port 8001"
        services_ok=false
    fi
    
    if [ "$services_ok" = false ]; then
        print_error "Required services are not running. Please start them first:"
        echo "  ./scripts/start-services.sh"
        exit 1
    fi
    
    print_success "All required services are running"
}

# Function to setup training environment
setup_training() {
    print_status "Setting up training environment..."
    
    # Create necessary directories
    mkdir -p data/training
    mkdir -p data/reports
    mkdir -p data/teams
    mkdir -p models/checkpoints
    mkdir -p logs
    
    # Create default config if it doesn't exist
    if [ ! -f "config/self_training.json" ]; then
        print_warning "No training config found, using defaults"
    fi
    
    print_success "Training environment ready"
}

# Function to run single training cycle
run_single_cycle() {
    local games=${1:-100}
    local format=${2:-"gen9ou"}
    local fast_mode=${3:-true}
    
    print_status "Running single training cycle with $games games in $format format (fast_mode: $fast_mode)"
    
    if [ "$fast_mode" = "true" ]; then
        python3 sims/selfplay/self_training_orchestrator.py \
            --games $games \
            --format $format \
            --fast
    else
        python3 sims/selfplay/self_training_orchestrator.py \
            --games $games \
            --format $format
    fi
    
    print_success "Single training cycle completed"
}

# Function to run continuous training
run_continuous_training() {
    local cycles=${1:-10}
    local games=${2:-100}
    local format=${3:-"gen9ou"}
    local fast_mode=${4:-true}
    
    print_status "Running continuous training for $cycles cycles with $games games per cycle in $format format (fast_mode: $fast_mode)"
    
    if [ "$fast_mode" = "true" ]; then
        python3 sims/selfplay/self_training_orchestrator.py \
            --continuous \
            --cycles $cycles \
            --games $games \
            --format $format \
            --fast
    else
        python3 sims/selfplay/self_training_orchestrator.py \
            --continuous \
            --cycles $cycles \
            --games $games \
            --format $format
    fi
    
    print_success "Continuous training completed"
}

# Function to analyze training results
analyze_results() {
    print_status "Analyzing training results..."
    
    # Check if training data exists
    if [ ! -d "data/training" ] || [ -z "$(ls -A data/training 2>/dev/null)" ]; then
        print_error "No training data found. Run training first."
        exit 1
    fi
    
    # Create analysis script if it doesn't exist
    if [ ! -f "scripts/analyze_training.py" ]; then
        print_warning "Analysis script not found, creating basic analysis..."
        python3 -c "
import json
import os
from pathlib import Path

# Load training history
history_file = Path('data/training/training_history.json')
if history_file.exists():
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    print('=== Training Analysis ===')
    print(f'Total cycles: {len(history)}')
    
    if history:
        latest = history[-1]
        print(f'Latest cycle: {latest.get(\"cycle_id\", \"unknown\")}')
        print(f'Games in latest cycle: {latest.get(\"games_played\", 0)}')
        print(f'Best team score: {latest.get(\"best_team_score\", 0.0):.3f}')
        
        # Calculate improvements
        if len(history) > 1:
            prev_score = history[-2].get('best_team_score', 0.0)
            curr_score = latest.get('best_team_score', 0.0)
            improvement = curr_score - prev_score
            print(f'Score improvement: {improvement:+.3f}')
    else:
        print('No training history found')
else:
    print('No training history file found')
"
    else
        python3 scripts/analyze_training.py
    fi
    
    print_success "Training analysis completed"
}

# Function to show training status
show_status() {
    print_status "Training Status:"
    
    # Check if training data exists
    if [ -d "data/training" ] && [ "$(ls -A data/training 2>/dev/null)" ]; then
        local cycle_count=$(find data/training -name "cycle_*.json" | wc -l)
        local selfplay_count=$(find data/training -name "selfplay_*.json" | wc -l)
        local analysis_count=$(find data/training -name "analysis_*.json" | wc -l)
        
        echo "  Training cycles completed: $cycle_count"
        echo "  Self-play datasets: $selfplay_count"
        echo "  Analysis files: $analysis_count"
        
        # Show latest results
        if [ -f "data/training/training_history.json" ]; then
            echo "  Latest results:"
            python3 -c "
import json
from pathlib import Path

history_file = Path('data/training/training_history.json')
if history_file.exists():
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    if history:
        latest = history[-1]
        print(f'    Cycle ID: {latest.get(\"cycle_id\", \"unknown\")}')
        print(f'    Games played: {latest.get(\"games_played\", 0)}')
        print(f'    Best team score: {latest.get(\"best_team_score\", 0.0):.3f}')
        print(f'    Duration: {latest.get(\"duration\", 0.0):.1f}s')
"
        fi
    else
        echo "  No training data found"
    fi
    
    # Check model checkpoints
    if [ -d "models/checkpoints" ] && [ "$(ls -A models/checkpoints 2>/dev/null)" ]; then
        local checkpoint_count=$(find models/checkpoints -name "*.pth" -o -name "*.pt" | wc -l)
        echo "  Model checkpoints: $checkpoint_count"
    else
        echo "  No model checkpoints found"
    fi
}

# Function to clean training data
clean_training_data() {
    local days=${1:-30}
    
    print_warning "Cleaning training data older than $days days..."
    
    # Clean old training files
    find data/training -name "*.json" -mtime +$days -delete 2>/dev/null || true
    find data/reports -name "*.json" -mtime +$days -delete 2>/dev/null || true
    find logs -name "*.log" -mtime +$days -delete 2>/dev/null || true
    
    print_success "Training data cleaned"
}

# Main script logic
case "${1:-help}" in
    "single")
        check_services
        setup_training
        run_single_cycle "${2:-100}" "${3:-gen9ou}" "${4:-true}"
        ;;
    "continuous")
        check_services
        setup_training
        run_continuous_training "${2:-10}" "${3:-100}" "${4:-gen9ou}" "${5:-true}"
        ;;
    "analyze")
        analyze_results
        ;;
    "status")
        show_status
        ;;
    "clean")
        clean_training_data "${2:-30}"
        ;;
    "help"|*)
        echo "PokéAI Self-Training Runner"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  single [games] [format] [fast]     Run a single training cycle"
        echo "  continuous [cycles] [games] [format] [fast]  Run continuous training"
        echo "  analyze                     Analyze training results"
        echo "  status                      Show training status"
        echo "  clean [days]                Clean old training data"
        echo "  help                        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 single 50 gen9ou true    Run 50 games in gen9ou format (fast mode)"
        echo "  $0 single 50 gen9ou false   Run 50 games in gen9ou format (detailed mode)"
        echo "  $0 continuous 5 100 gen9ou true  Run 5 cycles of 100 games each (fast mode)"
        echo "  $0 analyze                  Analyze training results"
        echo "  $0 status                   Show current training status"
        echo "  $0 clean 7                  Clean data older than 7 days"
        echo ""
        echo "Fast mode: Enables rapid training with shorter battles and reduced logging"
        echo "Detailed mode: Full battle simulation with comprehensive logging"
        echo ""
        echo "Prerequisites:"
        echo "  - All services must be running (./scripts/start-services.sh)"
        echo "  - Python 3 with required packages installed"
        echo "  - Sufficient disk space for training data"
        ;;
esac
