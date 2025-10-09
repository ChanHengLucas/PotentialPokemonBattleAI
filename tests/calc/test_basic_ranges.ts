/**
 * Test basic damage calculation ranges
 */

import { DamageCalculator } from '../../services/calc/src/calculator';
import { BattleState, LegalAction, Pokemon } from '../../data/schemas/battle-state';

describe('Damage Calculator', () => {
  let calculator: DamageCalculator;

  beforeEach(() => {
    calculator = new DamageCalculator();
  });

  test('Dragapult vs Kingambit damage calculation', async () => {
    const battleState: BattleState = {
      id: 'test-battle',
      format: 'gen9ou',
      turn: 1,
      phase: 'battle',
      p1: {
        name: 'Player1',
        team: { pokemon: [], format: 'gen9ou' },
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
        },
        active: {
          species: 'Dragapult',
          level: 100,
          hp: 100,
          maxhp: 100,
          boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
          moves: [{ id: 'shadowball', name: 'Shadow Ball', pp: 16, maxpp: 16, power: 80, type: 'Ghost', category: 'Special' }],
          ability: 'Clear Body',
          position: 'active'
        }
      },
      p2: {
        name: 'Player2',
        team: { pokemon: [], format: 'gen9ou' },
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
        },
        active: {
          species: 'Kingambit',
          level: 100,
          hp: 100,
          maxhp: 100,
          boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
          moves: [{ id: 'suckerpunch', name: 'Sucker Punch', pp: 8, maxpp: 8, power: 70, type: 'Dark', category: 'Physical' }],
          ability: 'Defiant',
          position: 'active'
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

    const actions: LegalAction[] = [
      { type: 'move', move: 'shadowball' }
    ];

    const results = await calculator.calculateDamage(battleState, actions);

    expect(results).toHaveLength(1);
    
    const result = results[0];
    expect(result.action.type).toBe('move');
    expect(result.action.move).toBe('shadowball');
    expect(result.accuracy).toBeGreaterThan(0);
    expect(result.accuracy).toBeLessThanOrEqual(100);
    
    if (result.damage) {
      expect(result.damage.min).toBeGreaterThan(0);
      expect(result.damage.max).toBeGreaterThan(result.damage.min);
      expect(result.damage.average).toBeGreaterThan(result.damage.min);
      expect(result.damage.average).toBeLessThan(result.damage.max);
      expect(result.damage.ohko).toBeGreaterThanOrEqual(0);
      expect(result.damage.ohko).toBeLessThanOrEqual(1);
      expect(result.damage.twohko).toBeGreaterThanOrEqual(0);
      expect(result.damage.twohko).toBeLessThanOrEqual(1);
    }
    
    expect(result.speedCheck).toBeDefined();
    expect(typeof result.speedCheck.faster).toBe('boolean');
    expect(typeof result.speedCheck.speedDiff).toBe('number');
    expect(result.priority).toBeDefined();
    expect(typeof result.priority).toBe('number');
  });

  test('Speed check calculation', async () => {
    const battleState: BattleState = {
      id: 'test-battle',
      format: 'gen9ou',
      turn: 1,
      phase: 'battle',
      p1: {
        name: 'Player1',
        team: { pokemon: [], format: 'gen9ou' },
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
        },
        active: {
          species: 'Dragapult',
          level: 100,
          hp: 100,
          maxhp: 100,
          boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
          moves: [{ id: 'shadowball', name: 'Shadow Ball', pp: 16, maxpp: 16 }],
          ability: 'Clear Body',
          position: 'active'
        }
      },
      p2: {
        name: 'Player2',
        team: { pokemon: [], format: 'gen9ou' },
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
        },
        active: {
          species: 'Garchomp',
          level: 100,
          hp: 100,
          maxhp: 100,
          boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
          moves: [{ id: 'earthquake', name: 'Earthquake', pp: 16, maxpp: 16 }],
          ability: 'Rough Skin',
          position: 'active'
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

    const actions: LegalAction[] = [
      { type: 'move', move: 'shadowball' }
    ];

    const results = await calculator.calculateDamage(battleState, actions);

    expect(results).toHaveLength(1);
    
    const result = results[0];
    expect(result.speedCheck).toBeDefined();
    expect(typeof result.speedCheck.faster).toBe('boolean');
    expect(typeof result.speedCheck.speedDiff).toBe('number');
    
    // Dragapult should be faster than Garchomp
    expect(result.speedCheck.faster).toBe(true);
    expect(result.speedCheck.speedDiff).toBeGreaterThan(0);
  });

  test('Hazard damage calculation', async () => {
    const battleState: BattleState = {
      id: 'test-battle',
      format: 'gen9ou',
      turn: 1,
      phase: 'battle',
      p1: {
        name: 'Player1',
        team: { pokemon: [], format: 'gen9ou' },
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
        },
        active: {
          species: 'Dragapult',
          level: 100,
          hp: 100,
          maxhp: 100,
          boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
          moves: [{ id: 'shadowball', name: 'Shadow Ball', pp: 16, maxpp: 16 }],
          ability: 'Clear Body',
          position: 'active'
        }
      },
      p2: {
        name: 'Player2',
        team: { pokemon: [], format: 'gen9ou' },
        bench: [],
        side: {
          hazards: { spikes: 2, toxicSpikes: 1, stealthRock: true, stickyWeb: false },
          screens: { reflect: false, lightScreen: false, auroraVeil: false },
          sideConditions: {
            tailwind: false,
            trickRoom: false,
            gravity: false,
            wonderRoom: false,
            magicRoom: false
          }
        },
        active: {
          species: 'Garchomp',
          level: 100,
          hp: 100,
          maxhp: 100,
          boosts: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, accuracy: 0, evasion: 0 },
          moves: [{ id: 'earthquake', name: 'Earthquake', pp: 16, maxpp: 16 }],
          ability: 'Rough Skin',
          position: 'active'
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

    const actions: LegalAction[] = [
      { type: 'switch', pokemon: 0 }
    ];

    const results = await calculator.calculateDamage(battleState, actions);

    expect(results).toHaveLength(1);
    
    const result = results[0];
    expect(result.hazardDamage).toBeDefined();
    expect(result.hazardDamage).toBeGreaterThan(0);
  });
});
