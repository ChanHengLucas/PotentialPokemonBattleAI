#!/usr/bin/env python3
"""
PokéAI Self-Play Simulator

Runs local self-play games for training and evaluation.
"""

import argparse
import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfPlaySimulator:
    """Simulates Pokémon battles for self-play training"""
    
    def __init__(self, format_name: str = "gen9ou"):
        self.format = format_name
        self.calc_url = "http://localhost:3001"
        self.policy_url = "http://localhost:8000"
        self.teambuilder_url = "http://localhost:8001"
        self.games_played = 0
        self.results = []
    
    def run_games(self, num_games: int) -> List[Dict[str, Any]]:
        """Run a series of self-play games"""
        logger.info(f"Starting {num_games} self-play games for {self.format}")
        
        for game_num in range(num_games):
            try:
                logger.info(f"Game {game_num + 1}/{num_games}")
                result = self.play_single_game()
                self.results.append(result)
                self.games_played += 1
                
                # Log progress
                if (game_num + 1) % 10 == 0:
                    self.log_progress()
                    
            except Exception as e:
                logger.error(f"Error in game {game_num + 1}: {e}")
                continue
        
        logger.info(f"Completed {self.games_played} games")
        return self.results
    
    def play_single_game(self) -> Dict[str, Any]:
        """Play a single self-play game"""
        # Generate two teams
        team1 = self.generate_team()
        team2 = self.generate_team()
        
        # Initialize battle state
        battle_state = self.initialize_battle_state(team1, team2)
        
        # Play the game
        game_result = self.play_battle(battle_state)
        
        return {
            "game_id": f"selfplay_{int(time.time())}_{random.randint(1000, 9999)}",
            "format": self.format,
            "team1": team1,
            "team2": team2,
            "result": game_result,
            "timestamp": time.time()
        }
    
    def generate_team(self) -> Dict[str, Any]:
        """Generate a random team for self-play"""
        try:
            # Call team builder service
            response = requests.post(
                f"{self.teambuilder_url}/build",
                json={
                    "format": self.format,
                    "includeTera": True,
                    "roleHints": random.sample(
                        ["sweeper", "wall", "hazard_setter", "hazard_removal", "speed_control"],
                        k=random.randint(2, 4)
                    )
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["team"]
            else:
                logger.warning(f"Team builder failed: {response.status_code}")
                return self.get_fallback_team()
                
        except Exception as e:
            logger.error(f"Error generating team: {e}")
            return self.get_fallback_team()
    
    def get_fallback_team(self) -> Dict[str, Any]:
        """Get a fallback team when team builder fails"""
        # Simple fallback team
        return {
            "pokemon": [
                {"species": "Dragapult", "ability": "Clear Body", "moves": ["Shadow Ball", "Dragon Pulse"]},
                {"species": "Garchomp", "ability": "Rough Skin", "moves": ["Earthquake", "Dragon Claw"]},
                {"species": "Landorus-Therian", "ability": "Intimidate", "moves": ["Earthquake", "U-turn"]},
                {"species": "Heatran", "ability": "Flash Fire", "moves": ["Magma Storm", "Earth Power"]},
                {"species": "Rotom-Wash", "ability": "Levitate", "moves": ["Volt Switch", "Hydro Pump"]},
                {"species": "Toxapex", "ability": "Regenerator", "moves": ["Scald", "Toxic"]}
            ],
            "format": self.format,
            "name": "Fallback Team"
        }
    
    def initialize_battle_state(self, team1: Dict[str, Any], team2: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize battle state for self-play"""
        return {
            "id": f"selfplay_{int(time.time())}",
            "format": self.format,
            "turn": 0,
            "phase": "battle",
            "p1": {
                "name": "Player1",
                "team": team1,
                "active": team1["pokemon"][0],
                "bench": team1["pokemon"][1:],
                "side": {
                    "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False},
                    "screens": {"reflect": False, "lightScreen": False, "auroraVeil": False},
                    "sideConditions": {
                        "tailwind": False,
                        "trickRoom": False,
                        "gravity": False,
                        "wonderRoom": False,
                        "magicRoom": False
                    }
                }
            },
            "p2": {
                "name": "Player2",
                "team": team2,
                "active": team2["pokemon"][0],
                "bench": team2["pokemon"][1:],
                "side": {
                    "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False},
                    "screens": {"reflect": False, "lightScreen": False, "auroraVeil": False},
                    "sideConditions": {
                        "tailwind": False,
                        "trickRoom": False,
                        "gravity": False,
                        "wonderRoom": False,
                        "magicRoom": False
                    }
                }
            },
            "field": {
                "hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False},
                "screens": {"reflect": False, "lightScreen": False, "auroraVeil": False},
                "sideConditions": {
                    "tailwind": False,
                    "trickRoom": False,
                    "gravity": False,
                    "wonderRoom": False,
                    "magicRoom": False
                }
            },
            "log": [],
            "lastActions": {},
            "opponentModel": {
                "evDistributions": {},
                "itemDistributions": {},
                "teraDistributions": {},
                "moveDistributions": {},
                "revealedSets": {}
            }
        }
    
    def play_battle(self, battle_state: Dict[str, Any]) -> Dict[str, Any]:
        """Play a battle between two AI agents"""
        max_turns = 200
        turn = 0
        
        while turn < max_turns:
            try:
                # Get legal actions for both players
                p1_actions = self.get_legal_actions(battle_state, "p1")
                p2_actions = self.get_legal_actions(battle_state, "p2")
                
                if not p1_actions or not p2_actions:
                    break
                
                # Get actions for both players
                p1_action = self.get_ai_action(battle_state, p1_actions, "p1")
                p2_action = self.get_ai_action(battle_state, p2_actions, "p2")
                
                # Apply actions
                self.apply_actions(battle_state, p1_action, p2_action)
                
                # Check for game end
                if self.check_game_end(battle_state):
                    break
                
                turn += 1
                battle_state["turn"] = turn
                
            except Exception as e:
                logger.error(f"Error in turn {turn}: {e}")
                break
        
        # Determine winner
        winner = self.determine_winner(battle_state)
        
        return {
            "winner": winner,
            "turns": turn,
            "p1_remaining": self.count_remaining_pokemon(battle_state["p1"]),
            "p2_remaining": self.count_remaining_pokemon(battle_state["p2"])
        }
    
    def get_legal_actions(self, battle_state: Dict[str, Any], player: str) -> List[Dict[str, Any]]:
        """Get legal actions for a player"""
        actions = []
        
        if player == "p1":
            active = battle_state["p1"]["active"]
            bench = battle_state["p1"]["bench"]
        else:
            active = battle_state["p2"]["active"]
            bench = battle_state["p2"]["bench"]
        
        # Add move actions
        if active and "moves" in active:
            for move in active["moves"]:
                actions.append({"type": "move", "move": move})
        
        # Add switch actions
        for i, pokemon in enumerate(bench):
            if pokemon.get("hp", 0) > 0:
                actions.append({"type": "switch", "pokemon": i})
        
        return actions
    
    def get_ai_action(self, battle_state: Dict[str, Any], legal_actions: List[Dict[str, Any]], player: str) -> Dict[str, Any]:
        """Get AI action for a player"""
        try:
            # Get calc results
            calc_results = self.get_calc_results(battle_state, legal_actions, player)
            
            # Get policy recommendation
            policy_result = self.get_policy_recommendation(battle_state, calc_results, player)
            
            return policy_result
            
        except Exception as e:
            logger.error(f"Error getting AI action for {player}: {e}")
            return random.choice(legal_actions)
    
    def get_calc_results(self, battle_state: Dict[str, Any], legal_actions: List[Dict[str, Any]], player: str) -> List[Dict[str, Any]]:
        """Get calculation results for legal actions"""
        try:
            response = requests.post(
                f"{self.calc_url}/batch-calc",
                json={
                    "state": battle_state,
                    "actions": legal_actions
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["results"]
            else:
                logger.warning(f"Calc service failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting calc results: {e}")
            return []
    
    def get_policy_recommendation(self, battle_state: Dict[str, Any], calc_results: List[Dict[str, Any]], player: str) -> Dict[str, Any]:
        """Get policy recommendation for a player"""
        try:
            response = requests.post(
                f"{self.policy_url}/policy",
                json={
                    "battleState": battle_state,
                    "calcResults": calc_results
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["action"]
            else:
                logger.warning(f"Policy service failed: {response.status_code}")
                return {"type": "pass"}
                
        except Exception as e:
            logger.error(f"Error getting policy recommendation: {e}")
            return {"type": "pass"}
    
    def apply_actions(self, battle_state: Dict[str, Any], p1_action: Dict[str, Any], p2_action: Dict[str, Any]) -> None:
        """Apply actions to battle state"""
        # Simplified action application
        # In a real implementation, this would properly simulate the battle
        
        # Random damage for moves
        if p1_action.get("type") == "move":
            damage = random.randint(20, 80)
            battle_state["p2"]["active"]["hp"] = max(0, battle_state["p2"]["active"]["hp"] - damage)
        
        if p2_action.get("type") == "move":
            damage = random.randint(20, 80)
            battle_state["p1"]["active"]["hp"] = max(0, battle_state["p1"]["active"]["hp"] - damage)
        
        # Handle switches
        if p1_action.get("type") == "switch" and p1_action.get("pokemon") is not None:
            pokemon_index = p1_action["pokemon"]
            if pokemon_index < len(battle_state["p1"]["bench"]):
                # Switch active and bench Pokémon
                active = battle_state["p1"]["active"]
                bench_pokemon = battle_state["p1"]["bench"][pokemon_index]
                battle_state["p1"]["active"] = bench_pokemon
                battle_state["p1"]["bench"][pokemon_index] = active
        
        if p2_action.get("type") == "switch" and p2_action.get("pokemon") is not None:
            pokemon_index = p2_action["pokemon"]
            if pokemon_index < len(battle_state["p2"]["bench"]):
                # Switch active and bench Pokémon
                active = battle_state["p2"]["active"]
                bench_pokemon = battle_state["p2"]["bench"][pokemon_index]
                battle_state["p2"]["active"] = bench_pokemon
                battle_state["p2"]["bench"][pokemon_index] = active
    
    def check_game_end(self, battle_state: Dict[str, Any]) -> bool:
        """Check if the game has ended"""
        p1_remaining = self.count_remaining_pokemon(battle_state["p1"])
        p2_remaining = self.count_remaining_pokemon(battle_state["p2"])
        
        return p1_remaining == 0 or p2_remaining == 0
    
    def count_remaining_pokemon(self, player: Dict[str, Any]) -> int:
        """Count remaining Pokémon for a player"""
        count = 0
        
        if player["active"] and player["active"].get("hp", 0) > 0:
            count += 1
        
        for pokemon in player["bench"]:
            if pokemon.get("hp", 0) > 0:
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
    
    def log_progress(self) -> None:
        """Log progress statistics"""
        if not self.results:
            return
        
        wins = sum(1 for r in self.results if r["result"]["winner"] == "p1")
        losses = sum(1 for r in self.results if r["result"]["winner"] == "p2")
        ties = sum(1 for r in self.results if r["result"]["winner"] == "tie")
        
        avg_turns = sum(r["result"]["turns"] for r in self.results) / len(self.results)
        
        logger.info(f"Progress: {wins}W-{losses}L-{ties}T, Avg turns: {avg_turns:.1f}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run self-play games")
    parser.add_argument("--games", type=int, default=50, help="Number of games to play")
    parser.add_argument("--format", default="gen9ou", help="Format to play")
    parser.add_argument("--output", default="data/reports/selfplay_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run simulator
    simulator = SelfPlaySimulator(args.format)
    results = simulator.run_games(args.games)
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {args.output}")
    
    # Print summary
    wins = sum(1 for r in results if r["result"]["winner"] == "p1")
    losses = sum(1 for r in results if r["result"]["winner"] == "p2")
    ties = sum(1 for r in results if r["result"]["winner"] == "tie")
    avg_turns = sum(r["result"]["turns"] for r in results) / len(results)
    
    print(f"\n=== Self-Play Results ===")
    print(f"Games played: {len(results)}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Ties: {ties}")
    print(f"Average turns: {avg_turns:.1f}")

if __name__ == "__main__":
    main()
