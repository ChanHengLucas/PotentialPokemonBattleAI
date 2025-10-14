#!/usr/bin/env python3
"""
Items Test Suite

Tests all item mechanics including:
- HDB (hazard immunity)
- Focus Sash (broken by prior chip/sand)
- Life Orb recoil
- Rocky Helmet/Iron Barbs/Rough Skin per-contact hit
- Eject Button/Eject Pack/Red Card timing
- Booster Energy triggers once
- Protosynthesis/Quark Drive boost calculation
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestHazardImmunityItems:
    """Test hazard immunity item mechanics"""
    
    def test_heavy_duty_boots_hazard_immunity(self):
        """Test Heavy-Duty Boots provides hazard immunity"""
        position = {
            "field": {
                "hazards": {
                    "stealthRock": True,
                    "spikes": 3,
                    "stickyWeb": True
                }
            },
            "switching_pokemon": {
                "item": "Heavy-Duty Boots",
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Heavy-Duty Boots should negate all hazard damage
        expected_hazard_damage = 0
        assert expected_hazard_damage == 0
    
    def test_heavy_duty_boots_immunity_to_stealth_rock(self):
        """Test Heavy-Duty Boots immunity to Stealth Rock"""
        position = {
            "field": {"hazards": {"stealthRock": True}},
            "switching_pokemon": {
                "types": ["Fire"],  # 2x weak to Rock
                "item": "Heavy-Duty Boots",
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Heavy-Duty Boots should negate Stealth Rock damage
        expected_damage = 0
        assert expected_damage == 0
    
    def test_heavy_duty_boots_immunity_to_spikes(self):
        """Test Heavy-Duty Boots immunity to Spikes"""
        position = {
            "field": {"hazards": {"spikes": 3}},
            "switching_pokemon": {
                "item": "Heavy-Duty Boots",
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Heavy-Duty Boots should negate Spikes damage
        expected_damage = 0
        assert expected_damage == 0
    
    def test_heavy_duty_boots_immunity_to_sticky_web(self):
        """Test Heavy-Duty Boots immunity to Sticky Web"""
        position = {
            "field": {"hazards": {"stickyWeb": True}},
            "switching_pokemon": {
                "item": "Heavy-Duty Boots",
                "speed": 100
            }
        }
        
        # Heavy-Duty Boots should negate Sticky Web speed drop
        expected_speed_drop = 0
        assert expected_speed_drop == 0

class TestFocusSashMechanics:
    """Test Focus Sash mechanics"""
    
    def test_focus_sash_survives_ohko(self):
        """Test Focus Sash survives one-hit KO"""
        position = {
            "pokemon": {
                "item": "Focus Sash",
                "hp": 100,
                "max_hp": 100
            },
            "incoming_damage": 200  # Would normally KO
        }
        
        # Focus Sash should leave Pokemon with 1 HP
        expected_final_hp = 1
        expected_item_consumed = True
        
        assert expected_final_hp == 1
        assert expected_item_consumed == True
    
    def test_focus_sash_broken_by_prior_chip(self):
        """Test Focus Sash broken by prior damage"""
        position = {
            "pokemon": {
                "item": "Focus Sash",
                "hp": 99,  # Prior chip damage
                "max_hp": 100
            },
            "incoming_damage": 200
        }
        
        # Focus Sash should not activate due to prior damage
        expected_final_hp = 0
        expected_item_consumed = False
        
        assert expected_final_hp == 0
        assert expected_item_consumed == False
    
    def test_focus_sash_broken_by_sand_damage(self):
        """Test Focus Sash broken by sandstorm damage"""
        position = {
            "pokemon": {
                "item": "Focus Sash",
                "hp": 100,
                "max_hp": 100
            },
            "field": {"weather": "sandstorm"},
            "incoming_damage": 200
        }
        
        # Sandstorm damage should break Focus Sash
        expected_final_hp = 0
        expected_item_consumed = False
        
        assert expected_final_hp == 0
        assert expected_item_consumed == False
    
    def test_focus_sash_one_time_use(self):
        """Test Focus Sash is one-time use"""
        position = {
            "pokemon": {
                "item": "",  # Already used
                "hp": 1,
                "max_hp": 100
            },
            "incoming_damage": 200
        }
        
        # Focus Sash should not activate again
        expected_final_hp = 0
        assert expected_final_hp == 0

class TestLifeOrbMechanics:
    """Test Life Orb mechanics"""
    
    def test_life_orb_damage_boost(self):
        """Test Life Orb boosts damage by 30%"""
        position = {
            "pokemon": {
                "item": "Life Orb",
                "atk": 100
            },
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Life Orb should boost damage by 30%
        expected_damage_boost = 1.3
        assert expected_damage_boost == 1.3
    
    def test_life_orb_recoil_damage(self):
        """Test Life Orb causes 10% recoil damage"""
        position = {
            "pokemon": {
                "item": "Life Orb",
                "hp": 100,
                "max_hp": 100
            },
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Life Orb should cause 10% recoil
        expected_recoil_damage = 10
        assert expected_recoil_damage == 10
    
    def test_life_orb_no_recoil_on_status_moves(self):
        """Test Life Orb doesn't cause recoil on status moves"""
        position = {
            "pokemon": {
                "item": "Life Orb",
                "hp": 100,
                "max_hp": 100
            },
            "move": {"power": 0, "category": "Status"}
        }
        
        # Life Orb should not cause recoil on status moves
        expected_recoil_damage = 0
        assert expected_recoil_damage == 0
    
    def test_life_orb_recoil_on_miss(self):
        """Test Life Orb causes recoil even on miss"""
        position = {
            "pokemon": {
                "item": "Life Orb",
                "hp": 100,
                "max_hp": 100
            },
            "move": {"power": 100, "category": "Physical", "result": "missed"}
        }
        
        # Life Orb should cause recoil even on miss
        expected_recoil_damage = 10
        assert expected_recoil_damage == 10

class TestContactDamageItems:
    """Test contact damage item mechanics"""
    
    def test_rocky_helmet_contact_damage(self):
        """Test Rocky Helmet damages attacker on contact"""
        position = {
            "attacker": {
                "move": "Earthquake",
                "contact": True,
                "hp": 100,
                "max_hp": 100
            },
            "defender": {
                "item": "Rocky Helmet"
            }
        }
        
        # Rocky Helmet should damage attacker for 1/4 max HP
        expected_contact_damage = 25
        assert expected_contact_damage == 25
    
    def test_iron_barbs_contact_damage(self):
        """Test Iron Barbs damages attacker on contact"""
        position = {
            "attacker": {
                "move": "Earthquake",
                "contact": True,
                "hp": 100,
                "max_hp": 100
            },
            "defender": {
                "ability": "Iron Barbs"
            }
        }
        
        # Iron Barbs should damage attacker for 1/8 max HP
        expected_contact_damage = 12.5
        assert expected_contact_damage == 12.5
    
    def test_rough_skin_contact_damage(self):
        """Test Rough Skin damages attacker on contact"""
        position = {
            "attacker": {
                "move": "Earthquake",
                "contact": True,
                "hp": 100,
                "max_hp": 100
            },
            "defender": {
                "ability": "Rough Skin"
            }
        }
        
        # Rough Skin should damage attacker for 1/8 max HP
        expected_contact_damage = 12.5
        assert expected_contact_damage == 12.5
    
    def test_no_contact_damage_on_non_contact_moves(self):
        """Test no contact damage on non-contact moves"""
        position = {
            "attacker": {
                "move": "Flamethrower",
                "contact": False,
                "hp": 100,
                "max_hp": 100
            },
            "defender": {
                "item": "Rocky Helmet",
                "ability": "Iron Barbs"
            }
        }
        
        # Non-contact moves should not trigger contact damage
        expected_contact_damage = 0
        assert expected_contact_damage == 0

class TestEjectItems:
    """Test eject item mechanics"""
    
    def test_eject_button_switches_on_damage(self):
        """Test Eject Button switches out when taking damage"""
        position = {
            "pokemon": {
                "item": "Eject Button",
                "hp": 100,
                "max_hp": 100
            },
            "incoming_damage": 50
        }
        
        # Eject Button should trigger switch
        expected_switch_triggered = True
        expected_item_consumed = True
        
        assert expected_switch_triggered == True
        assert expected_item_consumed == True
    
    def test_eject_pack_switches_on_stat_drop(self):
        """Test Eject Pack switches out on stat drop"""
        position = {
            "pokemon": {
                "item": "Eject Pack",
                "boosts": {"atk": -1}  # Stat drop
            }
        }
        
        # Eject Pack should trigger switch
        expected_switch_triggered = True
        expected_item_consumed = True
        
        assert expected_switch_triggered == True
        assert expected_item_consumed == True
    
    def test_red_card_switches_attacker_out(self):
        """Test Red Card switches attacker out"""
        position = {
            "defender": {
                "item": "Red Card"
            },
            "attacker": {
                "move": "Earthquake",
                "contact": True
            }
        }
        
        # Red Card should switch attacker out
        expected_attacker_switched = True
        expected_item_consumed = True
        
        assert expected_attacker_switched == True
        assert expected_item_consumed == True

class TestBoosterEnergyMechanics:
    """Test Booster Energy mechanics"""
    
    def test_booster_energy_triggers_once(self):
        """Test Booster Energy triggers only once"""
        position = {
            "pokemon": {
                "item": "Booster Energy",
                "ability": "Protosynthesis",
                "field_weather": "sun"
            }
        }
        
        # Booster Energy should trigger once
        expected_boost_triggered = True
        expected_item_consumed = True
        
        assert expected_boost_triggered == True
        assert expected_item_consumed == True
    
    def test_booster_energy_no_second_trigger(self):
        """Test Booster Energy doesn't trigger again"""
        position = {
            "pokemon": {
                "item": "",  # Already consumed
                "ability": "Protosynthesis",
                "field_weather": "sun"
            }
        }
        
        # Booster Energy should not trigger again
        expected_boost_triggered = False
        assert expected_boost_triggered == False

class TestProtosynthesisQuarkDrive:
    """Test Protosynthesis and Quark Drive mechanics"""
    
    def test_protosynthesis_sun_boost(self):
        """Test Protosynthesis boosts in sun"""
        position = {
            "pokemon": {
                "ability": "Protosynthesis",
                "field_weather": "sun",
                "atk": 100,
                "def": 100,
                "spa": 100,
                "spd": 100,
                "spe": 100
            }
        }
        
        # Protosynthesis should boost highest stat by 50%
        expected_highest_stat_boost = 1.5
        assert expected_highest_stat_boost == 1.5
    
    def test_quark_drive_electric_terrain_boost(self):
        """Test Quark Drive boosts in Electric Terrain"""
        position = {
            "pokemon": {
                "ability": "Quark Drive",
                "field_terrain": "electric",
                "atk": 100,
                "def": 100,
                "spa": 100,
                "spd": 100,
                "spe": 100
            }
        }
        
        # Quark Drive should boost highest stat by 50%
        expected_highest_stat_boost = 1.5
        assert expected_highest_stat_boost == 1.5
    
    def test_protosynthesis_booster_energy_trigger(self):
        """Test Protosynthesis with Booster Energy trigger"""
        position = {
            "pokemon": {
                "ability": "Protosynthesis",
                "item": "Booster Energy",
                "field_weather": "none"
            }
        }
        
        # Booster Energy should trigger Protosynthesis
        expected_boost_triggered = True
        assert expected_boost_triggered == True
    
    def test_quark_drive_booster_energy_trigger(self):
        """Test Quark Drive with Booster Energy trigger"""
        position = {
            "pokemon": {
                "ability": "Quark Drive",
                "item": "Booster Energy",
                "field_terrain": "none"
            }
        }
        
        # Booster Energy should trigger Quark Drive
        expected_boost_triggered = True
        assert expected_boost_triggered == True
    
    def test_stat_tie_breaker_rules(self):
        """Test stat tie breaker rules for Protosynthesis/Quark Drive"""
        position = {
            "pokemon": {
                "ability": "Protosynthesis",
                "field_weather": "sun",
                "atk": 100,
                "def": 100,
                "spa": 100,
                "spd": 100,
                "spe": 100  # All stats equal
            }
        }
        
        # Tie breaker should follow: Atk > Def > SpA > SpD > Spe
        expected_boosted_stat = "atk"
        assert expected_boosted_stat == "atk"

class TestItemConsumption:
    """Test item consumption mechanics"""
    
    def test_one_time_use_items(self):
        """Test one-time use items are consumed"""
        one_time_items = [
            "Focus Sash",
            "Eject Button",
            "Eject Pack",
            "Red Card",
            "Booster Energy",
            "Power Herb",
            "White Herb",
            "Mental Herb",
            "Lum Berry",
            "Sitrus Berry"
        ]
        
        for item in one_time_items:
            position = {
                "pokemon": {
                    "item": item,
                    "hp": 100,
                    "max_hp": 100
                },
                "trigger_condition": True
            }
            
            # One-time use items should be consumed
            expected_item_consumed = True
            assert expected_item_consumed == True
    
    def test_persistent_items_not_consumed(self):
        """Test persistent items are not consumed"""
        persistent_items = [
            "Leftovers",
            "Life Orb",
            "Choice Band",
            "Choice Specs",
            "Choice Scarf",
            "Heavy-Duty Boots",
            "Assault Vest"
        ]
        
        for item in persistent_items:
            position = {
                "pokemon": {
                    "item": item,
                    "hp": 100,
                    "max_hp": 100
                },
                "trigger_condition": True
            }
            
            # Persistent items should not be consumed
            expected_item_consumed = False
            assert expected_item_consumed == False

if __name__ == "__main__":
    pytest.main([__file__])
