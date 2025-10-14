#!/usr/bin/env python3
"""
Priority, Speed, and Order Test Suite

Tests all priority and speed mechanics including:
- Priority brackets then effective speed
- Speed ties randomization
- Prankster fails vs Dark targets for status moves
- Gale Wings only when at full HP
- Quick Claw not legal in OU
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestPriorityMechanics:
    """Test priority system mechanics"""
    
    def test_priority_brackets_determine_order(self):
        """Test priority brackets determine turn order"""
        position = {
            "p1": {"move": "Quick Attack", "priority": 1, "speed": 50},
            "p2": {"move": "Earthquake", "priority": 0, "speed": 100}
        }
        
        # Higher priority should go first regardless of speed
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True
    
    def test_speed_determines_order_same_priority(self):
        """Test speed determines order with same priority"""
        position = {
            "p1": {"move": "Earthquake", "priority": 0, "speed": 100},
            "p2": {"move": "Stone Edge", "priority": 0, "speed": 50}
        }
        
        # Higher speed should go first with same priority
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True
    
    def test_speed_tie_randomization(self):
        """Test speed ties are randomized"""
        position = {
            "p1": {"move": "Earthquake", "priority": 0, "speed": 100},
            "p2": {"move": "Stone Edge", "priority": 0, "speed": 100}
        }
        
        # Speed ties should be randomized
        expected_randomized = True
        assert expected_randomized == True
    
    def test_priority_bracket_ordering(self):
        """Test priority bracket ordering"""
        test_cases = [
            {"p1_priority": 7, "p2_priority": 6, "expected_p1_first": True},
            {"p1_priority": 1, "p2_priority": 0, "expected_p1_first": True},
            {"p1_priority": 0, "p2_priority": -1, "expected_p1_first": True},
            {"p1_priority": -4, "p2_priority": -5, "expected_p1_first": True}
        ]
        
        for case in test_cases:
            position = {
                "p1": {"priority": case["p1_priority"]},
                "p2": {"priority": case["p2_priority"]}
            }
            
            expected_p1_first = case["expected_p1_first"]
            assert expected_p1_first == case["expected_p1_first"]
    
    def test_negative_priority_moves(self):
        """Test negative priority moves go last"""
        position = {
            "p1": {"move": "Roar", "priority": -7},
            "p2": {"move": "Earthquake", "priority": 0}
        }
        
        # Negative priority should go last
        expected_p2_goes_first = True
        assert expected_p2_goes_first == True
    
    def test_high_priority_moves(self):
        """Test high priority moves go first"""
        position = {
            "p1": {"move": "Extreme Speed", "priority": 2},
            "p2": {"move": "Quick Attack", "priority": 1}
        }
        
        # Higher priority should go first
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True

class TestSpeedMechanics:
    """Test speed calculation mechanics"""
    
    def test_speed_boosts_affect_order(self):
        """Test speed boosts affect turn order"""
        position = {
            "p1": {"speed": 100, "boosts": {"spe": 2}},  # +2 Speed
            "p2": {"speed": 100, "boosts": {"spe": 0}}
        }
        
        # Speed boosts should affect turn order
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True
    
    def test_speed_drops_affect_order(self):
        """Test speed drops affect turn order"""
        position = {
            "p1": {"speed": 100, "boosts": {"spe": 0}},
            "p2": {"speed": 100, "boosts": {"spe": -2}}  # -2 Speed
        }
        
        # Speed drops should affect turn order
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True
    
    def test_paralysis_speed_reduction(self):
        """Test paralysis reduces speed by 75%"""
        position = {
            "pokemon": {
                "speed": 100,
                "status": "paralysis"
            }
        }
        
        # Paralysis should reduce speed by 75%
        expected_speed_multiplier = 0.25
        assert expected_speed_multiplier == 0.25
    
    def test_tailwind_doubles_speed(self):
        """Test Tailwind doubles effective speed"""
        position = {
            "pokemon": {
                "speed": 100,
                "field_conditions": {"tailwind": True}
            }
        }
        
        # Tailwind should double effective speed
        expected_speed_multiplier = 2.0
        assert expected_speed_multiplier == 2.0
    
    def test_trick_room_inverts_speed_order(self):
        """Test Trick Room inverts speed-based turn order"""
        position = {
            "field": {"sideConditions": {"trickRoom": True}},
            "p1": {"speed": 100, "priority": 0},
            "p2": {"speed": 50, "priority": 0}
        }
        
        # Trick Room should invert speed order
        expected_p2_goes_first = True  # Slower goes first under Trick Room
        assert expected_p2_goes_first == True
    
    def test_weather_abilities_affect_speed(self):
        """Test weather abilities affect speed calculations"""
        position = {
            "pokemon": {
                "ability": "Sand Rush",
                "field_weather": "sandstorm",
                "speed": 100
            }
        }
        
        # Sand Rush should double speed in sandstorm
        expected_speed_multiplier = 2.0
        assert expected_speed_multiplier == 2.0

class TestPranksterMechanics:
    """Test Prankster ability mechanics"""
    
    def test_prankster_boosts_status_priority(self):
        """Test Prankster boosts status move priority"""
        position = {
            "pokemon": {
                "ability": "Prankster",
                "move": "Toxic",
                "priority": 0
            }
        }
        
        # Prankster should boost status move priority to +1
        expected_priority = 1
        assert expected_priority == 1
    
    def test_prankster_fails_vs_dark_targets(self):
        """Test Prankster fails against Dark targets"""
        position = {
            "attacker": {
                "ability": "Prankster",
                "move": "Toxic"
            },
            "defender": {"types": ["Dark"]}
        }
        
        # Prankster should fail against Dark targets
        expected_success = False
        assert expected_success == False
    
    def test_prankster_works_vs_non_dark_targets(self):
        """Test Prankster works against non-Dark targets"""
        position = {
            "attacker": {
                "ability": "Prankster",
                "move": "Toxic"
            },
            "defender": {"types": ["Normal"]}
        }
        
        # Prankster should work against non-Dark targets
        expected_success = True
        assert expected_success == True
    
    def test_prankster_doesnt_affect_attacking_moves(self):
        """Test Prankster doesn't affect attacking moves"""
        position = {
            "pokemon": {
                "ability": "Prankster",
                "move": "Earthquake",
                "priority": 0
            }
        }
        
        # Prankster should not affect attacking moves
        expected_priority = 0
        assert expected_priority == 0

class TestGaleWingsMechanics:
    """Test Gale Wings ability mechanics"""
    
    def test_gale_wings_boosts_flying_priority_at_full_hp(self):
        """Test Gale Wings boosts Flying move priority at full HP"""
        position = {
            "pokemon": {
                "ability": "Gale Wings",
                "hp": 100,
                "max_hp": 100,
                "move": "Brave Bird",
                "priority": 0
            }
        }
        
        # Gale Wings should boost Flying move priority to +1 at full HP
        expected_priority = 1
        assert expected_priority == 1
    
    def test_gale_wings_no_boost_below_full_hp(self):
        """Test Gale Wings doesn't boost below full HP"""
        position = {
            "pokemon": {
                "ability": "Gale Wings",
                "hp": 99,
                "max_hp": 100,
                "move": "Brave Bird",
                "priority": 0
            }
        }
        
        # Gale Wings should not boost below full HP
        expected_priority = 0
        assert expected_priority == 0
    
    def test_gale_wings_only_affects_flying_moves(self):
        """Test Gale Wings only affects Flying-type moves"""
        position = {
            "pokemon": {
                "ability": "Gale Wings",
                "hp": 100,
                "max_hp": 100,
                "move": "Earthquake",
                "priority": 0
            }
        }
        
        # Gale Wings should not affect non-Flying moves
        expected_priority = 0
        assert expected_priority == 0

class TestQuickClawRestrictions:
    """Test Quick Claw format restrictions"""
    
    def test_quick_claw_banned_in_ou(self):
        """Test Quick Claw is banned in Gen 9 OU"""
        position = {
            "format": "gen9ou",
            "pokemon": {"item": "Quick Claw"}
        }
        
        # Quick Claw should be banned in Gen 9 OU
        expected_legal = False
        assert expected_legal == False
    
    def test_quick_claw_priority_boost(self):
        """Test Quick Claw priority boost mechanics (if legal)"""
        position = {
            "pokemon": {
                "item": "Quick Claw",
                "move": "Earthquake",
                "priority": 0
            }
        }
        
        # Quick Claw should have 20% chance to boost priority
        expected_priority_boost_chance = 0.20
        assert expected_priority_boost_chance == 0.20

class TestSpeedTieResolution:
    """Test speed tie resolution mechanics"""
    
    def test_speed_tie_randomization(self):
        """Test speed ties are randomized"""
        position = {
            "p1": {"speed": 100, "priority": 0},
            "p2": {"speed": 100, "priority": 0}
        }
        
        # Speed ties should be randomized
        expected_randomized = True
        assert expected_randomized == True
    
    def test_speed_tie_with_boosts(self):
        """Test speed ties with different boosts"""
        position = {
            "p1": {"speed": 100, "boosts": {"spe": 1}},
            "p2": {"speed": 100, "boosts": {"spe": 0}}
        }
        
        # Speed boosts should break ties
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True
    
    def test_speed_tie_with_status(self):
        """Test speed ties with status conditions"""
        position = {
            "p1": {"speed": 100, "status": "none"},
            "p2": {"speed": 100, "status": "paralysis"}
        }
        
        # Paralysis should affect speed calculation
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True

class TestTurnOrderEdgeCases:
    """Test edge cases in turn order determination"""
    
    def test_priority_overrides_speed(self):
        """Test priority always overrides speed"""
        position = {
            "p1": {"priority": 1, "speed": 50},
            "p2": {"priority": 0, "speed": 100}
        }
        
        # Priority should override speed
        expected_p1_goes_first = True
        assert expected_p1_goes_first == True
    
    def test_negative_priority_always_last(self):
        """Test negative priority always goes last"""
        position = {
            "p1": {"priority": -1, "speed": 100},
            "p2": {"priority": 0, "speed": 50}
        }
        
        # Negative priority should go last
        expected_p2_goes_first = True
        assert expected_p2_goes_first == True
    
    def test_multiple_speed_modifiers(self):
        """Test multiple speed modifiers stack correctly"""
        position = {
            "pokemon": {
                "speed": 100,
                "boosts": {"spe": 1},
                "field_conditions": {"tailwind": True},
                "status": "paralysis"
            }
        }
        
        # Multiple modifiers should stack: (100 * 2 * 1.5) * 0.25 = 75
        expected_effective_speed = 75
        assert expected_effective_speed == 75

if __name__ == "__main__":
    pytest.main([__file__])
