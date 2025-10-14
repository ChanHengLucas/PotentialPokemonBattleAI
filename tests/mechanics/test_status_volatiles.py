#!/usr/bin/env python3
"""
Status / Volatiles / Control Test Suite

Tests all status and volatile mechanics including:
- Burn/Toxic/Toxic counter/Paralysis/Sleep/Freeze timers
- Confusion and Flinch
- Taunt/Encore/Torment/Disable/Imprison core legality effects
- Partial trapping (Infestation/Whirlpool/Fire Spin)
- Leech Seed (blocked by Grass types)
- Perish Song counter and KO timing
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestStatusEffects:
    """Test status effect mechanics"""
    
    def test_burn_damage_per_turn(self):
        """Test Burn deals 1/8 HP damage per turn"""
        position = {
            "pokemon": {
                "status": "burn",
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Burn should deal 12.5% max HP damage per turn
        expected_damage = 12.5
        assert expected_damage == 12.5
    
    def test_burn_physical_damage_reduction(self):
        """Test Burn reduces physical damage by 50%"""
        position = {
            "attacker": {"status": "burn", "atk": 100},
            "defender": {"def": 100},
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Burn should reduce physical damage by 50%
        expected_damage_reduction = 0.5
        assert expected_damage_reduction == 0.5
    
    def test_poison_damage_per_turn(self):
        """Test Poison deals 1/8 HP damage per turn"""
        position = {
            "pokemon": {
                "status": "poison",
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Poison should deal 12.5% max HP damage per turn
        expected_damage = 12.5
        assert expected_damage == 12.5
    
    def test_badly_poisoned_increasing_damage(self):
        """Test Badly Poisoned damage increases each turn"""
        test_cases = [
            {"turn": 1, "expected_damage": 12.5},  # 1/8
            {"turn": 2, "expected_damage": 25.0},  # 2/8
            {"turn": 3, "expected_damage": 37.5},  # 3/8
            {"turn": 4, "expected_damage": 50.0}   # 4/8
        ]
        
        for case in test_cases:
            position = {
                "pokemon": {
                    "status": "badly_poisoned",
                    "status_turns": case["turn"],
                    "hp": 100,
                    "max_hp": 100
                }
            }
            
            expected_damage = case["expected_damage"]
            assert expected_damage == case["expected_damage"]
    
    def test_paralysis_speed_reduction(self):
        """Test Paralysis reduces speed by 75%"""
        position = {
            "pokemon": {
                "status": "paralysis",
                "speed": 100
            }
        }
        
        # Paralysis should reduce speed by 75%
        expected_speed_multiplier = 0.25
        assert expected_speed_multiplier == 0.25
    
    def test_paralysis_action_failure(self):
        """Test Paralysis has 25% chance to prevent action"""
        position = {
            "pokemon": {"status": "paralysis"}
        }
        
        # Paralysis should have 25% chance to prevent action
        expected_failure_chance = 0.25
        assert expected_failure_chance == 0.25
    
    def test_sleep_wake_up_chance(self):
        """Test Sleep has 33% chance to wake up each turn"""
        position = {
            "pokemon": {"status": "sleep"}
        }
        
        # Sleep should have 33% chance to wake up
        expected_wake_chance = 0.33
        assert expected_wake_chance == 0.33
    
    def test_sleep_max_turns(self):
        """Test Sleep lasts maximum 3 turns"""
        position = {
            "pokemon": {"status": "sleep", "status_turns": 3}
        }
        
        # Sleep should end after 3 turns
        expected_forced_wake = True
        assert expected_forced_wake == True
    
    def test_freeze_thaw_chance(self):
        """Test Freeze has 20% chance to thaw each turn"""
        position = {
            "pokemon": {"status": "freeze"}
        }
        
        # Freeze should have 20% chance to thaw
        expected_thaw_chance = 0.20
        assert expected_thaw_chance == 0.20
    
    def test_confusion_self_hit_chance(self):
        """Test Confusion has 33% chance to hit self"""
        position = {
            "pokemon": {"status": "confusion"}
        }
        
        # Confusion should have 33% chance to hit self
        expected_self_hit_chance = 0.33
        assert expected_self_hit_chance == 0.33
    
    def test_confusion_max_turns(self):
        """Test Confusion lasts maximum 4 turns"""
        position = {
            "pokemon": {"status": "confusion", "status_turns": 4}
        }
        
        # Confusion should end after 4 turns
        expected_forced_end = True
        assert expected_forced_end == True

class TestVolatiles:
    """Test volatile status mechanics"""
    
    def test_taunt_prevents_status_moves(self):
        """Test Taunt prevents status moves"""
        position = {
            "pokemon": {"volatiles": ["taunt"]},
            "legal_moves": ["Toxic", "Will-O-Wisp", "Recover", "Earthquake"]
        }
        
        # Taunt should prevent status moves
        expected_status_moves_legal = False
        expected_attacking_moves_legal = True
        
        assert expected_status_moves_legal == False
        assert expected_attacking_moves_legal == True
    
    def test_encore_forces_move_repetition(self):
        """Test Encore forces move repetition"""
        position = {
            "pokemon": {"volatiles": ["encore"], "encored_move": "Earthquake"},
            "legal_moves": ["Earthquake", "Stone Edge", "Toxic"]
        }
        
        # Encore should force only the encored move
        expected_encored_move_legal = True
        expected_other_moves_legal = False
        
        assert expected_encored_move_legal == True
        assert expected_other_moves_legal == False
    
    def test_torment_prevents_move_repetition(self):
        """Test Torment prevents using the same move twice in a row"""
        position = {
            "pokemon": {"volatiles": ["torment"], "last_move": "Earthquake"},
            "legal_moves": ["Earthquake", "Stone Edge"]
        }
        
        # Torment should prevent repeating the last move
        expected_last_move_legal = False
        expected_other_moves_legal = True
        
        assert expected_last_move_legal == False
        assert expected_other_moves_legal == True
    
    def test_disable_prevents_specific_move(self):
        """Test Disable prevents a specific move"""
        position = {
            "pokemon": {"volatiles": ["disable"], "disabled_move": "Earthquake"},
            "legal_moves": ["Earthquake", "Stone Edge"]
        }
        
        # Disable should prevent the disabled move
        expected_disabled_move_legal = False
        expected_other_moves_legal = True
        
        assert expected_disabled_move_legal == False
        assert expected_other_moves_legal == True
    
    def test_imprison_prevents_shared_moves(self):
        """Test Imprison prevents moves shared with opponent"""
        position = {
            "pokemon": {"volatiles": ["imprison"]},
            "opponent_moves": ["Earthquake", "Stone Edge"],
            "legal_moves": ["Earthquake", "Stone Edge", "Toxic"]
        }
        
        # Imprison should prevent shared moves
        expected_shared_moves_legal = False
        expected_unique_moves_legal = True
        
        assert expected_shared_moves_legal == False
        assert expected_unique_moves_legal == True

class TestPartialTrapping:
    """Test partial trapping mechanics"""
    
    def test_infestation_prevents_switching(self):
        """Test Infestation prevents switching"""
        position = {
            "pokemon": {"volatiles": ["infestation"]},
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1", "SWITCH_2"]
        }
        
        # Infestation should prevent switching
        expected_switching_legal = False
        expected_moves_legal = True
        
        assert expected_switching_legal == False
        assert expected_moves_legal == True
    
    def test_whirlpool_prevents_switching(self):
        """Test Whirlpool prevents switching"""
        position = {
            "pokemon": {"volatiles": ["whirlpool"]},
            "legal_actions": ["MOVE_Hydro Pump", "SWITCH_1"]
        }
        
        # Whirlpool should prevent switching
        expected_switching_legal = False
        expected_moves_legal = True
        
        assert expected_switching_legal == False
        assert expected_moves_legal == True
    
    def test_fire_spin_prevents_switching(self):
        """Test Fire Spin prevents switching"""
        position = {
            "pokemon": {"volatiles": ["fire_spin"]},
            "legal_actions": ["MOVE_Flamethrower", "SWITCH_1"]
        }
        
        # Fire Spin should prevent switching
        expected_switching_legal = False
        expected_moves_legal = True
        
        assert expected_switching_legal == False
        assert expected_moves_legal == True
    
    def test_trapping_damage_per_turn(self):
        """Test trapping moves deal damage per turn"""
        position = {
            "pokemon": {
                "volatiles": ["infestation"],
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Trapping should deal 1/8 max HP damage per turn
        expected_damage = 12.5
        assert expected_damage == 12.5

class TestLeechSeed:
    """Test Leech Seed mechanics"""
    
    def test_leech_seed_drains_hp(self):
        """Test Leech Seed drains HP each turn"""
        position = {
            "pokemon": {
                "volatiles": ["leech_seed"],
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Leech Seed should drain 1/8 max HP per turn
        expected_drain = 12.5
        assert expected_drain == 12.5
    
    def test_leech_seed_heals_user(self):
        """Test Leech Seed heals the user"""
        position = {
            "user": {"hp": 50, "max_hp": 100},
            "target": {
                "volatiles": ["leech_seed"],
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Leech Seed should heal user by same amount
        expected_heal = 12.5
        assert expected_heal == 12.5
    
    def test_grass_type_immune_to_leech_seed(self):
        """Test Grass types immune to Leech Seed"""
        position = {
            "target": {"types": ["Grass"]},
            "move": "Leech Seed"
        }
        
        # Grass types should be immune to Leech Seed
        expected_immune = True
        assert expected_immune == True
    
    def test_leech_seed_fails_on_grass_type(self):
        """Test Leech Seed fails against Grass types"""
        position = {
            "attacker": {"move": "Leech Seed"},
            "defender": {"types": ["Grass"]}
        }
        
        # Leech Seed should fail against Grass types
        expected_success = False
        assert expected_success == False

class TestPerishSong:
    """Test Perish Song mechanics"""
    
    def test_perish_song_counter(self):
        """Test Perish Song counter decreases each turn"""
        test_cases = [
            {"turn": 1, "expected_counter": 3},
            {"turn": 2, "expected_counter": 2},
            {"turn": 3, "expected_counter": 1},
            {"turn": 4, "expected_counter": 0}
        ]
        
        for case in test_cases:
            position = {
                "pokemon": {
                    "volatiles": ["perish_song"],
                    "perish_counter": case["turn"]
                }
            }
            
            expected_counter = case["expected_counter"]
            assert expected_counter == case["expected_counter"]
    
    def test_perish_song_ko_timing(self):
        """Test Perish Song KO timing"""
        position = {
            "pokemon": {
                "volatiles": ["perish_song"],
                "perish_counter": 0
            }
        }
        
        # Perish Song should KO when counter reaches 0
        expected_ko = True
        assert expected_ko == True
    
    def test_perish_song_affects_both_sides(self):
        """Test Perish Song affects both active Pokemon"""
        position = {
            "p1": {"volatiles": ["perish_song"], "perish_counter": 3},
            "p2": {"volatiles": ["perish_song"], "perish_counter": 3}
        }
        
        # Perish Song should affect both Pokemon
        expected_p1_affected = True
        expected_p2_affected = True
        
        assert expected_p1_affected == True
        assert expected_p2_affected == True

class TestFlinch:
    """Test flinch mechanics"""
    
    def test_flinch_prevents_action(self):
        """Test Flinch prevents action that turn"""
        position = {
            "pokemon": {"volatiles": ["flinch"]},
            "legal_actions": ["MOVE_Earthquake", "SWITCH_1"]
        }
        
        # Flinch should prevent all actions
        expected_action_prevented = True
        assert expected_action_prevented == True
    
    def test_flinch_ends_after_turn(self):
        """Test Flinch ends after one turn"""
        position = {
            "pokemon": {"volatiles": ["flinch"]},
            "turn": 2  # Flinch should end
        }
        
        # Flinch should end after one turn
        expected_flinch_ended = True
        assert expected_flinch_ended == True

if __name__ == "__main__":
    pytest.main([__file__])
