#!/bin/bash

# PokéAI Smoke Test Script

set -e

echo "Running PokéAI smoke tests..."

# Check if services are running
echo "Checking service health..."

# Check calc service
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✓ Calc service is healthy"
else
    echo "✗ Calc service is not responding"
    echo "Please start services with: ./scripts/dev.sh"
    exit 1
fi

# Check policy service
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Policy service is healthy"
else
    echo "✗ Policy service is not responding"
    echo "Please start services with: ./scripts/dev.sh"
    exit 1
fi

# Check team builder service
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✓ Team builder service is healthy"
else
    echo "✗ Team builder service is not responding"
    echo "Please start services with: ./scripts/dev.sh"
    exit 1
fi

echo ""
echo "Building a team..."

# Build a team
if ./scripts/build-team.sh gen9ou; then
    echo "✓ Team built successfully"
else
    echo "✗ Team building failed"
    exit 1
fi

echo ""
echo "Running offline test turn..."

# Create a simple test battle state
cat > /tmp/test_battle.json << 'EOF'
{
  "id": "test-battle",
  "format": "gen9ou",
  "turn": 1,
  "phase": "battle",
  "p1": {
    "name": "Player1",
    "team": {"pokemon": [], "format": "gen9ou"},
    "bench": [],
    "side": {
      "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": false, "stickyWeb": false},
      "screens": {"reflect": false, "lightScreen": false, "auroraVeil": false},
      "sideConditions": {
        "tailwind": false,
        "trickRoom": false,
        "gravity": false,
        "wonderRoom": false,
        "magicRoom": false
      }
    },
    "active": {
      "species": "Dragapult",
      "level": 100,
      "hp": 100,
      "maxhp": 100,
      "boosts": {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0},
      "moves": [{"id": "shadowball", "name": "Shadow Ball", "pp": 16, "maxpp": 16}],
      "ability": "Clear Body",
      "position": "active"
    }
  },
  "p2": {
    "name": "Player2",
    "team": {"pokemon": [], "format": "gen9ou"},
    "bench": [],
    "side": {
      "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": false, "stickyWeb": false},
      "screens": {"reflect": false, "lightScreen": false, "auroraVeil": false},
      "sideConditions": {
        "tailwind": false,
        "trickRoom": false,
        "gravity": false,
        "wonderRoom": false,
        "magicRoom": false
      }
    },
    "active": {
      "species": "Garchomp",
      "level": 100,
      "hp": 100,
      "maxhp": 100,
      "boosts": {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0},
      "moves": [{"id": "earthquake", "name": "Earthquake", "pp": 16, "maxpp": 16}],
      "ability": "Rough Skin",
      "position": "active"
    }
  },
  "field": {
    "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": false, "stickyWeb": false},
    "screens": {"reflect": false, "lightScreen": false, "auroraVeil": false},
    "sideConditions": {
      "tailwind": false,
      "trickRoom": false,
      "gravity": false,
      "wonderRoom": false,
      "magicRoom": false
    }
  },
  "log": [],
  "lastActions": {},
  "opponentModel": {
    "evDistributions": {},
    "itemDistributions": {},
    "teraDistributions": {},
    "moveDistributions": {},
    "revealedSets": {}
  }
}
EOF

# Test calc service
echo "Testing calc service..."
if curl -s -X POST http://localhost:3001/batch-calc \
    -H "Content-Type: application/json" \
    -d '{"state": '$(cat /tmp/test_battle.json)', "actions": [{"type": "move", "move": "shadowball"}]}' \
    | jq -e '.results | length > 0' > /dev/null; then
    echo "✓ Calc service test passed"
else
    echo "✗ Calc service test failed"
    exit 1
fi

# Test policy service
echo "Testing policy service..."
if curl -s -X POST http://localhost:8000/policy \
    -H "Content-Type: application/json" \
    -d '{"battleState": '$(cat /tmp/test_battle.json)', "calcResults": [{"action": {"type": "move", "move": "shadowball"}, "accuracy": 100, "speedCheck": {"faster": true, "speedDiff": 20}, "priority": 0}]}' \
    | jq -e '.action' > /dev/null; then
    echo "✓ Policy service test passed"
else
    echo "✗ Policy service test failed"
    exit 1
fi

# Clean up
rm -f /tmp/test_battle.json

echo ""
echo "All smoke tests passed! ✓"
echo ""
echo "PokéAI is ready for:"
echo "  - Team building: ./scripts/build-team.sh"
echo "  - Ladder battles: node client/src/ladder.ts --format gen9ou --maxGames 3"
echo "  - Self-play: python sims/selfplay/run.py --games 50"
echo "  - Team evaluation: python sims/selfplay/eval_teamset.py --candidates 8 --games 20"
