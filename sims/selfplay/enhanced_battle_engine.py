#!/usr/bin/env python3
"""
PokéAI Enhanced Battle Engine

A comprehensive battle simulation engine for Gen 9 OU that handles:
- All status effects, abilities, and held items
- Weather, terrain, and field effects
- Stage hazards and screens
- Move conditions and interactions
- Proper Gen 9 OU mechanics
"""

import json
import logging
import random
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoveCategory(Enum):
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"

class StatusCondition(Enum):
    NONE = "none"
    BURN = "burn"
    FREEZE = "freeze"
    PARALYSIS = "paralysis"
    POISON = "poison"
    BADLY_POISONED = "badly_poisoned"
    SLEEP = "sleep"
    CONFUSION = "confusion"
    INFATUATION = "infatuation"
    FLINCH = "flinch"

class WeatherType(Enum):
    NONE = "none"
    SUN = "sun"
    RAIN = "rain"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    SNOW = "snow"

class TerrainType(Enum):
    NONE = "none"
    ELECTRIC = "electric"
    GRASSY = "grassy"
    MISTY = "misty"
    PSYCHIC = "psychic"

@dataclass
class Move:
    name: str
    move_id: str
    type: str
    category: MoveCategory
    power: int
    accuracy: int
    pp: int
    priority: int
    effects: Dict[str, Any] = None
    contact: bool = False
    sound: bool = False
    powder: bool = False
    charge: bool = False
    recharge: bool = False

@dataclass
class Pokemon:
    species: str
    level: int
    hp: int
    max_hp: int
    atk: int
    def_: int
    spa: int
    spd: int
    spe: int
    types: List[str]
    ability: str
    item: str
    moves: List[Move]
    status: StatusCondition = StatusCondition.NONE
    status_turns: int = 0
    boosts: Dict[str, int] = None
    tera_type: str = None
    terastallized: bool = False
    last_move: str = None
    move_locked: bool = False
    substitute_hp: int = 0
    protect_turns: int = 0
    
    def __post_init__(self):
        if self.boosts is None:
            self.boosts = {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0}

@dataclass
class BattleLogEntry:
    turn: int
    player: str
    action: str
    details: Dict[str, Any]
    result: str
    damage: int = 0
    accuracy_roll: float = 0.0
    critical_hit: bool = False
    effectiveness: float = 1.0

class EnhancedBattleEngine:
    """Enhanced battle simulation engine with full Gen 9 OU mechanics"""
    
    def __init__(self, data_dir: str = "data/pokemon"):
        self.data_dir = Path(data_dir)
        self.moves_data = self.load_moves_data()
        self.pokemon_data = self.load_pokemon_data()
        self.type_effectiveness = self.load_type_effectiveness()
        self.abilities_data = self.load_abilities_data()
        self.items_data = self.load_items_data()
        self.weather_data = self.load_weather_data()
        self.terrain_data = self.load_terrain_data()
        self.battle_log = []
        
    def load_moves_data(self) -> Dict[str, Any]:
        """Load move data from JSON file"""
        moves_file = self.data_dir / "moves.json"
        if moves_file.exists():
            with open(moves_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_pokemon_data(self) -> Dict[str, Any]:
        """Load Pokemon data from JSON file"""
        pokemon_file = self.data_dir / "pokemon.json"
        if pokemon_file.exists():
            with open(pokemon_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_type_effectiveness(self) -> Dict[str, Any]:
        """Load type effectiveness data from JSON file"""
        type_file = self.data_dir / "type_effectiveness.json"
        if type_file.exists():
            with open(type_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_abilities_data(self) -> Dict[str, Any]:
        """Load abilities data from JSON file"""
        abilities_file = self.data_dir / "abilities.json"
        if abilities_file.exists():
            with open(abilities_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_items_data(self) -> Dict[str, Any]:
        """Load items data from JSON file"""
        items_file = self.data_dir / "items.json"
        if items_file.exists():
            with open(items_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_weather_data(self) -> Dict[str, Any]:
        """Load weather data from JSON file"""
        weather_file = self.data_dir / "weather.json"
        if weather_file.exists():
            with open(weather_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_terrain_data(self) -> Dict[str, Any]:
        """Load terrain data from JSON file"""
        terrain_file = self.data_dir / "terrain.json"
        if terrain_file.exists():
            with open(terrain_file, 'r') as f:
                return json.load(f)
        return {}
    
    def create_pokemon_from_species(self, species: str, level: int = 100) -> Pokemon:
        """Create a Pokemon instance from species data"""
        species_lower = species.lower().replace(" ", "-")
        
        if species_lower not in self.pokemon_data.get("pokemon", {}):
            return self.create_fallback_pokemon(species, level)
        
        data = self.pokemon_data["pokemon"][species_lower]
        base_stats = data["baseStats"]
        
        # Calculate actual stats (simplified)
        hp = int(base_stats["hp"] * 2 + 110)
        other_stats = {stat: int(base_stats[stat] * 2 + 5) for stat in ["atk", "def", "spa", "spd", "spe"]}
        
        # Create moves (simplified - would normally be more complex)
        moves = []
        for move_name in data.get("commonMoves", ["Tackle"]):
            move_data = self.get_move_data(move_name)
            if move_data:
                moves.append(Move(**move_data))
        
        return Pokemon(
            species=species,
            level=level,
            hp=hp,
            max_hp=hp,
            atk=other_stats["atk"],
            def_=other_stats["def"],
            spa=other_stats["spa"],
            spd=other_stats["spd"],
            spe=other_stats["spe"],
            types=data["types"],
            ability=data["abilities"][0],
            item="",
            moves=moves
        )
    
    def create_fallback_pokemon(self, species: str, level: int = 100) -> Pokemon:
        """Create a fallback Pokemon for unknown species"""
        return Pokemon(
            species=species,
            level=level,
            hp=100,
            max_hp=100,
            atk=100,
            def_=100,
            spa=100,
            spd=100,
            spe=100,
            types=["Normal"],
            ability="",
            item="",
            moves=[Move("Tackle", "tackle", "Normal", MoveCategory.PHYSICAL, 40, 100, 35, 0)]
        )
    
    def get_move_data(self, move_name: str) -> Optional[Dict[str, Any]]:
        """Get move data by name"""
        move_id = move_name.lower().replace(" ", "").replace("-", "")
        
        if move_id in self.moves_data.get("moves", {}):
            move_data = self.moves_data["moves"][move_id]
            return {
                "name": move_data["name"],
                "move_id": move_id,
                "type": move_data["type"],
                "category": MoveCategory(move_data["category"]),
                "power": move_data["power"],
                "accuracy": move_data["accuracy"],
                "pp": move_data["pp"],
                "priority": move_data.get("priority", 0),
                "effects": move_data.get("effects", {}),
                "contact": move_data.get("contact", False),
                "sound": move_data.get("sound", False),
                "powder": move_data.get("powder", False),
                "charge": move_data.get("charge", False),
                "recharge": move_data.get("recharge", False)
            }
        return None
    
    def get_ability_data(self, ability_name: str) -> Optional[Dict[str, Any]]:
        """Get ability data by name"""
        ability_id = ability_name.lower().replace(" ", "_")
        return self.abilities_data.get("abilities", {}).get(ability_id)
    
    def get_item_data(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get item data by name"""
        item_id = item_name.lower().replace(" ", "_").replace("-", "_")
        return self.items_data.get("items", {}).get(item_id)
    
    def apply_ability_effects(self, pokemon: Pokemon, battle_state: Dict[str, Any], trigger: str) -> List[BattleLogEntry]:
        """Apply ability effects based on trigger"""
        log_entries = []
        ability_data = self.get_ability_data(pokemon.ability)
        
        if not ability_data:
            return log_entries
        
        if ability_data.get("trigger") == trigger:
            if ability_data["effect"] == "lowers_attack" and trigger == "on_switch_in":
                # Intimidate
                opponent = battle_state["p2" if pokemon == battle_state["p1"]["active"] else "p1"]["active"]
                opponent.boosts["atk"] = max(-6, opponent.boosts["atk"] - 1)
                log_entries.append(BattleLogEntry(
                    turn=battle_state["turn"],
                    player="system",
                    action="ability",
                    details={"ability": pokemon.ability, "target": opponent.species, "effect": "attack_lowered"},
                    result="ability_triggered"
                ))
            
            elif ability_data["effect"] == "heal_on_switch" and trigger == "on_switch_out":
                # Regenerator
                heal_amount = int(pokemon.max_hp * 0.33)
                pokemon.hp = min(pokemon.max_hp, pokemon.hp + heal_amount)
                log_entries.append(BattleLogEntry(
                    turn=battle_state["turn"],
                    player="system",
                    action="ability",
                    details={"ability": pokemon.ability, "heal": heal_amount},
                    result="ability_triggered"
                ))
            
            elif ability_data["effect"] == "contact_damage" and trigger == "on_contact":
                # Rough Skin, Iron Barbs
                attacker = battle_state["p2" if pokemon == battle_state["p1"]["active"] else "p1"]["active"]
                damage = int(attacker.max_hp * 0.125)  # 1/8 HP
                attacker.hp = max(0, attacker.hp - damage)
                log_entries.append(BattleLogEntry(
                    turn=battle_state["turn"],
                    player="system",
                    action="ability",
                    details={"ability": pokemon.ability, "target": attacker.species, "damage": damage},
                    result="ability_triggered"
                ))
        
        return log_entries
    
    def apply_item_effects(self, pokemon: Pokemon, battle_state: Dict[str, Any], trigger: str) -> List[BattleLogEntry]:
        """Apply item effects based on trigger"""
        log_entries = []
        item_data = self.get_item_data(pokemon.item)
        
        if not item_data:
            return log_entries
        
        if item_data.get("trigger") == trigger:
            if item_data["effect"] == "heal_per_turn" and trigger == "end_of_turn":
                # Leftovers
                heal_amount = int(pokemon.max_hp * item_data["heal_percent"])
                pokemon.hp = min(pokemon.max_hp, pokemon.hp + heal_amount)
                log_entries.append(BattleLogEntry(
                    turn=battle_state["turn"],
                    player="system",
                    action="item",
                    details={"item": pokemon.item, "heal": heal_amount},
                    result="item_triggered"
                ))
            
            elif item_data["effect"] == "boost_damage" and trigger == "on_attack":
                # Life Orb
                # This would be handled in damage calculation
                pass
            
            elif item_data["effect"] == "survive_ohko" and trigger == "on_ohko":
                # Focus Sash
                if pokemon.hp <= 0:
                    pokemon.hp = 1
                    pokemon.item = ""  # One-time use
                    log_entries.append(BattleLogEntry(
                        turn=battle_state["turn"],
                        player="system",
                        action="item",
                        details={"item": "Focus Sash", "effect": "survived_ohko"},
                        result="item_triggered"
                    ))
        
        return log_entries
    
    def apply_weather_effects(self, battle_state: Dict[str, Any]) -> List[BattleLogEntry]:
        """Apply weather effects"""
        log_entries = []
        weather = battle_state.get("field", {}).get("weather")
        
        if not weather or weather == "none":
            return log_entries
        
        weather_data = self.weather_data.get("weather", {}).get(weather)
        if not weather_data:
            return log_entries
        
        # Apply weather damage
        for player in ["p1", "p2"]:
            pokemon = battle_state[player]["active"]
            if pokemon.hp > 0:
                # Check for weather immunity
                immune_types = weather_data.get("effects", {}).get("damage_immunity", [])
                if any(t in pokemon.types for t in immune_types):
                    continue
                
                damage = int(pokemon.max_hp * weather_data["effects"]["damage_per_turn"])
                pokemon.hp = max(0, pokemon.hp - damage)
                if damage > 0:
                    log_entries.append(BattleLogEntry(
                        turn=battle_state["turn"],
                        player="system",
                        action="weather",
                        details={"weather": weather, "target": pokemon.species, "damage": damage},
                        result="weather_damage"
                    ))
        
        return log_entries
    
    def apply_terrain_effects(self, battle_state: Dict[str, Any]) -> List[BattleLogEntry]:
        """Apply terrain effects"""
        log_entries = []
        terrain = battle_state.get("field", {}).get("terrain")
        
        if not terrain or terrain == "none":
            return log_entries
        
        terrain_data = self.terrain_data.get("terrain", {}).get(terrain)
        if not terrain_data:
            return log_entries
        
        # Apply terrain healing
        if terrain == "grassy":
            for player in ["p1", "p2"]:
                pokemon = battle_state[player]["active"]
                if pokemon.hp > 0 and pokemon.hp < pokemon.max_hp:
                    # Check if Pokemon is grounded
                    if "Flying" not in pokemon.types and pokemon.ability != "Levitate":
                        heal_amount = int(pokemon.max_hp * terrain_data["effects"]["heal_per_turn"])
                        pokemon.hp = min(pokemon.max_hp, pokemon.hp + heal_amount)
                        if heal_amount > 0:
                            log_entries.append(BattleLogEntry(
                                turn=battle_state["turn"],
                                player="system",
                                action="terrain",
                                details={"terrain": terrain, "target": pokemon.species, "heal": heal_amount},
                                result="terrain_heal"
                            ))
        
        return log_entries
    
    def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move, 
                        battle_state: Dict[str, Any]) -> Tuple[int, bool, float]:
        """Calculate damage with all modifiers"""
        if move.category == MoveCategory.STATUS:
            return 0, False, 1.0
        
        # Base damage calculation
        if move.category == MoveCategory.PHYSICAL:
            attack_stat = attacker.atk * self.get_stat_multiplier(attacker.boosts["atk"])
            defense_stat = defender.def_ * self.get_stat_multiplier(defender.boosts["def"])
        else:  # Special
            attack_stat = attacker.spa * self.get_stat_multiplier(attacker.boosts["spa"])
            defense_stat = defender.spd * self.get_stat_multiplier(defender.boosts["spd"])
        
        # Level factor
        level_factor = (2 * attacker.level + 10) / 250
        
        # Base power
        base_power = move.power
        
        # Type effectiveness
        effectiveness = self.calculate_type_effectiveness(move.type, defender.types)
        
        # Critical hit chance
        critical_hit = random.random() < 0.0625  # 6.25% base crit chance
        if critical_hit:
            level_factor *= 2
        
        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move.type in attacker.types else 1.0
        
        # Weather boost
        weather_boost = 1.0
        weather = battle_state.get("field", {}).get("weather")
        if weather:
            weather_data = self.weather_data.get("weather", {}).get(weather)
            if weather_data:
                if move.type == "Fire" and weather == "sun":
                    weather_boost = weather_data["effects"]["fire_boost"]
                elif move.type == "Water" and weather == "rain":
                    weather_boost = weather_data["effects"]["water_boost"]
        
        # Terrain boost
        terrain_boost = 1.0
        terrain = battle_state.get("field", {}).get("terrain")
        if terrain:
            terrain_data = self.terrain_data.get("terrain", {}).get(terrain)
            if terrain_data:
                if move.type == "Electric" and terrain == "electric":
                    terrain_boost = terrain_data["effects"]["electric_boost"]
                elif move.type == "Grass" and terrain == "grassy":
                    terrain_boost = terrain_data["effects"]["grass_boost"]
                elif move.type == "Fairy" and terrain == "misty":
                    terrain_boost = terrain_data["effects"]["fairy_boost"]
                elif move.type == "Psychic" and terrain == "psychic":
                    terrain_boost = terrain_data["effects"]["psychic_boost"]
        
        # Item boost
        item_boost = 1.0
        item_data = self.get_item_data(attacker.item)
        if item_data and item_data.get("effect") == "boost_damage":
            item_boost = item_data["damage_boost"]
        
        # Random factor (0.85 to 1.0)
        random_factor = random.uniform(0.85, 1.0)
        
        # Calculate final damage
        damage = int(((level_factor * attack_stat * base_power / defense_stat) + 2) * 
                    stab * effectiveness * weather_boost * terrain_boost * item_boost * random_factor)
        
        # Apply status condition damage reduction
        if attacker.status == StatusCondition.BURN and move.category == MoveCategory.PHYSICAL:
            damage = int(damage * 0.5)
        
        return max(1, damage), critical_hit, effectiveness
    
    def get_stat_multiplier(self, boost_level: int) -> float:
        """Get stat multiplier from boost level"""
        if boost_level >= 0:
            return (2 + boost_level) / 2
        else:
            return 2 / (2 + abs(boost_level))
    
    def calculate_type_effectiveness(self, move_type: str, target_types: List[str]) -> float:
        """Calculate type effectiveness multiplier"""
        if move_type not in self.type_effectiveness:
            return 1.0
        
        effectiveness = 1.0
        type_data = self.type_effectiveness[move_type]
        
        for target_type in target_types:
            if target_type in type_data["super_effective"]:
                effectiveness *= 2.0
            elif target_type in type_data["not_very_effective"]:
                effectiveness *= 0.5
            elif target_type in type_data["no_effect"]:
                effectiveness *= 0.0
        
        return effectiveness
    
    def check_accuracy(self, move: Move, attacker: Pokemon, defender: Pokemon, 
                      battle_state: Dict[str, Any]) -> bool:
        """Check if a move hits with all modifiers"""
        if move.accuracy == 100:
            return True
        
        # Calculate accuracy
        accuracy = move.accuracy * self.get_stat_multiplier(attacker.boosts["accuracy"])
        accuracy *= self.get_stat_multiplier(-defender.boosts["evasion"])
        
        # Weather effects
        weather = battle_state.get("field", {}).get("weather")
        if weather:
            weather_data = self.weather_data.get("weather", {}).get(weather)
            if weather_data:
                if move.name == "Thunder" and weather == "rain":
                    accuracy = 100
                elif move.name == "Hurricane" and weather == "rain":
                    accuracy = 100
        
        # Terrain effects
        terrain = battle_state.get("field", {}).get("terrain")
        if terrain == "misty" and move.type == "Dragon":
            accuracy *= 0.5
        
        # Status effects
        if attacker.status == StatusCondition.PARALYSIS:
            accuracy *= 0.8  # Paralysis reduces accuracy
        
        accuracy = max(1, min(100, accuracy))
        
        return random.random() < (accuracy / 100)
    
    def simulate_battle(self, team1: List[Pokemon], team2: List[Pokemon], 
                       max_turns: int = 200) -> Dict[str, Any]:
        """Simulate a complete battle with all Gen 9 OU mechanics"""
        # Initialize battle state
        battle_state = {
            "turn": 0,
            "p1": {
                "active": team1[0],
                "bench": team1[1:],
                "side": {
                    "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False},
                    "screens": {"reflect": False, "lightScreen": False, "auroraVeil": False},
                    "sideConditions": {"tailwind": False, "trickRoom": False, "gravity": False, "wonderRoom": False, "magicRoom": False}
                }
            },
            "p2": {
                "active": team2[0],
                "bench": team2[1:],
                "side": {
                    "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False},
                    "screens": {"reflect": False, "lightScreen": False, "auroraVeil": False},
                    "sideConditions": {"tailwind": False, "trickRoom": False, "gravity": False, "wonderRoom": False, "magicRoom": False}
                }
            },
            "field": {
                "weather": "none",
                "terrain": "none",
                "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False},
                "screens": {"reflect": False, "lightScreen": False, "auroraVeil": False},
                "sideConditions": {"tailwind": False, "trickRoom": False, "gravity": False, "wonderRoom": False, "magicRoom": False}
            }
        }
        
        battle_log = []
        
        # Battle loop
        for turn in range(1, max_turns + 1):
            battle_state["turn"] = turn
            
            # Check for battle end
            if self.check_battle_end(battle_state):
                break
            
            # Get actions (simplified - would normally use AI)
            p1_action = self.get_random_action(battle_state, "p1")
            p2_action = self.get_random_action(battle_state, "p2")
            
            # Simulate turn
            turn_log = self.simulate_turn(battle_state, p1_action, p2_action)
            battle_log.extend(turn_log)
        
        # Determine winner
        winner = self.determine_winner(battle_state)
        
        return {
            "winner": winner,
            "turns": battle_state["turn"],
            "battle_log": battle_log,
            "final_state": battle_state
        }
    
    def simulate_turn(self, battle_state: Dict[str, Any], p1_action: Dict[str, Any], 
                     p2_action: Dict[str, Any]) -> List[BattleLogEntry]:
        """Simulate a single turn with all mechanics"""
        turn_log = []
        
        # Determine action order based on priority and speed
        p1_priority = p1_action.get("priority", 0)
        p2_priority = p2_action.get("priority", 0)
        
        if p1_priority > p2_priority:
            action_order = [("p1", p1_action), ("p2", p2_action)]
        elif p2_priority > p1_priority:
            action_order = [("p2", p2_action), ("p1", p1_action)]
        else:
            # Same priority - use speed
            p1_speed = battle_state["p1"]["active"].spe * self.get_stat_multiplier(battle_state["p1"]["active"].boosts["spe"])
            p2_speed = battle_state["p2"]["active"].spe * self.get_stat_multiplier(battle_state["p2"]["active"].boosts["spe"])
            
            if p1_speed > p2_speed:
                action_order = [("p1", p1_action), ("p2", p2_action)]
            elif p2_speed > p1_speed:
                action_order = [("p2", p2_action), ("p1", p1_action)]
            else:
                # Speed tie - random
                action_order = random.choice([
                    [("p1", p1_action), ("p2", p2_action)],
                    [("p2", p2_action), ("p1", p1_action)]
                ])
        
        # Execute actions in order
        for player, action in action_order:
            if battle_state[player]["active"].hp <= 0:
                continue  # Skip if Pokemon is fainted
            
            # Check status effects
            if not self.check_status_effects(battle_state[player]["active"]):
                turn_log.append(BattleLogEntry(
                    turn=battle_state["turn"],
                    player=player,
                    action="status_prevented",
                    details={"status": battle_state[player]["active"].status.value},
                    result="action_prevented"
                ))
                continue
            
            # Execute action
            if action["type"] == "move":
                move_result = self.execute_move(battle_state, player, action)
                turn_log.extend(move_result)
            elif action["type"] == "switch":
                switch_result = self.execute_switch(battle_state, player, action)
                turn_log.extend(switch_result)
        
        # Apply end-of-turn effects
        end_turn_log = self.apply_end_of_turn_effects(battle_state)
        turn_log.extend(end_turn_log)
        
        return turn_log
    
    def execute_move(self, battle_state: Dict[str, Any], player: str, action: Dict[str, Any]) -> List[BattleLogEntry]:
        """Execute a move action with all mechanics"""
        log_entries = []
        attacker = battle_state[player]["active"]
        defender = battle_state["p2" if player == "p1" else "p1"]["active"]
        
        # Find the move
        move = None
        for m in attacker.moves:
            if m.move_id == action["move"]:
                move = m
                break
        
        if not move:
            return log_entries
        
        # Check accuracy
        if not self.check_accuracy(move, attacker, defender, battle_state):
            log_entries.append(BattleLogEntry(
                turn=battle_state["turn"],
                player=player,
                action="move",
                details={"move": move.name, "target": defender.species},
                result="missed",
                accuracy_roll=random.random()
            ))
            return log_entries
        
        # Calculate damage
        if move.category != MoveCategory.STATUS:
            damage, critical_hit, effectiveness = self.calculate_damage(attacker, defender, move, battle_state)
            defender.hp = max(0, defender.hp - damage)
            
            log_entries.append(BattleLogEntry(
                turn=battle_state["turn"],
                player=player,
                action="move",
                details={"move": move.name, "target": defender.species},
                result="hit",
                damage=damage,
                accuracy_roll=random.random(),
                critical_hit=critical_hit,
                effectiveness=effectiveness
            ))
        else:
            log_entries.append(BattleLogEntry(
                turn=battle_state["turn"],
                player=player,
                action="move",
                details={"move": move.name, "target": defender.species},
                result="status_move"
            ))
        
        # Apply move effects
        effect_log = self.apply_move_effects(attacker, defender, move, battle_state)
        log_entries.extend(effect_log)
        
        return log_entries
    
    def execute_switch(self, battle_state: Dict[str, Any], player: str, action: Dict[str, Any]) -> List[BattleLogEntry]:
        """Execute a switch action"""
        log_entries = []
        
        pokemon_index = action["pokemon"]
        if pokemon_index < len(battle_state[player]["bench"]):
            # Switch active and bench Pokemon
            active = battle_state[player]["active"]
            bench_pokemon = battle_state[player]["bench"][pokemon_index]
            
            battle_state[player]["active"] = bench_pokemon
            battle_state[player]["bench"][pokemon_index] = active
            
            log_entries.append(BattleLogEntry(
                turn=battle_state["turn"],
                player=player,
                action="switch",
                details={"from": active.species, "to": bench_pokemon.species},
                result="switched"
            ))
            
            # Apply ability effects on switch in
            ability_log = self.apply_ability_effects(bench_pokemon, battle_state, "on_switch_in")
            log_entries.extend(ability_log)
        
        return log_entries
    
    def apply_move_effects(self, attacker: Pokemon, defender: Pokemon, move: Move, 
                          battle_state: Dict[str, Any]) -> List[BattleLogEntry]:
        """Apply move effects with all mechanics"""
        log_entries = []
        
        if not move.effects:
            return log_entries
        
        # Secondary effects
        if "secondary" in move.effects:
            secondary = move.effects["secondary"]
            if random.random() < (secondary["chance"] / 100):
                if secondary["effect"] == "spdef_drop":
                    defender.boosts["spd"] = max(-6, defender.boosts["spd"] - 1)
                    log_entries.append(BattleLogEntry(
                        turn=battle_state["turn"],
                        player="system",
                        action="stat_change",
                        details={"target": defender.species, "stat": "spd", "change": -1},
                        result="spdef_dropped"
                    ))
                elif secondary["effect"] == "burn":
                    if defender.status == StatusCondition.NONE:
                        defender.status = StatusCondition.BURN
                        log_entries.append(BattleLogEntry(
                            turn=battle_state["turn"],
                            player="system",
                            action="status",
                            details={"target": defender.species, "status": "burn"},
                            result="burned"
                        ))
        
        # Status moves
        if "status" in move.effects:
            status_name = move.effects["status"]
            if defender.status == StatusCondition.NONE:
                if status_name == "badly_poisoned":
                    defender.status = StatusCondition.BADLY_POISONED
                    defender.status_turns = 0
                elif status_name == "burn":
                    defender.status = StatusCondition.BURN
                elif status_name == "paralysis":
                    defender.status = StatusCondition.PARALYSIS
        
        # Hazards
        if "hazard" in move.effects:
            hazard_type = move.effects["hazard"]
            if hazard_type == "stealthrock":
                battle_state["field"]["hazards"]["stealthRock"] = True
            elif hazard_type == "spikes":
                battle_state["field"]["hazards"]["spikes"] += 1
        
        # Screens
        if "screen" in move.effects:
            screen_type = move.effects["screen"]
            if screen_type == "reflect":
                battle_state["p1"]["side"]["screens"]["reflect"] = True
            elif screen_type == "lightscreen":
                battle_state["p1"]["side"]["screens"]["lightscreen"] = True
        
        # Healing
        if "heal" in move.effects:
            heal_percent = move.effects["heal"]
            heal_amount = int(attacker.max_hp * heal_percent)
            attacker.hp = min(attacker.max_hp, attacker.hp + heal_amount)
            log_entries.append(BattleLogEntry(
                turn=battle_state["turn"],
                player=attacker.species,
                action="heal",
                details={"amount": heal_amount},
                result="healed"
            ))
        
        return log_entries
    
    def apply_end_of_turn_effects(self, battle_state: Dict[str, Any]) -> List[BattleLogEntry]:
        """Apply end-of-turn effects"""
        log_entries = []
        
        # Apply status damage
        for player in ["p1", "p2"]:
            pokemon = battle_state[player]["active"]
            if pokemon.hp > 0:
                status_damage = self.apply_status_damage(pokemon)
                if status_damage > 0:
                    log_entries.append(BattleLogEntry(
                        turn=battle_state["turn"],
                        player=player,
                        action="status_damage",
                        details={"status": pokemon.status.value, "damage": status_damage},
                        result="status_damage"
                    ))
        
        # Apply weather effects
        weather_log = self.apply_weather_effects(battle_state)
        log_entries.extend(weather_log)
        
        # Apply terrain effects
        terrain_log = self.apply_terrain_effects(battle_state)
        log_entries.extend(terrain_log)
        
        # Apply item effects
        for player in ["p1", "p2"]:
            pokemon = battle_state[player]["active"]
            if pokemon.hp > 0:
                item_log = self.apply_item_effects(pokemon, battle_state, "end_of_turn")
                log_entries.extend(item_log)
        
        return log_entries
    
    def apply_status_damage(self, pokemon: Pokemon) -> int:
        """Apply damage from status conditions"""
        if pokemon.status == StatusCondition.BURN:
            damage = int(pokemon.max_hp * 0.125)  # 1/8 HP per turn
        elif pokemon.status == StatusCondition.POISON:
            damage = int(pokemon.max_hp * 0.125)  # 1/8 HP per turn
        elif pokemon.status == StatusCondition.BADLY_POISONED:
            pokemon.status_turns += 1
            damage = int(pokemon.max_hp * 0.125 * pokemon.status_turns)  # Increasing damage
        else:
            damage = 0
        
        pokemon.hp = max(0, pokemon.hp - damage)
        return damage
    
    def check_status_effects(self, pokemon: Pokemon) -> bool:
        """Check if status prevents action"""
        if pokemon.status == StatusCondition.SLEEP:
            return random.random() < 0.33  # 33% chance to wake up
        elif pokemon.status == StatusCondition.FREEZE:
            return random.random() < 0.20  # 20% chance to thaw
        elif pokemon.status == StatusCondition.PARALYSIS:
            return random.random() < 0.25  # 25% chance to be paralyzed
        elif pokemon.status == StatusCondition.CONFUSION:
            if random.random() < 0.33:  # 33% chance to hit self
                return False
        return True
    
    def get_random_action(self, battle_state: Dict[str, Any], player: str) -> Dict[str, Any]:
        """Get a random legal action (simplified AI)"""
        active = battle_state[player]["active"]
        
        # 70% chance to use a move, 30% chance to switch
        if random.random() < 0.7 and active.moves:
            move = random.choice(active.moves)
            return {"type": "move", "move": move.move_id, "priority": move.priority}
        else:
            # Switch to a random healthy Pokemon
            healthy_bench = [i for i, p in enumerate(battle_state[player]["bench"]) if p.hp > 0]
            if healthy_bench:
                return {"type": "switch", "pokemon": random.choice(healthy_bench), "priority": 0}
            else:
                # Struggle if no other options
                return {"type": "move", "move": "struggle", "priority": 0}
    
    def check_battle_end(self, battle_state: Dict[str, Any]) -> bool:
        """Check if the battle has ended"""
        p1_remaining = self.count_remaining_pokemon(battle_state["p1"])
        p2_remaining = self.count_remaining_pokemon(battle_state["p2"])
        return p1_remaining == 0 or p2_remaining == 0
    
    def count_remaining_pokemon(self, player_state: Dict[str, Any]) -> int:
        """Count remaining Pokemon for a player"""
        count = 0
        
        if player_state["active"].hp > 0:
            count += 1
        
        for pokemon in player_state["bench"]:
            if pokemon.hp > 0:
                count += 1
        
        return count
    
    def determine_winner(self, battle_state: Dict[str, Any]) -> str:
        """Determine the winner of the battle"""
        p1_remaining = self.count_remaining_pokemon(battle_state["p1"])
        p2_remaining = self.count_remaining_pokemon(battle_state["p2"])
        
        if p1_remaining > p2_remaining:
            return "p1"
        elif p2_remaining > p1_remaining:
            return "p2"
        else:
            return "tie"
    
    def analyze_battle_outcome(self, battle_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze battle outcome for learning insights"""
        analysis = {
            "winner": battle_result["winner"],
            "turns": battle_result["turns"],
            "move_effectiveness": {},
            "critical_moments": [],
            "status_impact": {},
            "hazard_impact": {},
            "learning_insights": []
        }
        
        # Analyze move effectiveness
        move_usage = {}
        move_success = {}
        
        for log_entry in battle_result["battle_log"]:
            if log_entry.action == "move":
                move_name = log_entry.details.get("move", "unknown")
                if move_name not in move_usage:
                    move_usage[move_name] = 0
                    move_success[move_name] = 0
                
                move_usage[move_name] += 1
                if log_entry.result == "hit":
                    move_success[move_name] += 1
        
        # Calculate effectiveness rates
        for move_name in move_usage:
            success_rate = move_success[move_name] / move_usage[move_name]
            analysis["move_effectiveness"][move_name] = {
                "usage_count": move_usage[move_name],
                "success_rate": success_rate,
                "effectiveness": success_rate
            }
        
        # Identify critical moments
        for log_entry in battle_result["battle_log"]:
            if log_entry.critical_hit or log_entry.effectiveness > 2.0:
                analysis["critical_moments"].append({
                    "turn": log_entry.turn,
                    "action": log_entry.action,
                    "details": log_entry.details,
                    "impact": "high"
                })
        
        # Generate learning insights
        if analysis["move_effectiveness"]:
            best_move = max(analysis["move_effectiveness"].items(), 
                          key=lambda x: x[1]["effectiveness"])
            analysis["learning_insights"].append(f"Most effective move: {best_move[0]} ({best_move[1]['effectiveness']:.2f} success rate)")
        
        if analysis["critical_moments"]:
            analysis["learning_insights"].append(f"Critical moments: {len(analysis['critical_moments'])} high-impact plays")
        
        return analysis
