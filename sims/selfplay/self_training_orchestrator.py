#!/usr/bin/env python3
"""
PokéAI Self-Training Orchestrator

This script orchestrates the complete self-training pipeline:
1. Generates self-play data through battles
2. Analyzes battle data to extract learning insights
3. Retrains models based on new data
4. Evaluates model improvements
5. Saves training data for future analysis
"""

import argparse
import json
import logging
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import subprocess
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sims.selfplay.run import SelfPlaySimulator
from sims.selfplay.eval_teamset import TeamEvaluator
from scripts.battle_analyzer import BattleAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/self_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SelfTrainingOrchestrator:
    """Orchestrates the complete self-training pipeline"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.training_data_dir = Path("data/training")
        self.models_dir = Path("models")
        self.checkpoints_dir = Path("models/checkpoints")
        self.reports_dir = Path("data/reports")
        self.logs_dir = Path("logs")
        
        # Create directories
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Training state
        self.current_iteration = 0
        self.training_history = []
        
    def run_full_training_cycle(self) -> Dict[str, Any]:
        """Run a complete self-training cycle"""
        logger.info("Starting full self-training cycle")
        
        cycle_start_time = time.time()
        cycle_id = f"cycle_{int(cycle_start_time)}"
        
        # Phase 1: Generate self-play data
        logger.info("Phase 1: Generating self-play data")
        selfplay_data = self.generate_selfplay_data()
        
        # Phase 2: Analyze battle data
        logger.info("Phase 2: Analyzing battle data")
        analysis_results = self.analyze_battle_data(selfplay_data)
        
        # Phase 3: Retrain models
        logger.info("Phase 3: Retraining models")
        training_results = self.retrain_models(analysis_results)
        
        # Phase 4: Evaluate improvements
        logger.info("Phase 4: Evaluating model improvements")
        evaluation_results = self.evaluate_model_improvements()
        
        # Phase 5: Save training data
        logger.info("Phase 5: Saving training data")
        self.save_training_data(cycle_id, {
            "selfplay_data": selfplay_data,
            "analysis_results": analysis_results,
            "training_results": training_results,
            "evaluation_results": evaluation_results
        })
        
        cycle_duration = time.time() - cycle_start_time
        
        # Update training history
        cycle_summary = {
            "cycle_id": cycle_id,
            "timestamp": cycle_start_time,
            "duration": cycle_duration,
            "games_played": len(selfplay_data),
            "model_improvements": evaluation_results.get("improvements", {}),
            "best_team_score": evaluation_results.get("best_team_score", 0.0)
        }
        
        self.training_history.append(cycle_summary)
        self.current_iteration += 1
        
        logger.info(f"Training cycle {cycle_id} completed in {cycle_duration:.2f} seconds")
        
        return cycle_summary
    
    def generate_selfplay_data(self) -> List[Dict[str, Any]]:
        """Generate self-play data through battles with fast simulation"""
        logger.info(f"Generating {self.config['selfplay_games']} self-play games")
        
        # Run self-play simulator in fast mode for training
        simulator = SelfPlaySimulator(self.config['format'], fast_mode=True)
        results = simulator.run_games(self.config['selfplay_games'])
        
        # Save raw self-play data
        timestamp = int(time.time())
        selfplay_file = self.training_data_dir / f"selfplay_{timestamp}.json"
        with open(selfplay_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Log detailed statistics
        total_moves = 0
        critical_hits = 0
        move_effectiveness = {}
        
        for result in results:
            if "battle_log" in result:
                for log_entry in result["battle_log"]:
                    if log_entry.get("action") == "move":
                        total_moves += 1
                        if log_entry.get("critical_hit", False):
                            critical_hits += 1
                        
                        move_name = log_entry.get("details", {}).get("move", "unknown")
                        if move_name not in move_effectiveness:
                            move_effectiveness[move_name] = {"hits": 0, "total": 0, "damage": 0}
                        
                        move_effectiveness[move_name]["total"] += 1
                        if log_entry.get("result") == "hit":
                            move_effectiveness[move_name]["hits"] += 1
                            move_effectiveness[move_name]["damage"] += log_entry.get("damage", 0)
        
        logger.info(f"Self-play data saved to {selfplay_file}")
        logger.info(f"Battle statistics: {total_moves} moves, {critical_hits} critical hits ({critical_hits/total_moves*100:.1f}% if total_moves > 0 else 0)")
        
        return results
    
    def analyze_battle_data(self, selfplay_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze battle data to extract learning insights using comprehensive battle analyzer"""
        logger.info("Analyzing battle data for learning insights")
        
        # Use the comprehensive battle analyzer
        analyzer = BattleAnalyzer(str(self.training_data_dir))
        analysis = analyzer.analyze_battle_data(selfplay_data)
        
        # Add additional training-specific analysis
        analysis["training_insights"] = self.extract_training_insights(selfplay_data)
        analysis["model_improvement_areas"] = self.identify_model_improvement_areas(analysis)
        
        # Save analysis results
        timestamp = int(time.time())
        analysis_file = self.training_data_dir / f"analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Comprehensive battle analysis saved to {analysis_file}")
        return analysis
    
    def extract_team_composition(self, team: Dict[str, Any]) -> str:
        """Extract team composition signature"""
        species = [pokemon["species"] for pokemon in team["pokemon"]]
        return "-".join(sorted(species))
    
    def identify_improvement_areas(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify areas for model improvement"""
        improvement_areas = []
        
        # Find low-performing team compositions
        for comp, stats in analysis["win_rates"].items():
            if stats["total"] >= 3 and stats["win_rate"] < 0.3:
                improvement_areas.append(f"Low-performing composition: {comp} ({stats['win_rate']:.2f} win rate)")
        
        # Add general improvement suggestions
        improvement_areas.extend([
            "Optimize move selection for different battle phases",
            "Improve team synergy calculations",
            "Better hazard control strategies",
            "Enhanced prediction of opponent moves"
        ])
        
        return improvement_areas
    
    def extract_training_insights(self, selfplay_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract training-specific insights from battle data"""
        insights = {
            "battle_length_distribution": [],
            "move_diversity": {},
            "critical_decision_points": [],
            "learning_opportunities": []
        }
        
        for battle in selfplay_data:
            # Track battle lengths
            insights["battle_length_distribution"].append(battle.get("result", {}).get("turns", 0))
            
            # Track move diversity
            if "battle_log" in battle:
                moves_used = set()
                for log_entry in battle["battle_log"]:
                    if log_entry.get("action") == "move":
                        move_name = log_entry.get("details", {}).get("move", "unknown")
                        moves_used.add(move_name)
                
                for move in moves_used:
                    insights["move_diversity"][move] = insights["move_diversity"].get(move, 0) + 1
        
        return insights
    
    def identify_model_improvement_areas(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify areas for model improvement based on comprehensive analysis"""
        improvement_areas = []
        
        # Move effectiveness improvements
        move_effectiveness = analysis.get("move_effectiveness", {})
        if move_effectiveness:
            low_accuracy_moves = [move for move, stats in move_effectiveness.items() 
                                if stats["hit_rate"] < 0.7 and stats["total_uses"] > 5]
            if low_accuracy_moves:
                improvement_areas.append(f"Improve accuracy for moves: {', '.join(low_accuracy_moves)}")
        
        # Team composition improvements
        team_compositions = analysis.get("team_composition_success", {})
        if team_compositions:
            low_win_rate_teams = [comp for comp, stats in team_compositions.items() 
                                if stats["win_rate"] < 0.3 and stats["total_games"] > 3]
            if low_win_rate_teams:
                improvement_areas.append(f"Optimize team compositions: {', '.join(low_win_rate_teams)}")
        
        # Battle strategy improvements
        battle_patterns = analysis.get("battle_patterns", {})
        if battle_patterns.get("switch_frequency", 0) > 0.3:
            improvement_areas.append("Reduce excessive switching - focus on positioning")
        elif battle_patterns.get("switch_frequency", 0) < 0.1:
            improvement_areas.append("Increase tactical switching for better positioning")
        
        # Critical moments analysis
        critical_moments = analysis.get("critical_moments", {})
        if critical_moments.get("total_critical_moments", 0) > 0:
            improvement_areas.append("Improve recognition and exploitation of critical moments")
        
        # Add general improvement suggestions
        improvement_areas.extend([
            "Enhance move selection algorithms for different battle phases",
            "Improve team synergy and type coverage calculations",
            "Better hazard control and screen management strategies",
            "Enhanced opponent move prediction and counter-play"
        ])
        
        return improvement_areas
    
    def retrain_models(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Retrain models based on analysis results"""
        logger.info("Retraining models with new data")
        
        training_results = {
            "policy_training": {},
            "teambuilder_training": {},
            "timestamp": time.time()
        }
        
        # Retrain policy model
        try:
            logger.info("Retraining policy model")
            policy_result = self.retrain_policy_model(analysis_results)
            training_results["policy_training"] = policy_result
        except Exception as e:
            logger.error(f"Policy model retraining failed: {e}")
            training_results["policy_training"] = {"error": str(e)}
        
        # Retrain team builder model
        try:
            logger.info("Retraining team builder model")
            teambuilder_result = self.retrain_teambuilder_model(analysis_results)
            training_results["teambuilder_training"] = teambuilder_result
        except Exception as e:
            logger.error(f"Team builder model retraining failed: {e}")
            training_results["teambuilder_training"] = {"error": str(e)}
        
        return training_results
    
    def retrain_policy_model(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Retrain the policy model"""
        # Run policy training script
        training_script = project_root / "models" / "training" / "train_policy.py"
        
        if not training_script.exists():
            logger.warning("Policy training script not found, skipping policy retraining")
            return {"status": "skipped", "reason": "script_not_found"}
        
        try:
            # Run training with new data
            result = subprocess.run([
                sys.executable, str(training_script),
                "--data_path", str(self.training_data_dir),
                "--output_path", str(self.checkpoints_dir / "policy"),
                "--epochs", str(self.config.get("policy_epochs", 5))
            ], capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info("Policy model retraining completed successfully")
                return {"status": "success", "output": result.stdout}
            else:
                logger.error(f"Policy model retraining failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            logger.error("Policy model retraining timed out")
            return {"status": "timeout"}
        except Exception as e:
            logger.error(f"Policy model retraining error: {e}")
            return {"status": "error", "error": str(e)}
    
    def retrain_teambuilder_model(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Retrain the team builder model"""
        # Run team builder training script
        training_script = project_root / "models" / "training" / "train_teambuilder.py"
        
        if not training_script.exists():
            logger.warning("Team builder training script not found, skipping teambuilder retraining")
            return {"status": "skipped", "reason": "script_not_found"}
        
        try:
            # Run training with new data
            result = subprocess.run([
                sys.executable, str(training_script),
                "--data_path", str(self.training_data_dir),
                "--output_path", str(self.checkpoints_dir / "teambuilder"),
                "--epochs", str(self.config.get("teambuilder_epochs", 5))
            ], capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info("Team builder model retraining completed successfully")
                return {"status": "success", "output": result.stdout}
            else:
                logger.error(f"Team builder model retraining failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            logger.error("Team builder model retraining timed out")
            return {"status": "timeout"}
        except Exception as e:
            logger.error(f"Team builder model retraining error: {e}")
            return {"status": "error", "error": str(e)}
    
    def evaluate_model_improvements(self) -> Dict[str, Any]:
        """Evaluate model improvements through team evaluation"""
        logger.info("Evaluating model improvements")
        
        # Run team evaluation
        evaluator = TeamEvaluator(self.config['format'])
        best_team = evaluator.evaluate_teams(
            self.config.get('evaluation_candidates', 8),
            self.config.get('evaluation_games', 20)
        )
        
        # Compare with previous best team if available
        improvements = self.calculate_improvements(best_team)
        
        evaluation_results = {
            "best_team": best_team,
            "improvements": improvements,
            "timestamp": time.time()
        }
        
        # Save evaluation results
        timestamp = int(time.time())
        eval_file = self.reports_dir / f"evaluation_{timestamp}.json"
        with open(eval_file, 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        
        logger.info(f"Model evaluation saved to {eval_file}")
        return evaluation_results
    
    def calculate_improvements(self, current_best: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate improvements over previous iterations"""
        improvements = {
            "score_improvement": 0.0,
            "team_quality_improvement": 0.0,
            "iteration": self.current_iteration
        }
        
        # Load previous best team for comparison
        latest_team_file = Path("data/teams/latest.json")
        if latest_team_file.exists():
            try:
                with open(latest_team_file, 'r') as f:
                    previous_best = json.load(f)
                
                if "score" in previous_best and "score" in current_best:
                    score_diff = current_best["score"] - previous_best["score"]
                    improvements["score_improvement"] = score_diff
                    
            except Exception as e:
                logger.warning(f"Could not load previous best team: {e}")
        
        return improvements
    
    def save_training_data(self, cycle_id: str, cycle_data: Dict[str, Any]) -> None:
        """Save training data for future analysis"""
        logger.info(f"Saving training data for cycle {cycle_id}")
        
        # Save complete cycle data
        cycle_file = self.training_data_dir / f"cycle_{cycle_id}.json"
        with open(cycle_file, 'w') as f:
            json.dump(cycle_data, f, indent=2)
        
        # Update training history
        history_file = self.training_data_dir / "training_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        # Create summary report
        self.create_training_summary(cycle_id, cycle_data)
        
        logger.info(f"Training data saved to {cycle_file}")
    
    def create_training_summary(self, cycle_id: str, cycle_data: Dict[str, Any]) -> None:
        """Create a summary report of the training cycle"""
        summary = {
            "cycle_id": cycle_id,
            "timestamp": time.time(),
            "games_played": len(cycle_data.get("selfplay_data", [])),
            "analysis_insights": cycle_data.get("analysis_results", {}).get("improvement_areas", []),
            "model_training_status": {
                "policy": cycle_data.get("training_results", {}).get("policy_training", {}).get("status", "unknown"),
                "teambuilder": cycle_data.get("training_results", {}).get("teambuilder_training", {}).get("status", "unknown")
            },
            "best_team_score": cycle_data.get("evaluation_results", {}).get("best_team", {}).get("score", 0.0)
        }
        
        summary_file = self.reports_dir / f"training_summary_{cycle_id}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Training summary saved to {summary_file}")
    
    def run_continuous_training(self, max_cycles: int = None) -> None:
        """Run continuous self-training cycles"""
        logger.info(f"Starting continuous self-training (max cycles: {max_cycles or 'unlimited'})")
        
        cycle_count = 0
        
        try:
            while max_cycles is None or cycle_count < max_cycles:
                logger.info(f"Starting training cycle {cycle_count + 1}")
                
                cycle_summary = self.run_full_training_cycle()
                
                # Log cycle results
                logger.info(f"Cycle {cycle_count + 1} completed:")
                logger.info(f"  Games played: {cycle_summary['games_played']}")
                logger.info(f"  Best team score: {cycle_summary['best_team_score']:.3f}")
                logger.info(f"  Duration: {cycle_summary['duration']:.2f} seconds")
                
                cycle_count += 1
                
                # Wait between cycles
                if max_cycles is None or cycle_count < max_cycles:
                    wait_time = self.config.get("cycle_interval", 300)  # 5 minutes default
                    logger.info(f"Waiting {wait_time} seconds before next cycle...")
                    time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("Training interrupted by user")
        except Exception as e:
            logger.error(f"Training error: {e}")
            raise
        
        logger.info(f"Continuous training completed after {cycle_count} cycles")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="PokéAI Self-Training Orchestrator")
    parser.add_argument("--config", default="config/self_training.json", help="Configuration file")
    parser.add_argument("--cycles", type=int, help="Number of training cycles to run")
    parser.add_argument("--continuous", action="store_true", help="Run continuous training")
    parser.add_argument("--format", default="gen9ou", help="Pokemon format")
    parser.add_argument("--games", type=int, default=100, help="Games per cycle")
    
    args = parser.parse_args()
    
    # Load configuration
    config_file = Path(args.config)
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "format": args.format,
            "selfplay_games": args.games,
            "evaluation_candidates": 8,
            "evaluation_games": 20,
            "policy_epochs": 5,
            "teambuilder_epochs": 5,
            "cycle_interval": 300
        }
    
    # Override with command line arguments
    if args.games:
        config["selfplay_games"] = args.games
    if args.format:
        config["format"] = args.format
    
    # Create orchestrator
    orchestrator = SelfTrainingOrchestrator(config)
    
    if args.continuous:
        orchestrator.run_continuous_training(args.cycles)
    else:
        # Run single cycle
        cycle_summary = orchestrator.run_full_training_cycle()
        
        print(f"\n=== Training Cycle Complete ===")
        print(f"Games played: {cycle_summary['games_played']}")
        print(f"Best team score: {cycle_summary['best_team_score']:.3f}")
        print(f"Duration: {cycle_summary['duration']:.2f} seconds")
        print(f"Training data saved to: data/training/")

if __name__ == "__main__":
    main()
