import axios from 'axios';
import { BattleStateModel } from './BattleState.js';
import { BattleAction, BattleState, CalcFeatureRow } from './types.js';

const CALC_URL = process.env.CALC_URL || 'http://localhost:4001/calc/evaluate';
const POLICY_URL = process.env.POLICY_URL || 'http://localhost:8001/policy/act';

export async function decideAction(state: BattleState): Promise<{ action: BattleAction; features: CalcFeatureRow[] } | null> {
  const model = new BattleStateModel(state);
  const actions = model.legalActions();
  if (actions.length === 0) return null;

  const { data: calcResp } = await axios.post(CALC_URL, { battleState: model.toJSON(), actions });
  const { data: policyResp } = await axios.post(POLICY_URL, { battleState: model.toJSON(), features: calcResp.features });

  const best = policyResp.actions?.[0];
  if (!best) return null;
  return { action: best.action, features: calcResp.features };
}
