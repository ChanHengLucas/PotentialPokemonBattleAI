# PokéAI Self-Training System

This document explains how to use the self-training system for the PokéAI project. The system allows the AI to learn and improve through self-play battles, team evaluation, and model retraining.

## Overview

The self-training system consists of several components:

1. **Comprehensive Battle Engine** - Realistic Pokemon battle simulation with proper mechanics
2. **Self-Training Orchestrator** - Main script that coordinates the entire training process
3. **Data Collection** - Gathers battle data, team compositions, and performance metrics
4. **Analysis Pipeline** - Analyzes training data to identify improvement areas
5. **Model Retraining** - Updates AI models based on new data
6. **Monitoring** - Tracks training progress and system health
7. **Easy-to-use Scripts** - Simple commands to run the training process

### Battle Simulation Features

- **Realistic Move Mechanics**: Accuracy, power, type effectiveness, critical hits
- **Status Conditions**: Burn, poison, paralysis, sleep, confusion, etc.
- **Battle Effects**: Hazards (Spikes, Stealth Rock), screens (Reflect, Light Screen), weather
- **Priority System**: Move priority and speed calculations
- **Detailed Logging**: Every action, damage, and effect is recorded
- **Fast Mode**: Optimized for rapid self-training with shorter battles
- **Comprehensive Analysis**: Move effectiveness, critical moments, team compositions

## Quick Start

### Prerequisites

1. **Start Required Services**
   ```bash
   ./scripts/start-services.sh
   ```

2. **Verify Services are Running**
   - Calculation Service: http://localhost:3001/health
   - Policy Service: http://localhost:8000/health
   - Team Builder Service: http://localhost:8001/health

### Running Self-Training

#### Single Training Cycle
```bash
# Run 100 games in gen9ou format (fast mode)
./scripts/run_self_training.sh single 100 gen9ou true

# Run 50 games in gen9ou format (detailed mode)
./scripts/run_self_training.sh single 50 gen9ou false

# Run 50 games in gen8ou format (fast mode)
./scripts/run_self_training.sh single 50 gen8ou true
```

#### Continuous Training
```bash
# Run 5 cycles of 100 games each (fast mode)
./scripts/run_self_training.sh continuous 5 100 gen9ou true

# Run 10 cycles of 50 games each (detailed mode)
./scripts/run_self_training.sh continuous 10 50 gen9ou false
```

#### Monitor Training Progress
```bash
# Check training status
./scripts/run_self_training.sh status

# Analyze training results
./scripts/run_self_training.sh analyze

# Monitor training in real-time
python3 scripts/monitor_training.py --interval 30

# Test battle system
python3 scripts/test_battle_system.py

# Analyze specific battle data
python3 scripts/battle_analyzer.py --data_file data/training/selfplay_1234567890.json --summary
```

## Detailed Usage

### Configuration

The training system uses a configuration file at `config/self_training.json`:

```json
{
  "format": "gen9ou",
  "selfplay_games": 100,
  "evaluation_candidates": 8,
  "evaluation_games": 20,
  "policy_epochs": 5,
  "teambuilder_epochs": 5,
  "cycle_interval": 300,
  "max_training_cycles": 10,
  "data_retention_days": 30,
  "model_checkpoint_interval": 5,
  "evaluation_metrics": [
    "win_rate",
    "team_synergy",
    "move_effectiveness",
    "prediction_accuracy"
  ],
  "improvement_thresholds": {
    "min_win_rate_improvement": 0.05,
    "min_team_score_improvement": 0.1,
    "max_stagnation_cycles": 3
  },
  "data_collection": {
    "save_battle_logs": true,
    "save_team_compositions": true,
    "save_move_sequences": true,
    "save_prediction_accuracy": true
  },
  "model_training": {
    "use_gpu": true,
    "batch_size": 32,
    "learning_rate": 0.001,
    "early_stopping_patience": 3,
    "validation_split": 0.2
  }
}
```

### Training Process

The self-training process follows these phases:

1. **Self-Play Data Generation**
   - Generates teams using the team builder
   - Plays battles between AI agents
   - Records battle states, actions, and outcomes
   - Saves data to `data/training/selfplay_*.json`

2. **Battle Data Analysis**
   - Analyzes win rates by team composition
   - Identifies successful strategies
   - Finds areas for improvement
   - Saves analysis to `data/training/analysis_*.json`

3. **Model Retraining**
   - Retrains policy model with new battle data
   - Retrains team builder model with new team compositions
   - Saves model checkpoints to `models/checkpoints/`

4. **Model Evaluation**
   - Evaluates improved models through team evaluation
   - Compares performance with previous iterations
   - Saves evaluation results to `data/reports/`

5. **Data Storage**
   - Saves complete training cycle data
   - Updates training history
   - Creates summary reports

### Data Storage

Training data is organized as follows:

```
data/
├── training/
│   ├── selfplay_*.json          # Raw battle data
│   ├── analysis_*.json          # Battle analysis results
│   ├── cycle_*.json             # Complete training cycles
│   └── training_history.json   # Training progress history
├── reports/
│   ├── evaluation_*.json        # Model evaluation results
│   ├── training_summary_*.json  # Training cycle summaries
│   └── monitoring_*.json        # System monitoring data
├── teams/
│   └── latest.json              # Best team from latest evaluation
└── models/
    └── checkpoints/             # Model checkpoints
        ├── policy/              # Policy model checkpoints
        └── teambuilder/         # Team builder model checkpoints
```

### Monitoring and Analysis

#### Real-time Monitoring
```bash
# Monitor training with 30-second intervals
python3 scripts/monitor_training.py --interval 30

# Generate monitoring report
python3 scripts/monitor_training.py --report
```

#### Training Analysis
```bash
# Analyze training results
python3 scripts/analyze_training.py

# Analyze specific data directory
python3 scripts/analyze_training.py --data_dir data/training
```

#### Model Retraining
```bash
# Retrain models with specific parameters
python3 scripts/retrain_models.py --epochs 10 --batch_size 64 --learning_rate 0.0005
```

### Advanced Usage

#### Custom Training Configuration
```bash
# Use custom configuration file
python3 sims/selfplay/self_training_orchestrator.py --config config/custom_training.json
```

#### Direct Script Execution
```bash
# Run orchestrator directly
python3 sims/selfplay/self_training_orchestrator.py --games 200 --format gen9ou

# Run continuous training
python3 sims/selfplay/self_training_orchestrator.py --continuous --cycles 20
```

#### Data Management
```bash
# Clean old training data (older than 7 days)
./scripts/run_self_training.sh clean 7

# Check training status
./scripts/run_self_training.sh status
```

## Troubleshooting

### Common Issues

1. **Services Not Running**
   ```bash
   # Check if services are running
   curl http://localhost:3001/health
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   
   # Start services if needed
   ./scripts/start-services.sh
   ```

2. **Insufficient Training Data**
   - Increase `selfplay_games` in configuration
   - Run more training cycles
   - Check data collection settings

3. **Model Training Failures**
   - Check GPU availability and CUDA installation
   - Verify model training scripts exist
   - Check system resources (CPU, RAM, disk space)

4. **Performance Issues**
   - Monitor system resources during training
   - Adjust batch size and learning rate
   - Consider reducing games per cycle

### Logs and Debugging

- Training logs: `logs/self_training.log`
- Service logs: Check individual service directories
- Monitoring data: `data/reports/monitoring_*.json`

### Performance Optimization

1. **GPU Usage**
   - Ensure CUDA is installed
   - Set `use_gpu: true` in configuration
   - Monitor GPU memory usage

2. **Batch Size Tuning**
   - Start with small batch sizes (16-32)
   - Increase based on available memory
   - Monitor training stability

3. **Learning Rate Tuning**
   - Start with default learning rate (0.001)
   - Reduce if training is unstable
   - Increase if training is too slow

## Best Practices

1. **Start Small**
   - Begin with 50-100 games per cycle
   - Monitor system performance
   - Gradually increase based on results

2. **Regular Monitoring**
   - Check training progress regularly
   - Monitor system health
   - Analyze results between cycles

3. **Data Management**
   - Clean old data regularly
   - Backup important checkpoints
   - Keep training history for analysis

4. **Iterative Improvement**
   - Run multiple training cycles
   - Compare performance over time
   - Adjust parameters based on results

## Example Workflow

1. **Initial Setup**
   ```bash
   # Start services
   ./scripts/start-services.sh
   
   # Verify services are running
   ./scripts/run_self_training.sh status
   ```

2. **First Training Cycle**
   ```bash
   # Run a small test cycle
   ./scripts/run_self_training.sh single 50 gen9ou
   
   # Check results
   ./scripts/run_self_training.sh analyze
   ```

3. **Continuous Training**
   ```bash
   # Run continuous training
   ./scripts/run_self_training.sh continuous 5 100 gen9ou
   
   # Monitor progress in another terminal
   python3 scripts/monitor_training.py --interval 60
   ```

4. **Analysis and Optimization**
   ```bash
   # Analyze results
   ./scripts/run_self_training.sh analyze
   
   # Check training status
   ./scripts/run_self_training.sh status
   
   # Clean old data if needed
   ./scripts/run_self_training.sh clean 7
   ```

This self-training system provides a comprehensive framework for improving the PokéAI through continuous learning and adaptation. The AI will analyze its own battles, identify successful strategies, and improve both its battle tactics and team-building capabilities over time.
