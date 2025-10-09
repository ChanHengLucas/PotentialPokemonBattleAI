"""
PokéAI Team Builder Data Ingestion

Loads Smogon usage stats and curated sets from data snapshots.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class DataIngester:
    """Handles loading and processing of Pokémon data"""
    
    def __init__(self, data_path: str = "data/snapshots"):
        self.data_path = Path(data_path)
        self.usage_stats = {}
        self.curated_sets = {}
        self.dex_data = {}
    
    def load_usage_stats(self, format_name: str) -> Dict[str, Any]:
        """Load usage statistics for a format"""
        try:
            usage_file = self.data_path / f"{format_name}_usage.json"
            if usage_file.exists():
                with open(usage_file, 'r') as f:
                    self.usage_stats[format_name] = json.load(f)
                    logger.info(f"Loaded usage stats for {format_name}")
                    return self.usage_stats[format_name]
            else:
                logger.warning(f"Usage stats file not found: {usage_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading usage stats for {format_name}: {e}")
            return {}
    
    def load_curated_sets(self, format_name: str) -> Dict[str, Any]:
        """Load curated Pokémon sets for a format"""
        try:
            sets_file = self.data_path / f"{format_name}_sets.json"
            if sets_file.exists():
                with open(sets_file, 'r') as f:
                    self.curated_sets[format_name] = json.load(f)
                    logger.info(f"Loaded curated sets for {format_name}")
                    return self.curated_sets[format_name]
            else:
                logger.warning(f"Curated sets file not found: {sets_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading curated sets for {format_name}: {e}")
            return {}
    
    def load_dex_data(self) -> Dict[str, Any]:
        """Load Pokémon dex data"""
        try:
            dex_file = self.data_path / "dex.json"
            if dex_file.exists():
                with open(dex_file, 'r') as f:
                    self.dex_data = json.load(f)
                    logger.info("Loaded dex data")
                    return self.dex_data
            else:
                logger.warning("Dex file not found, using fallback data")
                return self._get_fallback_dex_data()
        except Exception as e:
            logger.error(f"Error loading dex data: {e}")
            return self._get_fallback_dex_data()
    
    def _get_fallback_dex_data(self) -> Dict[str, Any]:
        """Fallback dex data for common Gen 9 OU Pokémon"""
        return {
            "Dragapult": {
                "types": ["Dragon", "Ghost"],
                "baseStats": {"hp": 88, "atk": 120, "def": 75, "spa": 100, "spd": 75, "spe": 142},
                "abilities": ["Clear Body", "Infiltrator", "Cursed Body"],
                "moves": ["Shadow Ball", "Dragon Pulse", "U-turn", "Thunderbolt", "Fire Blast", "Draco Meteor"],
                "tier": "OU"
            },
            "Garchomp": {
                "types": ["Dragon", "Ground"],
                "baseStats": {"hp": 108, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
                "abilities": ["Sand Veil", "Rough Skin"],
                "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance", "Outrage", "Fire Fang"],
                "tier": "OU"
            },
            "Landorus-Therian": {
                "types": ["Ground", "Flying"],
                "baseStats": {"hp": 89, "atk": 145, "def": 90, "spa": 105, "spd": 80, "spe": 91},
                "abilities": ["Intimidate"],
                "moves": ["Earthquake", "U-turn", "Stone Edge", "Stealth Rock", "Defog", "Knock Off"],
                "tier": "OU"
            },
            "Heatran": {
                "types": ["Fire", "Steel"],
                "baseStats": {"hp": 91, "atk": 90, "def": 106, "spa": 130, "spd": 106, "spe": 77},
                "abilities": ["Flash Fire", "Flame Body"],
                "moves": ["Magma Storm", "Earth Power", "Flash Cannon", "Stealth Rock", "Toxic", "Protect"],
                "tier": "OU"
            },
            "Rotom-Wash": {
                "types": ["Electric", "Water"],
                "baseStats": {"hp": 50, "atk": 65, "def": 107, "spa": 105, "spd": 107, "spe": 86},
                "abilities": ["Levitate"],
                "moves": ["Volt Switch", "Hydro Pump", "Thunderbolt", "Will-O-Wisp", "Pain Split", "Defog"],
                "tier": "OU"
            },
            "Toxapex": {
                "types": ["Poison", "Water"],
                "baseStats": {"hp": 50, "atk": 63, "def": 152, "spa": 53, "spd": 142, "spe": 35},
                "abilities": ["Merciless", "Limber", "Regenerator"],
                "moves": ["Scald", "Toxic", "Recover", "Haze", "Baneful Bunker", "Toxic Spikes"],
                "tier": "OU"
            }
        }
    
    def get_usage_stats(self, format_name: str) -> Dict[str, Any]:
        """Get usage statistics for a format"""
        if format_name not in self.usage_stats:
            self.load_usage_stats(format_name)
        return self.usage_stats.get(format_name, {})
    
    def get_curated_sets(self, format_name: str) -> Dict[str, Any]:
        """Get curated sets for a format"""
        if format_name not in self.curated_sets:
            self.load_curated_sets(format_name)
        return self.curated_sets.get(format_name, {})
    
    def get_dex_data(self) -> Dict[str, Any]:
        """Get dex data"""
        if not self.dex_data:
            self.load_dex_data()
        return self.dex_data
    
    def get_legal_pokemon(self, format_name: str) -> List[str]:
        """Get list of legal Pokémon for a format"""
        usage_stats = self.get_usage_stats(format_name)
        if usage_stats:
            return list(usage_stats.keys())
        
        # Fallback to dex data
        dex_data = self.get_dex_data()
        return [name for name, data in dex_data.items() if data.get("tier") == "OU"]
    
    def get_pokemon_sets(self, format_name: str, species: str) -> List[Dict[str, Any]]:
        """Get available sets for a Pokémon"""
        curated_sets = self.get_curated_sets(format_name)
        if species in curated_sets:
            return curated_sets[species]
        
        # Generate basic sets from dex data
        dex_data = self.get_dex_data()
        if species in dex_data:
            pokemon_data = dex_data[species]
            return [{
                "name": "Standard",
                "item": "Leftovers",
                "ability": pokemon_data["abilities"][0],
                "nature": "Timid",
                "evs": {"hp": 252, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252},
                "moves": pokemon_data["moves"][:4]
            }]
        
        return []

# Global instance
ingester = DataIngester()

def get_usage(format_name: str) -> Dict[str, Any]:
    """Get usage statistics for a format"""
    return ingester.get_usage_stats(format_name)

def get_sets(format_name: str) -> Dict[str, Any]:
    """Get curated sets for a format"""
    return ingester.get_curated_sets(format_name)

def get_legal_pokemon(format_name: str) -> List[str]:
    """Get legal Pokémon for a format"""
    return ingester.get_legal_pokemon(format_name)
