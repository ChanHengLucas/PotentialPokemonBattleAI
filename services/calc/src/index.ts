import express from 'express';
import { CalcRequestBody, CalcResponseBody } from './types.js';
import { evaluateActionsSimple } from './evaluator.js';

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/health', (_req, res) => {
  res.json({ ok: true });
});

app.post('/calc/evaluate', (req, res) => {
  const body = req.body as CalcRequestBody;
  if (!body || !body.battleState || !Array.isArray(body.actions)) {
    return res.status(400).json({ error: 'Invalid request body' });
  }
  const features = evaluateActionsSimple(body);
  const response: CalcResponseBody = { features };
  return res.json(response);
});

// Prefer CALC_PORT and ignore generic PORT to avoid PaaS-injected conflicts
const PORT = process.env.CALC_PORT ? Number(process.env.CALC_PORT) : 4001;
app.listen(PORT, () => {
  console.log(`Calc service listening on http://localhost:${PORT}`);
});
