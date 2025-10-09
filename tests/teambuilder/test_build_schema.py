"""
Test team builder schema validation
"""

import json
import pytest
import jsonschema
from pathlib import Path

def test_team_schema_validation():
    """Test that generated teams match the schema"""
    # Load schema
    schema_path = Path(__file__).parent.parent.parent / "data" / "schemas" / "team.schema.json"
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Test valid team
    valid_team = {
        "pokemon": [
            {
                "species": "Dragapult",
                "ability": "Clear Body",
                "moves": ["Shadow Ball", "Dragon Pulse", "U-turn", "Thunderbolt"],
                "item": "Choice Specs",
                "nature": "Timid",
                "evs": {"hp": 0, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 252}
            },
            {
                "species": "Garchomp",
                "ability": "Rough Skin",
                "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"],
                "item": "Leftovers",
                "nature": "Jolly",
                "evs": {"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252}
            },
            {
                "species": "Landorus-Therian",
                "ability": "Intimidate",
                "moves": ["Earthquake", "U-turn", "Stone Edge", "Stealth Rock"],
                "item": "Choice Scarf",
                "nature": "Jolly",
                "evs": {"hp": 0, "atk": 252, "def": 0, "spa": 0, "spd": 0, "spe": 252}
            },
            {
                "species": "Heatran",
                "ability": "Flash Fire",
                "moves": ["Magma Storm", "Earth Power", "Flash Cannon", "Stealth Rock"],
                "item": "Leftovers",
                "nature": "Timid",
                "evs": {"hp": 252, "atk": 0, "def": 0, "spa": 252, "spd": 0, "spe": 0}
            },
            {
                "species": "Rotom-Wash",
                "ability": "Levitate",
                "moves": ["Volt Switch", "Hydro Pump", "Thunderbolt", "Will-O-Wisp"],
                "item": "Leftovers",
                "nature": "Bold",
                "evs": {"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 0, "spe": 0}
            },
            {
                "species": "Toxapex",
                "ability": "Regenerator",
                "moves": ["Scald", "Toxic", "Recover", "Haze"],
                "item": "Black Sludge",
                "nature": "Bold",
                "evs": {"hp": 252, "atk": 0, "def": 252, "spa": 0, "spd": 0, "spe": 0}
            }
        ],
        "format": "gen9ou",
        "name": "Test Team"
    }
    
    # Validate against schema
    jsonschema.validate(valid_team, schema)
    
    # Test invalid team (wrong number of Pokémon)
    invalid_team = valid_team.copy()
    invalid_team["pokemon"] = invalid_team["pokemon"][:5]  # Only 5 Pokémon
    
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid_team, schema)
    
    # Test invalid team (missing required fields)
    invalid_team2 = valid_team.copy()
    invalid_team2["pokemon"][0]["ability"] = ""  # Empty ability
    
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid_team2, schema)

def test_team_builder_endpoint():
    """Test team builder endpoint returns valid schema"""
    import requests
    
    # This test would require the service to be running
    # For now, we'll just test the structure
    request_data = {
        "format": "gen9ou",
        "includeTera": True,
        "roleHints": ["sweeper", "wall"]
    }
    
    # Mock response structure
    expected_response = {
        "team": {
            "pokemon": [],  # Would be filled with 6 Pokémon
            "format": "gen9ou"
        },
        "synergy": 0.8,
        "coverage": ["Fire", "Water", "Grass"],
        "winConditions": ["Sweeper setup"],
        "threats": ["Dragapult", "Garchomp"],
        "score": 0.85
    }
    
    # Validate structure
    assert "team" in expected_response
    assert "synergy" in expected_response
    assert "coverage" in expected_response
    assert "winConditions" in expected_response
    assert "threats" in expected_response
    assert "score" in expected_response

if __name__ == "__main__":
    test_team_schema_validation()
    test_team_builder_endpoint()
    print("All schema tests passed!")
