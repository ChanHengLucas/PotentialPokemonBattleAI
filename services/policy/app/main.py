from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Union, Literal

app = FastAPI(title="PokeAI Policy Service", version="0.1.0")

class Move(BaseModel):
    id: str
    name: str
    type: str
    category: Literal['Physical', 'Special', 'Status']
    basePower: int
    accuracy: float
    pp: int
    priority: int

class HPInfo(BaseModel):
    current: int
    max: int
    percent: float

class Pokemon(BaseModel):
    species: str
    level: int
    hp: HPInfo
    status: Literal['none','brn','par','slp','frz','psn','tox']
    boosts: dict
    moves: List[Move]
    item: Optional[str] = None
    ability: Optional[str] = None
    types: List[str]
    nature: Optional[str] = None
    stats: dict
    fainted: bool
    revealed: bool
    tera: dict

class SideState(BaseModel):
    active: Pokemon
    bench: List[Pokemon]
    hazards: dict

class BattleActionMove(BaseModel):
    type: Literal['MOVE']
    moveId: str
    target: Optional[Union[str, int]] = None

class BattleActionSwitch(BaseModel):
    type: Literal['SWITCH']
    targetIndex: int

class BattleActionTera(BaseModel):
    type: Literal['TERASTALLIZE']
    teraType: Optional[str] = None

BattleAction = Union[BattleActionMove, BattleActionSwitch, BattleActionTera]

class BattleState(BaseModel):
    format: str
    turn: int
    sides: dict

class CalcFeatureRow(BaseModel):
    action: BattleAction
    accuracy: float
    minDamagePercent: float
    maxDamagePercent: float
    ohkoProb: float
    twohkoProb: float
    speedControl: Literal['outspeed','speed_tie','underspeed']
    hazardOnSwitchPercent: float
    expectedDamagePercent: float
    survivalProb: float
    expectedNetGain: float

class PolicyRequest(BaseModel):
    battleState: BattleState
    features: List[CalcFeatureRow]

class PolicyActionOut(BaseModel):
    action: BattleAction
    probability: float

class PolicyResponse(BaseModel):
    actions: List[PolicyActionOut]
    rationale: Optional[str] = None

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/policy/act", response_model=PolicyResponse)
async def act(req: PolicyRequest):
    # Heuristic placeholder: softmax over expectedNetGain and ohkoProb
    import math
    scores = []
    for f in req.features:
        score = 2.0 * f.expectedNetGain + 1.0 * f.ohkoProb - 0.2 * (f.hazardOnSwitchPercent / 100.0)
        if f.speedControl == 'outspeed':
            score += 0.1
        scores.append(score)
    if not scores:
        return PolicyResponse(actions=[], rationale="No legal actions provided")
    max_score = max(scores)
    exp_scores = [math.exp(s - max_score) for s in scores]
    total = sum(exp_scores)
    probs = [e / total for e in exp_scores]

    actions = [PolicyActionOut(action=req.features[i].action, probability=probs[i]) for i in range(len(req.features))]
    actions.sort(key=lambda a: a.probability, reverse=True)
    return PolicyResponse(actions=actions[:12], rationale="Heuristic policy prioritizing net gain and OHKOs")
