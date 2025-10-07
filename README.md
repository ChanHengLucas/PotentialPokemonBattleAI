# PokéAI — Competitive Pokémon AI System (MVP)

Monorepo for a modular AI agent that builds teams and makes real-time battle decisions by combining deterministic calculation with transformer-based policy.

## Services
- calc (TypeScript/Express): deterministic numeric features for legal actions
- policy (Python/FastAPI): policy head taking state + calc features, outputs action probabilities
- teambuilder (Python/FastAPI): generates legal teams for a format
- client (TypeScript): BattleState model, orchestrator to call calc -> policy, Showdown skeleton

## Quick start (local)
1. Install dependencies:
```bash
npm install --prefix services/calc
npm install --prefix client
pip3 install -r services/policy/requirements.txt
pip3 install -r services/teambuilder/requirements.txt
```

2. Start all services:
```bash
./scripts/dev.sh
```

3. In another shell, run client demo:
```bash
npm run --prefix client build && node client/dist/index.js
```

Health endpoints:
- Calc: http://localhost:4001/health
- Policy: http://localhost:8001/health
- Teambuilder: http://localhost:8002/health

## Next steps
- Swap calc placeholder for @smogon/calc and full matchup logic
- Implement real Showdown websocket client
- Add JSON schema validation and rich logging
- Add replay parser and training pipelines
