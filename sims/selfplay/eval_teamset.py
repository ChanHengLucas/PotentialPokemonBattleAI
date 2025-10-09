#!/usr/bin/env python3
"""
PokéAI Team Evaluation Script

Evaluates multiple candidate teams through self-play and selects the best one.
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

class TeamEvaluator:
    """Evaluates teams through self-play"""
    
    def __init__(self, format_name: str = "gen9ou"):
        self.format = format_name
        self.teambuilder_url = "http://localhost:8001"
        self.evaluation_results = []
    
    def evaluate_teams(self, num_candidates: int, games_per_team: int) -> Dict[str, Any]:
        """Evaluate multiple candidate teams"""
        logger.info(f"Evaluating {num_candidates} candidate teams with {games_per_team} games each")
        
        # Generate candidate teams
        candidates = self.generate_candidate_teams(num_candidates)
        
        # Evaluate each team
        team_scores = []
        for i, team in enumerate(candidates):
            logger.info(f"Evaluating team {i + 1}/{num_candidates}")
            score = self.evaluate_single_team(team, games_per_team)
            team_scores.append({
                "team": team,
                "score": score,
                "index": i
            })
        
        # Sort by score
        team_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Select best team
        best_team = team_scores[0]
        
        # Save results
        self.save_evaluation_results(team_scores, best_team)
        
        return best_team
    
    def generate_candidate_teams(self, num_candidates: int) -> List[Dict[str, Any]]:
        """Generate candidate teams with different strategies"""
        candidates = []
        
        # Different role combinations to try
        role_combinations = [
            ["sweeper", "wall", "hazard_setter"],
            ["sweeper", "wall", "hazard_removal"],
            ["sweeper", "speed_control", "hazard_setter"],
            ["wall", "hazard_setter", "hazard_removal"],
            ["sweeper", "wall", "speed_control", "hazard_setter"],
            ["sweeper", "wall", "hazard_setter", "hazard_removal"],
            ["sweeper", "speed_control", "hazard_setter", "hazard_removal"],
            ["wall", "speed_control", "hazard_setter", "hazard_removal"]
        ]
        
        for i in range(num_candidates):
            try:
                # Select role combination
                if i < len(role_combinations):
                    role_hints = role_combinations[i]
                else:
                    role_hints = random.sample(
                        ["sweeper", "wall", "hazard_setter", "hazard_removal", "speed_control"],
                        k=random.randint(2, 4)
                    )
                
                # Generate team
                team = self.generate_team(role_hints)
                candidates.append(team)
                
            except Exception as e:
                logger.error(f"Error generating candidate {i + 1}: {e}")
                # Use fallback team
                candidates.append(self.get_fallback_team())
        
        return candidates
    
    def generate_team(self, role_hints: List[str]) -> Dict[str, Any]:
        """Generate a team with specific role hints"""
        try:
            response = requests.post(
                f"{self.teambuilder_url}/build",
                json={
                    "format": self.format,
                    "includeTera": True,
                    "roleHints": role_hints
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
    
    def evaluate_single_team(self, team: Dict[str, Any], num_games: int) -> float:
        """Evaluate a single team through self-play"""
        wins = 0
        total_games = 0
        
        for game_num in range(num_games):
            try:
                # Generate opponent team
                opponent_team = self.generate_opponent_team()
                
                # Play game
                result = self.play_game(team, opponent_team)
                
                if result == "win":
                    wins += 1
                total_games += 1
                
            except Exception as e:
                logger.error(f"Error in evaluation game {game_num + 1}: {e}")
                continue
        
        if total_games == 0:
            return 0.0
        
        win_rate = wins / total_games
        
        # Calculate synergy score
        synergy_score = self.calculate_synergy_score(team)
        
        # Combined score
        combined_score = win_rate * 0.7 + synergy_score * 0.3
        
        logger.info(f"Team evaluation: {wins}W-{total_games-wins}L ({win_rate:.2f} win rate, {synergy_score:.2f} synergy)")
        
        return combined_score
    
    def generate_opponent_team(self) -> Dict[str, Any]:
        """Generate a random opponent team"""
        try:
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
                return self.get_fallback_team()
                
        except Exception as e:
            logger.error(f"Error generating opponent team: {e}")
            return self.get_fallback_team()
    
    def play_game(self, team1: Dict[str, Any], team2: Dict[str, Any]) -> str:
        """Play a game between two teams"""
        # Simplified game simulation
        # In a real implementation, this would use a proper battle simulator
        
        # Random outcome based on team quality
        team1_score = self.calculate_team_quality(team1)
        team2_score = self.calculate_team_quality(team2)
        
        # Add some randomness
        team1_score += random.uniform(-0.1, 0.1)
        team2_score += random.uniform(-0.1, 0.1)
        
        if team1_score > team2_score:
            return "win"
        elif team2_score > team1_score:
            return "loss"
        else:
            return "tie"
    
    def calculate_team_quality(self, team: Dict[str, Any]) -> float:
        """Calculate team quality score"""
        score = 0.0
        
        # Base score for having 6 Pokémon
        if len(team["pokemon"]) == 6:
            score += 1.0
        
        # Score for type diversity
        types = set()
        for pokemon in team["pokemon"]:
            # This would check actual types in a real implementation
            types.add("Normal")  # Placeholder
        
        score += len(types) * 0.1
        
        # Score for role coverage
        roles = set()
        for pokemon in team["pokemon"]:
            # This would determine roles in a real implementation
            roles.add("sweeper")  # Placeholder
        
        score += len(roles) * 0.1
        
        return min(1.0, score)
    
    def calculate_synergy_score(self, team: Dict[str, Any]) -> float:
        """Calculate team synergy score"""
        # Simplified synergy calculation
        # In a real implementation, this would analyze type coverage, role balance, etc.
        
        score = 0.5  # Base score
        
        # Check for type synergies
        if len(team["pokemon"]) >= 3:
            score += 0.2
        
        # Check for role balance
        if len(team["pokemon"]) == 6:
            score += 0.3
        
        return min(1.0, score)
    
    def save_evaluation_results(self, team_scores: List[Dict[str, Any]], best_team: Dict[str, Any]) -> None:
        """Save evaluation results"""
        # Create reports directory
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        results_file = reports_dir / "team_evaluation_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "evaluation_time": time.time(),
                "format": self.format,
                "team_scores": team_scores,
                "best_team": best_team
            }, f, indent=2)
        
        # Save best team to latest.json
        teams_dir = Path("data/teams")
        teams_dir.mkdir(parents=True, exist_ok=True)
        
        latest_file = teams_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump({
                "team": best_team["team"],
                "score": best_team["score"],
                "evaluation_time": time.time(),
                "format": self.format
            }, f, indent=2)
        
        logger.info(f"Best team saved to {latest_file}")
        logger.info(f"Detailed results saved to {results_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Evaluate candidate teams")
    parser.add_argument("--candidates", type=int, default=8, help="Number of candidate teams")
    parser.add_argument("--games", type=int, default=20, help="Games per team")
    parser.add_argument("--format", default="gen9ou", help="Format to evaluate")
    
    args = parser.parse_args()
    
    # Run evaluation
    evaluator = TeamEvaluator(args.format)
    best_team = evaluator.evaluate_teams(args.candidates, args.games)
    
    # Print results
    print(f"\n=== Team Evaluation Results ===")
    print(f"Best team score: {best_team['score']:.3f}")
    print(f"Best team saved to data/teams/latest.json")
    
    # Show team composition
    print(f"\nBest team composition:")
    for i, pokemon in enumerate(best_team["team"]["pokemon"]):
        print(f"  {i+1}. {pokemon['species']} ({pokemon.get('ability', 'Unknown')})")

if __name__ == "__main__":
    main()
