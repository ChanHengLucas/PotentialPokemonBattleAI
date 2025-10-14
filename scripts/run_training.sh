#!/bin/bash
# PokéAI Training Runner Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_CONFIG="config/training_config.json"
DEFAULT_STAGE="A"
DEFAULT_GAMES=10000
DEFAULT_SEED=1337

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
    print_status "Checking required services..."
    
    # Check calc service
    if ! curl -s http://localhost:3001/health > /dev/null; then
        print_error "Calc service not running on port 3001"
        print_status "Please start the calc service first"
        exit 1
    fi
    
    # Check policy service
    if ! curl -s http://localhost:8000/health > /dev/null; then
        print_error "Policy service not running on port 8000"
        print_status "Please start the policy service first"
        exit 1
    fi
    
    # Check teambuilder service
    if ! curl -s http://localhost:8001/health > /dev/null; then
        print_error "Teambuilder service not running on port 8001"
        print_status "Please start the teambuilder service first"
        exit 1
    fi
    
    print_success "All required services are running"
}

# Function to run pre-train assertions
run_pretrain_assertions() {
    print_status "Running pre-train assertions..."
    
    if python3 scripts/pretrain_smoke.py; then
        print_success "Pre-train assertions passed"
    else
        print_error "Pre-train assertions failed"
        print_status "Training aborted. Please fix the failing assertions."
        exit 1
    fi
}

# Function to run full training
run_full_training() {
    local config=${1:-$DEFAULT_CONFIG}
    local games=${2:-$DEFAULT_GAMES}
    local seed=${3:-$DEFAULT_SEED}
    local explain=${4:-false}
    
    print_status "Starting full training pipeline..."
    print_status "Config: $config"
    print_status "Games per stage: $games"
    print_status "Seed: $seed"
    print_status "Explain update: $explain"
    
    if [ "$explain" = "true" ]; then
        python3 scripts/training_orchestrator.py \
            --config "$config" \
            --games "$games" \
            --seed "$seed" \
            --explain-update
    else
        python3 scripts/training_orchestrator.py \
            --config "$config" \
            --games "$games" \
            --seed "$seed"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Full training completed successfully!"
    else
        print_error "Full training failed!"
        exit 1
    fi
}

# Function to run specific stage
run_stage() {
    local stage=${1:-$DEFAULT_STAGE}
    local config=${2:-$DEFAULT_CONFIG}
    local games=${3:-$DEFAULT_GAMES}
    local seed=${4:-$DEFAULT_SEED}
    local explain=${5:-false}
    
    print_status "Running Stage $stage..."
    print_status "Config: $config"
    print_status "Games: $games"
    print_status "Seed: $seed"
    print_status "Explain update: $explain"
    
    if [ "$explain" = "true" ]; then
        python3 scripts/training_orchestrator.py \
            --stage "$stage" \
            --config "$config" \
            --games "$games" \
            --seed "$seed" \
            --explain-update
    else
        python3 scripts/training_orchestrator.py \
            --stage "$stage" \
            --config "$config" \
            --games "$games" \
            --seed "$seed"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Stage $stage completed successfully!"
    else
        print_error "Stage $stage failed!"
        exit 1
    fi
}

# Function to run evaluation
run_evaluation() {
    local stage=${1:-"D"}
    local config=${2:-$DEFAULT_CONFIG}
    
    print_status "Running evaluation for Stage $stage..."
    
    python3 scripts/training_orchestrator.py \
        --stage "$stage" \
        --config "$config" \
        --games 1000  # Evaluation games
    
    if [ $? -eq 0 ]; then
        print_success "Evaluation completed successfully!"
    else
        print_error "Evaluation failed!"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "PokéAI Training Runner"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  full                    Run full training pipeline (all stages)"
    echo "  stage [STAGE]           Run specific stage (A, B, C, D)"
    echo "  eval [STAGE]            Run evaluation for specific stage"
    echo "  explain [STAGE]         Run training with update trace explanation"
    echo "  check                   Check service connectivity"
    echo "  pretrain                Run pre-train assertions only"
    echo "  audit                   Run comprehensive pre-simulation audit"
    echo "  help                    Show this help message"
    echo ""
    echo "Options:"
    echo "  --config FILE           Config file path (default: $DEFAULT_CONFIG)"
    echo "  --games NUM             Number of games per stage (default: $DEFAULT_GAMES)"
    echo "  --seed NUM              Random seed (default: $DEFAULT_SEED)"
    echo ""
    echo "Examples:"
    echo "  $0 full                                    # Run full training"
    echo "  $0 stage A --games 5000                   # Run Stage A with 5000 games"
    echo "  $0 stage C --config custom_config.json    # Run Stage C with custom config"
    echo "  $0 eval D                                  # Run evaluation for Stage D"
    echo "  $0 explain A                               # Run Stage A with update trace"
    echo "  $0 check                                   # Check service connectivity"
    echo "  $0 pretrain                               # Run pre-train assertions"
    echo "  $0 audit                                  # Run comprehensive audit"
}

# Main script logic
main() {
    local command=${1:-"help"}
    local config=""
    local games=""
    local seed=""
    local stage=""
    
    # Parse arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config)
                config="$2"
                shift 2
                ;;
            --games)
                games="$2"
                shift 2
                ;;
            --seed)
                seed="$2"
                shift 2
                ;;
            *)
                if [[ -z "$stage" && "$command" == "stage" ]]; then
                    stage="$1"
                elif [[ -z "$stage" && "$command" == "eval" ]]; then
                    stage="$1"
                elif [[ -z "$stage" && "$command" == "explain" ]]; then
                    stage="$1"
                else
                    print_error "Unknown argument: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Set defaults
    config=${config:-$DEFAULT_CONFIG}
    games=${games:-$DEFAULT_GAMES}
    seed=${seed:-$DEFAULT_SEED}
    stage=${stage:-$DEFAULT_STAGE}
    
    # Execute command
    case $command in
        "full")
            check_services
            run_pretrain_assertions
            run_full_training "$config" "$games" "$seed"
            ;;
        "stage")
            check_services
            run_pretrain_assertions
            run_stage "$stage" "$config" "$games" "$seed"
            ;;
        "eval")
            check_services
            run_evaluation "$stage" "$config"
            ;;
        "explain")
            check_services
            run_pretrain_assertions
            run_stage "$stage" "$config" "$games" "$seed" "true"
            ;;
        "check")
            check_services
            ;;
        "pretrain")
            run_pretrain_assertions
            ;;
        "audit")
            python3 scripts/run_pretrain_audit.py
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
