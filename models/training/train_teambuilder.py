"""
PokéAI Team Builder Model Training Script

This script implements the training pipeline for the team builder transformer:
1. Train on curated Smogon teams
2. Train on high-Elo ladder teams
3. Optional self-play data integration
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import pandas as pd
import json
import logging
from typing import Dict, List, Tuple, Any
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeamDataset(Dataset):
    """Dataset for team building training data"""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 512):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self.load_data()
    
    def load_data(self) -> List[Dict[str, Any]]:
        """Load team data from files"""
        data = []
        
        # Load team data
        team_files = Path(self.data_path).glob("**/*.json")
        for file_path in team_files:
            try:
                with open(file_path, 'r') as f:
                    team_data = json.load(f)
                    data.extend(self.parse_team(team_data))
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        
        logger.info(f"Loaded {len(data)} team examples")
        return data
    
    def parse_team(self, team_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a single team into training examples"""
        examples = []
        
        # Extract team information
        team = team_data.get('team', {})
        format_name = team_data.get('format', 'gen9ou')
        usage_stats = team_data.get('usageStats', {})
        win_rate = team_data.get('winRate', 0.5)
        
        # Create team representation
        team_text = self.team_to_text(team)
        
        # Calculate team metrics
        synergy = self.calculate_synergy(team)
        coverage = self.calculate_coverage(team)
        balance = self.calculate_balance(team)
        
        examples.append({
            'team': team,
            'format': format_name,
            'usage_stats': usage_stats,
            'win_rate': win_rate,
            'synergy': synergy,
            'coverage': coverage,
            'balance': balance,
            'team_text': team_text
        })
        
        return examples
    
    def team_to_text(self, team: Dict[str, Any]) -> str:
        """Convert team to text representation"""
        pokemon_list = team.get('pokemon', [])
        text_parts = []
        
        for pokemon in pokemon_list:
            species = pokemon.get('species', 'Unknown')
            item = pokemon.get('item', '')
            ability = pokemon.get('ability', '')
            moves = pokemon.get('moves', [])
            
            pokemon_text = f"{species}"
            if item:
                pokemon_text += f" @ {item}"
            if ability:
                pokemon_text += f" ({ability})"
            if moves:
                pokemon_text += f" - {', '.join(moves)}"
            
            text_parts.append(pokemon_text)
        
        return " | ".join(text_parts)
    
    def calculate_synergy(self, team: Dict[str, Any]) -> float:
        """Calculate team synergy score"""
        pokemon_list = team.get('pokemon', [])
        if len(pokemon_list) < 6:
            return 0.0
        
        synergy_score = 0.0
        
        # Type synergy checks
        types = [p.get('type', '') for p in pokemon_list]
        
        # Fire/Water/Grass core
        if 'Fire' in types and 'Water' in types and 'Grass' in types:
            synergy_score += 0.3
        
        # Steel/Fairy/Dragon core
        if 'Steel' in types and 'Fairy' in types and 'Dragon' in types:
            synergy_score += 0.3
        
        # Role synergy
        roles = [p.get('role', '') for p in pokemon_list]
        unique_roles = len(set(roles))
        synergy_score += unique_roles * 0.1
        
        return min(1.0, synergy_score)
    
    def calculate_coverage(self, team: Dict[str, Any]) -> float:
        """Calculate type coverage score"""
        pokemon_list = team.get('pokemon', [])
        if len(pokemon_list) < 6:
            return 0.0
        
        # This would be more sophisticated in a real implementation
        # For now, return a simple score based on type diversity
        types = [p.get('type', '') for p in pokemon_list]
        unique_types = len(set(types))
        
        return min(1.0, unique_types / 6.0)
    
    def calculate_balance(self, team: Dict[str, Any]) -> float:
        """Calculate team balance score"""
        pokemon_list = team.get('pokemon', [])
        if len(pokemon_list) < 6:
            return 0.0
        
        # Check for balanced roles
        roles = [p.get('role', '') for p in pokemon_list]
        role_counts = {}
        for role in roles:
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Ideal distribution (simplified)
        ideal_distribution = {'sweeper': 2, 'wall': 2, 'support': 2}
        balance_score = 0.0
        
        for role, count in ideal_distribution.items():
            actual_count = role_counts.get(role, 0)
            balance_score += min(1.0, actual_count / count)
        
        return balance_score / len(ideal_distribution)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        example = self.data[idx]
        
        # Tokenize team text
        team_tokens = self.tokenizer(
            example['team_text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Create target vector for team quality
        quality_score = (
            example['win_rate'] * 0.4 +
            example['synergy'] * 0.3 +
            example['coverage'] * 0.2 +
            example['balance'] * 0.1
        )
        
        return {
            'input_ids': team_tokens['input_ids'].squeeze(),
            'attention_mask': team_tokens['attention_mask'].squeeze(),
            'quality_score': torch.tensor(quality_score, dtype=torch.float32),
            'win_rate': torch.tensor(example['win_rate'], dtype=torch.float32),
            'synergy': torch.tensor(example['synergy'], dtype=torch.float32),
            'coverage': torch.tensor(example['coverage'], dtype=torch.float32),
            'balance': torch.tensor(example['balance'], dtype=torch.float32)
        }

class TeamBuilderModel(nn.Module):
    """Transformer-based team builder model"""
    
    def __init__(self, model_name: str = "bert-base-uncased", num_pokemon: int = 1000):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.pokemon_head = nn.Linear(self.bert.config.hidden_size, num_pokemon)
        self.quality_head = nn.Linear(self.bert.config.hidden_size, 1)
        self.synergy_head = nn.Linear(self.bert.config.hidden_size, 1)
        self.coverage_head = nn.Linear(self.bert.config.hidden_size, 1)
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        
        # Pokémon selection probabilities
        pokemon_logits = self.pokemon_head(self.dropout(pooled_output))
        
        # Quality metrics
        quality = self.quality_head(self.dropout(pooled_output))
        synergy = self.synergy_head(self.dropout(pooled_output))
        coverage = self.coverage_head(self.dropout(pooled_output))
        
        return pokemon_logits, quality, synergy, coverage

class TeamBuilderTrainer:
    """Trainer for the team builder model"""
    
    def __init__(self, model_name: str = "bert-base-uncased", learning_rate: float = 1e-4):
        self.model_name = model_name
        self.learning_rate = learning_rate
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = TeamBuilderModel(model_name)
        self.optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def train(self, data_path: str, epochs: int = 10, batch_size: int = 32):
        """Train the team builder model"""
        logger.info("Starting team builder training")
        
        # Load dataset
        dataset = TeamDataset(data_path, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Training loop
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                self.optimizer.zero_grad()
                
                # Forward pass
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                quality_scores = batch['quality_score'].to(self.device)
                synergy_scores = batch['synergy'].to(self.device)
                coverage_scores = batch['coverage'].to(self.device)
                
                pokemon_logits, quality, synergy, coverage = self.model(input_ids, attention_mask)
                
                # Calculate loss
                loss = self.calculate_loss(
                    pokemon_logits, quality, synergy, coverage,
                    quality_scores, synergy_scores, coverage_scores
                )
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataloader):.4f}")
    
    def calculate_loss(self, pokemon_logits, quality, synergy, coverage, 
                      quality_scores, synergy_scores, coverage_scores):
        """Calculate training loss"""
        # Quality prediction loss
        quality_loss = nn.MSELoss()(quality.squeeze(), quality_scores)
        
        # Synergy prediction loss
        synergy_loss = nn.MSELoss()(synergy.squeeze(), synergy_scores)
        
        # Coverage prediction loss
        coverage_loss = nn.MSELoss()(coverage.squeeze(), coverage_scores)
        
        # Combined loss
        total_loss = quality_loss + synergy_loss + coverage_loss
        
        return total_loss
    
    def save_model(self, output_path: str):
        """Save the trained model"""
        os.makedirs(output_path, exist_ok=True)
        
        # Save model
        torch.save(self.model.state_dict(), os.path.join(output_path, "model.pt"))
        
        # Save tokenizer
        self.tokenizer.save_pretrained(output_path)
        
        # Save config
        config = {
            "model_name": self.model_name,
            "learning_rate": self.learning_rate
        }
        with open(os.path.join(output_path, "config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Model saved to {output_path}")

def main():
    """Main training function"""
    # Configuration
    data_path = "data/parsed/teams"
    output_path = "models/checkpoints/teambuilder"
    epochs = 10
    batch_size = 32
    learning_rate = 1e-4
    
    # Initialize trainer
    trainer = TeamBuilderTrainer(learning_rate=learning_rate)
    
    # Train model
    trainer.train(data_path, epochs, batch_size)
    
    # Save model
    trainer.save_model(output_path)
    
    logger.info("Training completed!")

if __name__ == "__main__":
    main()
