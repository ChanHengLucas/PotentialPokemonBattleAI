# PokéAI — Competitive Pokémon Team-Building and Real-Time Battle Agent

A full-stack AI system that consistently wins competitive Pokémon battles by combining deterministic calculation-based decision models with probabilistic transformer-based strategic reasoning.

## 🎯 Core Features

- **Deterministic Calculations**: Damage ranges, KO chances, speed checks, hazard damage, status probability
- **Transformer-Based Strategy**: Team synergy, opponent move prediction, switching logic, win-condition planning
- **Real-Time Battle AI**: Makes optimal decisions turn-by-turn in Pokémon Showdown battles
- **Automated Team Building**: Generates competitive teams for any format (starting with Gen 9 OU)

## 🏗️ Architecture

### Services

- **Client** (`client/`): Node.js + TypeScript WebSocket client for Pokémon Showdown
- **Calc Service** (`services/calc/`): Deterministic calculation service using @smogon/calc
- **Policy Service** (`services/policy/`): Python FastAPI transformer-based battle policy
- **Team Builder** (`services/teambuilder/`): Python FastAPI transformer-based team construction

### Data Flow

1. **Battle State**: Client parses Showdown messages into structured `BattleState`
2. **Calculations**: Calc service evaluates all legal actions with deterministic metrics
3. **Policy Decision**: Transformer model combines calc results with strategic reasoning
4. **Action Execution**: Optimal action sent back to Showdown

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "Potential Pokemon Battle AI"

# Install dependencies
npm install

# Start all services
./scripts/start-services.sh
```

### Manual Service Startup

```bash
# Terminal 1: Calculation Service
cd services/calc
npm install
npm run dev

# Terminal 2: Policy Service
cd services/policy
pip install -r requirements.txt
python main.py

# Terminal 3: Team Builder Service
cd services/teambuilder
pip install -r requirements.txt
python main.py

# Terminal 4: Client
cd client
npm install
npm run dev
```

## 📊 BattleState Schema

The `BattleState` object captures complete game state:

```typescript
interface BattleState {
  id: string;
  format: string;
  turn: number;
  phase: 'preparation' | 'team-preview' | 'battle' | 'finished';
  p1: Player;
  p2: Player;
  field: Field;
  log: BattleLogEntry[];
  lastActions: { p1?: Action; p2?: Action };
  opponentModel: OpponentModel;
}
```

## 🧮 Calculation Service

Deterministic calculations for every legal action:

- **Damage**: Min/max/average damage, OHKO/2HKO probabilities
- **Accuracy**: Move accuracy with modifiers
- **Speed**: Speed checks and priority
- **Hazards**: Stealth Rock, Spikes, Toxic Spikes damage
- **Status**: Status condition probabilities
- **Survival**: Expected survival chances

## 🤖 Policy Service

Transformer-based strategic reasoning:

- **Context Analysis**: Battle state, opponent behavior, resource management
- **Long-term Planning**: Win condition preservation, endgame strategy
- **Opponent Modeling**: Probabilistic distributions over hidden information
- **Action Ranking**: Probability-weighted action selection

## 👥 Team Builder Service

Automated competitive team construction:

- **Format Analysis**: Usage stats, common threats, metagame trends
- **Synergy Optimization**: Type coverage, role balance, team chemistry
- **Constraint Handling**: Banned Pokémon, required roles, playstyle preferences
- **Quality Scoring**: Expected win rate against diverse opponent pools

## 🔧 Configuration

Environment variables (see `.env.example`):

```bash
# Showdown Connection
SHOWDOWN_SERVER=ws://sim.smogon.com:8000
POKEAI_USERNAME=PokeAI
POKEAI_PASSWORD=

# Service URLs
CALC_SERVICE_URL=http://localhost:3001
POLICY_SERVICE_URL=http://localhost:8000
TEAMBUILDER_SERVICE_URL=http://localhost:8001
```

## 📈 Training Pipeline

### Phase 1: Imitation Learning
- Parse 10k-100k high-Elo replays
- Extract state-action pairs
- Train policy transformer to mimic expert decisions

### Phase 2: Offline Reinforcement Learning
- Fine-tune with reward signals (win rate, KO differential, hazard control)
- Optimize for strategic position advantage

### Phase 3: Self-Play Reinforcement Learning
- Generate new data through self-play
- Improve beyond imitation learning
- Discover novel strategies

## 🎮 Usage Examples

### Battle Client

```typescript
import { ShowdownClient } from './client';

const client = new ShowdownClient('ws://sim.smogon.com:8000', 'PokeAI', '');
await client.connect();
await client.challengeUser('opponent', 'gen9ou');
```

### Team Building

```python
from services.teambuilder.main import TeamBuilderInput

input_data = TeamBuilderInput(
    format="gen9ou",
    constraints=TeamConstraints(
        playstyle="balance",
        requiredRoles=["sweeper", "wall", "hazard_setter"]
    )
)

team = teambuilder_service.build_team(input_data)
```

### Policy Decision

```python
from services.policy.main import PolicyRequest

request = PolicyRequest(
    battleState=battle_state,
    calcResults=calc_results
)

policy = policy_service.predict_action(request.battleState, request.calcResults)
```

## 🏆 Performance Goals

- **Inference Latency**: <500ms per turn
- **Win Rate**: >70% against diverse opponent pools
- **Team Quality**: Competitive teams for any format
- **Scalability**: Handle multiple concurrent battles

## 🔬 Development

### Project Structure

```
├── client/                 # WebSocket client
├── services/
│   ├── calc/              # Calculation service
│   ├── policy/            # Policy transformer
│   └── teambuilder/       # Team builder transformer
├── data/
│   ├── schemas/           # TypeScript schemas
│   ├── replays/           # Training data
│   └── pokemon/           # Pokémon data
├── models/                # Model checkpoints
├── sims/                  # Self-play simulations
└── scripts/               # Development tools
```

### Testing

```bash
# Run all tests
npm test

# Test individual services
cd services/calc && npm test
cd services/policy && python -m pytest
cd services/teambuilder && python -m pytest
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub.

---

**PokéAI** - The future of competitive Pokémon battle AI 🚀