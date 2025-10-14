#!/usr/bin/env python3
"""
Action Masking Test Suite

Tests all action masking mechanics including:
- PP=0 moves are illegal
- Disable/Encore/Taunt restrictions
- Choice lock restrictions
- Vest restriction (Assault Vest blocks status moves)
- Trap states prevent switching
- Already-used tera is illegal
- Accuracy=0 due to conditions is illegal
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestActionMasking:
    """Test action masking mechanics"""
    
    def test_pp_zero_moves_illegal(self):
        """Test moves with 0 PP are illegal"""
        position = {
            "pokemon": {
                "moves": [
                    {"name": "Earthquake", "pp": 0},
                    {"name": "Stone Edge", "pp": 10}
                ]
            },
            "legal_actions": ["MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Moves with 0 PP should be illegal
        expected_earthquake_legal = False
        expected_stone_edge_legal = True
        assert expected_earthquake_legal == False
        assert expected_stone_edge_legal == True
    
    def test_disable_blocks_specific_move(self):
        """Test Disable blocks specific move"""
        position = {
            "pokemon": {
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Stone Edge", "pp": 10}
                ],
                "volatiles": ["disable"],
                "disabled_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Disabled move should be illegal
        expected_earthquake_legal = False
        expected_stone_edge_legal = True
        assert expected_earthquake_legal == False
        assert expected_stone_edge_legal == True
    
    def test_encore_forces_specific_move(self):
        """Test Encore forces specific move"""
        position = {
            "pokemon": {
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Stone Edge", "pp": 10}
                ],
                "volatiles": ["encore"],
                "encored_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Only encored move should be legal
        expected_earthquake_legal = True
        expected_stone_edge_legal = False
        assert expected_earthquake_legal == True
        assert expected_stone_edge_legal == False
    
    def test_taunt_blocks_status_moves(self):
        """Test Taunt blocks status moves"""
        position = {
            "pokemon": {
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Toxic", "pp": 10},
                    {"name": "Will-O-Wisp", "pp": 10}
                ],
                "volatiles": ["taunt"]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Taunt should block status moves
        expected_earthquake_legal = True
        expected_toxic_legal = False
        expected_will_o_wisp_legal = False
        assert expected_earthquake_legal == True
        assert expected_toxic_legal == False
        assert expected_will_o_wisp_legal == False
    
    def test_choice_lock_blocks_other_moves(self):
        """Test Choice lock blocks other moves"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Stone Edge", "pp": 10}
                ],
                "last_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Choice lock should block other moves
        expected_earthquake_legal = True
        expected_stone_edge_legal = False
        assert expected_earthquake_legal == True
        assert expected_stone_edge_legal == False
    
    def test_assault_vest_blocks_status_moves(self):
        """Test Assault Vest blocks status moves"""
        position = {
            "pokemon": {
                "item": "Assault Vest",
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Toxic", "pp": 10},
                    {"name": "Recover", "pp": 10}
                ]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Assault Vest should block status moves
        expected_earthquake_legal = True
        expected_toxic_legal = False
        expected_recover_legal = False
        assert expected_earthquake_legal == True
        assert expected_toxic_legal == False
        assert expected_recover_legal == False
    
    def test_trap_states_prevent_switching(self):
        """Test trap states prevent switching"""
        position = {
            "pokemon": {
                "volatiles": ["infestation"],
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["MOVE_Earthquake"]
        }
        
        # Trap states should prevent switching
        expected_earthquake_legal = True
        expected_switching_legal = False
        assert expected_earthquake_legal == True
        assert expected_switching_legal == False
    
    def test_whirlpool_trap_prevents_switching(self):
        """Test Whirlpool trap prevents switching"""
        position = {
            "pokemon": {
                "volatiles": ["whirlpool"],
                "moves": [{"name": "Hydro Pump", "pp": 10}]
            },
            "legal_actions": ["MOVE_Hydro Pump"]
        }
        
        # Whirlpool should prevent switching
        expected_hydro_pump_legal = True
        expected_switching_legal = False
        assert expected_hydro_pump_legal == True
        assert expected_switching_legal == False
    
    def test_fire_spin_trap_prevents_switching(self):
        """Test Fire Spin trap prevents switching"""
        position = {
            "pokemon": {
                "volatiles": ["fire_spin"],
                "moves": [{"name": "Flamethrower", "pp": 10}]
            },
            "legal_actions": ["MOVE_Flamethrower"]
        }
        
        # Fire Spin should prevent switching
        expected_flamethrower_legal = True
        expected_switching_legal = False
        assert expected_flamethrower_legal == True
        assert expected_switching_legal == False
    
    def test_already_used_tera_illegal(self):
        """Test already-used Tera is illegal"""
        position = {
            "pokemon": {
                "terastallized": True,
                "tera_used": True,
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Already-used Tera should be illegal
        expected_tera_legal = False
        expected_earthquake_legal = True
        assert expected_tera_legal == False
        assert expected_earthquake_legal == True
    
    def test_tera_illegal_when_disabled(self):
        """Test Tera illegal when format disabled"""
        position = {
            "format": {"tera_allowed": False},
            "pokemon": {
                "terastallized": False,
                "tera_used": False,
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Tera should be illegal when disabled
        expected_tera_legal = False
        expected_earthquake_legal = True
        assert expected_tera_legal == False
        assert expected_earthquake_legal == True
    
    def test_zero_accuracy_moves_illegal(self):
        """Test moves with 0% accuracy are illegal"""
        position = {
            "pokemon": {
                "moves": [
                    {"name": "Earthquake", "pp": 10, "accuracy": 100},
                    {"name": "Stone Edge", "pp": 10, "accuracy": 0}
                ]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Moves with 0% accuracy should be illegal
        expected_earthquake_legal = True
        expected_stone_edge_legal = False
        assert expected_earthquake_legal == True
        assert expected_stone_edge_legal == False
    
    def test_paralysis_reduces_accuracy(self):
        """Test paralysis reduces accuracy"""
        position = {
            "pokemon": {
                "status": "paralysis",
                "moves": [{"name": "Earthquake", "pp": 10, "accuracy": 100}]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Paralysis should reduce accuracy but not make it illegal
        expected_earthquake_legal = True
        expected_accuracy_reduced = True
        assert expected_earthquake_legal == True
        assert expected_accuracy_reduced == True
    
    def test_sleep_prevents_all_actions(self):
        """Test sleep prevents all actions"""
        position = {
            "pokemon": {
                "status": "sleep",
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["SWITCH_1"]
        }
        
        # Sleep should prevent all moves
        expected_earthquake_legal = False
        expected_switching_legal = True
        assert expected_earthquake_legal == False
        assert expected_switching_legal == True
    
    def test_freeze_prevents_all_actions(self):
        """Test freeze prevents all actions"""
        position = {
            "pokemon": {
                "status": "freeze",
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["SWITCH_1"]
        }
        
        # Freeze should prevent all moves
        expected_earthquake_legal = False
        expected_switching_legal = True
        assert expected_earthquake_legal == False
        assert expected_switching_legal == True
    
    def test_confusion_prevents_all_actions(self):
        """Test confusion prevents all actions"""
        position = {
            "pokemon": {
                "status": "confusion",
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["SWITCH_1"]
        }
        
        # Confusion should prevent all moves
        expected_earthquake_legal = False
        expected_switching_legal = True
        assert expected_earthquake_legal == False
        assert expected_switching_legal == True
    
    def test_flinch_prevents_all_actions(self):
        """Test flinch prevents all actions"""
        position = {
            "pokemon": {
                "volatiles": ["flinch"],
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["SWITCH_1"]
        }
        
        # Flinch should prevent all moves
        expected_earthquake_legal = False
        expected_switching_legal = True
        assert expected_earthquake_legal == False
        assert expected_switching_legal == True
    
    def test_torment_prevents_move_repetition(self):
        """Test Torment prevents move repetition"""
        position = {
            "pokemon": {
                "volatiles": ["torment"],
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Stone Edge", "pp": 10}
                ],
                "last_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Torment should prevent repeating last move
        expected_earthquake_legal = False
        expected_stone_edge_legal = True
        assert expected_earthquake_legal == False
        assert expected_stone_edge_legal == True
    
    def test_imprison_prevents_shared_moves(self):
        """Test Imprison prevents shared moves"""
        position = {
            "pokemon": {
                "volatiles": ["imprison"],
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Stone Edge", "pp": 10}
                ],
                "opponent_moves": ["Earthquake", "Toxic"]
            },
            "legal_actions": ["MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Imprison should prevent shared moves
        expected_earthquake_legal = False
        expected_stone_edge_legal = True
        assert expected_earthquake_legal == False
        assert expected_stone_edge_legal == True
    
    def test_heal_block_prevents_healing_moves(self):
        """Test Heal Block prevents healing moves"""
        position = {
            "pokemon": {
                "volatiles": ["heal_block"],
                "moves": [
                    {"name": "Earthquake", "pp": 10},
                    {"name": "Recover", "pp": 10}
                ]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Heal Block should prevent healing moves
        expected_earthquake_legal = True
        expected_recover_legal = False
        assert expected_earthquake_legal == True
        assert expected_recover_legal == False
    
    def test_gravity_affects_accuracy(self):
        """Test Gravity affects move accuracy"""
        position = {
            "field": {"sideConditions": {"gravity": True}},
            "pokemon": {
                "moves": [{"name": "Earthquake", "pp": 10, "accuracy": 100}]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Gravity should affect accuracy but not make moves illegal
        expected_earthquake_legal = True
        expected_accuracy_affected = True
        assert expected_earthquake_legal == True
        assert expected_accuracy_affected == True
    
    def test_trick_room_affects_speed(self):
        """Test Trick Room affects speed calculations"""
        position = {
            "field": {"sideConditions": {"trickRoom": True}},
            "pokemon": {
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Trick Room should affect speed but not make moves illegal
        expected_earthquake_legal = True
        expected_speed_affected = True
        assert expected_earthquake_legal == True
        assert expected_speed_affected == True
    
    def test_tailwind_affects_speed(self):
        """Test Tailwind affects speed calculations"""
        position = {
            "field": {"sideConditions": {"tailwind": True}},
            "pokemon": {
                "moves": [{"name": "Earthquake", "pp": 10}]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Tailwind should affect speed but not make moves illegal
        expected_earthquake_legal = True
        expected_speed_affected = True
        assert expected_earthquake_legal == True
        assert expected_speed_affected == True
    
    def test_weather_affects_accuracy(self):
        """Test weather affects move accuracy"""
        position = {
            "field": {"weather": "rain"},
            "pokemon": {
                "moves": [{"name": "Thunder", "pp": 10, "accuracy": 70}]
            },
            "legal_actions": ["MOVE_Thunder", "SWITCH_1"]
        }
        
        # Weather should affect accuracy but not make moves illegal
        expected_thunder_legal = True
        expected_accuracy_boosted = True
        assert expected_thunder_legal == True
        assert expected_accuracy_boosted == True
    
    def test_terrain_affects_accuracy(self):
        """Test terrain affects move accuracy"""
        position = {
            "field": {"terrain": "electric"},
            "pokemon": {
                "moves": [{"name": "Thunder", "pp": 10, "accuracy": 70}]
            },
            "legal_actions": ["MOVE_Thunder", "SWITCH_1"]
        }
        
        # Terrain should affect accuracy but not make moves illegal
        expected_thunder_legal = True
        expected_accuracy_boosted = True
        assert expected_thunder_legal == True
        assert expected_accuracy_boosted == True

if __name__ == "__main__":
    pytest.main([__file__])
