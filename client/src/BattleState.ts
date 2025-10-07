import { BattleState, BattleAction, Move, Pokemon } from './types.js';

export class BattleStateModel {
  private state: BattleState;

  constructor(state: BattleState) {
    this.state = state;
  }

  toJSON(): BattleState { return this.state; }

  legalActions(): BattleAction[] {
    const actions: BattleAction[] = [];
    const me = this.state.sides.me;
    const active = me.active;

    for (const m of active.moves) {
      if (m.pp > 0) {
        actions.push({ type: 'MOVE', moveId: m.id });
      }
    }

    me.bench.forEach((_p, idx) => {
      actions.push({ type: 'SWITCH', targetIndex: idx });
    });

    if (me.active.tera?.available && !me.active.tera?.used) {
      actions.push({ type: 'TERASTALLIZE', teraType: me.active.tera.type ?? null });
    }

    return actions;
  }
}
