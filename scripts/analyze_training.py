#!/usr/bin/env python3
"""
PokéAI Training Data Analysis Script

Analyzes training data to provide insights into model performance,
learning progress, and areas for improvement.
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingAnalyzer:
    """Analyzes training data and provides insights"""
    
    def __init__(self, data_dir: str = "data/training"):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path("data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_training_history(self) -> Dict[str, Any]:
        """Analyze the complete training history"""
        logger.info("Analyzing training history")
        
        history_file = self.data_dir / "training_history.json"
        if not history_file.exists():
            logger.warning("No training history found")
            return {"error": "No training history found"}
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        if not history:
            logger.warning("Empty training history")
            return {"error": "Empty training history"}
        
        analysis = {
            "total_cycles": len(history),
            "total_games": sum(cycle.get("games_played", 0) for cycle in history),
            "total_duration": sum(cycle.get("duration", 0) for cycle in history),
            "score_progression": [],
            "performance_metrics": {},
            "improvement_areas": [],
            "recommendations": []
        }
        
        # Extract score progression
        for cycle in history:
            if "best_team_score" in cycle:
                analysis["score_progression"].append({
                    "cycle": cycle.get("cycle_id", "unknown"),
                    "score": cycle["best_team_score"],
                    "timestamp": cycle.get("timestamp", 0)
                })
        
        # Calculate performance metrics
        if len(analysis["score_progression"]) > 1:
            scores = [p["score"] for p in analysis["score_progression"]]
            analysis["performance_metrics"] = {
                "initial_score": scores[0],
                "final_score": scores[-1],
                "total_improvement": scores[-1] - scores[0],
                "average_score": np.mean(scores),
                "score_volatility": np.std(scores),
                "improvement_rate": (scores[-1] - scores[0]) / len(scores) if len(scores) > 1 else 0
            }
        
        # Identify improvement areas
        analysis["improvement_areas"] = self.identify_improvement_areas(history)
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_recommendations(analysis)
        
        return analysis
    
    def identify_improvement_areas(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify areas for improvement based on training history"""
        improvement_areas = []
        
        if len(history) < 2:
            return ["Insufficient data for analysis"]
        
        # Check for stagnant performance
        recent_scores = [cycle.get("best_team_score", 0) for cycle in history[-3:]]
        if len(recent_scores) >= 2 and max(recent_scores) - min(recent_scores) < 0.05:
            improvement_areas.append("Performance appears stagnant - consider adjusting training parameters")
        
        # Check for high volatility
        all_scores = [cycle.get("best_team_score", 0) for cycle in history if "best_team_score" in cycle]
        if len(all_scores) > 3:
            score_std = np.std(all_scores)
            if score_std > 0.1:
                improvement_areas.append("High score volatility - consider more stable training approach")
        
        # Check for low game counts
        recent_games = [cycle.get("games_played", 0) for cycle in history[-3:]]
        if any(games < 50 for games in recent_games):
            improvement_areas.append("Low game counts may limit learning - consider increasing games per cycle")
        
        # General improvement suggestions
        improvement_areas.extend([
            "Consider diversifying team compositions",
            "Analyze move selection patterns for optimization",
            "Review battle phase strategies",
            "Evaluate team synergy calculations"
        ])
        
        return improvement_areas
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        metrics = analysis.get("performance_metrics", {})
        
        # Score-based recommendations
        if metrics.get("total_improvement", 0) < 0.1:
            recommendations.append("Low improvement rate - consider increasing training cycles or games per cycle")
        
        if metrics.get("score_volatility", 0) > 0.15:
            recommendations.append("High score volatility - consider more stable training parameters")
        
        # Cycle-based recommendations
        if analysis["total_cycles"] < 5:
            recommendations.append("Limited training cycles - run more cycles for better insights")
        
        if analysis["total_games"] < 500:
            recommendations.append("Limited training data - increase games per cycle")
        
        # General recommendations
        recommendations.extend([
            "Monitor training progress regularly",
            "Save model checkpoints at regular intervals",
            "Analyze battle logs for specific improvement patterns",
            "Consider A/B testing different training strategies"
        ])
        
        return recommendations
    
    def analyze_battle_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in battle data"""
        logger.info("Analyzing battle patterns")
        
        battle_files = list(self.data_dir.glob("selfplay_*.json"))
        if not battle_files:
            logger.warning("No battle data found")
            return {"error": "No battle data found"}
        
        patterns = {
            "total_battles": 0,
            "average_turns": 0,
            "win_distribution": {},
            "team_compositions": {},
            "move_usage": {},
            "battle_outcomes": []
        }
        
        all_turns = []
        win_counts = {"p1": 0, "p2": 0, "tie": 0}
        
        for battle_file in battle_files:
            try:
                with open(battle_file, 'r') as f:
                    battles = json.load(f)
                
                for battle in battles:
                    patterns["total_battles"] += 1
                    
                    # Analyze turns
                    if "result" in battle and "turns" in battle["result"]:
                        all_turns.append(battle["result"]["turns"])
                    
                    # Analyze winners
                    if "result" in battle and "winner" in battle["result"]:
                        winner = battle["result"]["winner"]
                        win_counts[winner] = win_counts.get(winner, 0) + 1
                    
                    # Analyze team compositions
                    if "team1" in battle:
                        comp1 = self.extract_team_composition(battle["team1"])
                        patterns["team_compositions"][comp1] = patterns["team_compositions"].get(comp1, 0) + 1
                    
                    if "team2" in battle:
                        comp2 = self.extract_team_composition(battle["team2"])
                        patterns["team_compositions"][comp2] = patterns["team_compositions"].get(comp2, 0) + 1
                    
            except Exception as e:
                logger.warning(f"Error analyzing {battle_file}: {e}")
                continue
        
        # Calculate averages
        if all_turns:
            patterns["average_turns"] = np.mean(all_turns)
        
        patterns["win_distribution"] = win_counts
        
        return patterns
    
    def extract_team_composition(self, team: Dict[str, Any]) -> str:
        """Extract team composition signature"""
        if "pokemon" in team:
            species = [pokemon.get("species", "Unknown") for pokemon in team["pokemon"]]
            return "-".join(sorted(species))
        return "Unknown"
    
    def create_visualizations(self, analysis: Dict[str, Any]) -> None:
        """Create visualizations of training progress"""
        logger.info("Creating training visualizations")
        
        if "score_progression" not in analysis or not analysis["score_progression"]:
            logger.warning("No score progression data for visualization")
            return
        
        # Create score progression plot
        scores = [p["score"] for p in analysis["score_progression"]]
        cycles = list(range(1, len(scores) + 1))
        
        plt.figure(figsize=(12, 8))
        
        # Score progression
        plt.subplot(2, 2, 1)
        plt.plot(cycles, scores, 'b-o', linewidth=2, markersize=6)
        plt.title('Training Score Progression')
        plt.xlabel('Training Cycle')
        plt.ylabel('Best Team Score')
        plt.grid(True, alpha=0.3)
        
        # Score improvement
        if len(scores) > 1:
            improvements = [scores[i] - scores[i-1] for i in range(1, len(scores))]
            plt.subplot(2, 2, 2)
            plt.bar(range(1, len(improvements) + 1), improvements, color='green', alpha=0.7)
            plt.title('Score Improvement Per Cycle')
            plt.xlabel('Cycle')
            plt.ylabel('Score Improvement')
            plt.grid(True, alpha=0.3)
        
        # Training duration
        if "total_duration" in analysis:
            plt.subplot(2, 2, 3)
            duration_hours = analysis["total_duration"] / 3600
            plt.pie([duration_hours, 24 - duration_hours], 
                   labels=['Training Time', 'Other'], 
                   autopct='%1.1f%%',
                   colors=['lightblue', 'lightgray'])
            plt.title(f'Training Time Distribution\n({duration_hours:.1f} hours total)')
        
        # Games per cycle
        if "total_cycles" in analysis and "total_games" in analysis:
            plt.subplot(2, 2, 4)
            games_per_cycle = analysis["total_games"] / analysis["total_cycles"]
            plt.bar(['Games per Cycle'], [games_per_cycle], color='orange', alpha=0.7)
            plt.title(f'Average Games per Cycle\n({games_per_cycle:.0f} games)')
            plt.ylabel('Games')
        
        plt.tight_layout()
        
        # Save plot
        plot_file = self.reports_dir / "training_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Training visualizations saved to {plot_file}")
    
    def generate_report(self) -> None:
        """Generate comprehensive training analysis report"""
        logger.info("Generating comprehensive training analysis report")
        
        # Analyze training history
        history_analysis = self.analyze_training_history()
        
        # Analyze battle patterns
        battle_analysis = self.analyze_battle_patterns()
        
        # Create visualizations
        self.create_visualizations(history_analysis)
        
        # Generate report
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "training_history": history_analysis,
            "battle_patterns": battle_analysis,
            "summary": {
                "total_cycles": history_analysis.get("total_cycles", 0),
                "total_games": history_analysis.get("total_games", 0),
                "total_duration_hours": history_analysis.get("total_duration", 0) / 3600,
                "current_best_score": history_analysis.get("score_progression", [{}])[-1].get("score", 0) if history_analysis.get("score_progression") else 0,
                "improvement_areas": history_analysis.get("improvement_areas", []),
                "recommendations": history_analysis.get("recommendations", [])
            }
        }
        
        # Save report
        report_file = self.reports_dir / "training_analysis_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n=== Training Analysis Report ===")
        print(f"Total cycles: {report['summary']['total_cycles']}")
        print(f"Total games: {report['summary']['total_games']}")
        print(f"Total duration: {report['summary']['total_duration_hours']:.1f} hours")
        print(f"Current best score: {report['summary']['current_best_score']:.3f}")
        
        if report['summary']['improvement_areas']:
            print("\nImprovement Areas:")
            for area in report['summary']['improvement_areas']:
                print(f"  - {area}")
        
        if report['summary']['recommendations']:
            print("\nRecommendations:")
            for rec in report['summary']['recommendations']:
                print(f"  - {rec}")
        
        print(f"\nDetailed report saved to: {report_file}")
        print(f"Visualizations saved to: {self.reports_dir}/training_analysis.png")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Analyze PokéAI training data")
    parser.add_argument("--data_dir", default="data/training", help="Training data directory")
    parser.add_argument("--output_dir", default="data/reports", help="Output directory for reports")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = TrainingAnalyzer(args.data_dir)
    
    # Generate comprehensive report
    analyzer.generate_report()

if __name__ == "__main__":
    main()
