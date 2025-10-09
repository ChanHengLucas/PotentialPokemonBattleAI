export interface Pokemon {
  species: string;
  nickname?: string;
  level: number;
  gender?: 'M' | 'F' | 'N';
  shiny?: boolean;
  hp: number;
  maxhp: number;
  status?: StatusCondition;
  statusData?: StatusData;
  boosts: StatBoosts;
  moves: Move[];
  item?: string;
  ability: string;
  teraType?: string;
  terastallized?: boolean;
  position: 'active' | number; // 'active' or bench position (0-5)
}

export interface StatusCondition {
  name: 'par' | 'psn' | 'tox' | 'brn' | 'frz' | 'slp' | 'fnt';
  turnsLeft?: number;
}

export interface StatusData {
  toxicTurns?: number;
  sleepTurns?: number;
  freezeTurns?: number;
}

export interface StatBoosts {
  atk: number;
  def: number;
  spa: number;
  spd: number;
  spe: number;
  accuracy: number;
  evasion: number;
}

export interface Move {
  id: string;
  name: string;
  pp: number;
  maxpp: number;
  disabled?: boolean;
  target?: string;
  type?: string;
  category?: string;
  power?: number;
  accuracy?: number;
  priority?: number;
}

export interface Team {
  pokemon: Pokemon[];
  name?: string;
  format: string;
}

export interface Field {
  weather?: Weather;
  terrain?: Terrain;
  pseudoWeather?: PseudoWeather[];
  hazards: Hazards;
  screens: Screens;
  sideConditions: SideConditions;
}

export interface Weather {
  type: 'sunnyday' | 'raindance' | 'sandstorm' | 'hail' | 'snow';
  turnsLeft?: number;
}

export interface Terrain {
  type: 'electric' | 'grassy' | 'misty' | 'psychic';
  turnsLeft?: number;
}

export interface PseudoWeather {
  type: string;
  turnsLeft?: number;
}

export interface Hazards {
  spikes: number;
  toxicSpikes: number;
  stealthRock: boolean;
  stickyWeb: boolean;
}

export interface Screens {
  reflect: boolean;
  lightScreen: boolean;
  auroraVeil: boolean;
}

export interface SideConditions {
  tailwind: boolean;
  tailwindTurns?: number;
  trickRoom: boolean;
  trickRoomTurns?: number;
  gravity: boolean;
  gravityTurns?: number;
  wonderRoom: boolean;
  wonderRoomTurns?: number;
  magicRoom: boolean;
  magicRoomTurns?: number;
}

export interface BattleState {
  // Game metadata
  id: string;
  format: string;
  turn: number;
  phase: 'preparation' | 'team-preview' | 'battle' | 'finished';
  winner?: 'p1' | 'p2' | 'tie';
  
  // Player information
  p1: Player;
  p2: Player;
  
  // Field state
  field: Field;
  
  // Battle log
  log: BattleLogEntry[];
  
  // Last actions
  lastActions: {
    p1?: Action;
    p2?: Action;
  };
  
  // Opponent modeling
  opponentModel: OpponentModel;
}

export interface Player {
  name: string;
  team: Team;
  active?: Pokemon;
  bench: Pokemon[];
  side: Field;
  lastMove?: string;
  lastSwitch?: number;
  teraUsed?: boolean;
}

export interface Action {
  type: 'move' | 'switch' | 'tera' | 'mega' | 'zmove' | 'dynamax' | 'pass';
  target?: string | number;
  move?: string;
  pokemon?: string | number;
  teraType?: string;
}

export interface BattleLogEntry {
  turn: number;
  action: string;
  player: 'p1' | 'p2' | 'system';
  details?: any;
}

export interface OpponentModel {
  // Probabilistic distributions over hidden information
  evDistributions: { [pokemonId: string]: EVDistribution };
  itemDistributions: { [pokemonId: string]: ItemDistribution };
  teraDistributions: { [pokemonId: string]: TeraDistribution };
  moveDistributions: { [pokemonId: string]: MoveDistribution };
  
  // Inferred information
  revealedSets: { [pokemonId: string]: Partial<Pokemon> };
  likelyArchetype?: string;
  playstyle?: 'aggressive' | 'defensive' | 'balanced' | 'stall' | 'hyperoffense';
}

export interface EVDistribution {
  hp: number[];
  atk: number[];
  def: number[];
  spa: number[];
  spd: number[];
  spe: number[];
}

export interface ItemDistribution {
  [itemName: string]: number; // probability
}

export interface TeraDistribution {
  [teraType: string]: number; // probability
}

export interface MoveDistribution {
  [moveName: string]: number; // probability
}

export interface LegalAction {
  type: 'move' | 'switch' | 'tera' | 'mega' | 'zmove' | 'dynamax' | 'pass';
  target?: string | number;
  move?: string;
  pokemon?: string | number;
  teraType?: string;
  disabled?: boolean;
  reason?: string;
}

export interface CalcResult {
  action: LegalAction;
  damage?: {
    min: number;
    max: number;
    average: number;
    ohko: number; // probability
    twohko: number; // probability
  };
  accuracy: number;
  speedCheck: {
    faster: boolean;
    speedDiff: number;
  };
  hazardDamage?: number;
  statusChance?: number;
  expectedSurvival?: number;
  expectedGain?: number;
  priority: number;
}

export interface PolicyResult {
  action: LegalAction;
  probability: number;
  reasoning: string;
  confidence: number;
}

export interface TeamBuilderInput {
  format: string;
  usageStats?: UsageStats;
  threats?: string[];
  archetype?: string;
  constraints?: TeamConstraints;
}

export interface TeamConstraints {
  requiredPokemon?: string[];
  bannedPokemon?: string[];
  requiredRoles?: string[];
  playstyle?: 'offense' | 'defense' | 'balance' | 'stall';
}

export interface UsageStats {
  [pokemonName: string]: {
    usage: number;
    moves: { [moveName: string]: number };
    items: { [itemName: string]: number };
    abilities: { [abilityName: string]: number };
    spreads: { [spread: string]: number };
    teammates: { [pokemonName: string]: number };
  };
}

export interface TeamBuilderOutput {
  team: Team;
  synergy: number;
  coverage: string[];
  winConditions: string[];
  threats: string[];
  score: number;
}
