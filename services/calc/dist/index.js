import express from 'express';
import { evaluateActionsSimple } from './evaluator.js';
const app = express();
app.use(express.json({ limit: '1mb' }));
app.get('/health', (_req, res) => {
    res.json({ ok: true });
});
app.post('/calc/evaluate', (req, res) => {
    const body = req.body;
    if (!body || !body.battleState || !Array.isArray(body.actions)) {
        return res.status(400).json({ error: 'Invalid request body' });
    }
    const features = evaluateActionsSimple(body);
    const response = { features };
    return res.json(response);
});
const PORT = process.env.PORT ? Number(process.env.PORT) : 4001;
app.listen(PORT, () => {
    console.log(`Calc service listening on http://localhost:${PORT}`);
});
