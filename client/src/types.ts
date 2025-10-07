export type Status = 'none' | 'brn' | 'par' | 'slp' | 'frz' | 'psn' | 'tox';

export interface Stats { hp: number; atk: number; def: number; spa: number; spd: number; spe: number }
export interface Boosts { atk?: number; def?: number; spa?: number; spd?: number; spe?: number }
export interface Move { id: string; name: string; type: string; category: 'Physical'|'Special'|'Status'; basePower: number; accuracy: number; pp: number; priority: number }
export interface HPInfo { current: number; max: number; percent: number }
export interface Pokemon { species: string; level: number; gender?: string|null; hp: HPInfo; status: Status; boosts: Boosts; moves: Move[]; item?: string|null; ability?: string|null; types: string[]; nature?: string|null; stats: Stats; ivs?: Partial<Stats>; evs?: Partial<Stats>; fainted: boolean; revealed: boolean; tera: { available: boolean; used: boolean; type?: string|null } }
export interface Hazards { stealthRock?: boolean; spikes?: number; toxicSpikes?: number; stickyWeb?: boolean }
export interface SideState { active: Pokemon; bench: Pokemon[]; hazards: Hazards }
export interface BattleState { format: string; turn: number; weather?: string|null; terrain?: string|null; screens?: { reflect?: boolean; lightScreen?: boolean; auroraVeil?: boolean }; lastActions?: BattleAction[]; sides: { me: SideState; opponent: SideState } }
export type BattleAction = { type: 'MOVE'; moveId: string; target?: string|number|null } | { type: 'SWITCH'; targetIndex: number } | { type: 'TERASTALLIZE'; teraType?: string|null };
export interface CalcFeatureRow { action: BattleAction; accuracy: number; minDamagePercent: number; maxDamagePercent: number; ohkoProb: number; twohkoProb: number; speedControl: 'outspeed'|'speed_tie'|'underspeed'; hazardOnSwitchPercent: number; expectedDamagePercent: number; survivalProb: number; expectedNetGain: number }
