import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { DamageCalculator } from './calculator';
import { BattleState, LegalAction } from './schemas/battle-state';

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));

const calculator = new DamageCalculator();

// Load format configuration
let formatConfig: any = null;
try {
  const configPath = path.join(__dirname, '../../../config/formats/gen9ou.yaml');
  const configFile = fs.readFileSync(configPath, 'utf8');
  formatConfig = yaml.load(configFile);
  console.log(`Loaded format config: ${formatConfig?.format} v${formatConfig?.version}`);
} catch (error) {
  console.warn('Could not load format config, using defaults:', error);
  formatConfig = {
    format: 'gen9ou',
    version: '1.0.0',
    dexVersion: '1.0.0'
  };
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'pokeai-calc',
    dexVersion: formatConfig?.dexVersion || '1.0.0',
    format: formatConfig?.format || 'gen9ou',
    formatVersion: formatConfig?.version || '1.0.0',
    activeFormats: ['gen9ou', 'gen8ou', 'gen7ou']
  });
});

// Main calculation endpoint
app.post('/calculate', async (req, res) => {
  try {
    const { battleState, actions, format }: { battleState: BattleState; actions: LegalAction[]; format?: string } = req.body;

    if (!battleState || !actions) {
      return res.status(400).json({ error: 'Missing battleState or actions' });
    }

    // Format gating - only support gen9ou for now
    const requestedFormat = format || 'gen9ou';
    if (requestedFormat !== 'gen9ou') {
      return res.status(501).json({ 
        error: 'Format not implemented', 
        supportedFormats: ['gen9ou'],
        requestedFormat 
      });
    }

    console.log(`Calculating ${actions.length} actions for battle ${battleState.id}`);
    
    const results = await calculator.calculateDamage(battleState, actions);
    
    res.json({
      results,
      dexVersion: formatConfig?.dexVersion || '1.0.0',
      format: formatConfig?.format || 'gen9ou',
      formatVersion: formatConfig?.version || '1.0.0'
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

    const result = await calculator.calculateDamage(
      { p1: { active: attacker, side }, p2: { active: defender }, field } as any,
      [{ type: 'move', move: move.name } as LegalAction]
    );
    res.json(result[0]);
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

    const speed1 = 100; // Simplified speed calculation
    const speed2 = 100; // Simplified speed calculation
    
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

    const hazardDamage = 0; // Simplified hazard damage calculation
    
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
