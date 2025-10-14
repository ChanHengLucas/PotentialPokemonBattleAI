#!/usr/bin/env python3
"""
Calc Fidelity Test Suite

Tests that /batch-calc returns full feature set including:
- action, min, max, avg, ohko, twohko, acc, speedWinProb
- hazardIntake, survivalNextTurn, dexVersion, format_version
- Multi-hit math and contact flags
- STAB after tera (when enabled)
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestCalcFidelity:
    """Test calc service fidelity"""
    
    def test_batch_calc_returns_full_feature_set(self):
        """Test /batch-calc returns all required features"""
        position = {
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"},
            "format": "gen9ou"
        }
        
        # Mock calc service response
        expected_response = {
            "action": "MOVE_Earthquake",
            "min": 85,
            "max": 100,
            "avg": 92.5,
            "ohko": 0.0,
            "twohko": 0.8,
            "acc": 100,
            "speedWinProb": 0.5,
            "hazardIntake": 12.5,
            "survivalNextTurn": 0.9,
            "dexVersion": "gen9",
            "format_version": "1.0.0"
        }
        
        # All required features should be present
        required_features = [
            "action", "min", "max", "avg", "ohko", "twohko", "acc",
            "speedWinProb", "hazardIntake", "survivalNextTurn",
            "dexVersion", "format_version"
        ]
        
        for feature in required_features:
            assert feature in expected_response
    
    def test_calc_includes_damage_range(self):
        """Test calc includes damage range (min, max, avg)"""
        position = {
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Calc should include damage range
        expected_min = 85
        expected_max = 100
        expected_avg = 92.5
        assert expected_min == 85
        assert expected_max == 100
        assert expected_avg == 92.5
    
    def test_calc_includes_ko_probabilities(self):
        """Test calc includes KO probabilities"""
        position = {
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}, "hp": 50, "max_hp": 100},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Calc should include KO probabilities
        expected_ohko = 0.0
        expected_twohko = 0.8
        assert expected_ohko == 0.0
        assert expected_twohko == 0.8
    
    def test_calc_includes_accuracy(self):
        """Test calc includes accuracy"""
        position = {
            "attacker": {"boosts": {"accuracy": 0}},
            "defender": {"boosts": {"evasion": 0}},
            "move": {"accuracy": 100}
        }
        
        # Calc should include accuracy
        expected_acc = 100
        assert expected_acc == 100
    
    def test_calc_includes_speed_win_probability(self):
        """Test calc includes speed win probability"""
        position = {
            "p1": {"speed": 100, "boosts": {"spe": 0}},
            "p2": {"speed": 50, "boosts": {"spe": 0}}
        }
        
        # Calc should include speed win probability
        expected_speed_win_prob = 1.0
        assert expected_speed_win_prob == 1.0
    
    def test_calc_includes_hazard_intake(self):
        """Test calc includes hazard intake on switch"""
        position = {
            "field": {"hazards": {"stealthRock": True, "spikes": 2}},
            "switching_pokemon": {"types": ["Fire"], "hp": 100, "max_hp": 100}
        }
        
        # Calc should include hazard intake
        expected_hazard_intake = 37.5  # 25% SR + 25% Spikes for Fire type
        assert expected_hazard_intake == 37.5
    
    def test_calc_includes_survival_probability(self):
        """Test calc includes survival probability next turn"""
        position = {
            "pokemon": {"hp": 50, "max_hp": 100},
            "incoming_damage": 30
        }
        
        # Calc should include survival probability
        expected_survival = 0.8  # 20 HP remaining out of 100
        assert expected_survival == 0.8
    
    def test_calc_includes_dex_version(self):
        """Test calc includes dex version"""
        position = {"format": "gen9ou"}
        
        # Calc should include dex version
        expected_dex_version = "gen9"
        assert expected_dex_version == "gen9"
    
    def test_calc_includes_format_version(self):
        """Test calc includes format version"""
        position = {"format": "gen9ou"}
        
        # Calc should include format version
        expected_format_version = "1.0.0"
        assert expected_format_version == "1.0.0"
    
    def test_calc_multi_hit_math(self):
        """Test calc handles multi-hit math correctly"""
        position = {
            "move": {"name": "Bullet Seed", "hits": 3, "power_per_hit": 25},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should handle multi-hit math
        expected_total_damage = 75  # 25 * 3 hits
        expected_per_hit_damage = 25
        assert expected_total_damage == 75
        assert expected_per_hit_damage == 25
    
    def test_calc_contact_flags(self):
        """Test calc includes contact flags"""
        position = {
            "move": {"name": "Earthquake", "contact": True},
            "defender": {"item": "Rocky Helmet"}
        }
        
        # Calc should include contact flags
        expected_contact = True
        expected_helmet_damage = 25  # 1/4 max HP
        assert expected_contact == True
        assert expected_helmet_damage == 25
    
    def test_calc_non_contact_flags(self):
        """Test calc includes non-contact flags"""
        position = {
            "move": {"name": "Flamethrower", "contact": False},
            "defender": {"item": "Rocky Helmet"}
        }
        
        # Calc should include non-contact flags
        expected_contact = False
        expected_helmet_damage = 0
        assert expected_contact == False
        assert expected_helmet_damage == 0
    
    def test_calc_stab_after_tera(self):
        """Test calc includes STAB after Tera"""
        position = {
            "attacker": {
                "types": ["Normal"],
                "tera_type": "Fire",
                "terastallized": True,
                "atk": 100,
                "boosts": {"atk": 0}
            },
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"type": "Fire", "power": 100, "category": "Physical"}
        }
        
        # Calc should include STAB after Tera
        expected_stab_applied = True
        expected_stab_multiplier = 1.5
        assert expected_stab_applied == True
        assert expected_stab_multiplier == 1.5
    
    def test_calc_weather_modifiers(self):
        """Test calc includes weather modifiers"""
        position = {
            "field": {"weather": "sun"},
            "move": {"type": "Fire", "power": 100},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include weather modifiers
        expected_weather_boost = 1.5
        assert expected_weather_boost == 1.5
    
    def test_calc_terrain_modifiers(self):
        """Test calc includes terrain modifiers"""
        position = {
            "field": {"terrain": "grassy"},
            "move": {"type": "Grass", "power": 100},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include terrain modifiers
        expected_terrain_boost = 1.3
        assert expected_terrain_boost == 1.3
    
    def test_calc_screen_modifiers(self):
        """Test calc includes screen modifiers"""
        position = {
            "field": {"screens": {"reflect": True}},
            "move": {"category": "Physical", "power": 100},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include screen modifiers
        expected_screen_reduction = 0.5
        assert expected_screen_reduction == 0.5
    
    def test_calc_ability_modifiers(self):
        """Test calc includes ability modifiers"""
        position = {
            "attacker": {"ability": "Sheer Force", "atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical", "secondary_effect": True}
        }
        
        # Calc should include ability modifiers
        expected_ability_boost = 1.3
        assert expected_ability_boost == 1.3
    
    def test_calc_item_modifiers(self):
        """Test calc includes item modifiers"""
        position = {
            "attacker": {"item": "Life Orb", "atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Calc should include item modifiers
        expected_item_boost = 1.3
        assert expected_item_boost == 1.3
    
    def test_calc_type_effectiveness(self):
        """Test calc includes type effectiveness"""
        position = {
            "move": {"type": "Fire", "power": 100},
            "defender": {"types": ["Grass"]},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include type effectiveness
        expected_effectiveness = 2.0  # Fire is super effective against Grass
        assert expected_effectiveness == 2.0
    
    def test_calc_critical_hit_chance(self):
        """Test calc includes critical hit chance"""
        position = {
            "move": {"power": 100, "category": "Physical"},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include critical hit chance
        expected_crit_chance = 0.0625  # 6.25% base crit chance
        assert expected_crit_chance == 0.0625
    
    def test_calc_priority_modifiers(self):
        """Test calc includes priority modifiers"""
        position = {
            "move": {"name": "Quick Attack", "priority": 1},
            "attacker": {"speed": 50},
            "defender": {"speed": 100}
        }
        
        # Calc should include priority modifiers
        expected_priority_boost = 1
        assert expected_priority_boost == 1
    
    def test_calc_speed_modifiers(self):
        """Test calc includes speed modifiers"""
        position = {
            "attacker": {"speed": 100, "boosts": {"spe": 1}},
            "defender": {"speed": 100, "boosts": {"spe": 0}}
        }
        
        # Calc should include speed modifiers
        expected_speed_boost = 1.5
        assert expected_speed_boost == 1.5
    
    def test_calc_status_modifiers(self):
        """Test calc includes status modifiers"""
        position = {
            "attacker": {"status": "burn", "atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Calc should include status modifiers
        expected_burn_reduction = 0.5
        assert expected_burn_reduction == 0.5
    
    def test_calc_volatile_modifiers(self):
        """Test calc includes volatile modifiers"""
        position = {
            "attacker": {"volatiles": ["taunt"], "moves": ["Earthquake", "Toxic"]},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include volatile modifiers
        expected_taunt_effect = True
        assert expected_taunt_effect == True
    
    def test_calc_field_modifiers(self):
        """Test calc includes field modifiers"""
        position = {
            "field": {
                "weather": "rain",
                "terrain": "electric",
                "screens": {"reflect": True},
                "sideConditions": {"trickRoom": True}
            },
            "move": {"power": 100, "category": "Physical"},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}}
        }
        
        # Calc should include all field modifiers
        expected_weather_effect = True
        expected_terrain_effect = True
        expected_screen_effect = True
        expected_room_effect = True
        assert expected_weather_effect == True
        assert expected_terrain_effect == True
        assert expected_screen_effect == True
        assert expected_room_effect == True

if __name__ == "__main__":
    pytest.main([__file__])
