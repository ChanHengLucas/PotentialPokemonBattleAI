"""
PokéAI Policy Model Training Script

This script implements the training pipeline for the battle policy transformer:
1. Imitation learning from high-Elo replays
2. Offline reinforcement learning with reward signals
3. Self-play reinforcement learning
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

class BattleDataset(Dataset):
    """Dataset for battle state-action pairs"""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 512):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self.load_data()
    
    def load_data(self) -> List[Dict[str, Any]]:
        """Load battle data from files"""
        data = []
        
        # Load replay data
        replay_files = Path(self.data_path).glob("**/*.json")
        for file_path in replay_files:
            try:
                with open(file_path, 'r') as f:
                    replay_data = json.load(f)
                    data.extend(self.parse_replay(replay_data))
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        
        logger.info(f"Loaded {len(data)} battle examples")
        return data
    
    def parse_replay(self, replay_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a single replay into state-action pairs"""
        examples = []
        
        # Extract turns from replay
        turns = replay_data.get('turns', [])
        for i, turn in enumerate(turns):
            if i == 0:  # Skip first turn (team preview)
                continue
            
            # Extract state and action
            state = turn.get('state', {})
            action = turn.get('action', {})
            
            if state and action:
                examples.append({
                    'state': state,
                    'action': action,
                    'reward': self.calculate_reward(state, action, replay_data),
                    'turn': i
                })
        
        return examples
    
    def calculate_reward(self, state: Dict[str, Any], action: Dict[str, Any], replay_data: Dict[str, Any]) -> float:
        """Calculate reward signal for the action"""
        reward = 0.0
        
        # Win/loss reward
        if replay_data.get('winner') == 'p1':
            reward += 1.0
        elif replay_data.get('winner') == 'p2':
            reward -= 1.0
        
        # Damage reward
        if 'damage' in action:
            reward += action['damage'] * 0.01
        
        # KO reward
        if action.get('ko'):
            reward += 10.0
        
        # Hazard control reward
        if action.get('hazard_control'):
            reward += 2.0
        
        # Speed control reward
        if action.get('speed_control'):
            reward += 1.0
        
        return reward
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        example = self.data[idx]
        
        # Tokenize state
        state_text = self.state_to_text(example['state'])
        state_tokens = self.tokenizer(
            state_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Tokenize action
        action_text = self.action_to_text(example['action'])
        action_tokens = self.tokenizer(
            action_text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': state_tokens['input_ids'].squeeze(),
            'attention_mask': state_tokens['attention_mask'].squeeze(),
            'action_ids': action_tokens['input_ids'].squeeze(),
            'action_mask': action_tokens['attention_mask'].squeeze(),
            'reward': torch.tensor(example['reward'], dtype=torch.float32),
            'turn': torch.tensor(example['turn'], dtype=torch.long)
        }
    
    def state_to_text(self, state: Dict[str, Any]) -> str:
        """Convert battle state to text representation"""
        text_parts = []
        
        # Active Pokémon
        p1_active = state.get('p1', {}).get('active', {})
        if p1_active:
            text_parts.append(f"P1 Active: {p1_active.get('species', 'Unknown')} (HP: {p1_active.get('hp', 0)}/{p1_active.get('maxhp', 0)})")
        
        p2_active = state.get('p2', {}).get('active', {})
        if p2_active:
            text_parts.append(f"P2 Active: {p2_active.get('species', 'Unknown')} (HP: {p2_active.get('hp', 0)}/{p2_active.get('maxhp', 0)})")
        
        # Field conditions
        field = state.get('field', {})
        if field.get('weather'):
            text_parts.append(f"Weather: {field['weather']['type']}")
        if field.get('terrain'):
            text_parts.append(f"Terrain: {field['terrain']['type']}")
        
        # Hazards
        hazards = state.get('p2', {}).get('side', {}).get('hazards', {})
        if hazards.get('stealthRock'):
            text_parts.append("Stealth Rock on P2 side")
        if hazards.get('spikes', 0) > 0:
            text_parts.append(f"Spikes on P2 side: {hazards['spikes']} layers")
        
        return " | ".join(text_parts)
    
    def action_to_text(self, action: Dict[str, Any]) -> str:
        """Convert action to text representation"""
        action_type = action.get('type', 'unknown')
        
        if action_type == 'move':
            return f"Use move: {action.get('move', 'Unknown')}"
        elif action_type == 'switch':
            return f"Switch to: {action.get('pokemon', 'Unknown')}"
        elif action_type == 'tera':
            return f"Terastallize to: {action.get('teraType', 'Unknown')}"
        else:
            return f"Action: {action_type}"

class PolicyModel(nn.Module):
    """Transformer-based policy model"""
    
    def __init__(self, model_name: str = "bert-base-uncased", num_actions: int = 1000):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.action_head = nn.Linear(self.bert.config.hidden_size, num_actions)
        self.value_head = nn.Linear(self.bert.config.hidden_size, 1)
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        
        # Action probabilities
        action_logits = self.action_head(self.dropout(pooled_output))
        
        # Value estimation
        value = self.value_head(self.dropout(pooled_output))
        
        return action_logits, value

class PolicyTrainer:
    """Trainer for the policy model"""
    
    def __init__(self, model_name: str = "bert-base-uncased", learning_rate: float = 1e-4):
        self.model_name = model_name
        self.learning_rate = learning_rate
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = PolicyModel(model_name)
        self.optimizer = optim.AdamW(self.model.parameters(), lr=learning_rate)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def train_imitation_learning(self, data_path: str, epochs: int = 10, batch_size: int = 32):
        """Train using imitation learning from replays"""
        logger.info("Starting imitation learning training")
        
        # Load dataset
        dataset = BattleDataset(data_path, self.tokenizer)
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
                action_ids = batch['action_ids'].to(self.device)
                
                action_logits, value = self.model(input_ids, attention_mask)
                
                # Calculate loss
                loss = self.calculate_imitation_loss(action_logits, action_ids)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataloader):.4f}")
    
    def train_reinforcement_learning(self, data_path: str, epochs: int = 5, batch_size: int = 32):
        """Train using reinforcement learning with reward signals"""
        logger.info("Starting reinforcement learning training")
        
        # Load dataset
        dataset = BattleDataset(data_path, self.tokenizer)
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
                rewards = batch['reward'].to(self.device)
                
                action_logits, value = self.model(input_ids, attention_mask)
                
                # Calculate loss
                loss = self.calculate_rl_loss(action_logits, value, rewards)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataloader):.4f}")
    
    def calculate_imitation_loss(self, action_logits, action_ids):
        """Calculate imitation learning loss"""
        loss_fn = nn.CrossEntropyLoss()
        return loss_fn(action_logits, action_ids)
    
    def calculate_rl_loss(self, action_logits, value, rewards):
        """Calculate reinforcement learning loss"""
        # Policy loss
        action_probs = torch.softmax(action_logits, dim=-1)
        policy_loss = -torch.mean(torch.log(action_probs + 1e-8) * rewards.unsqueeze(-1))
        
        # Value loss
        value_loss = nn.MSELoss()(value.squeeze(), rewards)
        
        return policy_loss + value_loss
    
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
    data_path = "data/parsed"
    output_path = "models/checkpoints/policy"
    epochs_imitation = 10
    epochs_rl = 5
    batch_size = 32
    learning_rate = 1e-4
    
    # Initialize trainer
    trainer = PolicyTrainer(learning_rate=learning_rate)
    
    # Phase 1: Imitation Learning
    logger.info("Phase 1: Imitation Learning")
    trainer.train_imitation_learning(data_path, epochs_imitation, batch_size)
    
    # Phase 2: Reinforcement Learning
    logger.info("Phase 2: Reinforcement Learning")
    trainer.train_reinforcement_learning(data_path, epochs_rl, batch_size)
    
    # Save model
    trainer.save_model(output_path)
    
    logger.info("Training completed!")

if __name__ == "__main__":
    main()
