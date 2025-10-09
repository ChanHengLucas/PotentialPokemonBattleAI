"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = exports.ShowdownClient = exports.BattleStateManager = void 0;
const showdown_client_1 = require("./showdown-client");
async function main() {
    const username = process.env.POKEAI_USERNAME || 'PokeAI';
    const password = process.env.POKEAI_PASSWORD || '';
    const serverUrl = process.env.SHOWDOWN_SERVER || 'ws://sim.smogon.com:8000';
    const client = new showdown_client_1.ShowdownClient(serverUrl, username, password);
    try {
        console.log('Connecting to Pokémon Showdown...');
        await client.connect();
        console.log('Connected successfully!');
        console.log('Battle state:', client.getBattleStateJSON());
        // Keep the connection alive
        process.on('SIGINT', async () => {
            console.log('Disconnecting...');
            await client.disconnect();
            process.exit(0);
        });
    }
    catch (error) {
        console.error('Failed to connect:', error);
        process.exit(1);
    }
}
if (require.main === module) {
    main().catch(console.error);
}
var battle_state_1 = require("./battle-state");
Object.defineProperty(exports, "BattleStateManager", { enumerable: true, get: function () { return battle_state_1.BattleStateManager; } });
var showdown_client_2 = require("./showdown-client");
Object.defineProperty(exports, "ShowdownClient", { enumerable: true, get: function () { return showdown_client_2.ShowdownClient; } });
var showdown_client_3 = require("./showdown-client");
Object.defineProperty(exports, "default", { enumerable: true, get: function () { return showdown_client_3.ShowdownClient; } });
//# sourceMappingURL=index.js.map