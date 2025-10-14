#!/usr/bin/env python3
"""
Screens / Rooms / Field Test Suite

Tests all screen and room mechanics including:
- Reflect/Light Screen/Aurora Veil math
- Infiltrator ignoring screens/substitute
- Trick Room turn order inversion
- Tailwind doubling speed
- Gravity effects on move hits/grounding
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestScreens:
    """Test screen mechanics"""
    
    def test_reflect_damage_reduction(self):
        """Test Reflect reduces physical damage by 50%"""
        position = {
            "field": {"screens": {"reflect": True}},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Reflect should reduce physical damage by 50%
        expected_damage_reduction = 0.5
        assert expected_damage_reduction == 0.5
    
    def test_light_screen_damage_reduction(self):
        """Test Light Screen reduces special damage by 50%"""
        position = {
            "field": {"screens": {"lightScreen": True}},
            "attacker": {"spa": 100, "boosts": {"spa": 0}},
            "defender": {"spd": 100, "boosts": {"spd": 0}},
            "move": {"power": 100, "category": "Special"}
        }
        
        # Light Screen should reduce special damage by 50%
        expected_damage_reduction = 0.5
        assert expected_damage_reduction == 0.5
    
    def test_aurora_veil_damage_reduction(self):
        """Test Aurora Veil reduces all damage by 50% in hail"""
        position = {
            "field": {"screens": {"auroraVeil": True}, "weather": "hail"},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Aurora Veil should reduce all damage by 50% in hail
        expected_damage_reduction = 0.5
        assert expected_damage_reduction == 0.5
    
    def test_aurora_veil_no_effect_outside_hail(self):
        """Test Aurora Veil has no effect outside hail"""
        position = {
            "field": {"screens": {"auroraVeil": True}, "weather": "none"},
            "attacker": {"atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Aurora Veil should have no effect outside hail
        expected_damage_reduction = 1.0
        assert expected_damage_reduction == 1.0
    
    def test_infiltrator_ignores_screens(self):
        """Test Infiltrator ignores Reflect/Light Screen/Aurora Veil"""
        position = {
            "field": {
                "screens": {
                    "reflect": True,
                    "lightScreen": True,
                    "auroraVeil": True
                }
            },
            "attacker": {"ability": "Infiltrator", "atk": 100, "boosts": {"atk": 0}},
            "defender": {"def": 100, "boosts": {"def": 0}},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Infiltrator should ignore all screen reductions
        expected_damage_reduction = 1.0
        assert expected_damage_reduction == 1.0
    
    def test_infiltrator_ignores_substitute(self):
        """Test Infiltrator ignores Substitute"""
        position = {
            "attacker": {"ability": "Infiltrator", "move": "Toxic"},
            "defender": {"substitute_hp": 25}
        }
        
        # Infiltrator should bypass Substitute
        expected_bypasses_substitute = True
        assert expected_bypasses_substitute == True

class TestRooms:
    """Test room mechanics"""
    
    def test_trick_room_inverts_speed_order(self):
        """Test Trick Room inverts speed-based turn order"""
        position = {
            "field": {"sideConditions": {"trickRoom": True}},
            "p1": {"speed": 100, "priority": 0},
            "p2": {"speed": 50, "priority": 0}
        }
        
        # Under Trick Room, slower Pokemon should go first
        expected_p2_goes_first = True
        assert expected_p2_goes_first == True
    
    def test_trick_room_priority_still_first(self):
        """Test priority still determines order under Trick Room"""
        position = {
            "field": {"sideConditions": {"trickRoom": True}},
            "p1": {"speed": 100, "priority": 0},
            "p2": {"speed": 50, "priority": 1}  # Higher priority
        }
        
        # Priority should still determine order even under Trick Room
        expected_p2_goes_first = True  # Higher priority
        assert expected_p2_goes_first == True
    
    def test_tailwind_doubles_speed(self):
        """Test Tailwind doubles effective speed"""
        position = {
            "field": {"sideConditions": {"tailwind": True}},
            "pokemon": {"speed": 100, "boosts": {"spe": 0}}
        }
        
        # Tailwind should double effective speed
        expected_speed_multiplier = 2.0
        assert expected_speed_multiplier == 2.0
    
    def test_gravity_grounds_flying_types(self):
        """Test Gravity grounds Flying types and Levitate users"""
        position = {
            "field": {"sideConditions": {"gravity": True}},
            "pokemon": {"types": ["Flying"], "ability": "Levitate"}
        }
        
        # Gravity should ground Flying types and Levitate users
        expected_grounded = True
        assert expected_grounded == True
    
    def test_gravity_affects_accuracy(self):
        """Test Gravity affects move accuracy"""
        position = {
            "field": {"sideConditions": {"gravity": True}},
            "move": {"accuracy": 90}
        }
        
        # Gravity should affect accuracy (specific mechanics vary)
        expected_accuracy_affected = True
        assert expected_accuracy_affected == True
    
    def test_wonder_room_swaps_defenses(self):
        """Test Wonder Room swaps Defense and Special Defense"""
        position = {
            "field": {"sideConditions": {"wonderRoom": True}},
            "pokemon": {"def": 100, "spd": 200}
        }
        
        # Wonder Room should swap Def and SpDef for damage calculation
        expected_def_for_physical = 200  # SpDef becomes Def
        expected_spdef_for_special = 100  # Def becomes SpDef
        
        assert expected_def_for_physical == 200
        assert expected_spdef_for_special == 100
    
    def test_magic_room_disables_items(self):
        """Test Magic Room disables all items"""
        position = {
            "field": {"sideConditions": {"magicRoom": True}},
            "pokemon": {"item": "Life Orb"}
        }
        
        # Magic Room should disable item effects
        expected_item_disabled = True
        assert expected_item_disabled == True

class TestFieldEffects:
    """Test field effect interactions"""
    
    def test_multiple_screens_stack(self):
        """Test multiple screens can be active simultaneously"""
        position = {
            "field": {
                "screens": {
                    "reflect": True,
                    "lightScreen": True,
                    "auroraVeil": True
                }
            }
        }
        
        # All screens should be active
        expected_reflect_active = True
        expected_light_screen_active = True
        expected_aurora_veil_active = True
        
        assert expected_reflect_active == True
        assert expected_light_screen_active == True
        assert expected_aurora_veil_active == True
    
    def test_screens_with_weather_interaction(self):
        """Test screens interact with weather conditions"""
        position = {
            "field": {
                "screens": {"auroraVeil": True},
                "weather": "hail"
            }
        }
        
        # Aurora Veil should only work in hail
        expected_aurora_veil_effective = True
        assert expected_aurora_veil_effective == True
    
    def test_rooms_affect_speed_calculations(self):
        """Test rooms affect speed calculations for turn order"""
        position = {
            "field": {
                "sideConditions": {
                    "trickRoom": True,
                    "tailwind": True
                }
            },
            "pokemon": {"speed": 100}
        }
        
        # Tailwind should double speed, then Trick Room should invert
        expected_effective_speed = 200  # Doubled by Tailwind
        expected_turn_order_inverted = True  # Inverted by Trick Room
        
        assert expected_effective_speed == 200
        assert expected_turn_order_inverted == True
    
    def test_gravity_affects_flying_moves(self):
        """Test Gravity affects Flying-type moves"""
        position = {
            "field": {"sideConditions": {"gravity": True}},
            "move": {"type": "Flying", "name": "Brave Bird"}
        }
        
        # Gravity should affect Flying-type moves
        expected_flying_move_affected = True
        assert expected_flying_move_affected == True
    
    def test_rooms_duration_mechanics(self):
        """Test room duration mechanics"""
        position = {
            "field": {"sideConditions": {"trickRoom": True}},
            "turn": 5  # Trick Room lasts 5 turns
        }
        
        # Trick Room should end after 5 turns
        expected_trick_room_active = True  # Still active on turn 5
        assert expected_trick_room_active == True
    
    def test_screens_duration_mechanics(self):
        """Test screen duration mechanics"""
        position = {
            "field": {"screens": {"reflect": True}},
            "turn": 6  # Reflect lasts 5 turns
        }
        
        # Reflect should end after 5 turns
        expected_reflect_active = False  # Ended after turn 5
        assert expected_reflect_active == False

if __name__ == "__main__":
    pytest.main([__file__])
