import WebSocket from 'ws';
import { BattleStateManager } from './battle-state';
import { Action } from './schemas/battle-state';

export class ShowdownClient {
  private ws: WebSocket | null = null;
  private battleState: BattleStateManager;
  private serverUrl: string;
  private username: string;
  private password: string;
  private isConnected: boolean = false;
  private isInBattle: boolean = false;

  constructor(
    serverUrl: string = 'ws://sim.smogon.com:8000',
    username: string,
    password: string,
    calcServiceUrl?: string,
    policyServiceUrl?: string
  ) {
    this.serverUrl = serverUrl;
    this.username = username;
    this.password = password;
    this.battleState = new BattleStateManager(null, calcServiceUrl, policyServiceUrl);
  }

  public async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.serverUrl);
        
        this.ws.on('open', () => {
          console.log('Connected to Pokémon Showdown');
          this.isConnected = true;
          this.authenticate();
          resolve();
        });

        this.ws.on('message', (data: Buffer) => {
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

      } catch (error) {
        reject(error);
      }
    });
  }

  public async disconnect(): Promise<void> {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private authenticate(): void {
    this.send(`|/trn ${this.username},0,${this.password}`);
  }

  private handleMessage(message: string): void {
    const lines = message.split('\n');
    
    for (const line of lines) {
      if (line.trim() === '') continue;
      
      console.log('Received:', line);
      
      // Handle different message types
      if (line.startsWith('|challstr|')) {
        this.handleChallengeString(line);
      } else if (line.startsWith('|updateuser|')) {
        this.handleUserUpdate(line);
      } else if (line.startsWith('|battle|')) {
        this.handleBattleStart(line);
      } else if (line.startsWith('|init|')) {
        this.handleBattleInit(line);
      } else if (line.startsWith('|request|')) {
        this.handleBattleRequest(line);
      } else if (line.startsWith('|turn|')) {
        this.handleTurn(line);
      } else if (line.startsWith('|win|')) {
        this.handleBattleEnd(line);
      } else {
        // Update battle state with any battle-related message
        if (this.isInBattle) {
          this.battleState.updateFromShowdownMessage(line);
        }
      }
    }
  }

  private handleChallengeString(message: string): void {
    const parts = message.split('|');
    const challengeString = parts[2];
    
    // In a real implementation, you would need to implement the authentication protocol
    // For now, we'll assume authentication is handled elsewhere
    console.log('Challenge string received:', challengeString);
  }

  private handleUserUpdate(message: string): void {
    console.log('User update:', message);
  }

  private handleBattleStart(message: string): void {
    const parts = message.split('|');
    const battleId = parts[2];
    console.log('Battle started:', battleId);
    this.isInBattle = true;
  }

  private handleBattleInit(message: string): void {
    console.log('Battle initialized');
    this.battleState.updateFromShowdownMessage(message);
  }

  private handleBattleRequest(message: string): void {
    console.log('Battle request received');
    // Parse the request and make a decision
    this.makeBattleDecision();
  }

  private handleTurn(message: string): void {
    console.log('Turn started');
    this.battleState.updateFromShowdownMessage(message);
    
    // Get optimal action and send it
    this.makeBattleDecision();
  }

  private handleBattleEnd(message: string): void {
    const parts = message.split('|');
    const winner = parts[2];
    console.log('Battle ended. Winner:', winner);
    this.isInBattle = false;
  }

  private async makeBattleDecision(): Promise<void> {
    try {
      const optimalAction = await this.battleState.getOptimalAction();
      
      if (optimalAction) {
        this.sendAction(optimalAction);
      } else {
        console.log('No optimal action found, using fallback');
        this.sendFallbackAction();
      }
    } catch (error) {
      console.error('Error making battle decision:', error);
      this.sendFallbackAction();
    }
  }

  private sendAction(action: Action): void {
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

  private sendFallbackAction(): void {
    // Fallback to first available move
    const state = this.battleState.getState();
    const active = state.p1.active;
    
    if (active && active.moves.length > 0) {
      const firstMove = active.moves[0];
      this.send(`move ${firstMove.id}`);
    } else {
      this.send('pass');
    }
  }

  private send(message: string): void {
    if (this.ws && this.isConnected) {
      this.ws.send(message);
    }
  }

  public async challengeUser(username: string, format: string = 'gen9ou'): Promise<void> {
    this.send(`|/challenge ${username}, ${format}`);
  }

  public async acceptChallenge(): Promise<void> {
    this.send('|/accept');
  }

  public async rejectChallenge(): Promise<void> {
    this.send('|/reject');
  }

  public getBattleState(): any {
    return this.battleState.getState();
  }

  public getBattleStateJSON(): string {
    return this.battleState.toJSON();
  }
}
