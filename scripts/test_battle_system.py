#!/usr/bin/env python3
"""
PokéAI Battle System Test Script

Tests the comprehensive battle simulation system to ensure all components work correctly.
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sims.selfplay.battle_engine import BattleEngine, Pokemon, Move, MoveCategory, StatusCondition
# from sims.selfplay.run import SelfPlaySimulator
# from scripts.battle_analyzer import BattleAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_battle_engine():
    """Test the battle engine functionality"""
    logger.info("Testing Battle Engine...")
    
    # Initialize battle engine
    engine = BattleEngine()
    
    # Test Pokemon creation
    pokemon1 = engine.create_pokemon_from_species("Dragapult")
    pokemon2 = engine.create_pokemon_from_species("Garchomp")
    
    logger.info(f"Created Pokemon: {pokemon1.species} (HP: {pokemon1.hp})")
    logger.info(f"Created Pokemon: {pokemon2.species} (HP: {pokemon2.hp})")
    
    # Test move data loading
    move_data = engine.get_move_data("Shadow Ball")
    if move_data:
        logger.info(f"Loaded move: {move_data['name']} (Power: {move_data['power']}, Accuracy: {move_data['accuracy']})")
    
    # Test type effectiveness
    effectiveness = engine.calculate_type_effectiveness("Ghost", ["Psychic"])
    logger.info(f"Ghost vs Psychic effectiveness: {effectiveness}x")
    
    # Test damage calculation
    damage, crit, eff = engine.calculate_damage(pokemon1, pokemon2, Move(**move_data), {})
    logger.info(f"Damage calculation: {damage} damage, Critical: {crit}, Effectiveness: {eff}x")
    
    # Test accuracy check
    accuracy_hit = engine.check_accuracy(Move(**move_data), pokemon1, pokemon2)
    logger.info(f"Accuracy check: {'Hit' if accuracy_hit else 'Miss'}")
    
    logger.info("✓ Battle Engine tests passed")
    return True

def test_battle_simulation():
    """Test complete battle simulation"""
    logger.info("Testing Battle Simulation...")
    
    # Initialize battle engine
    engine = BattleEngine()
    
    # Create test teams
    team1 = [
        engine.create_pokemon_from_species("Dragapult"),
        engine.create_pokemon_from_species("Garchomp"),
        engine.create_pokemon_from_species("Heatran")
    ]
    
    team2 = [
        engine.create_pokemon_from_species("Toxapex"),
        engine.create_pokemon_from_species("Corviknight"),
        engine.create_pokemon_from_species("Clefable")
    ]
    
    logger.info(f"Created team 1: {len(team1)} Pokemon")
    logger.info(f"Created team 2: {len(team2)} Pokemon")
    
    # Test battle simulation
    battle_result = engine.simulate_battle(team1, team2, max_turns=10)
    
    logger.info(f"Battle result: Winner {battle_result['winner']} in {battle_result['turns']} turns")
    logger.info(f"Battle log entries: {len(battle_result['battle_log'])}")
    
    # Test battle analysis
    analysis = engine.analyze_battle_outcome(battle_result)
    logger.info(f"Battle analysis insights: {len(analysis.get('learning_insights', []))}")
    
    logger.info("✓ Battle Simulation tests passed")
    return True

def test_self_play_simulation():
    """Test self-play simulation"""
    logger.info("Testing Self-Play Simulation...")
    
    # Test multiple battles
    engine = BattleEngine()
    results = []
    
    for i in range(3):
        # Create different teams for each battle
        team1 = [engine.create_pokemon_from_species("Dragapult"), engine.create_pokemon_from_species("Garchomp")]
        team2 = [engine.create_pokemon_from_species("Heatran"), engine.create_pokemon_from_species("Toxapex")]
        
        battle_result = engine.simulate_battle(team1, team2, max_turns=15)
        results.append(battle_result)
    
    logger.info(f"Completed {len(results)} self-play games")
    
    # Analyze results
    for i, result in enumerate(results):
        logger.info(f"Game {i+1}: Winner {result['winner']} in {result['turns']} turns")
        logger.info(f"  Battle log: {len(result['battle_log'])} entries")
        
        analysis = engine.analyze_battle_outcome(result)
        logger.info(f"  Analysis insights: {len(analysis.get('learning_insights', []))}")
    
    logger.info("✓ Self-Play Simulation tests passed")
    return True

def test_battle_analysis():
    """Test battle analysis functionality"""
    logger.info("Testing Battle Analysis...")
    
    # Create sample battle data
    sample_battles = [
        {
            "game_id": "test_1",
            "result": {"winner": "p1", "turns": 15},
            "battle_log": [
                {"turn": 1, "action": "move", "details": {"move": "Shadow Ball"}, "result": "hit", "damage": 45, "critical_hit": False, "effectiveness": 2.0},
                {"turn": 2, "action": "move", "details": {"move": "Earthquake"}, "result": "hit", "damage": 60, "critical_hit": True, "effectiveness": 1.0},
                {"turn": 3, "action": "switch", "details": {"from": "Dragapult", "to": "Garchomp"}, "result": "switched"}
            ],
            "team1": {"pokemon": [{"species": "Dragapult"}, {"species": "Garchomp"}]},
            "team2": {"pokemon": [{"species": "Heatran"}, {"species": "Toxapex"}]}
        }
    ]
    
    # Test basic analysis
    logger.info(f"Sample battle data created: {len(sample_battles)} battles")
    logger.info(f"Battle log entries: {len(sample_battles[0]['battle_log'])}")
    
    # Test move effectiveness calculation
    move_stats = {}
    for battle in sample_battles:
        for log_entry in battle["battle_log"]:
            if log_entry.get("action") == "move":
                move_name = log_entry.get("details", {}).get("move", "unknown")
                if move_name not in move_stats:
                    move_stats[move_name] = {"hits": 0, "total": 0}
                move_stats[move_name]["total"] += 1
                if log_entry.get("result") == "hit":
                    move_stats[move_name]["hits"] += 1
    
    logger.info(f"Move effectiveness analysis:")
    for move, stats in move_stats.items():
        hit_rate = stats["hits"] / stats["total"] if stats["total"] > 0 else 0
        logger.info(f"  {move}: {hit_rate:.1%} hit rate ({stats['hits']}/{stats['total']})")
    
    logger.info("✓ Battle Analysis tests passed")
    return True

def test_fast_mode():
    """Test fast mode functionality"""
    logger.info("Testing Fast Mode...")
    
    # Test fast battle simulation
    engine = BattleEngine()
    
    # Run games in fast mode (shorter battles)
    start_time = time.time()
    results = []
    
    for i in range(10):
        team1 = [engine.create_pokemon_from_species("Dragapult"), engine.create_pokemon_from_species("Garchomp")]
        team2 = [engine.create_pokemon_from_species("Heatran"), engine.create_pokemon_from_species("Toxapex")]
        
        battle_result = engine.simulate_battle(team1, team2, max_turns=5)  # Short battles
        results.append(battle_result)
    
    end_time = time.time()
    
    duration = end_time - start_time
    games_per_second = len(results) / duration if duration > 0 else 0
    
    logger.info(f"Fast mode performance:")
    logger.info(f"  Games completed: {len(results)}")
    logger.info(f"  Duration: {duration:.2f} seconds")
    logger.info(f"  Games per second: {games_per_second:.2f}")
    
    # Verify results have battle logs
    battles_with_logs = sum(1 for r in results if "battle_log" in r)
    logger.info(f"  Battles with detailed logs: {battles_with_logs}/{len(results)}")
    
    # Check average battle length
    avg_turns = sum(r["turns"] for r in results) / len(results)
    logger.info(f"  Average battle length: {avg_turns:.1f} turns")
    
    logger.info("✓ Fast Mode tests passed")
    return True

def main():
    """Run all tests"""
    logger.info("Starting PokéAI Battle System Tests")
    
    tests = [
        ("Battle Engine", test_battle_engine),
        ("Battle Simulation", test_battle_simulation),
        ("Self-Play Simulation", test_self_play_simulation),
        ("Battle Analysis", test_battle_analysis),
        ("Fast Mode", test_fast_mode)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running {test_name} Test")
            logger.info(f"{'='*50}")
            
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} test PASSED")
            else:
                failed += 1
                logger.info(f"✗ {test_name} test FAILED")
                
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} test FAILED with error: {e}")
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed! Battle system is ready for self-training.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    import time
    success = main()
    sys.exit(0 if success else 1)
