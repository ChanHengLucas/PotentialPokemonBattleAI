#!/usr/bin/env python3
"""
PokéAI Advanced Battle Engine

A comprehensive battle simulation engine that handles:
- Move accuracy, power, and type effectiveness
- Status conditions and stat changes
- Hazards, screens, and field effects
- Priority and speed calculations
- Detailed battle logging and analysis
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

class BattleEngine:
    """Advanced battle simulation engine"""
    
    def __init__(self, data_dir: str = "data/pokemon"):
        self.data_dir = Path(data_dir)
        self.moves_data = self.load_moves_data()
        self.pokemon_data = self.load_pokemon_data()
        self.type_effectiveness = self.load_type_effectiveness()
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
    
    def create_pokemon_from_species(self, species: str, level: int = 100) -> Pokemon:
        """Create a Pokemon instance from species data"""
        species_lower = species.lower().replace(" ", "-")
        
        if species_lower not in self.pokemon_data.get("pokemon", {}):
            # Fallback for unknown species
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
                "effects": move_data.get("effects", {})
            }
        return None
    
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
    
    def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move, 
                        battle_state: Dict[str, Any]) -> Tuple[int, bool, float]:
        """Calculate damage dealt by a move"""
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
        
        # Critical hit chance (simplified)
        critical_hit = random.random() < 0.0625  # 6.25% base crit chance
        if critical_hit:
            level_factor *= 2
        
        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move.type in attacker.types else 1.0
        
        # Random factor (0.85 to 1.0)
        random_factor = random.uniform(0.85, 1.0)
        
        # Calculate final damage
        damage = int(((level_factor * attack_stat * base_power / defense_stat) + 2) * 
                    stab * effectiveness * random_factor)
        
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
    
    def check_accuracy(self, move: Move, attacker: Pokemon, defender: Pokemon) -> bool:
        """Check if a move hits"""
        if move.accuracy == 100:
            return True
        
        # Calculate accuracy
        accuracy = move.accuracy * self.get_stat_multiplier(attacker.boosts["accuracy"])
        accuracy *= self.get_stat_multiplier(-defender.boosts["evasion"])
        
        # Weather and other effects would be applied here
        accuracy = max(1, min(100, accuracy))
        
        return random.random() < (accuracy / 100)
    
    def apply_move_effects(self, attacker: Pokemon, defender: Pokemon, move: Move, 
                          battle_state: Dict[str, Any]) -> List[BattleLogEntry]:
        """Apply move effects and return log entries"""
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
                # Add other status conditions as needed
        
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
    
    def simulate_turn(self, battle_state: Dict[str, Any], p1_action: Dict[str, Any], 
                     p2_action: Dict[str, Any]) -> List[BattleLogEntry]:
        """Simulate a single turn of battle"""
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
        """Execute a move action"""
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
        if not self.check_accuracy(move, attacker, defender):
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
        
        return log_entries
    
    def apply_end_of_turn_effects(self, battle_state: Dict[str, Any]) -> List[BattleLogEntry]:
        """Apply end-of-turn effects like status damage"""
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
        
        return log_entries
    
    def simulate_battle(self, team1: List[Pokemon], team2: List[Pokemon], 
                       max_turns: int = 200) -> Dict[str, Any]:
        """Simulate a complete battle"""
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
