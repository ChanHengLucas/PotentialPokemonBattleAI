#!/usr/bin/env python3
"""
Pre-Simulation Audit Runner

Runs comprehensive pre-simulation audit including:
- Pre-train assertions
- Mechanics tests
- Masking tests
- Format guard tests
- Calc fidelity tests
- Coverage matrix
"""

import json
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pretrain_assertions():
    """Run pre-train assertions"""
    logger.info("Running Pre-Train Assertions...")
    
    try:
        result = subprocess.run([
            sys.executable, "scripts/pretrain_smoke.py"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Pre-train assertions passed")
            return True
        else:
            logger.error("❌ Pre-train assertions failed:")
            logger.error(result.stdout)
            logger.error(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Pre-train assertions timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Pre-train assertions error: {e}")
        return False

def run_mechanics_tests():
    """Run mechanics tests"""
    logger.info("Running Mechanics Tests...")
    
    test_files = [
        "tests/mechanics/test_hazards.py",
        "tests/mechanics/test_screens_rooms.py", 
        "tests/mechanics/test_status_volatiles.py",
        "tests/mechanics/test_priority_speed.py",
        "tests/mechanics/test_choice_locking.py",
        "tests/mechanics/test_items.py",
        "tests/mechanics/test_abilities.py",
        "tests/mechanics/test_move_specifics.py",
        "tests/mechanics/test_weather_terrain.py",
        "tests/mechanics/test_tera.py"
    ]
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_file, "-v"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info(f"✅ {test_file} passed")
                    passed += 1
                else:
                    logger.error(f"❌ {test_file} failed")
                    logger.error(result.stdout)
                    failed += 1
            except subprocess.TimeoutExpired:
                logger.error(f"❌ {test_file} timed out")
                failed += 1
            except Exception as e:
                logger.error(f"❌ {test_file} error: {e}")
                failed += 1
        else:
            logger.warning(f"⚠️ {test_file} not found")
    
    logger.info(f"Mechanics tests: {passed} passed, {failed} failed")
    return failed == 0

def run_masking_tests():
    """Run masking tests"""
    logger.info("Running Masking Tests...")
    
    test_file = "tests/masking/test_action_masking.py"
    
    if Path(test_file).exists():
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ {test_file} passed")
                return True
            else:
                logger.error(f"❌ {test_file} failed")
                logger.error(result.stdout)
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {test_file} timed out")
            return False
        except Exception as e:
            logger.error(f"❌ {test_file} error: {e}")
            return False
    else:
        logger.warning(f"⚠️ {test_file} not found")
        return False

def run_format_guard_tests():
    """Run format guard tests"""
    logger.info("Running Format Guard Tests...")
    
    test_file = "tests/format/test_format_guards.py"
    
    if Path(test_file).exists():
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ {test_file} passed")
                return True
            else:
                logger.error(f"❌ {test_file} failed")
                logger.error(result.stdout)
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {test_file} timed out")
            return False
        except Exception as e:
            logger.error(f"❌ {test_file} error: {e}")
            return False
    else:
        logger.warning(f"⚠️ {test_file} not found")
        return False

def run_calc_fidelity_tests():
    """Run calc fidelity tests"""
    logger.info("Running Calc Fidelity Tests...")
    
    test_file = "tests/calc/test_calc_fidelity.py"
    
    if Path(test_file).exists():
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ {test_file} passed")
                return True
            else:
                logger.error(f"❌ {test_file} failed")
                logger.error(result.stdout)
                return False
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {test_file} timed out")
            return False
        except Exception as e:
            logger.error(f"❌ {test_file} error: {e}")
            return False
    else:
        logger.warning(f"⚠️ {test_file} not found")
        return False

def load_pretrain_matrix():
    """Load pre-train matrix"""
    matrix_file = Path("scripts/pretrain_matrix.json")
    
    if matrix_file.exists():
        with open(matrix_file, 'r') as f:
            return json.load(f)
    else:
        logger.warning("⚠️ Pre-train matrix not found")
        return None

def print_coverage_table(matrix):
    """Print coverage table"""
    if not matrix:
        return
    
    logger.info("\n" + "="*60)
    logger.info("PRE-TRAIN AUDIT COVERAGE")
    logger.info("="*60)
    
    coverage = matrix.get("coverage", {})
    total = coverage.get("total_assertions", 0)
    categories = coverage.get("categories", {})
    
    logger.info(f"Total Assertions: {total}")
    logger.info("\nCategory Coverage:")
    
    for category, count in categories.items():
        percentage = (count / total) * 100 if total > 0 else 0
        logger.info(f"  {category:20} {count:3d} ({percentage:5.1f}%)")
    
    logger.info("\nAssertion Status:")
    
    assertions = matrix.get("assertions", {})
    for name, details in assertions.items():
        file_name = details.get("file", "unknown")
        test_name = details.get("test", "unknown")
        expected = details.get("expected", "unknown")
        
        logger.info(f"  {name:30} {file_name:40} {test_name:30} {expected}")
    
    logger.info("="*60)

def main():
    """Main function"""
    logger.info("Starting Pre-Simulation Audit")
    logger.info("="*60)
    
    # Load pre-train matrix
    matrix = load_pretrain_matrix()
    
    # Run all tests
    results = {
        "pretrain_assertions": run_pretrain_assertions(),
        "mechanics_tests": run_mechanics_tests(),
        "masking_tests": run_masking_tests(),
        "format_guard_tests": run_format_guard_tests(),
        "calc_fidelity_tests": run_calc_fidelity_tests()
    }
    
    # Print coverage table
    print_coverage_table(matrix)
    
    # Print results
    logger.info("\n" + "="*60)
    logger.info("AUDIT RESULTS")
    logger.info("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All pre-simulation audits passed!")
        logger.info("Training can proceed safely.")
        sys.exit(0)
    else:
        logger.error("\n❌ Some pre-simulation audits failed!")
        logger.error("Please fix failing tests before training.")
        sys.exit(1)

if __name__ == "__main__":
    main()
