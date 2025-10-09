import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { DamageCalculator } from './calculator';
import { BattleState, LegalAction } from '../../data/schemas/battle-state';

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));

const calculator = new DamageCalculator();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'pokeai-calc',
    dexVersion: '1.0.0',
    activeFormats: ['gen9ou', 'gen8ou', 'gen7ou']
  });
});

// Main calculation endpoint
app.post('/calculate', async (req, res) => {
  try {
    const { battleState, actions }: { battleState: BattleState; actions: LegalAction[] } = req.body;
    
    if (!battleState || !actions) {
      return res.status(400).json({ error: 'Missing battleState or actions' });
    }

    console.log(`Calculating ${actions.length} actions for battle ${battleState.id}`);
    
    const results = await calculator.calculateDamage(battleState, actions);
    
    res.json({
      results,
      dexVersion: '1.0.0'
    });
  } catch (error) {
    console.error('Calculation error:', error);
    res.status(500).json({ error: 'Internal calculation error' });
  }
});

// Batch calculation endpoint
app.post('/batch-calc', async (req, res) => {
  try {
    const { state, actions }: { state: BattleState; actions: LegalAction[] } = req.body;
    
    if (!state || !actions) {
      return res.status(400).json({ error: 'Missing state or actions' });
    }

    console.log(`Batch calculating ${actions.length} actions for battle ${state.id}`);
    
    const results = await calculator.calculateDamage(state, actions);
    
    res.json({
      results,
      dexVersion: '1.0.0'
    });
  } catch (error) {
    console.error('Batch calculation error:', error);
    res.status(500).json({ error: 'Internal calculation error' });
  }
});

// Individual move calculation endpoint
app.post('/calculate-move', async (req, res) => {
  try {
    const { attacker, defender, move, field, side } = req.body;
    
    if (!attacker || !defender || !move) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }

    const result = await calculator.calculateMoveDamage(
      { p1: { active: attacker }, p2: { active: defender }, field, p1: { side } } as any,
      { type: 'move', move: move.name } as LegalAction,
      attacker,
      defender
    );
    
    res.json(result);
  } catch (error) {
    console.error('Move calculation error:', error);
    res.status(500).json({ error: 'Internal calculation error' });
  }
});

// Speed check endpoint
app.post('/speed-check', async (req, res) => {
  try {
    const { pokemon1, pokemon2 } = req.body;
    
    if (!pokemon1 || !pokemon2) {
      return res.status(400).json({ error: 'Missing pokemon parameters' });
    }

    const speed1 = calculator.getEffectiveSpeed(pokemon1);
    const speed2 = calculator.getEffectiveSpeed(pokemon2);
    
    res.json({
      pokemon1: { speed: speed1 },
      pokemon2: { speed: speed2 },
      faster: speed1 > speed2,
      speedDiff: speed1 - speed2
    });
  } catch (error) {
    console.error('Speed check error:', error);
    res.status(500).json({ error: 'Internal calculation error' });
  }
});

// Hazard damage calculation endpoint
app.post('/hazard-damage', async (req, res) => {
  try {
    const { battleState, action } = req.body;
    
    if (!battleState || !action) {
      return res.status(400).json({ error: 'Missing battleState or action' });
    }

    const hazardDamage = calculator.calculateHazardDamage(battleState, action);
    
    res.json({ hazardDamage });
  } catch (error) {
    console.error('Hazard damage calculation error:', error);
    res.status(500).json({ error: 'Internal calculation error' });
  }
});

// Error handling middleware
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(port, () => {
  console.log(`PokéAI Calc Service running on port ${port}`);
  console.log(`Health check: http://localhost:${port}/health`);
});

export { DamageCalculator };
