from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
import json
import logging
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PokéAI Policy Service", version="1.0.0")

# Load format configuration
format_config = None
try:
    config_path = Path(__file__).parent.parent.parent / "config" / "formats" / "gen9ou.yaml"
    with open(config_path, 'r') as f:
        format_config = yaml.safe_load(f)
    logger.info(f"Loaded format config: {format_config.get('format')} v{format_config.get('version')}")
except Exception as e:
    logger.warning(f"Could not load format config, using defaults: {e}")
    format_config = {
        "format": "gen9ou",
        "version": "1.0.0",
        "dexVersion": "1.0.0"
    }

# Pydantic models for request/response
class LegalAction(BaseModel):
    type: str
    target: Optional[str] = None
    move: Optional[str] = None
    pokemon: Optional[int] = None
    teraType: Optional[str] = None
    disabled: Optional[bool] = False
    reason: Optional[str] = None

class CalcResult(BaseModel):
    action: LegalAction
    damage: Optional[Dict[str, float]] = None
    accuracy: float
    speedCheck: Dict[str, Any]
    hazardDamage: Optional[float] = None
    statusChance: Optional[float] = None
    expectedSurvival: Optional[float] = None
    expectedGain: Optional[float] = None
    priority: int

class PolicyRequest(BaseModel):
    battleState: Dict[str, Any]
    calcResults: List[CalcResult]

class PolicyResponse(BaseModel):
    action: LegalAction
    probability: float
    reasoning: str
    confidence: float

class PolicyService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_model()
    
    def load_model(self):
        """Load the transformer model for policy decisions"""
        try:
            # This would load a pre-trained model in a real implementation
            # For now, we'll use a placeholder
            logger.info("Loading policy model...")
            # self.model = AutoModel.from_pretrained("path/to/policy/model")
            # self.tokenizer = AutoTokenizer.from_pretrained("path/to/policy/model")
            logger.info("Policy model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict_action(self, battle_state: Dict[str, Any], calc_results: List[CalcResult]) -> PolicyResponse:
        """Predict the optimal action based on battle state and calc results"""
        try:
            # Convert battle state to features
            features = self.extract_features(battle_state, calc_results)
            
            # Get model prediction (placeholder implementation)
            action, probability, reasoning, confidence = self.model_predict(features, calc_results)
            
            return PolicyResponse(
                action=action,
                probability=probability,
                reasoning=reasoning,
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def extract_features(self, battle_state: Dict[str, Any], calc_results: List[CalcResult]) -> Dict[str, Any]:
        """Extract features from battle state for model input"""
        features = {
            "turn": battle_state.get("turn", 0),
            "phase": battle_state.get("phase", "battle"),
            "p1_hp": battle_state.get("p1", {}).get("active", {}).get("hp", 0),
            "p1_maxhp": battle_state.get("p1", {}).get("active", {}).get("maxhp", 0),
            "p2_hp": battle_state.get("p2", {}).get("active", {}).get("hp", 0),
            "p2_maxhp": battle_state.get("p2", {}).get("active", {}).get("maxhp", 0),
            "weather": battle_state.get("field", {}).get("weather", {}).get("type", None),
            "terrain": battle_state.get("field", {}).get("terrain", {}).get("type", None),
            "hazards": battle_state.get("p2", {}).get("side", {}).get("hazards", {}),
            "screens": battle_state.get("p2", {}).get("side", {}).get("screens", {}),
            "calc_results": []
        }
        
        # Add calc results features
        for result in calc_results:
            calc_features = {
                "action_type": result.action.type,
                "accuracy": result.accuracy,
                "priority": result.priority,
                "speed_faster": result.speedCheck.get("faster", False),
                "speed_diff": result.speedCheck.get("speedDiff", 0),
                "hazard_damage": result.hazardDamage or 0,
                "expected_survival": result.expectedSurvival or 0,
                "expected_gain": result.expectedGain or 0
            }
            
            if result.damage:
                calc_features.update({
                    "damage_min": result.damage.get("min", 0),
                    "damage_max": result.damage.get("max", 0),
                    "damage_avg": result.damage.get("average", 0),
                    "ohko_chance": result.damage.get("ohko", 0),
                    "twohko_chance": result.damage.get("twohko", 0)
                })
            
            features["calc_results"].append(calc_features)
        
        return features
    
    def model_predict(self, features: Dict[str, Any], calc_results: List[CalcResult]) -> tuple:
        """Get model prediction with masking and fallback logic"""
        # Apply masking to illegal actions
        masked_results = self.apply_action_masking(calc_results)
        
        # Check for NaN or invalid results
        if not masked_results or all(self.is_invalid_result(r) for r in masked_results):
            logger.warning("All results are invalid, using fallback")
            return self.get_fallback_action(calc_results)
        
        # Find the action with the highest expected gain
        best_action = None
        best_score = -float('inf')
        best_reasoning = ""
        
        for result in masked_results:
            if self.is_invalid_result(result):
                continue
                
            score = self.calculate_action_score(result)
            
            if score > best_score:
                best_score = score
                best_action = result.action
                best_reasoning = self.generate_reasoning(result)
        
        if best_action is None:
            # Fallback to first available action
            best_action = self.get_fallback_action(calc_results)
            best_reasoning = "Fallback action selected"
            best_score = 0
        
        # Convert score to probability (0-1 range)
        probability = min(1.0, max(0.0, (best_score + 100) / 200))
        confidence = min(1.0, probability * 1.2)
        
        return best_action, probability, best_reasoning, confidence
    
    def apply_action_masking(self, calc_results: List[CalcResult]) -> List[CalcResult]:
        """Apply masking to illegal actions"""
        masked_results = []
        
        for result in calc_results:
            # Check if action is illegal
            if self.is_illegal_action(result.action):
                # Set score to -inf (effectively removing from consideration)
                result.expectedGain = -float('inf')
                result.expectedSurvival = 0
                logger.debug(f"Masked illegal action: {result.action.type}")
            
            masked_results.append(result)
        
        return masked_results
    
    def is_illegal_action(self, action: LegalAction) -> bool:
        """Check if an action is illegal"""
        # Check for disabled actions
        if hasattr(action, 'disabled') and action.disabled:
            return True
        
        # Check for actions with 0 PP
        if action.type == 'move' and action.move:
            # This would check move PP in a real implementation
            pass
        
        # Check for invalid targets
        if action.type == 'switch' and isinstance(action.pokemon, int):
            if action.pokemon < 0 or action.pokemon >= 6:
                return True
        
        return False
    
    def is_invalid_result(self, result: CalcResult) -> bool:
        """Check if a result is invalid (NaN, None, etc.)"""
        if result is None:
            return True
        
        # Check for NaN values
        if result.accuracy is not None and (result.accuracy != result.accuracy):  # NaN check
            return True
        
        if result.expectedGain is not None and (result.expectedGain != result.expectedGain):
            return True
        
        if result.expectedSurvival is not None and (result.expectedSurvival != result.expectedSurvival):
            return True
        
        return False
    
    def calculate_action_score(self, result: CalcResult) -> float:
        """Calculate score for an action"""
        score = 0
        
        # Damage-based scoring
        if result.damage:
            score += result.damage.get("average", 0) * 0.1
            score += result.damage.get("ohko", 0) * 100
            score += result.damage.get("twohko", 0) * 50
        
        # Accuracy bonus
        if result.accuracy is not None:
            score += result.accuracy * 0.01
        
        # Speed advantage
        if result.speedCheck.get("faster", False):
            score += 10
        
        # Expected gain
        if result.expectedGain is not None:
            score += result.expectedGain * 5
        
        # Survival bonus
        if result.expectedSurvival is not None:
            score += result.expectedSurvival * 20
        
        # Penalty for hazard damage
        if result.hazardDamage:
            score -= result.hazardDamage * 0.5
        
        return score
    
    def get_fallback_action(self, calc_results: List[CalcResult]) -> LegalAction:
        """Get fallback action when model fails"""
        if not calc_results:
            return {"type": "pass"}
        
        # Prefer moves over switches
        move_actions = [r for r in calc_results if r.action.type == "move"]
        if move_actions:
            return move_actions[0].action
        
        # Then switches
        switch_actions = [r for r in calc_results if r.action.type == "switch"]
        if switch_actions:
            return switch_actions[0].action
        
        # Ultimate fallback
        return {"type": "pass"}
    
    def generate_reasoning(self, result: CalcResult) -> str:
        """Generate human-readable reasoning for the action"""
        reasoning_parts = []
        
        if result.damage:
            if result.damage.get("ohko", 0) > 0.5:
                reasoning_parts.append("High OHKO chance")
            elif result.damage.get("twohko", 0) > 0.5:
                reasoning_parts.append("Good 2HKO potential")
            elif result.damage.get("average", 0) > 50:
                reasoning_parts.append("Solid damage output")
        
        if result.speedCheck.get("faster", False):
            reasoning_parts.append("Speed advantage")
        
        if result.expectedSurvival and result.expectedSurvival > 0.8:
            reasoning_parts.append("Safe play")
        
        if result.hazardDamage and result.hazardDamage > 20:
            reasoning_parts.append("Risk of hazard damage")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Standard play"

# Initialize the policy service
policy_service = PolicyService()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "pokeai-policy",
        "format": format_config.get("format", "gen9ou"),
        "formatVersion": format_config.get("version", "1.0.0"),
        "dexVersion": format_config.get("dexVersion", "1.0.0")
    }

@app.post("/policy", response_model=PolicyResponse)
async def get_policy(request: PolicyRequest):
    """Get policy recommendation for the current battle state"""
    try:
        # Format gating - only support gen9ou for now
        requested_format = getattr(request, 'format', 'gen9ou')
        if requested_format != 'gen9ou':
            raise HTTPException(
                status_code=501, 
                detail={
                    "error": "Format not implemented",
                    "supportedFormats": ["gen9ou"],
                    "requestedFormat": requested_format
                }
            )
        logger.info(f"Policy request for battle {request.battleState.get('id', 'unknown')}")
        
        response = policy_service.predict_action(
            request.battleState,
            request.calcResults
        )
        
        logger.info(f"Policy recommendation: {response.action.type} (confidence: {response.confidence:.2f})")
        return response
        
    except Exception as e:
        logger.error(f"Policy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-policy")
async def get_batch_policy(requests: List[PolicyRequest]):
    """Get policy recommendations for multiple battle states"""
    try:
        responses = []
        for request in requests:
            response = policy_service.predict_action(
                request.battleState,
                request.calcResults
            )
            responses.append(response)
        return responses
    except Exception as e:
        logger.error(f"Batch policy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
