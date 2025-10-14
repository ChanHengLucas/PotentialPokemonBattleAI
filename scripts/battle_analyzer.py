#!/usr/bin/env python3
"""
PokéAI Battle Analysis Script

Analyzes battle data to extract learning insights about:
- Move effectiveness and accuracy
- Critical moments and turning points
- Team composition success patterns
- Battle strategy optimization
- AI learning recommendations
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BattleAnalyzer:
    """Analyzes battle data to extract learning insights"""
    
    def __init__(self, data_dir: str = "data/training"):
        self.data_dir = Path(data_dir)
        self.analysis_results = {}
        
    def analyze_battle_data(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze comprehensive battle data"""
        logger.info(f"Analyzing {len(battle_data)} battles")
        
        analysis = {
            "total_battles": len(battle_data),
            "move_effectiveness": self.analyze_move_effectiveness(battle_data),
            "critical_moments": self.analyze_critical_moments(battle_data),
            "team_composition_success": self.analyze_team_compositions(battle_data),
            "battle_patterns": self.analyze_battle_patterns(battle_data),
            "accuracy_analysis": self.analyze_accuracy_patterns(battle_data),
            "damage_analysis": self.analyze_damage_patterns(battle_data),
            "learning_insights": [],
            "recommendations": []
        }
        
        # Generate learning insights
        analysis["learning_insights"] = self.generate_learning_insights(analysis)
        analysis["recommendations"] = self.generate_recommendations(analysis)
        
        return analysis
    
    def analyze_move_effectiveness(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze move effectiveness across all battles"""
        move_stats = defaultdict(lambda: {
            "total_uses": 0,
            "hits": 0,
            "misses": 0,
            "critical_hits": 0,
            "total_damage": 0,
            "effectiveness_multipliers": [],
            "accuracy_rolls": []
        })
        
        for battle in battle_data:
            if "battle_log" not in battle:
                continue
                
            for log_entry in battle["battle_log"]:
                if log_entry.get("action") == "move":
                    move_name = log_entry.get("details", {}).get("move", "unknown")
                    stats = move_stats[move_name]
                    
                    stats["total_uses"] += 1
                    
                    if log_entry.get("result") == "hit":
                        stats["hits"] += 1
                        stats["total_damage"] += log_entry.get("damage", 0)
                        
                        if log_entry.get("critical_hit", False):
                            stats["critical_hits"] += 1
                        
                        if "effectiveness" in log_entry:
                            stats["effectiveness_multipliers"].append(log_entry["effectiveness"])
                    else:
                        stats["misses"] += 1
                    
                    if "accuracy_roll" in log_entry:
                        stats["accuracy_rolls"].append(log_entry["accuracy_roll"])
        
        # Calculate effectiveness metrics
        effectiveness_analysis = {}
        for move_name, stats in move_stats.items():
            if stats["total_uses"] > 0:
                hit_rate = stats["hits"] / stats["total_uses"]
                crit_rate = stats["critical_hits"] / stats["hits"] if stats["hits"] > 0 else 0
                avg_damage = stats["total_damage"] / stats["hits"] if stats["hits"] > 0 else 0
                avg_effectiveness = statistics.mean(stats["effectiveness_multipliers"]) if stats["effectiveness_multipliers"] else 1.0
                
                effectiveness_analysis[move_name] = {
                    "hit_rate": hit_rate,
                    "critical_hit_rate": crit_rate,
                    "average_damage": avg_damage,
                    "average_effectiveness": avg_effectiveness,
                    "total_uses": stats["total_uses"],
                    "reliability_score": hit_rate * avg_effectiveness,
                    "damage_potential": avg_damage * hit_rate
                }
        
        return effectiveness_analysis
    
    def analyze_critical_moments(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze critical moments that determined battle outcomes"""
        critical_moments = []
        
        for battle in battle_data:
            if "battle_log" not in battle:
                continue
            
            battle_critical_moments = []
            for log_entry in battle["battle_log"]:
                # Identify critical moments
                is_critical = False
                impact_score = 0
                
                if log_entry.get("critical_hit", False):
                    is_critical = True
                    impact_score += 2
                
                if log_entry.get("effectiveness", 1.0) > 2.0:
                    is_critical = True
                    impact_score += 1
                
                if log_entry.get("damage", 0) > 80:  # High damage
                    is_critical = True
                    impact_score += 1
                
                if log_entry.get("result") == "status_move" and "burn" in str(log_entry.get("details", {})):
                    is_critical = True
                    impact_score += 1
                
                if is_critical:
                    battle_critical_moments.append({
                        "turn": log_entry.get("turn", 0),
                        "action": log_entry.get("action", ""),
                        "details": log_entry.get("details", {}),
                        "impact_score": impact_score,
                        "damage": log_entry.get("damage", 0),
                        "effectiveness": log_entry.get("effectiveness", 1.0)
                    })
            
            if battle_critical_moments:
                critical_moments.append({
                    "battle_id": battle.get("game_id", "unknown"),
                    "winner": battle.get("result", {}).get("winner", "unknown"),
                    "critical_moments": battle_critical_moments
                })
        
        return {
            "total_critical_moments": sum(len(cm["critical_moments"]) for cm in critical_moments),
            "battles_with_critical_moments": len(critical_moments),
            "critical_moments": critical_moments
        }
    
    def analyze_team_compositions(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze team composition success patterns"""
        team_success = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
        
        for battle in battle_data:
            if "team1" not in battle or "team2" not in battle:
                continue
            
            # Extract team compositions
            team1_comp = self.extract_team_signature(battle["team1"])
            team2_comp = self.extract_team_signature(battle["team2"])
            winner = battle.get("result", {}).get("winner", "tie")
            
            # Track team performance
            if winner == "p1":
                team_success[team1_comp]["wins"] += 1
                team_success[team2_comp]["losses"] += 1
            elif winner == "p2":
                team_success[team2_comp]["wins"] += 1
                team_success[team1_comp]["losses"] += 1
            
            team_success[team1_comp]["total"] += 1
            team_success[team2_comp]["total"] += 1
        
        # Calculate win rates
        composition_analysis = {}
        for comp, stats in team_success.items():
            if stats["total"] > 0:
                win_rate = stats["wins"] / stats["total"]
                composition_analysis[comp] = {
                    "win_rate": win_rate,
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "total_games": stats["total"],
                    "success_score": win_rate * stats["total"]  # Weighted by usage
                }
        
        return composition_analysis
    
    def extract_team_signature(self, team: Dict[str, Any]) -> str:
        """Extract a signature for team composition"""
        if "pokemon" not in team:
            return "unknown"
        
        species = [pokemon.get("species", "Unknown") for pokemon in team["pokemon"]]
        return "-".join(sorted(species))
    
    def analyze_battle_patterns(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze battle patterns and strategies"""
        patterns = {
            "average_turns": 0,
            "turn_distribution": [],
            "early_game_moves": defaultdict(int),
            "late_game_moves": defaultdict(int),
            "switch_frequency": 0,
            "status_move_usage": defaultdict(int)
        }
        
        total_turns = 0
        total_switches = 0
        total_moves = 0
        
        for battle in battle_data:
            if "battle_log" not in battle:
                continue
            
            battle_turns = battle.get("result", {}).get("turns", 0)
            total_turns += battle_turns
            patterns["turn_distribution"].append(battle_turns)
            
            battle_moves = 0
            battle_switches = 0
            
            for i, log_entry in enumerate(battle["battle_log"]):
                if log_entry.get("action") == "move":
                    battle_moves += 1
                    move_name = log_entry.get("details", {}).get("move", "unknown")
                    
                    # Categorize by battle phase
                    if i < battle_turns * 0.3:  # Early game
                        patterns["early_game_moves"][move_name] += 1
                    elif i > battle_turns * 0.7:  # Late game
                        patterns["late_game_moves"][move_name] += 1
                    
                    # Check for status moves
                    if log_entry.get("result") == "status_move":
                        patterns["status_move_usage"][move_name] += 1
                
                elif log_entry.get("action") == "switch":
                    battle_switches += 1
            
            total_switches += battle_switches
            total_moves += battle_moves
        
        if len(battle_data) > 0:
            patterns["average_turns"] = total_turns / len(battle_data)
            patterns["switch_frequency"] = total_switches / total_moves if total_moves > 0 else 0
        
        return patterns
    
    def analyze_accuracy_patterns(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze accuracy patterns and miss causes"""
        accuracy_stats = {
            "overall_accuracy": 0,
            "move_accuracy": defaultdict(lambda: {"hits": 0, "total": 0}),
            "accuracy_by_effectiveness": defaultdict(list),
            "miss_analysis": defaultdict(int)
        }
        
        total_attempts = 0
        total_hits = 0
        
        for battle in battle_data:
            if "battle_log" not in battle:
                continue
            
            for log_entry in battle["battle_log"]:
                if log_entry.get("action") == "move":
                    move_name = log_entry.get("details", {}).get("move", "unknown")
                    stats = accuracy_stats["move_accuracy"][move_name]
                    
                    stats["total"] += 1
                    total_attempts += 1
                    
                    if log_entry.get("result") == "hit":
                        stats["hits"] += 1
                        total_hits += 1
                        
                        # Track accuracy by effectiveness
                        effectiveness = log_entry.get("effectiveness", 1.0)
                        accuracy_stats["accuracy_by_effectiveness"][effectiveness].append(1)
                    else:
                        # Analyze miss causes
                        accuracy_roll = log_entry.get("accuracy_roll", 0)
                        if accuracy_roll > 0.9:
                            accuracy_stats["miss_analysis"]["bad_luck"] += 1
                        else:
                            accuracy_stats["miss_analysis"]["low_accuracy"] += 1
                        
                        accuracy_stats["accuracy_by_effectiveness"][log_entry.get("effectiveness", 1.0)].append(0)
        
        if total_attempts > 0:
            accuracy_stats["overall_accuracy"] = total_hits / total_attempts
        
        return accuracy_stats
    
    def analyze_damage_patterns(self, battle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze damage patterns and effectiveness"""
        damage_stats = {
            "average_damage": 0,
            "damage_by_type": defaultdict(list),
            "high_damage_moves": defaultdict(list),
            "ko_potential": defaultdict(int)
        }
        
        all_damage = []
        
        for battle in battle_data:
            if "battle_log" not in battle:
                continue
            
            for log_entry in battle["battle_log"]:
                if log_entry.get("action") == "move" and log_entry.get("result") == "hit":
                    damage = log_entry.get("damage", 0)
                    move_name = log_entry.get("details", {}).get("move", "unknown")
                    
                    all_damage.append(damage)
                    damage_stats["high_damage_moves"][move_name].append(damage)
                    
                    # Track KO potential
                    if damage > 100:  # High damage threshold
                        damage_stats["ko_potential"][move_name] += 1
        
        if all_damage:
            damage_stats["average_damage"] = statistics.mean(all_damage)
            damage_stats["damage_std"] = statistics.stdev(all_damage) if len(all_damage) > 1 else 0
        
        return damage_stats
    
    def generate_learning_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate learning insights from analysis"""
        insights = []
        
        # Move effectiveness insights
        move_effectiveness = analysis.get("move_effectiveness", {})
        if move_effectiveness:
            best_move = max(move_effectiveness.items(), 
                          key=lambda x: x[1]["reliability_score"])
            worst_move = min(move_effectiveness.items(), 
                           key=lambda x: x[1]["reliability_score"])
            
            insights.append(f"Most reliable move: {best_move[0]} (reliability: {best_move[1]['reliability_score']:.2f})")
            insights.append(f"Least reliable move: {worst_move[0]} (reliability: {worst_move[1]['reliability_score']:.2f})")
        
        # Critical moments insights
        critical_moments = analysis.get("critical_moments", {})
        if critical_moments.get("total_critical_moments", 0) > 0:
            avg_critical_per_battle = critical_moments["total_critical_moments"] / analysis["total_battles"]
            insights.append(f"Average critical moments per battle: {avg_critical_per_battle:.1f}")
        
        # Team composition insights
        team_compositions = analysis.get("team_composition_success", {})
        if team_compositions:
            best_team = max(team_compositions.items(), 
                          key=lambda x: x[1]["success_score"])
            insights.append(f"Most successful team composition: {best_team[0]} (win rate: {best_team[1]['win_rate']:.2f})")
        
        # Accuracy insights
        accuracy_analysis = analysis.get("accuracy_analysis", {})
        if accuracy_analysis.get("overall_accuracy", 0) > 0:
            insights.append(f"Overall move accuracy: {accuracy_analysis['overall_accuracy']:.1%}")
        
        # Battle pattern insights
        battle_patterns = analysis.get("battle_patterns", {})
        if battle_patterns.get("average_turns", 0) > 0:
            insights.append(f"Average battle length: {battle_patterns['average_turns']:.1f} turns")
            insights.append(f"Switch frequency: {battle_patterns['switch_frequency']:.1%} of moves")
        
        return insights
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for AI improvement"""
        recommendations = []
        
        # Move selection recommendations
        move_effectiveness = analysis.get("move_effectiveness", {})
        if move_effectiveness:
            low_accuracy_moves = [move for move, stats in move_effectiveness.items() 
                                if stats["hit_rate"] < 0.7 and stats["total_uses"] > 5]
            if low_accuracy_moves:
                recommendations.append(f"Consider reducing usage of low-accuracy moves: {', '.join(low_accuracy_moves)}")
        
        # Team composition recommendations
        team_compositions = analysis.get("team_composition_success", {})
        if team_compositions:
            low_win_rate_teams = [comp for comp, stats in team_compositions.items() 
                                if stats["win_rate"] < 0.3 and stats["total_games"] > 3]
            if low_win_rate_teams:
                recommendations.append(f"Review team compositions with low win rates: {', '.join(low_win_rate_teams)}")
        
        # Battle strategy recommendations
        battle_patterns = analysis.get("battle_patterns", {})
        if battle_patterns.get("switch_frequency", 0) > 0.3:
            recommendations.append("High switch frequency detected - consider more aggressive play")
        elif battle_patterns.get("switch_frequency", 0) < 0.1:
            recommendations.append("Low switch frequency detected - consider more tactical switching")
        
        # Accuracy recommendations
        accuracy_analysis = analysis.get("accuracy_analysis", {})
        if accuracy_analysis.get("overall_accuracy", 0) < 0.8:
            recommendations.append("Overall accuracy is low - focus on high-accuracy moves")
        
        return recommendations
    
    def save_analysis(self, analysis: Dict[str, Any], output_file: str) -> None:
        """Save analysis results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Analysis saved to {output_path}")
    
    def print_summary(self, analysis: Dict[str, Any]) -> None:
        """Print analysis summary"""
        print("\n=== Battle Analysis Summary ===")
        print(f"Total battles analyzed: {analysis['total_battles']}")
        
        # Move effectiveness summary
        move_effectiveness = analysis.get("move_effectiveness", {})
        if move_effectiveness:
            print(f"\nMove Effectiveness (Top 5):")
            sorted_moves = sorted(move_effectiveness.items(), 
                                key=lambda x: x[1]["reliability_score"], 
                                reverse=True)[:5]
            for move, stats in sorted_moves:
                print(f"  {move}: {stats['hit_rate']:.1%} hit rate, {stats['average_damage']:.1f} avg damage, {stats['reliability_score']:.2f} reliability")
        
        # Critical moments summary
        critical_moments = analysis.get("critical_moments", {})
        if critical_moments.get("total_critical_moments", 0) > 0:
            print(f"\nCritical Moments:")
            print(f"  Total critical moments: {critical_moments['total_critical_moments']}")
            print(f"  Battles with critical moments: {critical_moments['battles_with_critical_moments']}")
        
        # Team composition summary
        team_compositions = analysis.get("team_composition_success", {})
        if team_compositions:
            print(f"\nTeam Composition Success (Top 3):")
            sorted_teams = sorted(team_compositions.items(), 
                                key=lambda x: x[1]["success_score"], 
                                reverse=True)[:3]
            for comp, stats in sorted_teams:
                print(f"  {comp}: {stats['win_rate']:.1%} win rate ({stats['wins']}/{stats['total_games']})")
        
        # Learning insights
        insights = analysis.get("learning_insights", [])
        if insights:
            print(f"\nKey Insights:")
            for insight in insights[:5]:  # Show top 5 insights
                print(f"  - {insight}")
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            print(f"\nRecommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Analyze PokéAI battle data")
    parser.add_argument("--data_file", help="Specific battle data file to analyze")
    parser.add_argument("--data_dir", default="data/training", help="Directory containing battle data")
    parser.add_argument("--output", default="data/reports/battle_analysis.json", help="Output file for analysis")
    parser.add_argument("--summary", action="store_true", help="Print analysis summary")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = BattleAnalyzer(args.data_dir)
    
    # Load battle data
    if args.data_file:
        with open(args.data_file, 'r') as f:
            battle_data = json.load(f)
    else:
        # Load all battle data from directory
        battle_files = list(Path(args.data_dir).glob("selfplay_*.json"))
        battle_data = []
        
        for file_path in battle_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        battle_data.extend(data)
                    else:
                        battle_data.append(data)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
    
    if not battle_data:
        logger.error("No battle data found to analyze")
        return
    
    # Analyze data
    analysis = analyzer.analyze_battle_data(battle_data)
    
    # Save analysis
    analyzer.save_analysis(analysis, args.output)
    
    # Print summary if requested
    if args.summary:
        analyzer.print_summary(analysis)

if __name__ == "__main__":
    main()
