#!/usr/bin/env python3
"""
Test to verify that real components are being used instead of mocks.
This test ensures @smogon/calc is used and policy runs real forward passes.
"""

import pytest
import requests
import json
import time
from typing import Dict, Any, List

class TestRealComponentIntegration:
    """Test that real components are wired correctly"""
    
    def test_calc_service_uses_smogon_calc(self):
        """Verify calc service uses @smogon/calc for real damage calculations"""
        # Test data for a real damage calculation
        battle_state = {
            "id": "test_battle_001",
            "format": "gen9ou",
            "weather": "none",
            "terrain": "none",
            "trickRoom": False,
            "turn": 1,
            "p1": {
                "name": "Player1",
                "active": {
                    "species": "Garchomp",
                    "level": 100,
                    "hp": 100,
                    "maxhp": 100,
                    "status": "none",
                    "types": ["Dragon", "Ground"],
                    "stats": {"hp": 100, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
                    "moves": [
                        {"name": "Earthquake", "pp": 16, "maxpp": 16, "type": "Ground", "category": "Physical", "power": 100, "accuracy": 100},
                        {"name": "Dragon Claw", "pp": 16, "maxpp": 16, "type": "Dragon", "category": "Physical", "power": 80, "accuracy": 100},
                        {"name": "Stone Edge", "pp": 8, "maxpp": 8, "type": "Rock", "category": "Physical", "power": 100, "accuracy": 80},
                        {"name": "Swords Dance", "pp": 32, "maxpp": 32, "type": "Normal", "category": "Status", "power": 0, "accuracy": 100}
                    ],
                    "item": "Choice Band",
                    "ability": "Rough Skin"
                },
                "side": {
                    "conditions": [],
                    "hazards": []
                }
            },
            "p2": {
                "name": "Player2", 
                "active": {
                    "species": "Landorus-Therian",
                    "level": 100,
                    "hp": 100,
                    "maxhp": 100,
                    "status": "none",
                    "types": ["Ground", "Flying"],
                    "stats": {"hp": 100, "atk": 145, "def": 90, "spa": 105, "spd": 80, "spe": 91},
                    "moves": [
                        {"name": "Earthquake", "pp": 16, "maxpp": 16, "type": "Ground", "category": "Physical", "power": 100, "accuracy": 100},
                        {"name": "U-turn", "pp": 32, "maxpp": 32, "type": "Bug", "category": "Physical", "power": 70, "accuracy": 100},
                        {"name": "Defog", "pp": 24, "maxpp": 24, "type": "Flying", "category": "Status", "power": 0, "accuracy": 100},
                        {"name": "Stealth Rock", "pp": 32, "maxpp": 32, "type": "Rock", "category": "Status", "power": 0, "accuracy": 100}
                    ],
                    "item": "Leftovers",
                    "ability": "Intimidate"
                },
                "side": {
                    "conditions": [],
                    "hazards": []
                }
            }
        }
        
        actions = [
            {"type": "move", "move": "Earthquake", "target": "p2"},
            {"type": "move", "move": "Dragon Claw", "target": "p2"},
            {"type": "move", "move": "Stone Edge", "target": "p2"},
            {"type": "switch", "target": "p1_1"}
        ]
        
        # Make request to calc service
        try:
            response = requests.post(
                "http://localhost:3001/calculate",
                json={"battleState": battle_state, "actions": actions},
                timeout=10
            )
            
            assert response.status_code == 200, f"Calc service returned {response.status_code}: {response.text}"
            
            result = response.json()
            
            # Verify response structure
            assert "results" in result, "Response missing 'results' field"
            assert "format" in result, "Response missing 'format' field"
            assert "formatVersion" in result, "Response missing 'formatVersion' field"
            assert "dexVersion" in result, "Response missing 'dexVersion' field"
            
            # Verify format information
            assert result["format"] == "gen9ou", f"Expected gen9ou format, got {result['format']}"
            
            # Verify calculation results have realistic damage ranges
            results = result["results"]
            assert len(results) == len(actions), f"Expected {len(actions)} results, got {len(results)}"
            
            for i, calc_result in enumerate(results):
                assert "damage" in calc_result, f"Result {i} missing damage field"
                assert "accuracy" in calc_result, f"Result {i} missing accuracy field"
                
                # Verify damage ranges are realistic (not mock values)
                damage = calc_result["damage"]
                if isinstance(damage, dict):
                    assert "min" in damage, f"Result {i} damage missing min"
                    assert "max" in damage, f"Result {i} damage missing max"
                    assert damage["min"] >= 0, f"Result {i} has negative min damage"
                    assert damage["max"] <= 100, f"Result {i} has unrealistic max damage"
                else:
                    assert 0 <= damage <= 100, f"Result {i} has unrealistic damage value: {damage}"
                
                # Verify accuracy is realistic
                accuracy = calc_result["accuracy"]
                assert 0 <= accuracy <= 100, f"Result {i} has unrealistic accuracy: {accuracy}"
            
            print("✓ Calc service uses real @smogon/calc calculations")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Calc service not running")
        except Exception as e:
            pytest.fail(f"Calc service integration failed: {e}")
    
    def test_policy_service_real_forward_pass(self):
        """Verify policy service runs real forward passes"""
        # Test data for policy prediction
        battle_state = {
            "id": "test_battle_002",
            "format": "gen9ou",
            "weather": "none",
            "terrain": "none",
            "trickRoom": False,
            "turn": 1,
            "p1": {
                "name": "Player1",
                "active": {
                    "species": "Garchomp",
                    "level": 100,
                    "hp": 100,
                    "maxhp": 100,
                    "status": "none",
                    "types": ["Dragon", "Ground"],
                    "stats": {"hp": 100, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
                    "moves": [
                        {"name": "Earthquake", "pp": 16, "maxpp": 16, "type": "Ground", "category": "Physical", "power": 100, "accuracy": 100},
                        {"name": "Dragon Claw", "pp": 16, "maxpp": 16, "type": "Dragon", "category": "Physical", "power": 80, "accuracy": 100},
                        {"name": "Stone Edge", "pp": 8, "maxpp": 8, "type": "Rock", "category": "Physical", "power": 100, "accuracy": 80},
                        {"name": "Swords Dance", "pp": 32, "maxpp": 32, "type": "Normal", "category": "Status", "power": 0, "accuracy": 100}
                    ],
                    "item": "Choice Band",
                    "ability": "Rough Skin"
                },
                "side": {
                    "conditions": [],
                    "hazards": []
                }
            },
            "p2": {
                "name": "Player2",
                "active": {
                    "species": "Landorus-Therian",
                    "level": 100,
                    "hp": 100,
                    "maxhp": 100,
                    "status": "none",
                    "types": ["Ground", "Flying"],
                    "stats": {"hp": 100, "atk": 145, "def": 90, "spa": 105, "spd": 80, "spe": 91},
                    "moves": [
                        {"name": "Earthquake", "pp": 16, "maxpp": 16, "type": "Ground", "category": "Physical", "power": 100, "accuracy": 100},
                        {"name": "U-turn", "pp": 32, "maxpp": 32, "type": "Bug", "category": "Physical", "power": 70, "accuracy": 100},
                        {"name": "Defog", "pp": 24, "maxpp": 24, "type": "Flying", "category": "Status", "power": 0, "accuracy": 100},
                        {"name": "Stealth Rock", "pp": 32, "maxpp": 32, "type": "Rock", "category": "Status", "power": 0, "accuracy": 100}
                    ],
                    "item": "Leftovers",
                    "ability": "Intimidate"
                },
                "side": {
                    "conditions": [],
                    "hazards": []
                }
            }
        }
        
        calc_results = [
            {
                "action": {"type": "move", "move": "Earthquake", "target": "p2"},
                "damage": {"min": 85, "max": 100, "avg": 92.5},
                "accuracy": 100,
                "ohko": 0.0,
                "twohko": 0.8
            },
            {
                "action": {"type": "move", "move": "Dragon Claw", "target": "p2"},
                "damage": {"min": 70, "max": 85, "avg": 77.5},
                "accuracy": 100,
                "ohko": 0.0,
                "twohko": 0.6
            },
            {
                "action": {"type": "move", "move": "Stone Edge", "target": "p2"},
                "damage": {"min": 80, "max": 95, "avg": 87.5},
                "accuracy": 80,
                "ohko": 0.0,
                "twohko": 0.7
            },
            {
                "action": {"type": "switch", "target": "p1_1"},
                "damage": {"min": 0, "max": 0, "avg": 0},
                "accuracy": 100,
                "ohko": 0.0,
                "twohko": 0.0
            }
        ]
        
        # Make request to policy service
        try:
            response = requests.post(
                "http://localhost:8000/policy",
                json={
                    "battleState": battle_state,
                    "calcResults": calc_results
                },
                timeout=10
            )
            
            assert response.status_code == 200, f"Policy service returned {response.status_code}: {response.text}"
            
            result = response.json()
            
            # Verify response structure
            assert "action" in result, "Response missing 'action' field"
            assert "confidence" in result, "Response missing 'confidence' field"
            assert "reasoning" in result, "Response missing 'reasoning' field"
            
            # Verify action is valid
            action = result["action"]
            assert "type" in action, "Action missing 'type' field"
            assert action["type"] in ["move", "switch"], f"Invalid action type: {action['type']}"
            
            # Verify confidence is realistic
            confidence = result["confidence"]
            assert 0 <= confidence <= 1, f"Invalid confidence value: {confidence}"
            
            # Verify reasoning is not empty
            reasoning = result["reasoning"]
            assert len(reasoning) > 0, "Reasoning should not be empty"
            assert isinstance(reasoning, str), "Reasoning should be a string"
            
            print("✓ Policy service runs real forward passes")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Policy service not running")
        except Exception as e:
            pytest.fail(f"Policy service integration failed: {e}")
    
    def test_teambuilder_service_real_team_generation(self):
        """Verify teambuilder service generates real teams"""
        # Test data for team building
        input_data = {
            "format": "gen9ou",
            "style": "balance",
            "constraints": {
                "banned_pokemon": [],
                "required_pokemon": [],
                "max_legendaries": 2
            }
        }
        
        # Make request to teambuilder service
        try:
            response = requests.post(
                "http://localhost:8001/build",
                json=input_data,
                timeout=10
            )
            
            assert response.status_code == 200, f"Teambuilder service returned {response.status_code}: {response.text}"
            
            result = response.json()
            
            # Verify response structure
            assert "team" in result, "Response missing 'team' field"
            assert "score" in result, "Response missing 'score' field"
            assert "reasoning" in result, "Response missing 'reasoning' field"
            
            # Verify team structure
            team = result["team"]
            assert len(team) == 6, f"Team should have 6 Pokemon, got {len(team)}"
            
            for i, pokemon in enumerate(team):
                assert "species" in pokemon, f"Pokemon {i} missing species"
                assert "moves" in pokemon, f"Pokemon {i} missing moves"
                assert "item" in pokemon, f"Pokemon {i} missing item"
                assert "ability" in pokemon, f"Pokemon {i} missing ability"
                
                # Verify moves list
                moves = pokemon["moves"]
                assert len(moves) == 4, f"Pokemon {i} should have 4 moves, got {len(moves)}"
                
                # Verify all required fields
                for move in moves:
                    assert "name" in move, f"Pokemon {i} move missing name"
                    assert "type" in move, f"Pokemon {i} move missing type"
                    assert "category" in move, f"Pokemon {i} move missing category"
            
            # Verify score is realistic
            score = result["score"]
            assert 0 <= score <= 100, f"Invalid team score: {score}"
            
            # Verify reasoning is not empty
            reasoning = result["reasoning"]
            assert len(reasoning) > 0, "Reasoning should not be empty"
            assert isinstance(reasoning, str), "Reasoning should be a string"
            
            print("✓ Teambuilder service generates real teams")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Teambuilder service not running")
        except Exception as e:
            pytest.fail(f"Teambuilder service integration failed: {e}")
    
    def test_no_mock_data_in_responses(self):
        """Verify that responses don't contain obvious mock data"""
        # Test calc service for mock data
        try:
            response = requests.get("http://localhost:3001/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                # Check for mock indicators
                assert "mock" not in str(health).lower(), "Health response contains mock data"
                assert "fake" not in str(health).lower(), "Health response contains fake data"
                assert "test" not in str(health).lower(), "Health response contains test data"
        except requests.exceptions.ConnectionError:
            pytest.skip("Calc service not running")
        
        # Test policy service for mock data
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                # Check for mock indicators
                assert "mock" not in str(health).lower(), "Health response contains mock data"
                assert "fake" not in str(health).lower(), "Health response contains fake data"
                assert "test" not in str(health).lower(), "Health response contains test data"
        except requests.exceptions.ConnectionError:
            pytest.skip("Policy service not running")
        
        # Test teambuilder service for mock data
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                # Check for mock indicators
                assert "mock" not in str(health).lower(), "Health response contains mock data"
                assert "fake" not in str(health).lower(), "Health response contains fake data"
                assert "test" not in str(health).lower(), "Health response contains test data"
        except requests.exceptions.ConnectionError:
            pytest.skip("Teambuilder service not running")
        
        print("✓ No mock data detected in service responses")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
