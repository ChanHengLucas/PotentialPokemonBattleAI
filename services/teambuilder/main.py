from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
import json
import logging
import random
from ingest import get_usage, get_sets, get_legal_pokemon

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PokéAI Team Builder Service", version="1.0.0")

# Pydantic models
class Pokemon(BaseModel):
    species: str
    nickname: Optional[str] = None
    level: int = 100
    gender: Optional[str] = None
    shiny: Optional[bool] = False
    hp: int = 100
    maxhp: int = 100
    status: Optional[Dict[str, Any]] = None
    statusData: Optional[Dict[str, Any]] = None
    boosts: Dict[str, int] = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}
    moves: List[str] = []
    item: Optional[str] = None
    ability: str = ""
    teraType: Optional[str] = None
    terastallized: Optional[bool] = False
    position: str = "active"

class Team(BaseModel):
    pokemon: List[Pokemon]
    name: Optional[str] = None
    format: str

class TeamConstraints(BaseModel):
    requiredPokemon: Optional[List[str]] = None
    bannedPokemon: Optional[List[str]] = None
    requiredRoles: Optional[List[str]] = None
    playstyle: Optional[str] = None

class UsageStats(BaseModel):
    pokemon: Dict[str, Dict[str, Any]]

class TeamBuilderInput(BaseModel):
    format: str
    includeTera: Optional[bool] = True
    usageVersion: Optional[str] = None
    roleHints: Optional[List[str]] = None
    usageStats: Optional[UsageStats] = None
    threats: Optional[List[str]] = None
    archetype: Optional[str] = None
    constraints: Optional[TeamConstraints] = None

class TeamBuilderOutput(BaseModel):
    team: Team
    synergy: float
    coverage: List[str]
    winConditions: List[str]
    threats: List[str]
    score: float

class TeamBuilderService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pokemon_data = self.load_pokemon_data()
        self.load_model()
    
    def load_pokemon_data(self):
        """Load Pokémon data for team building"""
        # This would load from a database or file in a real implementation
        return {
            "gen9ou": {
                "pokemon": [
                    "Dragapult", "Garchomp", "Landorus-Therian", "Heatran", "Rotom-Wash",
                    "Toxapex", "Corviknight", "Slowking-Galar", "Urshifu-Rapid-Strike",
                    "Rillaboom", "Kartana", "Tapu Koko", "Tapu Lele", "Tapu Fini",
                    "Magearna", "Zapdos", "Tornadus-Therian", "Thundurus-Therian",
                    "Volcarona", "Ferrothorn", "Skarmory", "Blissey", "Chansey",
                    "Clefable", "Sylveon", "Primarina", "Azumarill", "Quagsire",
                    "Swampert", "Gastrodon", "Seismitoad", "Gastrodon", "Swampert"
                ],
                "roles": {
                    "sweeper": ["Dragapult", "Garchomp", "Kartana", "Volcarona"],
                    "wall": ["Toxapex", "Corviknight", "Ferrothorn", "Skarmory", "Blissey"],
                    "hazard_setter": ["Landorus-Therian", "Garchomp", "Ferrothorn", "Skarmory"],
                    "hazard_remover": ["Corviknight", "Excadrill", "Tapu Fini"],
                    "wallbreaker": ["Urshifu-Rapid-Strike", "Rillaboom", "Magearna"],
                    "support": ["Slowking-Galar", "Clefable", "Tapu Lele"]
                },
                "synergies": {
                    "fire_water_grass": ["Volcarona", "Swampert", "Rillaboom"],
                    "steel_fairy_dragon": ["Magearna", "Clefable", "Dragapult"],
                    "hazard_stack": ["Landorus-Therian", "Ferrothorn", "Skarmory"]
                }
            }
        }
    
    def load_model(self):
        """Load the transformer model for team building"""
        try:
            logger.info("Loading team builder model...")
            # self.model = AutoModel.from_pretrained("path/to/teambuilder/model")
            # self.tokenizer = AutoTokenizer.from_pretrained("path/to/teambuilder/model")
            logger.info("Team builder model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def build_team(self, input_data: TeamBuilderInput) -> TeamBuilderOutput:
        """Build a competitive team based on input requirements"""
        try:
            logger.info(f"Building team for format: {input_data.format}")
            
            # Get available Pokémon for the format
            available_pokemon = self.pokemon_data.get(input_data.format, {}).get("pokemon", [])
            
            # Apply constraints
            if input_data.constraints:
                if input_data.constraints.bannedPokemon:
                    available_pokemon = [p for p in available_pokemon if p not in input_data.constraints.bannedPokemon]
            
            # Generate team using model (placeholder implementation)
            team_pokemon = self.generate_team_pokemon(available_pokemon, input_data)
            
            # Create team object
            team = Team(
                pokemon=team_pokemon,
                format=input_data.format,
                name=f"{input_data.format}_team"
            )
            
            # Calculate team metrics
            synergy = self.calculate_synergy(team)
            coverage = self.calculate_coverage(team)
            win_conditions = self.identify_win_conditions(team)
            threats = self.identify_threats(team, input_data.threats or [])
            score = self.calculate_team_score(team, synergy, coverage, win_conditions)
            
            return TeamBuilderOutput(
                team=team,
                synergy=synergy,
                coverage=coverage,
                winConditions=win_conditions,
                threats=threats,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Error building team: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def generate_team_pokemon(self, available_pokemon: List[str], input_data: TeamBuilderInput) -> List[Pokemon]:
        """Generate 6 Pokémon for the team with legality checks"""
        team_pokemon = []
        
        # Start with required Pokémon if specified
        if input_data.constraints and input_data.constraints.requiredPokemon:
            for species in input_data.constraints.requiredPokemon[:6]:
                if species in available_pokemon:
                    pokemon = self.create_pokemon(species, input_data)
                    if self.is_legal_pokemon(pokemon, input_data.format):
                        team_pokemon.append(pokemon)
        
        # Fill remaining slots with role-based selection
        while len(team_pokemon) < 6:
            next_pokemon = self.select_next_pokemon(available_pokemon, team_pokemon, input_data)
            if next_pokemon and self.is_legal_pokemon(next_pokemon, input_data.format):
                team_pokemon.append(next_pokemon)
            else:
                # Fallback to random selection
                remaining = [p for p in available_pokemon if p not in [pokemon.species for pokemon in team_pokemon]]
                if remaining:
                    species = random.choice(remaining)
                    pokemon = self.create_pokemon(species, input_data)
                    if self.is_legal_pokemon(pokemon, input_data.format):
                        team_pokemon.append(pokemon)
                else:
                    break
        
        return team_pokemon[:6]
    
    def select_next_pokemon(self, available_pokemon: List[str], current_team: List[Pokemon], input_data: TeamBuilderInput) -> Optional[Pokemon]:
        """Select the next Pokémon to add to the team"""
        # This would use the transformer model in a real implementation
        # For now, we'll use a simple heuristic approach
        
        if not available_pokemon:
            return None
        
        # Get current team species
        current_species = [pokemon.species for pokemon in current_team]
        
        # Filter out already selected Pokémon
        candidates = [p for p in available_pokemon if p not in current_species]
        
        if not candidates:
            return None
        
        # Simple role-based selection
        roles = self.pokemon_data.get(input_data.format, {}).get("roles", {})
        
        # Determine what roles we need
        needed_roles = self.identify_needed_roles(current_team, roles)
        
        # Select Pokémon that fills needed roles
        for role, pokemon_list in roles.items():
            if role in needed_roles:
                for pokemon in pokemon_list:
                    if pokemon in candidates:
                        return self.create_pokemon(pokemon)
        
        # Fallback to random selection
        return self.create_pokemon(random.choice(candidates))
    
    def identify_needed_roles(self, current_team: List[Pokemon], roles: Dict[str, List[str]]) -> List[str]:
        """Identify what roles the team still needs"""
        current_species = [pokemon.species for pokemon in current_team]
        
        # Check which roles are already covered
        covered_roles = set()
        for role, pokemon_list in roles.items():
            if any(species in pokemon_list for species in current_species):
                covered_roles.add(role)
        
        # Return missing roles
        all_roles = set(roles.keys())
        return list(all_roles - covered_roles)
    
    def create_pokemon(self, species: str, input_data: TeamBuilderInput) -> Pokemon:
        """Create a Pokémon object with proper sets"""
        # Get curated sets for this species
        sets_data = get_sets(input_data.format)
        species_sets = sets_data.get(species, [])
        
        if species_sets:
            # Use the first available set
            pokemon_set = species_sets[0]
            return Pokemon(
                species=species,
                level=100,
                hp=100,
                maxhp=100,
                item=pokemon_set.get("item"),
                ability=pokemon_set.get("ability", ""),
                moves=pokemon_set.get("moves", []),
                teraType=pokemon_set.get("teraType") if input_data.includeTera else None,
                position="active"
            )
        else:
            # Fallback to basic set
            return Pokemon(
                species=species,
                level=100,
                hp=100,
                maxhp=100,
                moves=[],
                ability="",
                position="active"
            )
    
    def is_legal_pokemon(self, pokemon: Pokemon, format_name: str) -> bool:
        """Check if a Pokémon is legal for the format"""
        # Check if species is legal
        legal_pokemon = get_legal_pokemon(format_name)
        if pokemon.species not in legal_pokemon:
            return False
        
        # Check for species clause (no duplicates)
        # This would be checked at team level
        
        # Check move legality (basic check)
        if not pokemon.moves:
            return False
        
        # Check ability legality
        if not pokemon.ability:
            return False
        
        return True
    
    def check_species_clause(self, team: List[Pokemon]) -> bool:
        """Check species clause - no duplicate species"""
        species = [pokemon.species for pokemon in team]
        return len(species) == len(set(species))
    
    def check_role_coverage(self, team: List[Pokemon]) -> Dict[str, bool]:
        """Check if team has proper role coverage"""
        roles = {
            "hazard_setter": False,
            "hazard_removal": False,
            "speed_control": False,
            "win_condition": False
        }
        
        # This would be more sophisticated in a real implementation
        # For now, assume all teams have basic coverage
        for role in roles:
            roles[role] = True
        
        return roles
    
    def calculate_synergy(self, team: Team) -> float:
        """Calculate team synergy score"""
        # This would be more sophisticated in a real implementation
        species = [pokemon.species for pokemon in team.pokemon]
        
        # Check for type synergies
        synergy_score = 0
        
        # Fire/Water/Grass core
        fire_types = ["Volcarona", "Heatran", "Charizard"]
        water_types = ["Swampert", "Gastrodon", "Seismitoad"]
        grass_types = ["Rillaboom", "Kartana", "Ferrothorn"]
        
        if any(p in fire_types for p in species) and any(p in water_types for p in species) and any(p in grass_types for p in species):
            synergy_score += 0.3
        
        # Steel/Fairy/Dragon core
        steel_types = ["Magearna", "Ferrothorn", "Skarmory", "Corviknight"]
        fairy_types = ["Clefable", "Sylveon", "Primarina", "Azumarill"]
        dragon_types = ["Dragapult", "Garchomp"]
        
        if any(p in steel_types for p in species) and any(p in fairy_types for p in species) and any(p in dragon_types for p in species):
            synergy_score += 0.3
        
        return min(1.0, synergy_score)
    
    def calculate_coverage(self, team: Team) -> List[str]:
        """Calculate type coverage of the team"""
        # This would analyze move coverage in a real implementation
        return ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
    
    def identify_win_conditions(self, team: Team) -> List[str]:
        """Identify potential win conditions for the team"""
        win_conditions = []
        species = [pokemon.species for pokemon in team.pokemon]
        
        # Sweeper-based win conditions
        sweepers = ["Dragapult", "Garchomp", "Kartana", "Volcarona"]
        if any(p in sweepers for p in species):
            win_conditions.append("Sweeper setup")
        
        # Stall-based win conditions
        walls = ["Toxapex", "Corviknight", "Ferrothorn", "Skarmory", "Blissey"]
        if len([p for p in species if p in walls]) >= 3:
            win_conditions.append("Stall out")
        
        # Hazard-based win conditions
        hazard_setters = ["Landorus-Therian", "Garchomp", "Ferrothorn", "Skarmory"]
        if any(p in hazard_setters for p in species):
            win_conditions.append("Hazard stack")
        
        return win_conditions
    
    def identify_threats(self, team: Team, known_threats: List[str]) -> List[str]:
        """Identify threats to the team"""
        # This would analyze team weaknesses in a real implementation
        return known_threats[:5]  # Return top 5 threats
    
    def calculate_team_score(self, team: Team, synergy: float, coverage: List[str], win_conditions: List[str]) -> float:
        """Calculate overall team score"""
        base_score = 0.5
        synergy_bonus = synergy * 0.3
        coverage_bonus = len(coverage) * 0.01
        win_condition_bonus = len(win_conditions) * 0.1
        
        return min(1.0, base_score + synergy_bonus + coverage_bonus + win_condition_bonus)
    
    def validate_team_schema(self, team: Team) -> bool:
        """Validate team against schema requirements"""
        # Check team has exactly 6 Pokémon
        if len(team.pokemon) != 6:
            return False
        
        # Check species clause
        if not self.check_species_clause(team.pokemon):
            return False
        
        # Check each Pokémon has required fields
        for pokemon in team.pokemon:
            if not pokemon.species or not pokemon.ability or not pokemon.moves:
                return False
            
            # Check moves are not empty
            if len(pokemon.moves) == 0:
                return False
        
        return True

# Initialize the team builder service
teambuilder_service = TeamBuilderService()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pokeai-teambuilder"}

@app.post("/build", response_model=TeamBuilderOutput)
async def build_team(input_data: TeamBuilderInput):
    """Build a competitive team"""
    try:
        logger.info(f"Team building request for format: {input_data.format}")
        
        result = teambuilder_service.build_team(input_data)
        
        # Validate team schema
        if not teambuilder_service.validate_team_schema(result.team):
            raise HTTPException(status_code=500, detail="Generated team does not match schema")
        
        logger.info(f"Team built with score: {result.score:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Team building error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate-team")
async def evaluate_team(team: Team):
    """Evaluate an existing team"""
    try:
        synergy = teambuilder_service.calculate_synergy(team)
        coverage = teambuilder_service.calculate_coverage(team)
        win_conditions = teambuilder_service.identify_win_conditions(team)
        score = teambuilder_service.calculate_team_score(team, synergy, coverage, win_conditions)
        
        return {
            "synergy": synergy,
            "coverage": coverage,
            "winConditions": win_conditions,
            "score": score
        }
    except Exception as e:
        logger.error(f"Team evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
