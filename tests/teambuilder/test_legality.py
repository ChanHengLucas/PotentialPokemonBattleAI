"""
Test team builder legality checks
"""

import pytest
from services.teambuilder.main import TeamBuilderService, Pokemon, Team

def test_species_clause():
    """Test species clause enforcement"""
    service = TeamBuilderService()
    
    # Valid team (no duplicates)
    valid_team = [
        Pokemon(species="Dragapult", ability="Clear Body", moves=["Shadow Ball"]),
        Pokemon(species="Garchomp", ability="Rough Skin", moves=["Earthquake"]),
        Pokemon(species="Landorus-Therian", ability="Intimidate", moves=["Earthquake"]),
        Pokemon(species="Heatran", ability="Flash Fire", moves=["Magma Storm"]),
        Pokemon(species="Rotom-Wash", ability="Levitate", moves=["Volt Switch"]),
        Pokemon(species="Toxapex", ability="Regenerator", moves=["Scald"])
    ]
    
    assert service.check_species_clause(valid_team) == True
    
    # Invalid team (duplicate species)
    invalid_team = valid_team.copy()
    invalid_team[1] = Pokemon(species="Dragapult", ability="Clear Body", moves=["Shadow Ball"])
    
    assert service.check_species_clause(invalid_team) == False

def test_illegal_combos():
    """Test detection of illegal move/ability/item combinations"""
    service = TeamBuilderService()
    
    # Test illegal ability combinations
    illegal_pokemon = Pokemon(
        species="Dragapult",
        ability="Intimidate",  # Dragapult doesn't have Intimidate
        moves=["Shadow Ball"],
        item="Choice Specs"
    )
    
    # This would be caught by the legality checker
    assert not service.is_legal_pokemon(illegal_pokemon, "gen9ou")
    
    # Test illegal move combinations
    illegal_moves_pokemon = Pokemon(
        species="Dragapult",
        ability="Clear Body",
        moves=[],  # No moves
        item="Choice Specs"
    )
    
    assert not service.is_legal_pokemon(illegal_moves_pokemon, "gen9ou")

def test_role_coverage():
    """Test role coverage detection"""
    service = TeamBuilderService()
    
    # Create a team with good role coverage
    team = Team(
        pokemon=[
            Pokemon(species="Dragapult", ability="Clear Body", moves=["Shadow Ball"]),
            Pokemon(species="Garchomp", ability="Rough Skin", moves=["Earthquake"]),
            Pokemon(species="Landorus-Therian", ability="Intimidate", moves=["Stealth Rock"]),
            Pokemon(species="Heatran", ability="Flash Fire", moves=["Magma Storm"]),
            Pokemon(species="Rotom-Wash", ability="Levitate", moves=["Volt Switch"]),
            Pokemon(species="Toxapex", ability="Regenerator", moves=["Scald"])
        ],
        format="gen9ou"
    )
    
    role_coverage = service.check_role_coverage(team.pokemon)
    
    # Should have all basic roles covered
    assert "hazard_setter" in role_coverage
    assert "hazard_removal" in role_coverage
    assert "speed_control" in role_coverage
    assert "win_condition" in role_coverage

def test_team_validation():
    """Test complete team validation"""
    service = TeamBuilderService()
    
    # Valid team
    valid_team = Team(
        pokemon=[
            Pokemon(species="Dragapult", ability="Clear Body", moves=["Shadow Ball", "Dragon Pulse"]),
            Pokemon(species="Garchomp", ability="Rough Skin", moves=["Earthquake", "Dragon Claw"]),
            Pokemon(species="Landorus-Therian", ability="Intimidate", moves=["Earthquake", "U-turn"]),
            Pokemon(species="Heatran", ability="Flash Fire", moves=["Magma Storm", "Earth Power"]),
            Pokemon(species="Rotom-Wash", ability="Levitate", moves=["Volt Switch", "Hydro Pump"]),
            Pokemon(species="Toxapex", ability="Regenerator", moves=["Scald", "Toxic"])
        ],
        format="gen9ou"
    )
    
    assert service.validate_team_schema(valid_team) == True
    
    # Invalid team (wrong number of Pokémon)
    invalid_team = Team(
        pokemon=valid_team.pokemon[:5],  # Only 5 Pokémon
        format="gen9ou"
    )
    
    assert service.validate_team_schema(invalid_team) == False
    
    # Invalid team (missing required fields)
    invalid_team2 = Team(
        pokemon=[
            Pokemon(species="Dragapult", ability="", moves=[]),  # Missing ability and moves
            Pokemon(species="Garchomp", ability="Rough Skin", moves=["Earthquake"]),
            Pokemon(species="Landorus-Therian", ability="Intimidate", moves=["Earthquake"]),
            Pokemon(species="Heatran", ability="Flash Fire", moves=["Magma Storm"]),
            Pokemon(species="Rotom-Wash", ability="Levitate", moves=["Volt Switch"]),
            Pokemon(species="Toxapex", ability="Regenerator", moves=["Scald"])
        ],
        format="gen9ou"
    )
    
    assert service.validate_team_schema(invalid_team2) == False

if __name__ == "__main__":
    test_species_clause()
    test_illegal_combos()
    test_role_coverage()
    test_team_validation()
    print("All legality tests passed!")
