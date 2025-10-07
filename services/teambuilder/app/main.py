from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="PokeAI Teambuilder Service", version="0.1.0")

class EVs(BaseModel):
    hp: int = 0
    atk: int = 0
    def_: int | None = None
    spa: int = 0
    spd: int = 0
    spe: int = 0

class PokemonSet(BaseModel):
    species: str
    item: str
    ability: str
    level: int = 100
    teraType: Optional[str] = None
    evs: dict
    nature: str
    moves: List[str]

class TeamRequest(BaseModel):
    format: str
    archetype: Optional[str] = None

class TeamResponse(BaseModel):
    format: str
    team: List[PokemonSet]

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/teambuilder/generate", response_model=TeamResponse)
async def generate(req: TeamRequest):
    # Placeholder: A balanced Gen9OU-legal-ish team
    team = [
        PokemonSet(species="Gholdengo", item="Leftovers", ability="Good as Gold", teraType="Water", evs={"hp": 252, "def": 168, "spe": 88}, nature="Bold", moves=["Make It Rain", "Shadow Ball", "Recover", "Nasty Plot"]),
        PokemonSet(species="Great Tusk", item="Rocky Helmet", ability="Protosynthesis", teraType="Water", evs={"hp": 252, "def": 252, "spe": 4}, nature="Impish", moves=["Headlong Rush", "Close Combat", "Rapid Spin", "Stealth Rock"]),
        PokemonSet(species="Dragapult", item="Choice Specs", ability="Infiltrator", teraType="Ghost", evs={"spa": 252, "spe": 252, "hp": 4}, nature="Timid", moves=["Shadow Ball", "Draco Meteor", "Flamethrower", "U-turn"]),
        PokemonSet(species="Kingambit", item="Black Glasses", ability="Supreme Overlord", teraType="Dark", evs={"hp": 252, "atk": 252, "spe": 4}, nature="Adamant", moves=["Kowtow Cleave", "Sucker Punch", "Iron Head", "Swords Dance"]),
        PokemonSet(species="Ting-Lu", item="Leftovers", ability="Vessel of Ruin", teraType="Water", evs={"hp": 252, "spd": 252, "def": 4}, nature="Careful", moves=["Earthquake", "Ruination", "Spikes", "Whirlwind"]),
        PokemonSet(species="Iron Valiant", item="Booster Energy", ability="Quark Drive", teraType="Fairy", evs={"spa": 252, "spe": 252, "hp": 4}, nature="Timid", moves=["Moonblast", "Thunderbolt", "Focus Blast", "Psyshock"]),
    ]
    return TeamResponse(format=req.format, team=team)
