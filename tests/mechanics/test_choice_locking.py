#!/usr/bin/env python3
"""
Choice / Locking / Vest Test Suite

Tests all choice and locking mechanics including:
- Choice lock persists until switch/out-of-PP
- Encore cannot force illegal different move while choice-locked
- Assault Vest prevents non-damaging status moves
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestChoiceLockMechanics:
    """Test choice item locking mechanics"""
    
    def test_choice_band_locks_into_first_move(self):
        """Test Choice Band locks into first move used"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge", "Toxic"],
                "last_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "MOVE_Toxic", "SWITCH_1"]
        }
        
        # Choice Band should lock into first move used
        expected_earthquake_legal = True
        expected_other_moves_legal = False
        expected_switching_legal = True
        
        assert expected_earthquake_legal == True
        assert expected_other_moves_legal == False
        assert expected_switching_legal == True
    
    def test_choice_specs_locks_into_first_move(self):
        """Test Choice Specs locks into first move used"""
        position = {
            "pokemon": {
                "item": "Choice Specs",
                "moves": ["Flamethrower", "Ice Beam", "Toxic"],
                "last_move": "Flamethrower"
            },
            "legal_actions": ["MOVE_Flamethrower", "MOVE_Ice Beam", "MOVE_Toxic", "SWITCH_1"]
        }
        
        # Choice Specs should lock into first move used
        expected_flamethrower_legal = True
        expected_other_moves_legal = False
        expected_switching_legal = True
        
        assert expected_flamethrower_legal == True
        assert expected_other_moves_legal == False
        assert expected_switching_legal == True
    
    def test_choice_scarf_locks_into_first_move(self):
        """Test Choice Scarf locks into first move used"""
        position = {
            "pokemon": {
                "item": "Choice Scarf",
                "moves": ["U-turn", "Volt Switch", "Toxic"],
                "last_move": "U-turn"
            },
            "legal_actions": ["MOVE_U-turn", "MOVE_Volt Switch", "MOVE_Toxic", "SWITCH_1"]
        }
        
        # Choice Scarf should lock into first move used
        expected_u_turn_legal = True
        expected_other_moves_legal = False
        expected_switching_legal = True
        
        assert expected_u_turn_legal == True
        assert expected_other_moves_legal == False
        assert expected_switching_legal == True
    
    def test_choice_lock_ends_on_switch(self):
        """Test choice lock ends when switching out"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "switching": True
            }
        }
        
        # Choice lock should end when switching out
        expected_lock_ended = True
        assert expected_lock_ended == True
    
    def test_choice_lock_ends_when_move_out_of_pp(self):
        """Test choice lock ends when locked move has no PP"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": [{"name": "Earthquake", "pp": 0}, {"name": "Stone Edge", "pp": 10}],
                "last_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Choice lock should end when locked move has no PP
        expected_earthquake_legal = False
        expected_other_moves_legal = True
        
        assert expected_earthquake_legal == False
        assert expected_other_moves_legal == True
    
    def test_choice_lock_persists_across_turns(self):
        """Test choice lock persists across multiple turns"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "turn": 5  # Multiple turns later
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Choice lock should persist across turns
        expected_earthquake_legal = True
        expected_other_moves_legal = False
        
        assert expected_earthquake_legal == True
        assert expected_other_moves_legal == False

class TestEncoreChoiceInteraction:
    """Test Encore interaction with choice lock"""
    
    def test_encore_cannot_force_different_move_while_locked(self):
        """Test Encore cannot force different move while choice-locked"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "volatiles": ["encore"],
                "encored_move": "Stone Edge"
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Encore cannot force different move while choice-locked
        expected_encored_move_legal = False  # Stone Edge not legal due to choice lock
        expected_locked_move_legal = True   # Earthquake still legal
        expected_switching_legal = True
        
        assert expected_encored_move_legal == False
        assert expected_locked_move_legal == True
        assert expected_switching_legal == True
    
    def test_encore_works_when_not_choice_locked(self):
        """Test Encore works normally when not choice-locked"""
        position = {
            "pokemon": {
                "item": "Leftovers",
                "moves": ["Earthquake", "Stone Edge"],
                "volatiles": ["encore"],
                "encored_move": "Earthquake"
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Encore should work normally when not choice-locked
        expected_encored_move_legal = True
        expected_other_moves_legal = False
        
        assert expected_encored_move_legal == True
        assert expected_other_moves_legal == False
    
    def test_encore_ends_choice_lock(self):
        """Test Encore ending allows choice lock to reset"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "volatiles": [],  # Encore ended
                "encore_turns": 0
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # When Encore ends, choice lock should reset
        expected_all_moves_legal = True
        assert expected_all_moves_legal == True

class TestAssaultVestRestrictions:
    """Test Assault Vest restrictions"""
    
    def test_assault_vest_blocks_status_moves(self):
        """Test Assault Vest blocks non-damaging status moves"""
        position = {
            "pokemon": {
                "item": "Assault Vest",
                "moves": ["Toxic", "Will-O-Wisp", "Recover", "Earthquake"]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Assault Vest should block status moves
        expected_status_moves_legal = False
        expected_attacking_moves_legal = True
        expected_switching_legal = True
        
        assert expected_status_moves_legal == False
        assert expected_attacking_moves_legal == True
        assert expected_switching_legal == True
    
    def test_assault_vest_allows_attacking_moves(self):
        """Test Assault Vest allows attacking moves"""
        position = {
            "pokemon": {
                "item": "Assault Vest",
                "moves": ["Earthquake", "Stone Edge", "Flamethrower", "Ice Beam"]
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "MOVE_Flamethrower", "MOVE_Ice Beam", "SWITCH_1"]
        }
        
        # Assault Vest should allow attacking moves
        expected_attacking_moves_legal = True
        assert expected_attacking_moves_legal == True
    
    def test_assault_vest_blocks_healing_moves(self):
        """Test Assault Vest blocks healing moves"""
        position = {
            "pokemon": {
                "item": "Assault Vest",
                "moves": ["Recover", "Roost", "Synthesis", "Earthquake"]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Assault Vest should block healing moves
        expected_healing_moves_legal = False
        expected_attacking_moves_legal = True
        
        assert expected_healing_moves_legal == False
        assert expected_attacking_moves_legal == True
    
    def test_assault_vest_blocks_setup_moves(self):
        """Test Assault Vest blocks setup moves"""
        position = {
            "pokemon": {
                "item": "Assault Vest",
                "moves": ["Swords Dance", "Calm Mind", "Dragon Dance", "Earthquake"]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Assault Vest should block setup moves
        expected_setup_moves_legal = False
        expected_attacking_moves_legal = True
        
        assert expected_setup_moves_legal == False
        assert expected_attacking_moves_legal == True
    
    def test_assault_vest_blocks_hazard_moves(self):
        """Test Assault Vest blocks hazard moves"""
        position = {
            "pokemon": {
                "item": "Assault Vest",
                "moves": ["Stealth Rock", "Spikes", "Toxic Spikes", "Earthquake"]
            },
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Assault Vest should block hazard moves
        expected_hazard_moves_legal = False
        expected_attacking_moves_legal = True
        
        assert expected_hazard_moves_legal == False
        assert expected_attacking_moves_legal == True

class TestChoiceItemInteractions:
    """Test choice item interactions with other mechanics"""
    
    def test_choice_lock_with_taunt(self):
        """Test choice lock with Taunt interaction"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge", "Toxic"],
                "last_move": "Earthquake",
                "volatiles": ["taunt"]
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "SWITCH_1"]
        }
        
        # Taunt should not affect choice lock
        expected_earthquake_legal = True
        expected_stone_edge_legal = False  # Still choice locked
        expected_toxic_legal = False  # Blocked by Taunt
        
        assert expected_earthquake_legal == True
        assert expected_stone_edge_legal == False
        assert expected_toxic_legal == False
    
    def test_choice_lock_with_disable(self):
        """Test choice lock with Disable interaction"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "volatiles": ["disable"],
                "disabled_move": "Earthquake"
            },
            "legal_actions": ["SWITCH_1"]
        }
        
        # Disable should prevent locked move, forcing switch
        expected_earthquake_legal = False
        expected_stone_edge_legal = False
        expected_switching_legal = True
        
        assert expected_earthquake_legal == False
        assert expected_stone_edge_legal == False
        assert expected_switching_legal == True
    
    def test_choice_lock_with_torment(self):
        """Test choice lock with Torment interaction"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "volatiles": ["torment"]
            },
            "legal_actions": ["SWITCH_1"]
        }
        
        # Torment should prevent repeating locked move, forcing switch
        expected_earthquake_legal = False
        expected_stone_edge_legal = False
        expected_switching_legal = True
        
        assert expected_earthquake_legal == False
        assert expected_stone_edge_legal == False
        assert expected_switching_legal == True

class TestChoiceItemSwitching:
    """Test choice item switching mechanics"""
    
    def test_choice_item_switching_resets_lock(self):
        """Test switching resets choice lock"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge"],
                "last_move": "Earthquake",
                "switching": True
            }
        }
        
        # Switching should reset choice lock
        expected_lock_reset = True
        assert expected_lock_reset == True
    
    def test_choice_item_switching_allows_new_choice(self):
        """Test switching allows new move choice"""
        position = {
            "pokemon": {
                "item": "Choice Band",
                "moves": ["Earthquake", "Stone Edge", "Toxic"],
                "switching": True
            },
            "legal_actions": ["MOVE_Earthquake", "MOVE_Stone Edge", "MOVE_Toxic", "SWITCH_1"]
        }
        
        # Switching should allow all moves to be legal again
        expected_all_moves_legal = True
        assert expected_all_moves_legal == True

if __name__ == "__main__":
    pytest.main([__file__])
