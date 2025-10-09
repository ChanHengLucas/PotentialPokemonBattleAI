#!/bin/bash

# PokéAI Complete Setup Script

set -e

echo "🚀 Setting up PokéAI - Competitive Pokémon Battle AI"
echo "=================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js $(node --version) found"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ from https://python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3"
    exit 1
fi
echo "✅ pip3 found"

# Check curl
if ! command -v curl &> /dev/null; then
    echo "❌ curl is not installed. Please install curl"
    exit 1
fi
echo "✅ curl found"

# Check jq (optional but recommended)
if command -v jq &> /dev/null; then
    echo "✅ jq found (recommended for JSON processing)"
else
    echo "⚠️  jq not found (optional but recommended for JSON processing)"
fi

echo ""
echo "📦 Installing dependencies..."

# Install root dependencies
echo "Installing root dependencies..."
npm install

# Install calc service dependencies
echo "Installing calc service dependencies..."
cd services/calc
npm install
cd ../..

# Install client dependencies
echo "Installing client dependencies..."
cd client
npm install
cd ..

# Install Python dependencies
echo "Installing Python dependencies..."
cd services/policy
pip3 install -r requirements.txt
cd ../teambuilder
pip3 install -r requirements.txt
cd ../..

# Build TypeScript
echo "Building TypeScript..."
npm run build
cd services/calc && npm run build && cd ../..

# Create necessary directories
echo "Creating directories..."
mkdir -p data/teams
mkdir -p data/logs
mkdir -p data/reports
mkdir -p data/snapshots
mkdir -p models/checkpoints

# Create sample data files
echo "Creating sample data files..."

# Create sample team
cat > data/teams/latest.json << 'EOF'
{
  "team": {
    "pokemon": [
      {
        "species": "Dragapult",
        "ability": "Clear Body",
        "moves": ["Shadow Ball", "Dragon Pulse", "U-turn", "Thunderbolt"],
        "item": "Choice Specs",
        "nature": "Timid",
        "evs": {"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252}
      },
      {
        "species": "Garchomp",
        "ability": "Rough Skin",
        "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"],
        "item": "Leftovers",
        "nature": "Jolly",
        "evs": {"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252}
      },
      {
        "species": "Landorus-Therian",
        "ability": "Intimidate",
        "moves": ["Earthquake", "U-turn", "Stone Edge", "Stealth Rock"],
        "item": "Choice Scarf",
        "nature": "Jolly",
        "evs": {"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252}
      },
      {
        "species": "Heatran",
        "ability": "Flash Fire",
        "moves": ["Magma Storm", "Earth Power", "Flash Cannon", "Stealth Rock"],
        "item": "Leftovers",
        "nature": "Timid",
        "evs": {"hp": 252, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 0}
      },
      {
        "species": "Rotom-Wash",
        "ability": "Levitate",
        "moves": ["Volt Switch", "Hydro Pump", "Thunderbolt", "Will-O-Wisp"],
        "item": "Leftovers",
        "nature": "Bold",
        "evs": {"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 0, "spe": 0}
      },
      {
        "species": "Toxapex",
        "ability": "Regenerator",
        "moves": ["Scald", "Toxic", "Recover", "Haze"],
        "item": "Black Sludge",
        "nature": "Bold",
        "evs": {"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 0, "spe": 0}
      }
    ],
    "format": "gen9ou",
    "name": "Sample Team"
  },
  "score": 0.85,
  "synergy": 0.8,
  "coverage": ["Fire", "Water", "Grass", "Electric", "Ground", "Dragon", "Ghost", "Poison"],
  "winConditions": ["Sweeper setup", "Hazard stack"],
  "threats": ["Dragapult", "Garchomp", "Landorus-Therian"]
}
EOF

# Create sample usage stats
cat > data/snapshots/gen9ou_usage.json << 'EOF'
{
  "Dragapult": {
    "usage": 0.15,
    "moves": {
      "Shadow Ball": 0.8,
      "Dragon Pulse": 0.6,
      "U-turn": 0.7,
      "Thunderbolt": 0.4
    },
    "items": {
      "Choice Specs": 0.4,
      "Choice Band": 0.3,
      "Leftovers": 0.2
    },
    "abilities": {
      "Clear Body": 0.6,
      "Infiltrator": 0.4
    }
  },
  "Garchomp": {
    "usage": 0.12,
    "moves": {
      "Earthquake": 0.9,
      "Dragon Claw": 0.7,
      "Stone Edge": 0.5,
      "Swords Dance": 0.4
    },
    "items": {
      "Leftovers": 0.4,
      "Choice Scarf": 0.3,
      "Life Orb": 0.2
    },
    "abilities": {
      "Rough Skin": 0.8,
      "Sand Veil": 0.2
    }
  }
}
EOF

# Create sample curated sets
cat > data/snapshots/gen9ou_sets.json << 'EOF'
{
  "Dragapult": [
    {
      "name": "Choice Specs",
      "item": "Choice Specs",
      "ability": "Clear Body",
      "nature": "Timid",
      "evs": {"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
      "moves": ["Shadow Ball", "Dragon Pulse", "U-turn", "Thunderbolt"],
      "teraType": "Ghost"
    }
  ],
  "Garchomp": [
    {
      "name": "Swords Dance",
      "item": "Leftovers",
      "ability": "Rough Skin",
      "nature": "Jolly",
      "evs": {"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252},
      "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"],
      "teraType": "Ground"
    }
  ]
}
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎮 PokéAI is ready to use!"
echo ""
echo "📋 Quick Start Commands:"
echo "  1. Start services:     ./scripts/dev.sh"
echo "  2. Build a team:       ./scripts/build-team.sh gen9ou"
echo "  3. Run smoke test:     ./scripts/smoke.sh"
echo "  4. Self-play:          python sims/selfplay/run.py --games 50"
echo "  5. Team evaluation:    python sims/selfplay/eval_teamset.py --candidates 8 --games 20"
echo ""
echo "🔧 Development Commands:"
echo "  - Integration test:    python scripts/test-integration.py"
echo "  - Ladder battles:      node client/src/ladder.ts --format gen9ou --maxGames 3"
echo "  - Train models:        python models/training/train_policy.py"
echo ""
echo "📚 Documentation:"
echo "  - README.md:           Complete system overview"
echo "  - data/schemas/:       JSON schemas for all data structures"
echo "  - tests/:              Unit and integration tests"
echo ""
echo "🚀 Ready to battle! Good luck trainer!"
