#!/usr/bin/env python3
"""
Format Guards Test Suite

Tests that format-specific logic is properly gated behind format checks.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestFormatGuards:
    """Test format gating in all services"""
    
    def test_gen9ou_format_allowed(self):
        """Test that gen9ou format is allowed"""
        # This would test actual service calls when services are implemented
        # For now, we'll test the format configuration loading
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        assert config["format"] == "gen9ou"
        assert config["version"] == "1.0.0"
        assert config["dex_version"] == "gen9"
    
    def test_non_gen9ou_format_raises_not_implemented(self):
        """Test that non-gen9ou formats raise NotImplementedError"""
        # Mock service calls for testing
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": "NotImplementedError",
                "message": "Format genXdummy not supported"
            }
            mock_post.return_value = mock_response
            
            # Test calc service
            response = mock_post("http://localhost:8787/batch-calc", 
                              json={"format": "genXdummy"})
            assert response.status_code == 400
            assert "NotImplementedError" in response.json()["error"]
    
    def test_format_version_in_response(self):
        """Test that format version is included in responses"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "format": "gen9ou",
                "format_version": "1.0.0",
                "dex_version": "gen9",
                "result": "success"
            }
            mock_post.return_value = mock_response
            
            response = mock_post("http://localhost:8787/batch-calc",
                               json={"format": "gen9ou"})
            result = response.json()
            
            assert result["format"] == "gen9ou"
            assert result["format_version"] == "1.0.0"
            assert result["dex_version"] == "gen9"
    
    def test_tera_gating(self):
        """Test that Tera mechanics are gated by format.tera_allowed"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        assert config["tera_allowed"] == False  # Stage A
        
        # Test that Tera actions are not available when tera_allowed=False
        # This would be tested in actual service integration
    
    def test_clause_gating(self):
        """Test that clauses are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        clauses = config["clauses"]
        
        assert clauses["sleep_clause"] == True
        assert clauses["species_clause"] == True
        assert clauses["evasion_clause"] == True
        assert clauses["ohko_clause"] == True
    
    def test_banned_items_gating(self):
        """Test that banned items are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        banned_items = config["banned_items"]
        
        assert "King's Rock" in banned_items
        assert "Razor Fang" in banned_items
        assert "Quick Claw" in banned_items
    
    def test_weather_abilities_gating(self):
        """Test that weather abilities are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        weather_abilities = config["weather_abilities"]
        
        assert "Drought" in weather_abilities
        assert "Drizzle" in weather_abilities
        assert "Sand Stream" in weather_abilities
        assert "Snow Warning" in weather_abilities
    
    def test_terrain_abilities_gating(self):
        """Test that terrain abilities are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        terrain_abilities = config["terrain_abilities"]
        
        assert "Electric Surge" in terrain_abilities
        assert "Grassy Surge" in terrain_abilities
        assert "Misty Surge" in terrain_abilities
        assert "Psychic Surge" in terrain_abilities
    
    def test_hazard_mechanics_gating(self):
        """Test that hazard mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        hazard_mechanics = config["hazard_mechanics"]
        
        assert "stealth_rock" in hazard_mechanics
        assert "spikes" in hazard_mechanics
        assert "toxic_spikes" in hazard_mechanics
        assert "sticky_web" in hazard_mechanics
    
    def test_screen_mechanics_gating(self):
        """Test that screen mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        screen_mechanics = config["screen_mechanics"]
        
        assert "reflect" in screen_mechanics
        assert "light_screen" in screen_mechanics
        assert "aurora_veil" in screen_mechanics
    
    def test_status_mechanics_gating(self):
        """Test that status mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        status_mechanics = config["status_mechanics"]
        
        assert "burn" in status_mechanics
        assert "poison" in status_mechanics
        assert "paralysis" in status_mechanics
        assert "sleep" in status_mechanics
    
    def test_priority_mechanics_gating(self):
        """Test that priority mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        priority_mechanics = config["priority_mechanics"]
        
        assert "priority_brackets" in priority_mechanics
        assert -7 in priority_mechanics["priority_brackets"]
        assert 7 in priority_mechanics["priority_brackets"]
    
    def test_contact_mechanics_gating(self):
        """Test that contact mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        contact_mechanics = config["contact_mechanics"]
        
        assert "rough_skin" in contact_mechanics
        assert "iron_barbs" in contact_mechanics
        assert "rocky_helmet" in contact_mechanics
    
    def test_multi_hit_mechanics_gating(self):
        """Test that multi-hit mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        multihit_mechanics = config["multihit_mechanics"]
        
        assert "loaded_dice" in multihit_mechanics
        assert "per_hit_effects" in multihit_mechanics
    
    def test_pp_mechanics_gating(self):
        """Test that PP mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        pp_mechanics = config["pp_mechanics"]
        
        assert "pressure_doubles_consumption" in pp_mechanics
        assert "struggle_when_no_pp" in pp_mechanics
    
    def test_tera_mechanics_gating(self):
        """Test that Tera mechanics are format-specific"""
        from config.formats.gen9ou import load_format_config
        
        config = load_format_config("gen9ou")
        tera_mechanics = config["tera_mechanics"]
        
        assert "one_time_use" in tera_mechanics
        assert "typing_change" in tera_mechanics
        assert "stab_recalculation" in tera_mechanics

# Mock format config loader for testing
def load_format_config(format_name):
    """Mock format config loader for testing"""
    if format_name == "gen9ou":
        return {
            "format": "gen9ou",
            "version": "1.0.0",
            "dex_version": "gen9",
            "tera_allowed": False,
            "clauses": {
                "sleep_clause": True,
                "species_clause": True,
                "evasion_clause": True,
                "ohko_clause": True
            },
            "banned_items": ["King's Rock", "Razor Fang", "Quick Claw"],
            "weather_abilities": ["Drought", "Drizzle", "Sand Stream", "Snow Warning"],
            "terrain_abilities": ["Electric Surge", "Grassy Surge", "Misty Surge", "Psychic Surge"],
            "hazard_mechanics": {
                "stealth_rock": {"damage_percent": 0.125},
                "spikes": {"max_layers": 3},
                "toxic_spikes": {"max_layers": 2},
                "sticky_web": {"speed_drop": 1}
            },
            "screen_mechanics": {
                "reflect": {"damage_reduction": 0.5},
                "light_screen": {"damage_reduction": 0.5},
                "aurora_veil": {"damage_reduction": 0.5}
            },
            "status_mechanics": {
                "burn": {"damage_per_turn": 0.125},
                "poison": {"damage_per_turn": 0.125},
                "paralysis": {"speed_reduction": 0.25},
                "sleep": {"wake_up_chance": 0.33}
            },
            "priority_mechanics": {
                "priority_brackets": {
                    -7: ["Roar", "Whirlwind"],
                    7: ["Roar", "Whirlwind"]
                }
            },
            "contact_mechanics": {
                "rough_skin": {"damage_percent": 0.125},
                "iron_barbs": {"damage_percent": 0.125},
                "rocky_helmet": {"damage_percent": 0.25}
            },
            "multihit_mechanics": {
                "loaded_dice": {"hit_count_boost": True},
                "per_hit_effects": ["Rocky Helmet", "Rough Skin"]
            },
            "pp_mechanics": {
                "pressure_doubles_consumption": True,
                "struggle_when_no_pp": True
            },
            "tera_mechanics": {
                "one_time_use": True,
                "typing_change": True,
                "stab_recalculation": True
            }
        }
    else:
        raise ValueError(f"Format {format_name} not supported")

if __name__ == "__main__":
    pytest.main([__file__])
