#!/usr/bin/env python3
"""
PokéAI Self-Play Simulator

Runs local self-play games for training and evaluation with comprehensive battle mechanics.
"""

import argparse
import json
import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sims.selfplay.battle_engine import BattleEngine, Pokemon, Move, MoveCategory, StatusCondition

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfPlaySimulator:
    """Simulates Pokémon battles for self-play training with comprehensive mechanics"""
    
    def __init__(self, format_name: str = "gen9ou", fast_mode: bool = False):
        self.format = format_name
        self.fast_mode = fast_mode
        self.calc_url = "http://localhost:3001"
        self.policy_url = "http://localhost:8000"
        self.teambuilder_url = "http://localhost:8001"
        self.games_played = 0
        self.results = []
        
        # Initialize battle engine
        self.battle_engine = BattleEngine()
        
        # Fast mode settings
        if fast_mode:
            self.max_turns = 50  # Shorter battles for faster training
            self.log_level = logging.WARNING  # Reduce logging
        else:
            self.max_turns = 200
            self.log_level = logging.INFO
    
    def run_games(self, num_games: int) -> List[Dict[str, Any]]:
        """Run a series of self-play games with comprehensive battle mechanics"""
        logger.info(f"Starting {num_games} self-play games for {self.format} (fast_mode: {self.fast_mode})")
        
        start_time = time.time()
        
        for game_num in range(num_games):
            try:
                if not self.fast_mode or (game_num + 1) % 10 == 0:
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
        
        total_time = time.time() - start_time
        games_per_second = self.games_played / total_time if total_time > 0 else 0
        
        logger.info(f"Completed {self.games_played} games in {total_time:.2f}s ({games_per_second:.2f} games/sec)")
        return self.results
    
    def play_single_game(self) -> Dict[str, Any]:
        """Play a single self-play game with comprehensive battle mechanics"""
        # Generate two teams
        team1_data = self.generate_team()
        team2_data = self.generate_team()
        
        # Convert team data to Pokemon objects
        team1 = self.convert_team_to_pokemon(team1_data)
        team2 = self.convert_team_to_pokemon(team2_data)
        
        # Simulate battle using battle engine
        battle_result = self.battle_engine.simulate_battle(team1, team2, self.max_turns)
        
        # Analyze battle outcome
        analysis = self.battle_engine.analyze_battle_outcome(battle_result)
        
        return {
            "game_id": f"selfplay_{int(time.time())}_{random.randint(1000, 9999)}",
            "format": self.format,
            "team1": team1_data,
            "team2": team2_data,
            "result": {
                "winner": battle_result["winner"],
                "turns": battle_result["turns"],
                "p1_remaining": self.count_remaining_pokemon_from_teams(team1),
                "p2_remaining": self.count_remaining_pokemon_from_teams(team2)
            },
            "battle_log": battle_result["battle_log"],
            "analysis": analysis,
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
                {"species": "Dragapult", "ability": "Clear Body", "moves": ["Shadow Ball", "Dragon Pulse", "U-turn", "Dragon Dance"]},
                {"species": "Garchomp", "ability": "Rough Skin", "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"]},
                {"species": "Landorus-Therian", "ability": "Intimidate", "moves": ["Earthquake", "U-turn", "Stone Edge", "Stealth Rock"]},
                {"species": "Heatran", "ability": "Flash Fire", "moves": ["Magma Storm", "Earth Power", "Flash Cannon", "Toxic"]},
                {"species": "Rotom-Wash", "ability": "Levitate", "moves": ["Volt Switch", "Hydro Pump", "Will-O-Wisp", "Pain Split"]},
                {"species": "Toxapex", "ability": "Regenerator", "moves": ["Scald", "Toxic", "Recover", "Haze"]}
            ],
            "format": self.format,
            "name": "Fallback Team"
        }
    
    def convert_team_to_pokemon(self, team_data: Dict[str, Any]) -> List[Pokemon]:
        """Convert team data to Pokemon objects"""
        pokemon_list = []
        
        for pokemon_data in team_data["pokemon"]:
            # Create Pokemon from species
            pokemon = self.battle_engine.create_pokemon_from_species(pokemon_data["species"])
            
            # Update with team data
            pokemon.ability = pokemon_data.get("ability", pokemon.ability)
            pokemon.item = pokemon_data.get("item", "")
            
            # Update moves
            pokemon.moves = []
            for move_name in pokemon_data.get("moves", []):
                move_data = self.battle_engine.get_move_data(move_name)
                if move_data:
                    pokemon.moves.append(Move(**move_data))
            
            pokemon_list.append(pokemon)
        
        return pokemon_list
    
    def count_remaining_pokemon_from_teams(self, team: List[Pokemon]) -> int:
        """Count remaining Pokemon from team list"""
        return sum(1 for pokemon in team if pokemon.hp > 0)
    
    
    def log_progress(self) -> None:
        """Log progress statistics with detailed analysis"""
        if not self.results:
            return
        
        wins = sum(1 for r in self.results if r["result"]["winner"] == "p1")
        losses = sum(1 for r in self.results if r["result"]["winner"] == "p2")
        ties = sum(1 for r in self.results if r["result"]["winner"] == "tie")
        
        avg_turns = sum(r["result"]["turns"] for r in self.results) / len(self.results)
        
        # Analyze move effectiveness
        move_stats = {}
        critical_hits = 0
        total_moves = 0
        
        for result in self.results:
            if "battle_log" in result:
                for log_entry in result["battle_log"]:
                    if log_entry.get("action") == "move":
                        total_moves += 1
                        if log_entry.get("critical_hit", False):
                            critical_hits += 1
                        
                        move_name = log_entry.get("details", {}).get("move", "unknown")
                        if move_name not in move_stats:
                            move_stats[move_name] = {"hits": 0, "total": 0}
                        
                        move_stats[move_name]["total"] += 1
                        if log_entry.get("result") == "hit":
                            move_stats[move_name]["hits"] += 1
        
        logger.info(f"Progress: {wins}W-{losses}L-{ties}T, Avg turns: {avg_turns:.1f}")
        
        if total_moves > 0:
            crit_rate = (critical_hits / total_moves) * 100
            logger.info(f"Critical hit rate: {crit_rate:.1f}% ({critical_hits}/{total_moves})")
        
        # Log most effective moves
        if move_stats:
            best_moves = sorted(move_stats.items(), 
                              key=lambda x: x[1]["hits"] / x[1]["total"] if x[1]["total"] > 0 else 0, 
                              reverse=True)[:3]
            logger.info(f"Most effective moves: {', '.join([f'{move}({stats['hits']}/{stats['total']})' for move, stats in best_moves])}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run self-play games with comprehensive battle mechanics")
    parser.add_argument("--games", type=int, default=50, help="Number of games to play")
    parser.add_argument("--format", default="gen9ou", help="Format to play")
    parser.add_argument("--output", default="data/reports/selfplay_results.json", help="Output file")
    parser.add_argument("--fast", action="store_true", help="Enable fast mode for rapid training")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.fast:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run simulator
    simulator = SelfPlaySimulator(args.format, fast_mode=args.fast)
    results = simulator.run_games(args.games)
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {args.output}")
    
    # Print detailed summary
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
    
    # Analyze battle mechanics
    total_critical_hits = 0
    total_moves = 0
    move_effectiveness = {}
    
    for result in results:
        if "battle_log" in result:
            for log_entry in result["battle_log"]:
                if log_entry.get("action") == "move":
                    total_moves += 1
                    if log_entry.get("critical_hit", False):
                        total_critical_hits += 1
                    
                    move_name = log_entry.get("details", {}).get("move", "unknown")
                    if move_name not in move_effectiveness:
                        move_effectiveness[move_name] = {"hits": 0, "total": 0, "damage": 0}
                    
                    move_effectiveness[move_name]["total"] += 1
                    if log_entry.get("result") == "hit":
                        move_effectiveness[move_name]["hits"] += 1
                        move_effectiveness[move_name]["damage"] += log_entry.get("damage", 0)
    
    if total_moves > 0:
        crit_rate = (total_critical_hits / total_moves) * 100
        print(f"Critical hit rate: {crit_rate:.1f}% ({total_critical_hits}/{total_moves})")
    
    # Show most effective moves
    if move_effectiveness:
        best_moves = sorted(move_effectiveness.items(), 
                          key=lambda x: x[1]["hits"] / x[1]["total"] if x[1]["total"] > 0 else 0, 
                          reverse=True)[:5]
        print(f"\nMost effective moves:")
        for move, stats in best_moves:
            hit_rate = (stats["hits"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            avg_damage = stats["damage"] / stats["hits"] if stats["hits"] > 0 else 0
            print(f"  {move}: {hit_rate:.1f}% hit rate, {avg_damage:.1f} avg damage ({stats['hits']}/{stats['total']})")

if __name__ == "__main__":
    main()
