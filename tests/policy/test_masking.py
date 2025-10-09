"""
Test policy service masking and fallback logic
"""

import pytest
import sys
import os

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'policy'))

from main import PolicyService, LegalAction, CalcResult

def test_illegal_action_masking():
    """Test that illegal actions are properly masked"""
    service = PolicyService()
    
    # Create test calc results with illegal actions
    calc_results = [
        CalcResult(
            action={"type": "move", "move": "shadowball", "disabled": True},
            accuracy=100,
            speedCheck={"faster": True, "speedDiff": 20},
            priority=0
        ),
        CalcResult(
            action={"type": "move", "move": "earthquake"},
            accuracy=100,
            speedCheck={"faster": False, "speedDiff": -10},
            priority=0
        ),
        CalcResult(
            action={"type": "switch", "pokemon": 7},  # Invalid pokemon index
            accuracy=100,
            speedCheck={"faster": False, "speedDiff": 0},
            priority=0
        )
    ]
    
    # Apply masking
    masked_results = service.apply_action_masking(calc_results)
    
    # Check that illegal actions are masked
    assert len(masked_results) == 3
    
    # First action should be masked (disabled)
    assert masked_results[0].expectedGain == -float('inf')
    assert masked_results[0].expectedSurvival == 0
    
    # Second action should not be masked
    assert masked_results[1].expectedGain != -float('inf')
    
    # Third action should be masked (invalid pokemon)
    assert masked_results[2].expectedGain == -float('inf')
    assert masked_results[2].expectedSurvival == 0

def test_invalid_result_detection():
    """Test detection of invalid results (NaN, None)"""
    service = PolicyService()
    
    # Test NaN detection
    import math
    
    result_with_nan = CalcResult(
        action={"type": "move", "move": "shadowball"},
        accuracy=float('nan'),
        speedCheck={"faster": True, "speedDiff": 20},
        priority=0
    )
    
    assert service.is_invalid_result(result_with_nan) == True
    
    # Test None result
    assert service.is_invalid_result(None) == True
    
    # Test valid result
    valid_result = CalcResult(
        action={"type": "move", "move": "shadowball"},
        accuracy=100,
        speedCheck={"faster": True, "speedDiff": 20},
        priority=0
    )
    
    assert service.is_invalid_result(valid_result) == False

def test_fallback_action_selection():
    """Test fallback action selection when model fails"""
    service = PolicyService()
    
    # Test with empty results
    empty_results = []
    fallback = service.get_fallback_action(empty_results)
    assert fallback == {"type": "pass"}
    
    # Test with move actions
    move_results = [
        CalcResult(
            action={"type": "move", "move": "shadowball"},
            accuracy=100,
            speedCheck={"faster": True, "speedDiff": 20},
            priority=0
        ),
        CalcResult(
            action={"type": "switch", "pokemon": 0},
            accuracy=100,
            speedCheck={"faster": False, "speedDiff": 0},
            priority=0
        )
    ]
    
    fallback = service.get_fallback_action(move_results)
    assert fallback["type"] == "move"
    assert fallback["move"] == "shadowball"
    
    # Test with only switch actions
    switch_results = [
        CalcResult(
            action={"type": "switch", "pokemon": 0},
            accuracy=100,
            speedCheck={"faster": False, "speedDiff": 0},
            priority=0
        )
    ]
    
    fallback = service.get_fallback_action(switch_results)
    assert fallback["type"] == "switch"
    assert fallback["pokemon"] == 0

def test_action_score_calculation():
    """Test action score calculation"""
    service = PolicyService()
    
    # Create a result with good stats
    good_result = CalcResult(
        action={"type": "move", "move": "shadowball"},
        damage={"min": 80, "max": 95, "average": 87.5, "ohko": 0.8, "twohko": 0.9},
        accuracy=100,
        speedCheck={"faster": True, "speedDiff": 20},
        expectedGain=10,
        expectedSurvival=0.9,
        priority=0
    )
    
    score = service.calculate_action_score(good_result)
    assert score > 0
    
    # Create a result with poor stats
    poor_result = CalcResult(
        action={"type": "move", "move": "splash"},
        damage={"min": 0, "max": 0, "average": 0, "ohko": 0, "twohko": 0},
        accuracy=100,
        speedCheck={"faster": False, "speedDiff": -20},
        expectedGain=-5,
        expectedSurvival=0.1,
        priority=0
    )
    
    score = service.calculate_action_score(poor_result)
    assert score < 0

def test_model_prediction_with_masking():
    """Test model prediction with masking applied"""
    service = PolicyService()
    
    # Create test features
    features = {
        "turn": 1,
        "phase": "battle",
        "p1_hp": 100,
        "p1_maxhp": 100,
        "p2_hp": 100,
        "p2_maxhp": 100,
        "calc_results": []
    }
    
    # Create calc results with mixed legal/illegal actions
    calc_results = [
        CalcResult(
            action={"type": "move", "move": "shadowball", "disabled": True},
            accuracy=100,
            speedCheck={"faster": True, "speedDiff": 20},
            priority=0
        ),
        CalcResult(
            action={"type": "move", "move": "earthquake"},
            damage={"min": 60, "max": 70, "average": 65, "ohko": 0, "twohko": 0.5},
            accuracy=100,
            speedCheck={"faster": False, "speedDiff": -10},
            expectedGain=5,
            expectedSurvival=0.8,
            priority=0
        )
    ]
    
    # Get prediction
    action, probability, reasoning, confidence = service.model_predict(features, calc_results)
    
    # Should return the legal action (earthquake)
    assert action["type"] == "move"
    assert action["move"] == "earthquake"
    assert probability > 0
    assert confidence > 0
    assert len(reasoning) > 0

def test_model_prediction_with_all_invalid():
    """Test model prediction when all results are invalid"""
    service = PolicyService()
    
    # Create test features
    features = {
        "turn": 1,
        "phase": "battle",
        "calc_results": []
    }
    
    # Create calc results with all invalid actions
    calc_results = [
        CalcResult(
            action={"type": "move", "move": "shadowball", "disabled": True},
            accuracy=float('nan'),
            speedCheck={"faster": True, "speedDiff": 20},
            priority=0
        )
    ]
    
    # Get prediction
    action, probability, reasoning, confidence = service.model_predict(features, calc_results)
    
    # Should return fallback action
    assert action["type"] == "pass"
    assert probability >= 0
    assert confidence >= 0
    assert "Fallback" in reasoning

if __name__ == "__main__":
    test_illegal_action_masking()
    test_invalid_result_detection()
    test_fallback_action_selection()
    test_action_score_calculation()
    test_model_prediction_with_masking()
    test_model_prediction_with_all_invalid()
    print("All policy masking tests passed!")
