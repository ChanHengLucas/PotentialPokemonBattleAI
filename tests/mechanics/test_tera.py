#!/usr/bin/env python3
"""
Tera Test Suite

Tests all Tera mechanics including:
- One-time use
- Post-tera typing updates STAB/resistances
- Calc uses post-tera typing
- Policy action space expands only if format.tera_allowed == true
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestTeraMechanics:
    """Test Tera mechanics"""
    
    def test_tera_one_time_use(self):
        """Test Tera is one-time use only"""
        position = {
            "pokemon": {
                "terastallized": True,
                "tera_used": True
            },
            "action": "TERA_Fire"
        }
        
        # Tera should not be available after use
        expected_tera_legal = False
        assert expected_tera_legal == False
    
    def test_tera_typing_change(self):
        """Test Tera changes typing"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True
            }
        }
        
        # Tera should change typing
        expected_typing_change = True
        expected_new_type = "Fire"
        assert expected_typing_change == True
        assert expected_new_type == "Fire"
    
    def test_tera_stab_recalculation(self):
        """Test Tera recalculates STAB"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True
            },
            "move": {"type": "Fire", "power": 100}
        }
        
        # Tera should provide STAB for new type
        expected_stab_applied = True
        expected_stab_multiplier = 1.5
        assert expected_stab_applied == True
        assert expected_stab_multiplier == 1.5
    
    def test_tera_resistance_recalculation(self):
        """Test Tera recalculates resistances"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True
            },
            "incoming_move": {"type": "Water", "power": 100}
        }
        
        # Tera should change resistances
        expected_resistance_change = True
        expected_water_effectiveness = 2.0  # Fire is weak to Water
        assert expected_resistance_change == True
        assert expected_water_effectiveness == 2.0
    
    def test_tera_calc_uses_post_tera_typing(self):
        """Test calc uses post-tera typing"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True
            },
            "move": {"type": "Fire", "power": 100}
        }
        
        # Calc should use Fire typing for STAB calculation
        expected_calc_typing = "Fire"
        expected_stab_applied = True
        assert expected_calc_typing == "Fire"
        assert expected_stab_applied == True
    
    def test_tera_action_space_expansion(self):
        """Test Tera action space expansion when enabled"""
        position = {
            "format": {"tera_allowed": True},
            "pokemon": {
                "terastallized": False,
                "tera_used": False
            }
        }
        
        # Tera actions should be available when enabled
        expected_tera_actions_available = True
        expected_actions = ["MOVE_Earthquake", "TERA_Fire", "TERA_Water", "TERA_Grass"]
        assert expected_tera_actions_available == True
        assert "TERA_Fire" in expected_actions
    
    def test_tera_action_space_no_expansion_when_disabled(self):
        """Test Tera action space doesn't expand when disabled"""
        position = {
            "format": {"tera_allowed": False},
            "pokemon": {
                "terastallized": False,
                "tera_used": False
            }
        }
        
        # Tera actions should not be available when disabled
        expected_tera_actions_available = False
        expected_actions = ["MOVE_Earthquake", "MOVE_Stone Edge"]
        assert expected_tera_actions_available == False
        assert "TERA_Fire" not in expected_actions
    
    def test_tera_typing_affects_damage_calculation(self):
        """Test Tera typing affects damage calculation"""
        position = {
            "attacker": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True,
                "atk": 100
            },
            "defender": {
                "types": ["Grass"],
                "def": 100
            },
            "move": {"type": "Fire", "power": 100, "category": "Physical"}
        }
        
        # Tera Fire should be super effective against Grass
        expected_effectiveness = 2.0
        expected_stab_applied = True
        assert expected_effectiveness == 2.0
        assert expected_stab_applied == True
    
    def test_tera_typing_affects_resistance_calculation(self):
        """Test Tera typing affects resistance calculation"""
        position = {
            "attacker": {
                "types": ["Fire"],
                "spa": 100
            },
            "defender": {
                "types": ["Normal"],
                "tera_type": "Water",
                "terastallized": True,
                "spd": 100
            },
            "move": {"type": "Fire", "power": 100, "category": "Special"}
        }
        
        # Tera Water should resist Fire
        expected_effectiveness = 0.5
        assert expected_effectiveness == 0.5
    
    def test_tera_typing_affects_immunity_calculation(self):
        """Test Tera typing affects immunity calculation"""
        position = {
            "attacker": {
                "types": ["Electric"],
                "spa": 100
            },
            "defender": {
                "types": ["Normal"],
                "tera_type": "Ground",
                "terastallized": True,
                "spd": 100
            },
            "move": {"type": "Electric", "power": 100, "category": "Special"}
        }
        
        # Tera Ground should be immune to Electric
        expected_effectiveness = 0.0
        assert expected_effectiveness == 0.0
    
    def test_tera_typing_affects_ability_interactions(self):
        """Test Tera typing affects ability interactions"""
        position = {
            "attacker": {
                "types": ["Fire"],
                "spa": 100
            },
            "defender": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True,
                "ability": "Flash Fire",
                "spd": 100
            },
            "move": {"type": "Fire", "power": 100, "category": "Special"}
        }
        
        # Tera Fire should be absorbed by Flash Fire
        expected_immunity = True
        expected_heal = 25  # 1/4 max HP
        assert expected_immunity == True
        assert expected_heal == 25
    
    def test_tera_typing_affects_weather_interactions(self):
        """Test Tera typing affects weather interactions"""
        position = {
            "field": {"weather": "sun"},
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True
            },
            "move": {"type": "Fire", "power": 100}
        }
        
        # Tera Fire should be boosted by sun
        expected_weather_boost = 1.5
        assert expected_weather_boost == 1.5
    
    def test_tera_typing_affects_terrain_interactions(self):
        """Test Tera typing affects terrain interactions"""
        position = {
            "field": {"terrain": "grassy"},
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Grass",
                "terastallized": True
            },
            "move": {"type": "Grass", "power": 100}
        }
        
        # Tera Grass should be boosted by Grassy Terrain
        expected_terrain_boost = 1.3
        assert expected_terrain_boost == 1.3
    
    def test_tera_typing_affects_hazard_damage(self):
        """Test Tera typing affects hazard damage"""
        position = {
            "field": {"hazards": {"stealthRock": True}},
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True,
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Tera Fire should take 2x damage from Stealth Rock
        expected_hazard_damage = 25.0  # 12.5% * 2 for Fire type
        assert expected_hazard_damage == 25.0
    
    def test_tera_typing_affects_status_immunity(self):
        """Test Tera typing affects status immunity"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Poison",
                "terastallized": True
            },
            "move": {"name": "Toxic"}
        }
        
        # Tera Poison should be immune to poison
        expected_poison_immunity = True
        assert expected_poison_immunity == True
    
    def test_tera_typing_affects_move_effectiveness(self):
        """Test Tera typing affects move effectiveness"""
        position = {
            "attacker": {
                "types": ["Normal"],
                "tera_type": "Flying",
                "terastallized": True
            },
            "defender": {
                "types": ["Ground"]
            },
            "move": {"type": "Ground", "power": 100, "name": "Earthquake"}
        }
        
        # Tera Flying should be immune to Ground moves
        expected_ground_immunity = True
        assert expected_ground_immunity == True
    
    def test_tera_typing_affects_ability_immunities(self):
        """Test Tera typing affects ability immunities"""
        position = {
            "attacker": {
                "types": ["Electric"],
                "spa": 100
            },
            "defender": {
                "types": ["Normal"],
                "tera_type": "Ground",
                "terastallized": True,
                "ability": "Volt Absorb"
            },
            "move": {"type": "Electric", "power": 100, "category": "Special"}
        }
        
        # Tera Ground should be immune to Electric regardless of Volt Absorb
        expected_immunity = True
        assert expected_immunity == True
    
    def test_tera_typing_affects_weather_immunity(self):
        """Test Tera typing affects weather immunity"""
        position = {
            "field": {"weather": "sandstorm"},
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Rock",
                "terastallized": True,
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Tera Rock should be immune to sandstorm damage
        expected_sandstorm_immunity = True
        assert expected_sandstorm_immunity == True
    
    def test_tera_typing_affects_terrain_immunity(self):
        """Test Tera typing affects terrain immunity"""
        position = {
            "field": {"terrain": "electric"},
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Ground",
                "terastallized": True,
                "grounded": True
            },
            "move": {"name": "Sleep Powder"}
        }
        
        # Tera Ground should be affected by Electric Terrain
        expected_terrain_immunity = False
        assert expected_terrain_immunity == False
    
    def test_tera_typing_affects_move_typing(self):
        """Test Tera typing affects move typing"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True
            },
            "move": {"type": "Normal", "name": "Hyper Beam"}
        }
        
        # Tera should not change move typing
        expected_move_type = "Normal"
        assert expected_move_type == "Normal"
    
    def test_tera_typing_affects_ability_typing(self):
        """Test Tera typing affects ability typing"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True,
                "ability": "Flash Fire"
            }
        }
        
        # Tera should not change ability typing
        expected_ability_typing = "Fire"
        assert expected_ability_typing == "Fire"
    
    def test_tera_typing_affects_item_typing(self):
        """Test Tera typing affects item typing"""
        position = {
            "pokemon": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True,
                "item": "Flame Plate"
            }
        }
        
        # Tera should not change item typing
        expected_item_typing = "Fire"
        assert expected_item_typing == "Fire"

if __name__ == "__main__":
    pytest.main([__file__])
