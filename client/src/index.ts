import { decideAction } from './orchestrator.js';
import { BattleState } from './types.js';

async function main() {
  const dummy: BattleState = {
    format: 'gen9ou',
    turn: 1,
    sides: {
      me: {
        active: {
          species: 'Garchomp',
          level: 100,
          hp: { current: 357, max: 357, percent: 100 },
          status: 'none',
          boosts: {},
          moves: [
            { id: 'earthquake', name: 'Earthquake', type: 'Ground', category: 'Physical', basePower: 100, accuracy: 1, pp: 16, priority: 0 },
            { id: 'dragonclaw', name: 'Dragon Claw', type: 'Dragon', category: 'Physical', basePower: 80, accuracy: 1, pp: 24, priority: 0 },
            { id: 'stealthrock', name: 'Stealth Rock', type: 'Rock', category: 'Status', basePower: 0, accuracy: 1, pp: 32, priority: 0 },
            { id: 'swordsdance', name: 'Swords Dance', type: 'Normal', category: 'Status', basePower: 0, accuracy: 1, pp: 32, priority: 0 }
          ],
          item: 'Rocky Helmet',
          ability: 'Rough Skin',
          types: ['Dragon','Ground'],
          nature: 'Jolly',
          stats: { hp: 357, atk: 339, def: 226, spa: 176, spd: 206, spe: 333 },
          fainted: false,
          revealed: true,
          tera: { available: true, used: false, type: 'Ground' }
        },
        bench: [],
        hazards: { stealthRock: false, spikes: 0, toxicSpikes: 0, stickyWeb: false }
      },
      opponent: {
        active: {
          species: 'Toxapex',
          level: 100,
          hp: { current: 304, max: 304, percent: 100 },
          status: 'none',
          boosts: {},
          moves: [
            { id: 'banefulbunker', name: 'Baneful Bunker', type: 'Poison', category: 'Status', basePower: 0, accuracy: 1, pp: 16, priority: 4 }
          ],
          item: null,
          ability: 'Regenerator',
          types: ['Water','Poison'],
          nature: null,
          stats: { hp: 304, atk: 121, def: 443, spa: 131, spd: 458, spe: 139 },
          fainted: false,
          revealed: true,
          tera: { available: true, used: false, type: null }
        },
        bench: [],
        hazards: { stealthRock: false, spikes: 0, toxicSpikes: 0, stickyWeb: false }
      }
    }
  };

  const decision = await decideAction(dummy);
  console.log('Best action', decision?.action);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
