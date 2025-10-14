#!/usr/bin/env python3
"""
PokéAI Model Retraining Script

This script handles the retraining of both policy and team builder models
based on new self-play data and analysis results.
"""

import json
import logging
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import torch
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelRetrainer:
    """Handles model retraining based on new data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.training_data_dir = Path("data/training")
        self.checkpoints_dir = Path("models/checkpoints")
        self.models_dir = Path("models")
        
        # Create directories
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Training state
        self.retraining_history = []
        
    def retrain_all_models(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Retrain all models based on analysis results"""
        logger.info("Starting model retraining process")
        
        retraining_results = {
            "timestamp": datetime.now().isoformat(),
            "policy_retraining": {},
            "teambuilder_retraining": {},
            "overall_status": "pending"
        }
        
        # Retrain policy model
        try:
            logger.info("Retraining policy model")
            policy_result = self.retrain_policy_model(analysis_results)
            retraining_results["policy_retraining"] = policy_result
        except Exception as e:
            logger.error(f"Policy model retraining failed: {e}")
            retraining_results["policy_retraining"] = {"status": "failed", "error": str(e)}
        
        # Retrain team builder model
        try:
            logger.info("Retraining team builder model")
            teambuilder_result = self.retrain_teambuilder_model(analysis_results)
            retraining_results["teambuilder_retraining"] = teambuilder_result
        except Exception as e:
            logger.error(f"Team builder model retraining failed: {e}")
            retraining_results["teambuilder_retraining"] = {"status": "failed", "error": str(e)}
        
        # Determine overall status
        policy_status = retraining_results["policy_retraining"].get("status", "unknown")
        teambuilder_status = retraining_results["teambuilder_retraining"].get("status", "unknown")
        
        if policy_status == "success" and teambuilder_status == "success":
            retraining_results["overall_status"] = "success"
        elif policy_status == "success" or teambuilder_status == "success":
            retraining_results["overall_status"] = "partial"
        else:
            retraining_results["overall_status"] = "failed"
        
        # Save retraining results
        self.save_retraining_results(retraining_results)
        
        logger.info(f"Model retraining completed with status: {retraining_results['overall_status']}")
        return retraining_results
    
    def retrain_policy_model(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Retrain the policy model with new data"""
        logger.info("Retraining policy model")
        
        # Prepare training data
        training_data = self.prepare_policy_training_data(analysis_results)
        
        # Check if we have enough data
        if not training_data or len(training_data) < 10:
            logger.warning("Insufficient data for policy retraining")
            return {"status": "skipped", "reason": "insufficient_data"}
        
        # Run policy training
        training_script = self.models_dir / "training" / "train_policy.py"
        if not training_script.exists():
            logger.warning("Policy training script not found")
            return {"status": "skipped", "reason": "script_not_found"}
        
        try:
            # Prepare training arguments
            args = [
                sys.executable, str(training_script),
                "--data_path", str(self.training_data_dir),
                "--output_path", str(self.checkpoints_dir / "policy"),
                "--epochs", str(self.config.get("policy_epochs", 5)),
                "--batch_size", str(self.config.get("batch_size", 32)),
                "--learning_rate", str(self.config.get("learning_rate", 0.001))
            ]
            
            # Add GPU support if available
            if self.config.get("use_gpu", True) and torch.cuda.is_available():
                args.append("--use_gpu")
            
            # Run training
            logger.info(f"Running policy training with args: {' '.join(args)}")
            result = subprocess.run(args, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info("Policy model retraining completed successfully")
                return {
                    "status": "success",
                    "output": result.stdout,
                    "data_size": len(training_data)
                }
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
        """Retrain the team builder model with new data"""
        logger.info("Retraining team builder model")
        
        # Prepare training data
        training_data = self.prepare_teambuilder_training_data(analysis_results)
        
        # Check if we have enough data
        if not training_data or len(training_data) < 5:
            logger.warning("Insufficient data for team builder retraining")
            return {"status": "skipped", "reason": "insufficient_data"}
        
        # Run team builder training
        training_script = self.models_dir / "training" / "train_teambuilder.py"
        if not training_script.exists():
            logger.warning("Team builder training script not found")
            return {"status": "skipped", "reason": "script_not_found"}
        
        try:
            # Prepare training arguments
            args = [
                sys.executable, str(training_script),
                "--data_path", str(self.training_data_dir),
                "--output_path", str(self.checkpoints_dir / "teambuilder"),
                "--epochs", str(self.config.get("teambuilder_epochs", 5)),
                "--batch_size", str(self.config.get("batch_size", 32)),
                "--learning_rate", str(self.config.get("learning_rate", 0.001))
            ]
            
            # Add GPU support if available
            if self.config.get("use_gpu", True) and torch.cuda.is_available():
                args.append("--use_gpu")
            
            # Run training
            logger.info(f"Running team builder training with args: {' '.join(args)}")
            result = subprocess.run(args, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                logger.info("Team builder model retraining completed successfully")
                return {
                    "status": "success",
                    "output": result.stdout,
                    "data_size": len(training_data)
                }
            else:
                logger.error(f"Team builder model retraining failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            logger.error("Team builder model retraining timed out")
            return {"status": "timeout"}
        except Exception as e:
            logger.error(f"Team builder model retraining error: {e}")
            return {"status": "error", "error": str(e)}
    
    def prepare_policy_training_data(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare training data for policy model"""
        logger.info("Preparing policy training data")
        
        training_data = []
        
        # Load self-play data
        selfplay_files = list(self.training_data_dir.glob("selfplay_*.json"))
        for file_path in selfplay_files:
            try:
                with open(file_path, 'r') as f:
                    battles = json.load(f)
                
                for battle in battles:
                    # Extract battle states and actions
                    if "result" in battle and "winner" in battle["result"]:
                        # Create training examples from battle
                        examples = self.extract_policy_examples(battle)
                        training_data.extend(examples)
                        
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
                continue
        
        logger.info(f"Prepared {len(training_data)} policy training examples")
        return training_data
    
    def prepare_teambuilder_training_data(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare training data for team builder model"""
        logger.info("Preparing team builder training data")
        
        training_data = []
        
        # Load self-play data
        selfplay_files = list(self.training_data_dir.glob("selfplay_*.json"))
        for file_path in selfplay_files:
            try:
                with open(file_path, 'r') as f:
                    battles = json.load(f)
                
                for battle in battles:
                    # Extract team compositions and their performance
                    if "team1" in battle and "team2" in battle:
                        # Create training examples from teams
                        examples = self.extract_teambuilder_examples(battle)
                        training_data.extend(examples)
                        
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
                continue
        
        logger.info(f"Prepared {len(training_data)} team builder training examples")
        return training_data
    
    def extract_policy_examples(self, battle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract policy training examples from a battle"""
        examples = []
        
        # This is a simplified extraction - in a real implementation,
        # you would extract actual battle states and actions
        if "result" in battle:
            winner = battle["result"].get("winner", "tie")
            turns = battle["result"].get("turns", 0)
            
            # Create example based on battle outcome
            example = {
                "battle_state": "simplified_state",  # Would be actual battle state
                "action": "simplified_action",  # Would be actual action taken
                "reward": 1.0 if winner == "p1" else -1.0 if winner == "p2" else 0.0,
                "turns": turns
            }
            examples.append(example)
        
        return examples
    
    def extract_teambuilder_examples(self, battle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract team builder training examples from a battle"""
        examples = []
        
        # Extract team compositions and their performance
        if "team1" in battle and "team2" in battle:
            team1 = battle["team1"]
            team2 = battle["team2"]
            winner = battle.get("result", {}).get("winner", "tie")
            
            # Create examples for both teams
            for team, team_name in [(team1, "team1"), (team2, "team2")]:
                if "pokemon" in team:
                    # Calculate team quality score
                    quality_score = self.calculate_team_quality(team)
                    
                    # Determine if this team won
                    won = (team_name == "team1" and winner == "p1") or (team_name == "team2" and winner == "p2")
                    
                    example = {
                        "team_composition": team["pokemon"],
                        "quality_score": quality_score,
                        "performance": 1.0 if won else 0.0,
                        "synergy_score": self.calculate_synergy_score(team)
                    }
                    examples.append(example)
        
        return examples
    
    def calculate_team_quality(self, team: Dict[str, Any]) -> float:
        """Calculate team quality score"""
        if "pokemon" not in team:
            return 0.0
        
        # Simple quality calculation based on team size and diversity
        pokemon_count = len(team["pokemon"])
        if pokemon_count == 0:
            return 0.0
        
        # Base score for having a full team
        base_score = min(1.0, pokemon_count / 6.0)
        
        # Add diversity bonus
        species = set(pokemon.get("species", "Unknown") for pokemon in team["pokemon"])
        diversity_bonus = len(species) * 0.1
        
        return min(1.0, base_score + diversity_bonus)
    
    def calculate_synergy_score(self, team: Dict[str, Any]) -> float:
        """Calculate team synergy score"""
        if "pokemon" not in team:
            return 0.0
        
        # Simple synergy calculation
        pokemon_count = len(team["pokemon"])
        if pokemon_count == 0:
            return 0.0
        
        # Base synergy score
        base_synergy = 0.5
        
        # Bonus for full team
        if pokemon_count == 6:
            base_synergy += 0.3
        
        # Bonus for type diversity (simplified)
        species = set(pokemon.get("species", "Unknown") for pokemon in team["pokemon"])
        diversity_bonus = min(0.2, len(species) * 0.05)
        
        return min(1.0, base_synergy + diversity_bonus)
    
    def save_retraining_results(self, results: Dict[str, Any]) -> None:
        """Save retraining results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.training_data_dir / f"retraining_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Retraining results saved to {results_file}")
    
    def evaluate_model_improvements(self) -> Dict[str, Any]:
        """Evaluate improvements after retraining"""
        logger.info("Evaluating model improvements")
        
        # This would typically involve running evaluation games
        # and comparing performance before and after retraining
        
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "policy_improvement": 0.0,  # Would be calculated
            "teambuilder_improvement": 0.0,  # Would be calculated
            "overall_improvement": 0.0  # Would be calculated
        }
        
        return evaluation_results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Retrain PokéAI models")
    parser.add_argument("--config", default="config/self_training.json", help="Configuration file")
    parser.add_argument("--analysis_file", help="Analysis results file")
    parser.add_argument("--epochs", type=int, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, help="Batch size for training")
    parser.add_argument("--learning_rate", type=float, help="Learning rate for training")
    
    args = parser.parse_args()
    
    # Load configuration
    config_file = Path(args.config)
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "policy_epochs": 5,
            "teambuilder_epochs": 5,
            "batch_size": 32,
            "learning_rate": 0.001,
            "use_gpu": True
        }
    
    # Override with command line arguments
    if args.epochs:
        config["policy_epochs"] = args.epochs
        config["teambuilder_epochs"] = args.epochs
    if args.batch_size:
        config["batch_size"] = args.batch_size
    if args.learning_rate:
        config["learning_rate"] = args.learning_rate
    
    # Load analysis results if provided
    analysis_results = {}
    if args.analysis_file:
        with open(args.analysis_file, 'r') as f:
            analysis_results = json.load(f)
    
    # Create retrainer
    retrainer = ModelRetrainer(config)
    
    # Run retraining
    results = retrainer.retrain_all_models(analysis_results)
    
    # Print results
    print("\n=== Model Retraining Results ===")
    print(f"Overall status: {results['overall_status']}")
    print(f"Policy retraining: {results['policy_retraining'].get('status', 'unknown')}")
    print(f"Team builder retraining: {results['teambuilder_retraining'].get('status', 'unknown')}")
    
    if results['overall_status'] == 'success':
        print("All models retrained successfully!")
    elif results['overall_status'] == 'partial':
        print("Some models retrained successfully")
    else:
        print("Model retraining failed")

if __name__ == "__main__":
    main()
