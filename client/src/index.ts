import { ShowdownClient } from './showdown-client';

async function main() {
  const username = process.env.POKEAI_USERNAME || 'PokeAI';
  const password = process.env.POKEAI_PASSWORD || '';
  const serverUrl = process.env.SHOWDOWN_SERVER || 'ws://sim.smogon.com:8000';
  
  const client = new ShowdownClient(serverUrl, username, password);
  
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
    
  } catch (error) {
    console.error('Failed to connect:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { ShowdownClient, BattleStateManager } from './battle-state';
export { ShowdownClient as default } from './showdown-client';
