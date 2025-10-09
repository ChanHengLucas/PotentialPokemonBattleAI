"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ShowdownClient = void 0;
const ws_1 = __importDefault(require("ws"));
const battle_state_1 = require("./battle-state");
class ShowdownClient {
    ws = null;
    battleState;
    serverUrl;
    username;
    password;
    isConnected = false;
    isInBattle = false;
    constructor(serverUrl = 'ws://sim.smogon.com:8000', username, password, calcServiceUrl, policyServiceUrl) {
        this.serverUrl = serverUrl;
        this.username = username;
        this.password = password;
        this.battleState = new battle_state_1.BattleStateManager(null, calcServiceUrl, policyServiceUrl);
    }
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new ws_1.default(this.serverUrl);
                this.ws.on('open', () => {
                    console.log('Connected to Pokémon Showdown');
                    this.isConnected = true;
                    this.authenticate();
                    resolve();
                });
                this.ws.on('message', (data) => {
                    this.handleMessage(data.toString());
                });
                this.ws.on('close', () => {
                    console.log('Disconnected from Pokémon Showdown');
                    this.isConnected = false;
                    this.isInBattle = false;
                });
                this.ws.on('error', (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                });
            }
            catch (error) {
                reject(error);
            }
        });
    }
    async disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    authenticate() {
        this.send(`|/trn ${this.username},0,${this.password}`);
    }
    handleMessage(message) {
        const lines = message.split('\n');
        for (const line of lines) {
            if (line.trim() === '')
                continue;
            console.log('Received:', line);
            // Handle different message types
            if (line.startsWith('|challstr|')) {
                this.handleChallengeString(line);
            }
            else if (line.startsWith('|updateuser|')) {
                this.handleUserUpdate(line);
            }
            else if (line.startsWith('|battle|')) {
                this.handleBattleStart(line);
            }
            else if (line.startsWith('|init|')) {
                this.handleBattleInit(line);
            }
            else if (line.startsWith('|request|')) {
                this.handleBattleRequest(line);
            }
            else if (line.startsWith('|turn|')) {
                this.handleTurn(line);
            }
            else if (line.startsWith('|win|')) {
                this.handleBattleEnd(line);
            }
            else {
                // Update battle state with any battle-related message
                if (this.isInBattle) {
                    this.battleState.updateFromShowdownMessage(line);
                }
            }
        }
    }
    handleChallengeString(message) {
        const parts = message.split('|');
        const challengeString = parts[2];
        // In a real implementation, you would need to implement the authentication protocol
        // For now, we'll assume authentication is handled elsewhere
        console.log('Challenge string received:', challengeString);
    }
    handleUserUpdate(message) {
        console.log('User update:', message);
    }
    handleBattleStart(message) {
        const parts = message.split('|');
        const battleId = parts[2];
        console.log('Battle started:', battleId);
        this.isInBattle = true;
    }
    handleBattleInit(message) {
        console.log('Battle initialized');
        this.battleState.updateFromShowdownMessage(message);
    }
    handleBattleRequest(message) {
        console.log('Battle request received');
        // Parse the request and make a decision
        this.makeBattleDecision();
    }
    handleTurn(message) {
        console.log('Turn started');
        this.battleState.updateFromShowdownMessage(message);
        // Get optimal action and send it
        this.makeBattleDecision();
    }
    handleBattleEnd(message) {
        const parts = message.split('|');
        const winner = parts[2];
        console.log('Battle ended. Winner:', winner);
        this.isInBattle = false;
    }
    async makeBattleDecision() {
        try {
            const optimalAction = await this.battleState.getOptimalAction();
            if (optimalAction) {
                this.sendAction(optimalAction);
            }
            else {
                console.log('No optimal action found, using fallback');
                this.sendFallbackAction();
            }
        }
        catch (error) {
            console.error('Error making battle decision:', error);
            this.sendFallbackAction();
        }
    }
    sendAction(action) {
        let command = '';
        switch (action.type) {
            case 'move':
                command = `move ${action.move}`;
                if (action.target) {
                    command += ` ${action.target}`;
                }
                break;
            case 'switch':
                command = `switch ${action.pokemon}`;
                break;
            case 'tera':
                command = `tera ${action.teraType}`;
                break;
            case 'mega':
                command = 'mega';
                break;
            case 'zmove':
                command = 'zmove';
                break;
            case 'dynamax':
                command = 'dynamax';
                break;
            case 'pass':
                command = 'pass';
                break;
        }
        console.log('Sending action:', command);
        this.send(command);
    }
    sendFallbackAction() {
        // Fallback to first available move
        const state = this.battleState.getState();
        const active = state.p1.active;
        if (active && active.moves.length > 0) {
            const firstMove = active.moves[0];
            this.send(`move ${firstMove.id}`);
        }
        else {
            this.send('pass');
        }
    }
    send(message) {
        if (this.ws && this.isConnected) {
            this.ws.send(message);
        }
    }
    async challengeUser(username, format = 'gen9ou') {
        this.send(`|/challenge ${username}, ${format}`);
    }
    async acceptChallenge() {
        this.send('|/accept');
    }
    async rejectChallenge() {
        this.send('|/reject');
    }
    getBattleState() {
        return this.battleState.getState();
    }
    getBattleStateJSON() {
        return this.battleState.toJSON();
    }
}
exports.ShowdownClient = ShowdownClient;
//# sourceMappingURL=showdown-client.js.map