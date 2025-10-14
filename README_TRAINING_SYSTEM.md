# PokéAI Training System

## Overview

This is a comprehensive training system for a competitive Pokémon battle agent optimized for Gen 9 OU. The system combines a deterministic calculation layer for mechanics with a transformer-based policy for strategy, implementing a staged curriculum for progressive learning.

## Architecture

### Core Components

1. **Deterministic Calc Layer**: Handles all battle mechanics (damage, KO%, speed order, hazards, etc.)
2. **Transformer Policy**: Learns battle strategy and decision-making
3. **Team Builder**: Generates legal teams for training
4. **Training Orchestrator**: Manages the complete training pipeline

### Key Features

- **Gen 9 OU Compliance**: Full legality enforcement with all clauses
- **Staged Curriculum**: Progressive learning from basic to advanced mechanics
- **Self-Play Training**: Diverse opponent pool with different playstyles
- **Safety Rules**: Prevents illegal actions and suboptimal plays
- **Comprehensive Logging**: Detailed metrics and analysis

## Training Stages

### Stage A: Baseline
- **Duration**: 10,000 games
- **Features**: No tera, limited volatiles (hazards/screens/weather/terrain)
- **Training**: Imitation learning from replays → offline RL
- **Focus**: Basic battle mechanics and fundamental strategy

### Stage B: Expanded Volatiles
- **Duration**: 15,000 games
- **Features**: Add Encore/Taunt/Torment/Disable, Trick/Switcheroo items
- **Training**: Offline RL and short self-play
- **Focus**: Advanced status effects and item interactions

### Stage C: Tera Enabled
- **Duration**: 20,000 games
- **Features**: Enable terastallization, expand action space
- **Training**: Self-play with tera mechanics
- **Focus**: Tera timing and post-tera strategy

### Stage D: Beliefs + Long Horizon
- **Duration**: 25,000 games
- **Features**: Strengthen opponent belief modeling, endgame heuristics
- **Training**: Advanced self-play with belief modeling
- **Focus**: Long-term planning and opponent prediction

## Pre-Simulation Audit

Before running any training, perform a comprehensive pre-simulation audit:

### Run Pre-Train Assertions
```bash
./scripts/run_training.sh pretrain
```

### Run Comprehensive Audit
```bash
./scripts/run_training.sh audit
```

### Run Specific Test Categories
```bash
# Mechanics tests
pytest tests/mechanics/ -v

# Masking tests  
pytest tests/masking/ -v

# Format guard tests
pytest tests/format/ -v

# Calc fidelity tests
pytest tests/calc/ -v
```

### Coverage Matrix
The audit includes a coverage matrix showing all 70 assertions across 13 categories:
- Hazards (6), Screens/Rooms (5), Status/Volatiles (7)
- Priority/Speed (3), Choice/Locking (3), Items (4)
- Abilities (4), Moves (4), Weather/Terrain (6)
- Tera (3), Masking (8), Calc Fidelity (9), Format Guards (13)

## Quick Start

### Prerequisites

1. **Services Running**:
   ```bash
   # Calc service (port 8787)
   # Policy service (port 8001) 
   # Teambuilder service (port 8002)
   ```

2. **Data Files**:
   - `data/pokemon/` - Pokemon, moves, abilities, items data
   - `data/formats/` - Format rules and restrictions
   - `data/usage/` - Usage statistics and team priors

### Running Training

#### Full Training Pipeline
```bash
./scripts/run_training.sh full
```

#### Specific Stage
```bash
./scripts/run_training.sh stage A --games 5000
./scripts/run_training.sh stage C --config custom_config.json
```

#### Evaluation Only
```bash
./scripts/run_training.sh eval D
```

#### Training with Update Trace
```bash
./scripts/run_training.sh explain A
```

#### Check Services
```bash
./scripts/run_training.sh check
```

#### Pre-Train Assertions
```bash
./scripts/run_training.sh pretrain
```

#### Comprehensive Audit
```bash
./scripts/run_training.sh audit
```

## Configuration

### Training Config (`config/training_config.json`)

```json
{
  "seed": 1337,
  "num_games_per_stage": 10000,
  "time_budget_ms_per_turn": 500,
  "calc_service_url": "http://localhost:8787",
  "policy_service_url": "http://localhost:8001",
  "teambuilder_service_url": "http://localhost:8002",
  "format": "gen9ou",
  "include_tera": false,
  "log_dir": "data/logs/train",
  "checkpoint_dir": "models/checkpoints"
}
```

### Stage-Specific Settings

Each stage has specific configuration for:
- **Volatiles**: Which field effects are enabled
- **Abilities**: Which abilities are available
- **Items**: Which items are available
- **Training Method**: Imitation learning, offline RL, or self-play

## Pre-Train Assertions

Before training begins, the system runs comprehensive assertions to validate all critical battle mechanics:

### Hazards & Boots
- Heavy-Duty Boots negate SR/Spikes/Web chip
- Poison-type removes Toxic Spikes
- Flying types immune to Spikes/Web

### Screens & Infiltrator
- Reflect/Light Screen reduce damage correctly
- Infiltrator ignores screen reductions

### Unaware
- Defender Unaware ignores attacker boosts
- Attacker Unaware ignores defender boosts

### Choice Lock + Encore
- Choice items lock into first move
- Encore cannot force different move while locked

### Assault Vest
- Blocks status moves while held
- Allows attacking moves

### Sucker Punch Logic
- Fails against status moves
- Succeeds against attacking moves

### Substitute Interactions
- Status moves fail against Substitute
- Sound moves bypass Substitute

### Contact & Recoil/Helmet
- Contact moves trigger Rocky Helmet
- Non-contact moves don't trigger recoil
- Life Orb recoil on damaging moves

### Weather/Terrain
- Rain boosts Water, halves Fire
- Sun boosts Fire, halves Water
- Grassy Terrain weakens Earthquake
- Misty Terrain prevents status

### Speed/Priority/Rooms
- Priority determines turn order
- Speed determines order with same priority
- Trick Room reverses speed order

### Multi-hit & Loaded Dice
- Multi-hit damage per hit
- Loaded Dice increases hit count

### PP/Struggle/Pressure
- Pressure doubles PP consumption
- Struggle only when no PP left

### Tera (when enabled)
- Tera changes typing for STAB
- Tera is one-time only

## Safety Rules

The system enforces several safety rules during inference:

1. **Never choose Struggle** unless no other moves available
2. **Avoid 0% accurate actions** due to conditions
3. **Preserve unique roles** (only spinner/scarfer/wincon)
4. **Avoid defensive tera** into typing that enables opponent sweep
5. **Respect move timer budgets**
6. **Limit PP waste** to reasonable levels

## Logging & Metrics

### Per-Turn Logging
- State hash for reproducibility
- Legal actions and calc features
- Policy logits and chosen action
- Safety overrides and RNG seed
- Total latency per turn

### Aggregate Metrics
- Win percentage and average turns
- Endgame conversion when favored
- Hazard efficiency and switch efficiency
- Tera timing accuracy (when enabled)
- PP waste rate and matchup breakdown

### Checkpoints
- Model weights saved per stage
- Training seeds for reproducibility
- JSON reports with stage metrics

## Data Sources

- **Dex Data**: Pokemon, moves, abilities, items from Showdown
- **Format Data**: Gen 9 OU rules and restrictions
- **Usage Data**: Team priors and usage statistics
- **Replay Buffer**: Imitation learning data
- **Self-Play Buffer**: RL training data

## Opponent Pool

The system uses a diverse opponent pool:

- **Scripted Heuristics** (20%): Rule-based opponents
- **Prior Checkpoints** (30%): Previous model versions
- **Legal Random Bots** (10%): Random legal actions
- **Stall Archetype** (15%): Defensive teams
- **Balance Archetype** (15%): Balanced teams
- **Hyper Offense** (10%): Aggressive teams

## Evaluation

Each stage includes comprehensive evaluation:

- **Fixed Holdout Suite**: No training leakage
- **ELO vs Baselines**: Performance comparison
- **Matchup Analysis**: Win rates by opponent type
- **Metric Tracking**: All key performance indicators

## Troubleshooting

### Common Issues

1. **Services Not Running**: Check all required services are running
2. **Pre-Train Assertions Failed**: Fix failing mechanics before training
3. **Out of Memory**: Reduce batch size or games per stage
4. **Slow Training**: Check calc service performance

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
./scripts/run_training.sh full
```

### Service Health Checks

```bash
curl http://localhost:8787/health  # Calc service
curl http://localhost:8001/health  # Policy service  
curl http://localhost:8002/health  # Teambuilder service
```

## Advanced Usage

### Custom Configurations

Create custom config files for specific experiments:

```json
{
  "stage_a_games": 5000,
  "stage_b_games": 7500,
  "opponent_pool_size": 20,
  "exploration_temperature": 0.05
}
```

### Stage-Specific Training

Train only specific stages for focused learning:

```bash
./scripts/run_training.sh stage A --games 20000
./scripts/run_training.sh stage C --config advanced_config.json
```

### Evaluation Only

Run evaluation without training:

```bash
./scripts/run_training.sh eval D --config production_config.json
```

## Production Deployment

### Requirements

- **Hardware**: GPU recommended for policy training
- **Memory**: 16GB+ RAM for large datasets
- **Storage**: 100GB+ for logs and checkpoints
- **Network**: Low latency between services

### Monitoring

- **Training Progress**: Real-time metrics dashboard
- **Service Health**: Automated health checks
- **Resource Usage**: CPU, memory, disk monitoring
- **Error Tracking**: Comprehensive error logging

### Scaling

- **Horizontal**: Multiple training instances
- **Vertical**: Larger instances for faster training
- **Distributed**: Multi-node training for large datasets

### CI Integration

The system includes GitHub Actions CI that runs pre-train smoke tests:

```yaml
# .github/workflows/pretrain-smoke.yml
name: Pre-Train Smoke Tests
on: [push, pull_request]
jobs:
  pretrain-smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install pytest requests pyyaml
      - name: Run pre-train assertions
        run: python scripts/pretrain_smoke.py
      - name: Run comprehensive audit
        run: python scripts/run_pretrain_audit.py
```

This ensures all PRs pass pre-simulation audit before merging.

## Contributing

### Adding New Mechanics

1. Update battle engine with new mechanics
2. Add pre-train assertions for validation
3. Update training curriculum if needed
4. Test thoroughly before production

### Adding New Opponents

1. Implement opponent logic
2. Add to opponent pool configuration
3. Update evaluation metrics
4. Test against existing opponents

### Performance Optimization

1. Profile calc service performance
2. Optimize policy inference speed
3. Reduce memory usage
4. Improve training efficiency

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For questions and support:
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: README files and inline comments
- **Examples**: Example configurations and scripts
