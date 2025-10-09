import { ShowdownClient } from './showdown-client';
import { BattleStateManager } from './battle-state';
import { Action } from '../data/schemas/battle-state';
import * as fs from 'fs';
import * as path from 'path';

interface LadderConfig {
  format: string;
  maxGames: number;
  username: string;
  password: string;
  serverUrl: string;
  teamPath: string;
  logPath: string;
}

class LadderClient {
  private client: ShowdownClient;
  private config: LadderConfig;
  private gameCount: number = 0;
  private wins: number = 0;
  private losses: number = 0;

  constructor(config: LadderConfig) {
    this.config = config;
    this.client = new ShowdownClient(
      config.serverUrl,
      config.username,
      config.password
    );
  }

  public async start(): Promise<void> {
    console.log(`Starting ladder client for ${this.config.format}`);
    console.log(`Max games: ${this.config.maxGames}`);
    
    try {
      // Connect to Showdown
      await this.client.connect();
      console.log('Connected to Pokémon Showdown');

      // Load team
      const team = this.loadTeam();
      if (!team) {
        throw new Error('Failed to load team');
      }

      // Submit team
      await this.submitTeam(team);
      console.log('Team submitted');

      // Start ladder loop
      await this.ladderLoop();

    } catch (error) {
      console.error('Ladder client error:', error);
      throw error;
    }
  }

  private loadTeam(): any | null {
    try {
      const teamPath = path.resolve(this.config.teamPath);
      if (!fs.existsSync(teamPath)) {
        console.error(`Team file not found: ${teamPath}`);
        return null;
      }

      const teamData = fs.readFileSync(teamPath, 'utf8');
      const team = JSON.parse(teamData);
      
      console.log(`Loaded team: ${team.team?.name || 'Unknown'}`);
      return team.team || team;
    } catch (error) {
      console.error('Error loading team:', error);
      return null;
    }
  }

  private async submitTeam(team: any): Promise<void> {
    // Convert team to Showdown format
    const showdownTeam = this.convertTeamToShowdown(team);
    
    // Submit team (this would be done through the WebSocket)
    console.log('Team converted to Showdown format');
    console.log(showdownTeam);
  }

  private convertTeamToShowdown(team: any): string {
    let showdownTeam = '';
    
    for (const pokemon of team.pokemon) {
      showdownTeam += `${pokemon.species}`;
      
      if (pokemon.nickname) {
        showdownTeam += ` (${pokemon.nickname})`;
      }
      
      if (pokemon.item) {
        showdownTeam += ` @ ${pokemon.item}`;
      }
      
      if (pokemon.ability) {
        showdownTeam += `\nAbility: ${pokemon.ability}`;
      }
      
      if (pokemon.level !== 100) {
        showdownTeam += `\nLevel: ${pokemon.level}`;
      }
      
      if (pokemon.evs) {
        const evString = Object.entries(pokemon.evs)
          .filter(([_, value]) => value > 0)
          .map(([stat, value]) => `${value} ${stat.toUpperCase()}`)
          .join(' / ');
        if (evString) {
          showdownTeam += `\nEVs: ${evString}``;
        }
      }
      
      if (pokemon.nature) {
        showdownTeam += `\n${pokemon.nature} Nature`;
      }
      
      if (pokemon.moves && pokemon.moves.length > 0) {
        showdownTeam += '\n- ' + pokemon.moves.join('\n- ');
      }
      
      showdownTeam += '\n\n';
    }
    
    return showdownTeam.trim();
  }

  private async ladderLoop(): Promise<void> {
    while (this.gameCount < this.config.maxGames) {
      try {
        console.log(`\n--- Game ${this.gameCount + 1}/${this.config.maxGames} ---`);
        
        // Request a battle
        await this.requestBattle();
        
        // Wait for battle to start
        await this.waitForBattle();
        
        // Play the battle
        const result = await this.playBattle();
        
        // Record result
        if (result === 'win') {
          this.wins++;
          console.log('Victory!');
        } else if (result === 'loss') {
          this.losses++;
          console.log('Defeat!');
        }
        
        this.gameCount++;
        
        // Show stats
        this.showStats();
        
        // Wait before next game
        await this.sleep(5000);
        
      } catch (error) {
        console.error('Error in ladder loop:', error);
        await this.sleep(10000); // Wait longer on error
      }
    }
    
    console.log('\nLadder session completed!');
    this.showFinalStats();
  }

  private async requestBattle(): Promise<void> {
    // Request a battle for the format
    console.log(`Requesting battle for ${this.config.format}...`);
    // This would be implemented through the WebSocket client
  }

  private async waitForBattle(): Promise<void> {
    console.log('Waiting for battle to start...');
    // This would wait for battle initialization messages
  }

  private async playBattle(): Promise<string> {
    console.log('Battle started! Playing...');
    
    let turn = 0;
    const maxTurns = 200; // Prevent infinite battles
    
    while (turn < maxTurns) {
      try {
        // Get current battle state
        const battleState = this.client.getBattleState();
        
        if (battleState.phase === 'finished') {
          return battleState.winner === 'p1' ? 'win' : 'loss';
        }
        
        if (battleState.phase !== 'battle') {
          await this.sleep(1000);
          continue;
        }
        
        // Get legal actions
        const legalActions = await this.getLegalActions(battleState);
        if (legalActions.length === 0) {
          console.log('No legal actions available');
          break;
        }
        
        // Get optimal action
        const action = await this.getOptimalAction(battleState, legalActions);
        if (!action) {
          console.log('No optimal action found, using fallback');
          break;
        }
        
        // Apply safety layer
        const safeAction = this.applySafetyLayer(action, battleState, legalActions);
        
        // Send action
        await this.sendAction(safeAction);
        
        // Log telemetry
        this.logTelemetry(battleState, legalActions, safeAction);
        
        turn++;
        await this.sleep(1000); // Wait for next turn
        
      } catch (error) {
        console.error(`Error in turn ${turn}:`, error);
        break;
      }
    }
    
    return 'timeout';
  }

  private async getLegalActions(battleState: any): Promise<any[]> {
    // This would get legal actions from the battle state
    return [];
  }

  private async getOptimalAction(battleState: any, legalActions: any[]): Promise<Action | null> {
    try {
      // Get calc results
      const calcResults = await this.getCalcResults(battleState, legalActions);
      
      // Get policy recommendation
      const policyResult = await this.getPolicyRecommendation(battleState, calcResults);
      
      return policyResult;
    } catch (error) {
      console.error('Error getting optimal action:', error);
      return null;
    }
  }

  private async getCalcResults(battleState: any, legalActions: any[]): Promise<any[]> {
    try {
      const response = await fetch('http://localhost:3001/batch-calc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          state: battleState,
          actions: legalActions
        })
      });
      
      if (!response.ok) {
        throw new Error(`Calc service error: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.results;
    } catch (error) {
      console.error('Error getting calc results:', error);
      return [];
    }
  }

  private async getPolicyRecommendation(battleState: any, calcResults: any[]): Promise<Action | null> {
    try {
      const response = await fetch('http://localhost:8000/policy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          battleState,
          calcResults
        })
      });
      
      if (!response.ok) {
        throw new Error(`Policy service error: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data.action;
    } catch (error) {
      console.error('Error getting policy recommendation:', error);
      return null;
    }
  }

  private applySafetyLayer(action: Action, battleState: any, legalActions: any[]): Action {
    // Never Struggle
    if (action.type === 'move' && action.move === 'struggle') {
      console.log('Safety: Preventing Struggle');
      return this.getFallbackAction(legalActions);
    }
    
    // Avoid 0% accurate options
    if (action.type === 'move') {
      // This would check move accuracy
      // For now, just return the action
    }
    
    // Don't switch into guaranteed lethal hazards
    if (action.type === 'switch') {
      // This would check hazard damage
      // For now, just return the action
    }
    
    return action;
  }

  private getFallbackAction(legalActions: any[]): Action {
    // Return first legal action as fallback
    if (legalActions.length > 0) {
      return legalActions[0];
    }
    
    // Ultimate fallback
    return { type: 'pass' };
  }

  private async sendAction(action: Action): Promise<void> {
    // This would send the action through the WebSocket
    console.log(`Sending action: ${action.type} ${action.move || action.pokemon || ''}`);
  }

  private logTelemetry(battleState: any, legalActions: any[], chosenAction: Action): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      turn: battleState.turn,
      game: this.gameCount + 1,
      legalActions: legalActions.length,
      chosenAction,
      battleState: {
        p1_hp: battleState.p1?.active?.hp || 0,
        p2_hp: battleState.p2?.active?.hp || 0,
        phase: battleState.phase
      }
    };
    
    // Write to log file
    const logPath = path.resolve(this.config.logPath);
    const logDir = path.dirname(logPath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    
    fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  }

  private showStats(): void {
    const total = this.wins + this.losses;
    const winRate = total > 0 ? (this.wins / total * 100).toFixed(1) : '0.0';
    
    console.log(`Stats: ${this.wins}W-${this.losses}L (${winRate}% win rate)`);
  }

  private showFinalStats(): void {
    const total = this.wins + this.losses;
    const winRate = total > 0 ? (this.wins / total * 100).toFixed(1) : '0.0';
    
    console.log('\n=== Final Stats ===');
    console.log(`Games played: ${this.gameCount}`);
    console.log(`Wins: ${this.wins}`);
    console.log(`Losses: ${this.losses}`);
    console.log(`Win rate: ${winRate}%`);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  const config: LadderConfig = {
    format: 'gen9ou',
    maxGames: 3,
    username: 'PokeAI',
    password: '',
    serverUrl: 'ws://sim.smogon.com:8000',
    teamPath: 'data/teams/latest.json',
    logPath: 'data/logs/ladder.log'
  };
  
  // Parse arguments
  for (let i = 0; i < args.length; i += 2) {
    const flag = args[i];
    const value = args[i + 1];
    
    switch (flag) {
      case '--format':
        config.format = value;
        break;
      case '--maxGames':
        config.maxGames = parseInt(value);
        break;
      case '--username':
        config.username = value;
        break;
      case '--password':
        config.password = value;
        break;
      case '--server':
        config.serverUrl = value;
        break;
      case '--team':
        config.teamPath = value;
        break;
      case '--log':
        config.logPath = value;
        break;
    }
  }
  
  const ladderClient = new LadderClient(config);
  
  try {
    await ladderClient.start();
  } catch (error) {
    console.error('Ladder client failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

export { LadderClient };
