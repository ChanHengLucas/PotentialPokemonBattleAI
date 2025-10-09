import {
  BattleState,
  Pokemon,
  Player,
  Field,
  Action,
  LegalAction,
  OpponentModel,
  BattleLogEntry,
  StatBoosts,
  StatusCondition,
  Move,
  Team
} from '../../data/schemas/battle-state';

export class BattleStateManager {
  private state: BattleState;
  private websocket: any;
  private calcServiceUrl: string;
  private policyServiceUrl: string;

  constructor(
    websocket: any,
    calcServiceUrl: string = 'http://localhost:3001',
    policyServiceUrl: string = 'http://localhost:8000'
  ) {
    this.websocket = websocket;
    this.calcServiceUrl = calcServiceUrl;
    this.policyServiceUrl = policyServiceUrl;
    this.state = this.initializeEmptyState();
  }

  private initializeEmptyState(): BattleState {
    return {
      id: '',
      format: '',
      turn: 0,
      phase: 'preparation',
      p1: {
        name: '',
        team: { pokemon: [], format: '' },
        bench: [],
        side: {
          hazards: { spikes: 0, toxicSpikes: 0, stealthRock: false, stickyWeb: false },
          screens: { reflect: false, lightScreen: false, auroraVeil: false },
          sideConditions: {
            tailwind: false,
            trickRoom: false,
            gravity: false,
            wonderRoom: false,
            magicRoom: false
          }
        }
      },
      p2: {
        name: '',
        team: { pokemon: [], format: '' },
        bench: [],
        side: {
          hazards: { spikes: 0, toxicSpikes: 0, stealthRock: false, stickyWeb: false },
          screens: { reflect: false, lightScreen: false, auroraVeil: false },
          sideConditions: {
            tailwind: false,
            trickRoom: false,
            gravity: false,
            wonderRoom: false,
            magicRoom: false
          }
        }
      },
      field: {
        hazards: { spikes: 0, toxicSpikes: 0, stealthRock: false, stickyWeb: false },
        screens: { reflect: false, lightScreen: false, auroraVeil: false },
        sideConditions: {
          tailwind: false,
          trickRoom: false,
          gravity: false,
          wonderRoom: false,
          magicRoom: false
        }
      },
      log: [],
      lastActions: {},
      opponentModel: {
        evDistributions: {},
        itemDistributions: {},
        teraDistributions: {},
        moveDistributions: {},
        revealedSets: {}
      }
    };
  }

  public getState(): BattleState {
    return this.state;
  }

  public toJSON(): string {
    return JSON.stringify(this.state, null, 2);
  }

  public async getLegalActions(): Promise<LegalAction[]> {
    const actions: LegalAction[] = [];
    
    // Get active Pokémon
    const active = this.state.p1.active;
    if (!active) return actions;

    // Add move actions (with PP and disabled checks)
    for (const move of active.moves) {
      if (move.pp > 0 && !move.disabled) {
        actions.push({
          type: 'move',
          move: move.id,
          target: move.target
        });
      }
    }

    // Add switch actions (only to healthy Pokémon)
    for (let i = 0; i < this.state.p1.bench.length; i++) {
      const pokemon = this.state.p1.bench[i];
      if (pokemon.hp > 0) {
        actions.push({
          type: 'switch',
          pokemon: i
        });
      }
    }

    // Add tera action if available (one-time use)
    if (!this.state.p1.teraUsed && active.teraType) {
      actions.push({
        type: 'tera',
        teraType: active.teraType
      });
    }

    // Add mega evolution if available
    if (active.item && active.item.includes('ite') && !active.terastallized) {
      actions.push({
        type: 'mega'
      });
    }

    // Add Z-move if available
    if (active.item && active.item.includes('Z') && !active.terastallized) {
      actions.push({
        type: 'zmove'
      });
    }

    // Add Dynamax if available
    if (!active.terastallized && this.state.turn <= 10) {
      actions.push({
        type: 'dynamax'
      });
    }

    // If no legal actions, add pass
    if (actions.length === 0) {
      actions.push({
        type: 'pass'
      });
    }

    return actions;
  }

  public async getOptimalAction(): Promise<Action | null> {
    try {
      // Get legal actions
      const legalActions = await this.getLegalActions();
      if (legalActions.length === 0) return null;

      // Get calc results for all legal actions
      const calcResults = await this.getCalcResults(legalActions);
      
      // Get policy recommendation
      const policyResult = await this.getPolicyRecommendation(calcResults);
      
      return this.convertToAction(policyResult.action);
    } catch (error) {
      console.error('Error getting optimal action:', error);
      return null;
    }
  }

  private async getCalcResults(actions: LegalAction[]): Promise<any[]> {
    try {
      const response = await fetch(`${this.calcServiceUrl}/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          battleState: this.state,
          actions
        })
      });
      
      if (!response.ok) {
        throw new Error(`Calc service error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting calc results:', error);
      return [];
    }
  }

  private async getPolicyRecommendation(calcResults: any[]): Promise<any> {
    try {
      const response = await fetch(`${this.policyServiceUrl}/policy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          battleState: this.state,
          calcResults
        })
      });
      
      if (!response.ok) {
        throw new Error(`Policy service error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting policy recommendation:', error);
      return null;
    }
  }

  private convertToAction(legalAction: LegalAction): Action {
    return {
      type: legalAction.type,
      target: legalAction.target,
      move: legalAction.move,
      pokemon: legalAction.pokemon,
      teraType: legalAction.teraType
    };
  }

  public updateFromShowdownMessage(message: any): void {
    // Parse different types of Showdown messages
    if (message.startsWith('|init|')) {
      this.handleInitMessage(message);
    } else if (message.startsWith('|player|')) {
      this.handlePlayerMessage(message);
    } else if (message.startsWith('|poke|')) {
      this.handlePokeMessage(message);
    } else if (message.startsWith('|switch|') || message.startsWith('|drag|')) {
      this.handleSwitchMessage(message);
    } else if (message.startsWith('|move|')) {
      this.handleMoveMessage(message);
    } else if (message.startsWith('|turn|')) {
      this.handleTurnMessage(message);
    } else if (message.startsWith('|win|')) {
      this.handleWinMessage(message);
    } else if (message.startsWith('|field|')) {
      this.handleFieldMessage(message);
    } else if (message.startsWith('|side|')) {
      this.handleSideMessage(message);
    }
  }

  private handleInitMessage(message: string): void {
    const parts = message.split('|');
    this.state.format = parts[2];
    this.state.id = parts[3];
  }

  private handlePlayerMessage(message: string): void {
    const parts = message.split('|');
    const playerId = parts[2] === this.state.p1.name ? 'p1' : 'p2';
    const playerName = parts[3];
    
    if (playerId === 'p1') {
      this.state.p1.name = playerName;
    } else {
      this.state.p2.name = playerName;
    }
  }

  private handlePokeMessage(message: string): void {
    const parts = message.split('|');
    const playerId = parts[2] === this.state.p1.name ? 'p1' : 'p2';
    const pokemonData = this.parsePokemonData(parts[3]);
    
    if (playerId === 'p1') {
      this.state.p1.team.pokemon.push(pokemonData);
    } else {
      this.state.p2.team.pokemon.push(pokemonData);
    }
  }

  private handleSwitchMessage(message: string): void {
    const parts = message.split('|');
    const playerId = parts[2] === this.state.p1.name ? 'p1' : 'p2';
    const pokemonName = parts[3];
    const pokemonData = this.parsePokemonData(parts[4]);
    
    if (playerId === 'p1') {
      this.state.p1.active = pokemonData;
      this.state.p1.lastSwitch = this.state.turn;
    } else {
      this.state.p2.active = pokemonData;
      this.state.p2.lastSwitch = this.state.turn;
    }
  }

  private handleMoveMessage(message: string): void {
    const parts = message.split('|');
    const playerId = parts[2] === this.state.p1.name ? 'p1' : 'p2';
    const moveName = parts[3];
    
    if (playerId === 'p1') {
      this.state.p1.lastMove = moveName;
    } else {
      this.state.p2.lastMove = moveName;
    }
    
    this.addLogEntry({
      turn: this.state.turn,
      action: `used ${moveName}`,
      player: playerId,
      details: { move: moveName }
    });
  }

  private handleTurnMessage(message: string): void {
    const parts = message.split('|');
    this.state.turn = parseInt(parts[2]);
    this.state.phase = 'battle';
  }

  private handleWinMessage(message: string): void {
    const parts = message.split('|');
    this.state.winner = parts[2] === this.state.p1.name ? 'p1' : 'p2';
    this.state.phase = 'finished';
  }

  private handleFieldMessage(message: string): void {
    const parts = message.split('|');
    // Parse field conditions like weather, terrain, etc.
    // Implementation depends on specific field effects
  }

  private handleSideMessage(message: string): void {
    const parts = message.split('|');
    const playerId = parts[2] === this.state.p1.name ? 'p1' : 'p2';
    // Parse side conditions like hazards, screens, etc.
    // Implementation depends on specific side effects
  }

  private parsePokemonData(pokemonString: string): Pokemon {
    // Parse Pokémon data from Showdown format
    // This is a simplified version - full implementation would handle all cases
    const parts = pokemonString.split(',');
    const species = parts[0];
    const level = parseInt(parts[1]) || 100;
    
    return {
      species,
      level,
      hp: 100,
      maxhp: 100,
      boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
      moves: [],
      ability: '',
      position: 'active'
    };
  }

  private addLogEntry(entry: BattleLogEntry): void {
    this.state.log.push(entry);
  }

  public updateOpponentModel(): void {
    // Update probabilistic distributions based on revealed information
    // This is a complex process that involves Bayesian inference
    // Implementation would depend on specific modeling requirements
  }

  public applySafetyLayer(action: Action, legalActions: LegalAction[]): Action {
    // Never Struggle
    if (action.type === 'move' && action.move === 'struggle') {
      console.log('Safety: Preventing Struggle');
      return this.getFallbackAction(legalActions);
    }
    
    // Avoid 0% accurate options
    if (action.type === 'move' && action.move) {
      const move = this.state.p1.active?.moves.find(m => m.id === action.move);
      if (move && move.accuracy === 0) {
        console.log('Safety: Avoiding 0% accuracy move');
        return this.getFallbackAction(legalActions);
      }
    }
    
    // Don't switch into guaranteed lethal hazards
    if (action.type === 'switch' && typeof action.pokemon === 'number') {
      const switchPokemon = this.state.p1.bench[action.pokemon];
      if (switchPokemon) {
        const hazardDamage = this.calculateHazardDamage(switchPokemon);
        if (hazardDamage >= switchPokemon.hp) {
          console.log('Safety: Preventing lethal hazard damage');
          return this.getFallbackAction(legalActions);
        }
      }
    }
    
    // Preserve unique role holders when hazards/speed matter
    if (this.shouldPreserveRoleHolder(action)) {
      console.log('Safety: Preserving unique role holder');
      return this.getFallbackAction(legalActions);
    }
    
    return action;
  }

  private getFallbackAction(legalActions: LegalAction[]): Action {
    // Prefer moves over switches
    const moveActions = legalActions.filter(a => a.type === 'move');
    if (moveActions.length > 0) {
      return moveActions[0];
    }
    
    // Then switches
    const switchActions = legalActions.filter(a => a.type === 'switch');
    if (switchActions.length > 0) {
      return switchActions[0];
    }
    
    // Ultimate fallback
    return { type: 'pass' };
  }

  private calculateHazardDamage(pokemon: Pokemon): number {
    let damage = 0;
    const hazards = this.state.p2.side.hazards;
    
    if (hazards.stealthRock) {
      // Simplified stealth rock damage calculation
      damage += 12.5;
    }
    
    if (hazards.spikes > 0) {
      damage += hazards.spikes * 12.5;
    }
    
    if (hazards.toxicSpikes > 0) {
      damage += 12.5;
    }
    
    return damage;
  }

  private shouldPreserveRoleHolder(action: Action): boolean {
    // This would check if the action would sacrifice a unique role holder
    // For now, return false (no preservation needed)
    return false;
  }
}
