"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DamageCalculator = void 0;
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const morgan_1 = __importDefault(require("morgan"));
const calculator_1 = require("./calculator");
Object.defineProperty(exports, "DamageCalculator", { enumerable: true, get: function () { return calculator_1.DamageCalculator; } });
const app = (0, express_1.default)();
const port = process.env.PORT || 3001;
// Middleware
app.use((0, helmet_1.default)());
app.use((0, cors_1.default)());
app.use((0, morgan_1.default)('combined'));
app.use(express_1.default.json({ limit: '10mb' }));
const calculator = new calculator_1.DamageCalculator();
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
        const { battleState, actions } = req.body;
        if (!battleState || !actions) {
            return res.status(400).json({ error: 'Missing battleState or actions' });
        }
        console.log(`Calculating ${actions.length} actions for battle ${battleState.id}`);
        const results = await calculator.calculateDamage(battleState, actions);
        res.json({
            results,
            dexVersion: '1.0.0'
        });
    }
    catch (error) {
        console.error('Calculation error:', error);
        res.status(500).json({ error: 'Internal calculation error' });
    }
});
// Batch calculation endpoint
app.post('/batch-calc', async (req, res) => {
    try {
        const { state, actions } = req.body;
        if (!state || !actions) {
            return res.status(400).json({ error: 'Missing state or actions' });
        }
        console.log(`Batch calculating ${actions.length} actions for battle ${state.id}`);
        const results = await calculator.calculateDamage(state, actions);
        res.json({
            results,
            dexVersion: '1.0.0'
        });
    }
    catch (error) {
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
        const result = await calculator.calculateDamage({ p1: { active: attacker, side }, p2: { active: defender }, field }, [{ type: 'move', move: move.name }]);
        res.json(result[0]);
    }
    catch (error) {
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
    }
    catch (error) {
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
    }
    catch (error) {
        console.error('Hazard damage calculation error:', error);
        res.status(500).json({ error: 'Internal calculation error' });
    }
});
// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({ error: 'Internal server error' });
});
// Start server
app.listen(port, () => {
    console.log(`PokéAI Calc Service running on port ${port}`);
    console.log(`Health check: http://localhost:${port}/health`);
});
//# sourceMappingURL=index.js.map