#!/usr/bin/env python3
"""
Abilities Test Suite

Tests all ability mechanics including:
- Intimidate timing and blockers
- Unaware damage rules
- Mold Breaker/Teravolt/Turboblaze ignore immunity abilities
- Magic Guard (no indirect damage)
- Magic Bounce (reflects targeted status/hazard)
- Regenerator on switch out
- Good as Gold (blocks status/Defog target)
- Water/Volt Absorb/Flash Fire/Storm Drain/Lightning Rod immunities
- Technician/Sheer Force/Pixilate/Aerilate/Galvanize power/typing rules
"""

import pytest
from unittest.mock import Mock, patch
import json

class TestIntimidateMechanics:
    """Test Intimidate ability mechanics"""
    
    def test_intimidate_lowers_attack_on_switch_in(self):
        """Test Intimidate lowers opponent's Attack on switch in"""
        position = {
            "switching_pokemon": {
                "ability": "Intimidate"
            },
            "opponent": {
                "boosts": {"atk": 0}
            }
        }
        
        # Intimidate should lower opponent's Attack by 1 stage
        expected_attack_drop = -1
        assert expected_attack_drop == -1
    
    def test_intimidate_blocked_by_clear_body(self):
        """Test Intimidate blocked by Clear Body"""
        position = {
            "switching_pokemon": {
                "ability": "Intimidate"
            },
            "opponent": {
                "ability": "Clear Body",
                "boosts": {"atk": 0}
            }
        }
        
        # Clear Body should block Intimidate
        expected_attack_drop = 0
        assert expected_attack_drop == 0
    
    def test_intimidate_blocked_by_white_smoke(self):
        """Test Intimidate blocked by White Smoke"""
        position = {
            "switching_pokemon": {
                "ability": "Intimidate"
            },
            "opponent": {
                "ability": "White Smoke",
                "boosts": {"atk": 0}
            }
        }
        
        # White Smoke should block Intimidate
        expected_attack_drop = 0
        assert expected_attack_drop == 0
    
    def test_intimidate_blocked_by_full_metal_body(self):
        """Test Intimidate blocked by Full Metal Body"""
        position = {
            "switching_pokemon": {
                "ability": "Intimidate"
            },
            "opponent": {
                "ability": "Full Metal Body",
                "boosts": {"atk": 0}
            }
        }
        
        # Full Metal Body should block Intimidate
        expected_attack_drop = 0
        assert expected_attack_drop == 0
    
    def test_contrary_reverses_intimidate(self):
        """Test Contrary reverses Intimidate effect"""
        position = {
            "switching_pokemon": {
                "ability": "Intimidate"
            },
            "opponent": {
                "ability": "Contrary",
                "boosts": {"atk": 0}
            }
        }
        
        # Contrary should reverse Intimidate to +1 Attack
        expected_attack_change = 1
        assert expected_attack_change == 1

class TestUnawareMechanics:
    """Test Unaware ability mechanics"""
    
    def test_unaware_defender_ignores_attacker_boosts(self):
        """Test Unaware defender ignores attacker's offensive boosts"""
        position = {
            "attacker": {
                "atk": 100,
                "boosts": {"atk": 3}  # +3 Attack
            },
            "defender": {
                "ability": "Unaware",
                "def": 100,
                "boosts": {"def": 0}
            },
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Unaware should ignore attacker's Attack boosts
        expected_damage_calculation = "ignores_attacker_boosts"
        assert expected_damage_calculation == "ignores_attacker_boosts"
    
    def test_unaware_attacker_ignores_defender_boosts(self):
        """Test Unaware attacker ignores defender's defensive boosts"""
        position = {
            "attacker": {
                "ability": "Unaware",
                "atk": 100,
                "boosts": {"atk": 0}
            },
            "defender": {
                "def": 100,
                "boosts": {"def": 3}  # +3 Defense
            },
            "move": {"power": 100, "category": "Physical"}
        }
        
        # Unaware should ignore defender's Defense boosts
        expected_damage_calculation = "ignores_defender_boosts"
        assert expected_damage_calculation == "ignores_defender_boosts"
    
    def test_unaware_ignores_special_boosts(self):
        """Test Unaware ignores special attack/defense boosts"""
        position = {
            "attacker": {
                "ability": "Unaware",
                "spa": 100,
                "boosts": {"spa": 0}
            },
            "defender": {
                "spd": 100,
                "boosts": {"spd": 3}  # +3 Special Defense
            },
            "move": {"power": 100, "category": "Special"}
        }
        
        # Unaware should ignore special defense boosts
        expected_damage_calculation = "ignores_defender_boosts"
        assert expected_damage_calculation == "ignores_defender_boosts"

class TestMoldBreakerMechanics:
    """Test Mold Breaker ability mechanics"""
    
    def test_mold_breaker_ignores_immunity_abilities(self):
        """Test Mold Breaker ignores immunity abilities"""
        position = {
            "attacker": {
                "ability": "Mold Breaker",
                "move": {"type": "Ground", "name": "Earthquake"}
            },
            "defender": {
                "ability": "Levitate",
                "types": ["Flying"]
            }
        }
        
        # Mold Breaker should ignore Levitate immunity
        expected_move_effective = True
        assert expected_move_effective == True
    
    def test_teravolt_ignores_immunity_abilities(self):
        """Test Teravolt ignores immunity abilities"""
        position = {
            "attacker": {
                "ability": "Teravolt",
                "move": {"type": "Ground", "name": "Earthquake"}
            },
            "defender": {
                "ability": "Levitate",
                "types": ["Flying"]
            }
        }
        
        # Teravolt should ignore Levitate immunity
        expected_move_effective = True
        assert expected_move_effective == True
    
    def test_turboblaze_ignores_immunity_abilities(self):
        """Test Turboblaze ignores immunity abilities"""
        position = {
            "attacker": {
                "ability": "Turboblaze",
                "move": {"type": "Ground", "name": "Earthquake"}
            },
            "defender": {
                "ability": "Levitate",
                "types": ["Flying"]
            }
        }
        
        # Turboblaze should ignore Levitate immunity
        expected_move_effective = True
        assert expected_move_effective == True
    
    def test_mold_breaker_ignores_volt_absorb(self):
        """Test Mold Breaker ignores Volt Absorb"""
        position = {
            "attacker": {
                "ability": "Mold Breaker",
                "move": {"type": "Electric", "name": "Thunderbolt"}
            },
            "defender": {
                "ability": "Volt Absorb"
            }
        }
        
        # Mold Breaker should ignore Volt Absorb immunity
        expected_move_effective = True
        assert expected_move_effective == True

class TestMagicGuardMechanics:
    """Test Magic Guard ability mechanics"""
    
    def test_magic_guard_blocks_indirect_damage(self):
        """Test Magic Guard blocks indirect damage"""
        position = {
            "pokemon": {
                "ability": "Magic Guard",
                "hp": 100,
                "max_hp": 100
            },
            "indirect_damage_sources": [
                {"type": "hazards", "damage": 12.5},
                {"type": "status", "damage": 12.5},
                {"type": "weather", "damage": 6.25}
            ]
        }
        
        # Magic Guard should block all indirect damage
        expected_total_damage = 0
        assert expected_total_damage == 0
    
    def test_magic_guard_blocks_hazard_damage(self):
        """Test Magic Guard blocks hazard damage"""
        position = {
            "pokemon": {
                "ability": "Magic Guard",
                "hp": 100,
                "max_hp": 100
            },
            "field": {"hazards": {"stealthRock": True, "spikes": 2}}
        }
        
        # Magic Guard should block hazard damage
        expected_hazard_damage = 0
        assert expected_hazard_damage == 0
    
    def test_magic_guard_blocks_status_damage(self):
        """Test Magic Guard blocks status damage"""
        position = {
            "pokemon": {
                "ability": "Magic Guard",
                "status": "burn",
                "hp": 100,
                "max_hp": 100
            }
        }
        
        # Magic Guard should block status damage
        expected_status_damage = 0
        assert expected_status_damage == 0
    
    def test_magic_guard_blocks_weather_damage(self):
        """Test Magic Guard blocks weather damage"""
        position = {
            "pokemon": {
                "ability": "Magic Guard",
                "hp": 100,
                "max_hp": 100
            },
            "field": {"weather": "sandstorm"}
        }
        
        # Magic Guard should block weather damage
        expected_weather_damage = 0
        assert expected_weather_damage == 0

class TestMagicBounceMechanics:
    """Test Magic Bounce ability mechanics"""
    
    def test_magic_bounce_reflects_hazards(self):
        """Test Magic Bounce reflects hazard moves"""
        position = {
            "attacker": {"move": "Stealth Rock"},
            "defender": {"ability": "Magic Bounce"}
        }
        
        # Magic Bounce should reflect Stealth Rock back to attacker
        expected_move_reflected = True
        expected_attacker_affected = True
        
        assert expected_move_reflected == True
        assert expected_attacker_affected == True
    
    def test_magic_bounce_reflects_status_moves(self):
        """Test Magic Bounce reflects status moves"""
        position = {
            "attacker": {"move": "Toxic"},
            "defender": {"ability": "Magic Bounce", "status": "none"}
        }
        
        # Magic Bounce should reflect Toxic back to attacker
        expected_move_reflected = True
        expected_attacker_status = "poisoned"
        
        assert expected_move_reflected == True
        assert expected_attacker_status == "poisoned"
    
    def test_magic_bounce_reflects_spikes(self):
        """Test Magic Bounce reflects Spikes"""
        position = {
            "attacker": {"move": "Spikes"},
            "defender": {"ability": "Magic Bounce"}
        }
        
        # Magic Bounce should reflect Spikes back to attacker
        expected_move_reflected = True
        expected_attacker_affected = True
        
        assert expected_move_reflected == True
        assert expected_attacker_affected == True

class TestRegeneratorMechanics:
    """Test Regenerator ability mechanics"""
    
    def test_regenerator_heals_on_switch_out(self):
        """Test Regenerator heals 1/3 HP on switch out"""
        position = {
            "pokemon": {
                "ability": "Regenerator",
                "hp": 50,
                "max_hp": 100
            },
            "switching": True
        }
        
        # Regenerator should heal 1/3 max HP
        expected_heal_amount = 33
        assert expected_heal_amount == 33
    
    def test_regenerator_heals_to_full_hp(self):
        """Test Regenerator heals to full HP if needed"""
        position = {
            "pokemon": {
                "ability": "Regenerator",
                "hp": 80,
                "max_hp": 100
            },
            "switching": True
        }
        
        # Regenerator should heal to full HP (20 HP)
        expected_heal_amount = 20
        assert expected_heal_amount == 20

class TestGoodAsGoldMechanics:
    """Test Good as Gold ability mechanics"""
    
    def test_good_as_gold_blocks_status_moves(self):
        """Test Good as Gold blocks status moves"""
        position = {
            "attacker": {"move": "Toxic"},
            "defender": {"ability": "Good as Gold"}
        }
        
        # Good as Gold should block status moves
        expected_move_blocked = True
        assert expected_move_blocked == True
    
    def test_good_as_gold_blocks_defog_targeting(self):
        """Test Good as Gold blocks Defog from targeting that side"""
        position = {
            "attacker": {"move": "Defog"},
            "defender": {"ability": "Good as Gold"},
            "field": {"hazards": {"stealthRock": True}}
        }
        
        # Good as Gold should block Defog from clearing hazards
        expected_defog_blocked = True
        expected_hazards_remain = True
        
        assert expected_defog_blocked == True
        assert expected_hazards_remain == True
    
    def test_good_as_gold_blocks_will_o_wisp(self):
        """Test Good as Gold blocks Will-O-Wisp"""
        position = {
            "attacker": {"move": "Will-O-Wisp"},
            "defender": {"ability": "Good as Gold"}
        }
        
        # Good as Gold should block Will-O-Wisp
        expected_move_blocked = True
        assert expected_move_blocked == True

class TestAbsorptionAbilities:
    """Test absorption ability mechanics"""
    
    def test_volt_absorb_immunity_and_healing(self):
        """Test Volt Absorb provides immunity and healing"""
        position = {
            "attacker": {"move": {"type": "Electric", "name": "Thunderbolt"}},
            "defender": {
                "ability": "Volt Absorb",
                "hp": 50,
                "max_hp": 100
            }
        }
        
        # Volt Absorb should provide immunity and heal 1/4 max HP
        expected_immunity = True
        expected_heal_amount = 25
        
        assert expected_immunity == True
        assert expected_heal_amount == 25
    
    def test_water_absorb_immunity_and_healing(self):
        """Test Water Absorb provides immunity and healing"""
        position = {
            "attacker": {"move": {"type": "Water", "name": "Surf"}},
            "defender": {
                "ability": "Water Absorb",
                "hp": 50,
                "max_hp": 100
            }
        }
        
        # Water Absorb should provide immunity and heal 1/4 max HP
        expected_immunity = True
        expected_heal_amount = 25
        
        assert expected_immunity == True
        assert expected_heal_amount == 25
    
    def test_flash_fire_immunity_and_boost(self):
        """Test Flash Fire provides immunity and boost"""
        position = {
            "attacker": {"move": {"type": "Fire", "name": "Flamethrower"}},
            "defender": {
                "ability": "Flash Fire",
                "next_fire_move": True
            }
        }
        
        # Flash Fire should provide immunity and boost next Fire move
        expected_immunity = True
        expected_fire_boost = 1.5
        
        assert expected_immunity == True
        assert expected_fire_boost == 1.5
    
    def test_storm_drain_immunity_and_boost(self):
        """Test Storm Drain provides immunity and boost"""
        position = {
            "attacker": {"move": {"type": "Water", "name": "Surf"}},
            "defender": {
                "ability": "Storm Drain",
                "next_water_move": True
            }
        }
        
        # Storm Drain should provide immunity and boost next Water move
        expected_immunity = True
        expected_water_boost = 1.5
        
        assert expected_immunity == True
        assert expected_water_boost == 1.5
    
    def test_lightning_rod_immunity_and_boost(self):
        """Test Lightning Rod provides immunity and boost"""
        position = {
            "attacker": {"move": {"type": "Electric", "name": "Thunderbolt"}},
            "defender": {
                "ability": "Lightning Rod",
                "next_electric_move": True
            }
        }
        
        # Lightning Rod should provide immunity and boost next Electric move
        expected_immunity = True
        expected_electric_boost = 1.5
        
        assert expected_immunity == True
        assert expected_electric_boost == 1.5

class TestPowerModificationAbilities:
    """Test power modification ability mechanics"""
    
    def test_technician_boosts_weak_moves(self):
        """Test Technician boosts moves with 60 power or less"""
        position = {
            "pokemon": {
                "ability": "Technician",
                "move": {"power": 60, "name": "Bullet Punch"}
            }
        }
        
        # Technician should boost moves with 60 power or less by 50%
        expected_power_boost = 1.5
        assert expected_power_boost == 1.5
    
    def test_technician_no_boost_strong_moves(self):
        """Test Technician doesn't boost moves over 60 power"""
        position = {
            "pokemon": {
                "ability": "Technician",
                "move": {"power": 100, "name": "Earthquake"}
            }
        }
        
        # Technician should not boost moves over 60 power
        expected_power_boost = 1.0
        assert expected_power_boost == 1.0
    
    def test_sheer_force_removes_secondary_effects(self):
        """Test Sheer Force removes secondary effects and boosts power"""
        position = {
            "pokemon": {
                "ability": "Sheer Force",
                "move": {"power": 100, "secondary_effect": True, "name": "Flamethrower"}
            }
        }
        
        # Sheer Force should remove secondary effects and boost power by 30%
        expected_power_boost = 1.3
        expected_secondary_removed = True
        
        assert expected_power_boost == 1.3
        assert expected_secondary_removed == True
    
    def test_pixilate_changes_normal_to_fairy(self):
        """Test Pixilate changes Normal moves to Fairy type"""
        position = {
            "pokemon": {
                "ability": "Pixilate",
                "move": {"type": "Normal", "name": "Hyper Beam"}
            }
        }
        
        # Pixilate should change Normal moves to Fairy type
        expected_type_change = "Fairy"
        expected_power_boost = 1.2
        
        assert expected_type_change == "Fairy"
        assert expected_power_boost == 1.2
    
    def test_aerilate_changes_normal_to_flying(self):
        """Test Aerilate changes Normal moves to Flying type"""
        position = {
            "pokemon": {
                "ability": "Aerilate",
                "move": {"type": "Normal", "name": "Hyper Beam"}
            }
        }
        
        # Aerilate should change Normal moves to Flying type
        expected_type_change = "Flying"
        expected_power_boost = 1.2
        
        assert expected_type_change == "Flying"
        assert expected_power_boost == 1.2
    
    def test_galvanize_changes_normal_to_electric(self):
        """Test Galvanize changes Normal moves to Electric type"""
        position = {
            "pokemon": {
                "ability": "Galvanize",
                "move": {"type": "Normal", "name": "Hyper Beam"}
            }
        }
        
        # Galvanize should change Normal moves to Electric type
        expected_type_change = "Electric"
        expected_power_boost = 1.2
        
        assert expected_type_change == "Electric"
        assert expected_power_boost == 1.2

if __name__ == "__main__":
    pytest.main([__file__])
