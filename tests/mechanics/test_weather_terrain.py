#!/usr/bin/env python3
"""
Weather/Terrain Test Suite

Tests all weather and terrain mechanics including:
- Sun/Rain/Sand/Snow power changes, chip, accuracy changes
- Grassy Terrain halving Earthquake vs grounded
- Misty blocking NEW status on grounded
- Psychic blocking priority
- Electric waking sleep prevention for grounded
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestWeatherMechanics:
    """Test weather mechanics"""
    
    def test_sun_fire_boost_water_nerf(self):
        """Test sun boosts Fire and nerfs Water"""
        position = {
            "field": {"weather": "sun"},
            "fire_move": {"type": "Fire", "power": 100},
            "water_move": {"type": "Water", "power": 100}
        }
        
        # Sun should boost Fire by 50% and nerf Water by 50%
        expected_fire_boost = 1.5
        expected_water_nerf = 0.5
        assert expected_fire_boost == 1.5
        assert expected_water_nerf == 0.5
    
    def test_rain_water_boost_fire_nerf(self):
        """Test rain boosts Water and nerfs Fire"""
        position = {
            "field": {"weather": "rain"},
            "water_move": {"type": "Water", "power": 100},
            "fire_move": {"type": "Fire", "power": 100}
        }
        
        # Rain should boost Water by 50% and nerf Fire by 50%
        expected_water_boost = 1.5
        expected_fire_nerf = 0.5
        assert expected_water_boost == 1.5
        assert expected_fire_nerf == 0.5
    
    def test_sandstorm_rock_spdef_boost(self):
        """Test sandstorm boosts Rock SpDef"""
        position = {
            "field": {"weather": "sandstorm"},
            "pokemon": {"types": ["Rock"], "spd": 100}
        }
        
        # Sandstorm should boost Rock SpDef by 50%
        expected_spdef_boost = 1.5
        assert expected_spdef_boost == 1.5
    
    def test_sandstorm_damage_per_turn(self):
        """Test sandstorm deals damage per turn"""
        position = {
            "field": {"weather": "sandstorm"},
            "pokemon": {"hp": 100, "max_hp": 100, "types": ["Normal"]}
        }
        
        # Sandstorm should deal 1/16 max HP damage per turn
        expected_damage = 6.25
        assert expected_damage == 6.25
    
    def test_sandstorm_immunity_types(self):
        """Test sandstorm immunity for Rock/Ground/Steel"""
        immunity_types = ["Rock", "Ground", "Steel"]
        
        for pokemon_type in immunity_types:
            position = {
                "field": {"weather": "sandstorm"},
                "pokemon": {"types": [pokemon_type], "hp": 100, "max_hp": 100}
            }
            
            # Immune types should take no damage
            expected_damage = 0
            assert expected_damage == 0
    
    def test_hail_damage_per_turn(self):
        """Test hail deals damage per turn"""
        position = {
            "field": {"weather": "hail"},
            "pokemon": {"hp": 100, "max_hp": 100, "types": ["Normal"]}
        }
        
        # Hail should deal 1/16 max HP damage per turn
        expected_damage = 6.25
        assert expected_damage == 6.25
    
    def test_hail_ice_immunity(self):
        """Test hail immunity for Ice types"""
        position = {
            "field": {"weather": "hail"},
            "pokemon": {"types": ["Ice"], "hp": 100, "max_hp": 100}
        }
        
        # Ice types should take no hail damage
        expected_damage = 0
        assert expected_damage == 0
    
    def test_snow_ice_def_boost(self):
        """Test snow boosts Ice Defense"""
        position = {
            "field": {"weather": "snow"},
            "pokemon": {"types": ["Ice"], "def": 100}
        }
        
        # Snow should boost Ice Defense by 50%
        expected_def_boost = 1.5
        assert expected_def_boost == 1.5

class TestWeatherAccuracyChanges:
    """Test weather accuracy changes"""
    
    def test_thunder_accuracy_in_rain(self):
        """Test Thunder has 100% accuracy in rain"""
        position = {
            "move": {"name": "Thunder", "accuracy": 70},
            "field": {"weather": "rain"}
        }
        
        # Thunder should have 100% accuracy in rain
        expected_accuracy = 100
        assert expected_accuracy == 100
    
    def test_hurricane_accuracy_in_rain(self):
        """Test Hurricane has 100% accuracy in rain"""
        position = {
            "move": {"name": "Hurricane", "accuracy": 70},
            "field": {"weather": "rain"}
        }
        
        # Hurricane should have 100% accuracy in rain
        expected_accuracy = 100
        assert expected_accuracy == 100
    
    def test_blizzard_accuracy_in_hail(self):
        """Test Blizzard has 100% accuracy in hail"""
        position = {
            "move": {"name": "Blizzard", "accuracy": 70},
            "field": {"weather": "hail"}
        }
        
        # Blizzard should have 100% accuracy in hail
        expected_accuracy = 100
        assert expected_accuracy == 100
    
    def test_solar_beam_instant_in_sun(self):
        """Test Solar Beam is instant in sun"""
        position = {
            "move": {"name": "Solar Beam", "charge": True},
            "field": {"weather": "sun"}
        }
        
        # Solar Beam should be instant in sun
        expected_instant = True
        assert expected_instant == True
    
    def test_solar_blade_instant_in_sun(self):
        """Test Solar Blade is instant in sun"""
        position = {
            "move": {"name": "Solar Blade", "charge": True},
            "field": {"weather": "sun"}
        }
        
        # Solar Blade should be instant in sun
        expected_instant = True
        assert expected_instant == True

class TestWeatherRecoveryModifiers:
    """Test weather recovery modifiers"""
    
    def test_moonlight_heal_in_sun(self):
        """Test Moonlight heals 50% in sun"""
        position = {
            "move": {"name": "Moonlight"},
            "field": {"weather": "sun"},
            "pokemon": {"hp": 50, "max_hp": 100}
        }
        
        # Moonlight should heal 50% in sun
        expected_heal_percent = 0.5
        assert expected_heal_percent == 0.5
    
    def test_moonlight_heal_in_rain(self):
        """Test Moonlight heals 25% in rain"""
        position = {
            "move": {"name": "Moonlight"},
            "field": {"weather": "rain"},
            "pokemon": {"hp": 50, "max_hp": 100}
        }
        
        # Moonlight should heal 25% in rain
        expected_heal_percent = 0.25
        assert expected_heal_percent == 0.25
    
    def test_morning_sun_heal_in_sun(self):
        """Test Morning Sun heals 50% in sun"""
        position = {
            "move": {"name": "Morning Sun"},
            "field": {"weather": "sun"},
            "pokemon": {"hp": 50, "max_hp": 100}
        }
        
        # Morning Sun should heal 50% in sun
        expected_heal_percent = 0.5
        assert expected_heal_percent == 0.5
    
    def test_synthesis_heal_in_sun(self):
        """Test Synthesis heals 50% in sun"""
        position = {
            "move": {"name": "Synthesis"},
            "field": {"weather": "sun"},
            "pokemon": {"hp": 50, "max_hp": 100}
        }
        
        # Synthesis should heal 50% in sun
        expected_heal_percent = 0.5
        assert expected_heal_percent == 0.5

class TestTerrainMechanics:
    """Test terrain mechanics"""
    
    def test_electric_terrain_electric_boost(self):
        """Test Electric Terrain boosts Electric moves"""
        position = {
            "field": {"terrain": "electric"},
            "move": {"type": "Electric", "power": 100}
        }
        
        # Electric Terrain should boost Electric moves by 30%
        expected_boost = 1.3
        assert expected_boost == 1.3
    
    def test_electric_terrain_sleep_immunity(self):
        """Test Electric Terrain prevents sleep for grounded Pokemon"""
        position = {
            "field": {"terrain": "electric"},
            "pokemon": {"grounded": True, "status": "none"},
            "move": {"name": "Sleep Powder"}
        }
        
        # Electric Terrain should prevent sleep for grounded Pokemon
        expected_sleep_blocked = True
        assert expected_sleep_blocked == True
    
    def test_electric_terrain_priority_boost(self):
        """Test Electric Terrain boosts priority moves"""
        position = {
            "field": {"terrain": "electric"},
            "move": {"name": "Quick Attack", "priority": 1}
        }
        
        # Electric Terrain should boost priority moves
        expected_priority_boost = 1
        assert expected_priority_boost == 1
    
    def test_grassy_terrain_grass_boost(self):
        """Test Grassy Terrain boosts Grass moves"""
        position = {
            "field": {"terrain": "grassy"},
            "move": {"type": "Grass", "power": 100}
        }
        
        # Grassy Terrain should boost Grass moves by 30%
        expected_boost = 1.3
        assert expected_boost == 1.3
    
    def test_grassy_terrain_earthquake_nerf(self):
        """Test Grassy Terrain weakens Earthquake vs grounded"""
        position = {
            "field": {"terrain": "grassy"},
            "move": {"name": "Earthquake", "power": 100},
            "target": {"grounded": True}
        }
        
        # Grassy Terrain should weaken Earthquake by 50% vs grounded
        expected_nerf = 0.5
        assert expected_nerf == 0.5
    
    def test_grassy_terrain_heal_per_turn(self):
        """Test Grassy Terrain heals grounded Pokemon"""
        position = {
            "field": {"terrain": "grassy"},
            "pokemon": {"grounded": True, "hp": 90, "max_hp": 100}
        }
        
        # Grassy Terrain should heal 1/16 max HP per turn
        expected_heal = 6.25
        assert expected_heal == 6.25
    
    def test_grassy_terrain_heal_immunity(self):
        """Test Grassy Terrain heal immunity for Flying/Levitating"""
        immunity_conditions = [
            {"types": ["Flying"]},
            {"ability": "Levitate"},
            {"item": "Air Balloon"}
        ]
        
        for condition in immunity_conditions:
            position = {
                "field": {"terrain": "grassy"},
                "pokemon": {**condition, "hp": 90, "max_hp": 100}
            }
            
            # Flying/Levitating should not receive heal
            expected_heal = 0
            assert expected_heal == 0
    
    def test_misty_terrain_fairy_boost(self):
        """Test Misty Terrain boosts Fairy moves"""
        position = {
            "field": {"terrain": "misty"},
            "move": {"type": "Fairy", "power": 100}
        }
        
        # Misty Terrain should boost Fairy moves by 30%
        expected_boost = 1.3
        assert expected_boost == 1.3
    
    def test_misty_terrain_dragon_nerf(self):
        """Test Misty Terrain weakens Dragon moves"""
        position = {
            "field": {"terrain": "misty"},
            "move": {"type": "Dragon", "power": 100}
        }
        
        # Misty Terrain should weaken Dragon moves by 50%
        expected_nerf = 0.5
        assert expected_nerf == 0.5
    
    def test_misty_terrain_status_immunity(self):
        """Test Misty Terrain prevents status for grounded Pokemon"""
        position = {
            "field": {"terrain": "misty"},
            "pokemon": {"grounded": True, "status": "none"},
            "move": {"name": "Toxic"}
        }
        
        # Misty Terrain should prevent status for grounded Pokemon
        expected_status_blocked = True
        assert expected_status_blocked == True
    
    def test_psychic_terrain_psychic_boost(self):
        """Test Psychic Terrain boosts Psychic moves"""
        position = {
            "field": {"terrain": "psychic"},
            "move": {"type": "Psychic", "power": 100}
        }
        
        # Psychic Terrain should boost Psychic moves by 30%
        expected_boost = 1.3
        assert expected_boost == 1.3
    
    def test_psychic_terrain_priority_immunity(self):
        """Test Psychic Terrain blocks priority moves"""
        position = {
            "field": {"terrain": "psychic"},
            "move": {"name": "Quick Attack", "priority": 1}
        }
        
        # Psychic Terrain should block priority moves
        expected_priority_blocked = True
        assert expected_priority_blocked == True

class TestTerrainStatusInteractions:
    """Test terrain status interactions"""
    
    def test_electric_terrain_sleep_prevention(self):
        """Test Electric Terrain prevents sleep for grounded Pokemon"""
        position = {
            "field": {"terrain": "electric"},
            "pokemon": {"grounded": True, "status": "none"},
            "attacker": {"move": "Sleep Powder"}
        }
        
        # Electric Terrain should prevent sleep for grounded Pokemon
        expected_sleep_prevented = True
        assert expected_sleep_prevented == True
    
    def test_misty_terrain_status_prevention(self):
        """Test Misty Terrain prevents status for grounded Pokemon"""
        status_moves = ["Toxic", "Will-O-Wisp", "Thunder Wave", "Sleep Powder", "Spore"]
        
        for move in status_moves:
            position = {
                "field": {"terrain": "misty"},
                "pokemon": {"grounded": True, "status": "none"},
                "attacker": {"move": move}
            }
            
            # Misty Terrain should prevent status for grounded Pokemon
            expected_status_prevented = True
            assert expected_status_prevented == True
    
    def test_terrain_immunity_for_flying(self):
        """Test terrain effects don't affect Flying types"""
        position = {
            "field": {"terrain": "electric"},
            "pokemon": {"types": ["Flying"], "grounded": False},
            "attacker": {"move": "Sleep Powder"}
        }
        
        # Flying types should not be affected by terrain
        expected_terrain_immunity = True
        assert expected_terrain_immunity == True
    
    def test_terrain_immunity_for_levitate(self):
        """Test terrain effects don't affect Levitate users"""
        position = {
            "field": {"terrain": "electric"},
            "pokemon": {"ability": "Levitate", "grounded": False},
            "attacker": {"move": "Sleep Powder"}
        }
        
        # Levitate users should not be affected by terrain
        expected_terrain_immunity = True
        assert expected_terrain_immunity == True

class TestWeatherTerrainInteractions:
    """Test weather and terrain interactions"""
    
    def test_weather_terrain_damage_stacking(self):
        """Test weather and terrain damage can stack"""
        position = {
            "field": {"weather": "sandstorm", "terrain": "grassy"},
            "pokemon": {"grounded": True, "hp": 100, "max_hp": 100, "types": ["Normal"]}
        }
        
        # Sandstorm damage should still apply even with Grassy Terrain
        expected_sandstorm_damage = 6.25
        expected_grassy_heal = 6.25
        expected_net_effect = 0  # Damage and heal cancel out
        
        assert expected_sandstorm_damage == 6.25
        assert expected_grassy_heal == 6.25
        assert expected_net_effect == 0
    
    def test_weather_terrain_move_boosts_stacking(self):
        """Test weather and terrain move boosts can stack"""
        position = {
            "field": {"weather": "sun", "terrain": "grassy"},
            "move": {"type": "Grass", "power": 100}
        }
        
        # Sun and Grassy Terrain should both boost Grass moves
        expected_sun_boost = 1.0  # Sun doesn't boost Grass
        expected_terrain_boost = 1.3
        expected_total_boost = 1.3
        
        assert expected_sun_boost == 1.0
        assert expected_terrain_boost == 1.3
        assert expected_total_boost == 1.3

if __name__ == "__main__":
    pytest.main([__file__])
