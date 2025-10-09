#!/usr/bin/env python3
"""
PokéAI Integration Test Script

This script tests the full system integration:
1. Start all services
2. Test calculation service
3. Test policy service
4. Test team builder service
5. Test client connection
6. Measure inference latency
"""

import asyncio
import aiohttp
import json
import time
import logging
import subprocess
import sys
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationTester:
    """Integration tester for PokéAI services"""
    
    def __init__(self):
        self.calc_url = "http://localhost:3001"
        self.policy_url = "http://localhost:8000"
        self.teambuilder_url = "http://localhost:8001"
        self.services = []
    
    async def start_services(self):
        """Start all PokéAI services"""
        logger.info("Starting PokéAI services...")
        
        # Start calculation service
        calc_process = subprocess.Popen([
            "cd", "services/calc", "&&", "npm", "run", "dev"
        ], shell=True)
        self.services.append(calc_process)
        
        # Start policy service
        policy_process = subprocess.Popen([
            "cd", "services/policy", "&&", "python", "main.py"
        ], shell=True)
        self.services.append(policy_process)
        
        # Start team builder service
        teambuilder_process = subprocess.Popen([
            "cd", "services/teambuilder", "&&", "python", "main.py"
        ], shell=True)
        self.services.append(teambuilder_process)
        
        # Wait for services to start
        await asyncio.sleep(10)
        
        logger.info("Services started")
    
    async def test_calc_service(self) -> bool:
        """Test calculation service"""
        logger.info("Testing calculation service...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.calc_url}/health") as response:
                    if response.status != 200:
                        logger.error("Calc service health check failed")
                        return False
                
                # Test calculation endpoint
                test_data = {
                    "battleState": {
                        "id": "test-battle",
                        "format": "gen9ou",
                        "turn": 1,
                        "phase": "battle",
                        "p1": {
                            "active": {
                                "species": "Dragapult",
                                "hp": 100,
                                "maxhp": 100,
                                "moves": [{"id": "shadowball", "name": "Shadow Ball", "pp": 16, "maxpp": 16}],
                                "ability": "Clear Body",
                                "position": "active"
                            },
                            "bench": [],
                            "side": {"hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False}}
                        },
                        "p2": {
                            "active": {
                                "species": "Garchomp",
                                "hp": 100,
                                "maxhp": 100,
                                "moves": [{"id": "earthquake", "name": "Earthquake", "pp": 16, "maxpp": 16}],
                                "ability": "Rough Skin",
                                "position": "active"
                            },
                            "bench": [],
                            "side": {"hazards": {"spikes": 0, "toxicSpikes": 0, "stealthRock": False, "stickyWeb": False}}
                        },
                        "field": {"weather": None, "terrain": None},
                        "log": [],
                        "lastActions": {},
                        "opponentModel": {}
                    },
                    "actions": [
                        {"type": "move", "move": "shadowball", "target": "p2"}
                    ]
                }
                
                start_time = time.time()
                async with session.post(f"{self.calc_url}/calculate", json=test_data) as response:
                    if response.status != 200:
                        logger.error("Calc service calculation failed")
                        return False
                    
                    result = await response.json()
                    latency = time.time() - start_time
                    
                    logger.info(f"Calc service test passed (latency: {latency:.3f}s)")
                    return True
                    
        except Exception as e:
            logger.error(f"Calc service test failed: {e}")
            return False
    
    async def test_policy_service(self) -> bool:
        """Test policy service"""
        logger.info("Testing policy service...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.policy_url}/health") as response:
                    if response.status != 200:
                        logger.error("Policy service health check failed")
                        return False
                
                # Test policy endpoint
                test_data = {
                    "battleState": {
                        "id": "test-battle",
                        "format": "gen9ou",
                        "turn": 1,
                        "phase": "battle",
                        "p1": {"active": {"species": "Dragapult", "hp": 100, "maxhp": 100}},
                        "p2": {"active": {"species": "Garchomp", "hp": 100, "maxhp": 100}},
                        "field": {},
                        "log": [],
                        "lastActions": {},
                        "opponentModel": {}
                    },
                    "calcResults": [
                        {
                            "action": {"type": "move", "move": "shadowball"},
                            "damage": {"min": 80, "max": 95, "average": 87.5, "ohko": 0.0, "twohko": 0.8},
                            "accuracy": 100,
                            "speedCheck": {"faster": True, "speedDiff": 20},
                            "expectedSurvival": 0.9,
                            "expectedGain": 5.0,
                            "priority": 0
                        }
                    ]
                }
                
                start_time = time.time()
                async with session.post(f"{self.policy_url}/policy", json=test_data) as response:
                    if response.status != 200:
                        logger.error("Policy service policy failed")
                        return False
                    
                    result = await response.json()
                    latency = time.time() - start_time
                    
                    logger.info(f"Policy service test passed (latency: {latency:.3f}s)")
                    return True
                    
        except Exception as e:
            logger.error(f"Policy service test failed: {e}")
            return False
    
    async def test_teambuilder_service(self) -> bool:
        """Test team builder service"""
        logger.info("Testing team builder service...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.teambuilder_url}/health") as response:
                    if response.status != 200:
                        logger.error("Team builder service health check failed")
                        return False
                
                # Test team building endpoint
                test_data = {
                    "format": "gen9ou",
                    "constraints": {
                        "playstyle": "balance",
                        "requiredRoles": ["sweeper", "wall", "hazard_setter"]
                    }
                }
                
                start_time = time.time()
                async with session.post(f"{self.teambuilder_url}/build-team", json=test_data) as response:
                    if response.status != 200:
                        logger.error("Team builder service team building failed")
                        return False
                    
                    result = await response.json()
                    latency = time.time() - start_time
                    
                    logger.info(f"Team builder service test passed (latency: {latency:.3f}s)")
                    return True
                    
        except Exception as e:
            logger.error(f"Team builder service test failed: {e}")
            return False
    
    async def test_full_pipeline(self) -> bool:
        """Test the full decision pipeline"""
        logger.info("Testing full decision pipeline...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Get calc results
                calc_data = {
                    "battleState": {
                        "id": "test-battle",
                        "format": "gen9ou",
                        "turn": 1,
                        "phase": "battle",
                        "p1": {"active": {"species": "Dragapult", "hp": 100, "maxhp": 100}},
                        "p2": {"active": {"species": "Garchomp", "hp": 100, "maxhp": 100}},
                        "field": {},
                        "log": [],
                        "lastActions": {},
                        "opponentModel": {}
                    },
                    "actions": [
                        {"type": "move", "move": "shadowball"},
                        {"type": "move", "move": "dragonpulse"},
                        {"type": "switch", "pokemon": 0}
                    ]
                }
                
                start_time = time.time()
                
                # Get calc results
                async with session.post(f"{self.calc_url}/calculate", json=calc_data) as response:
                    if response.status != 200:
                        logger.error("Calc service failed in pipeline test")
                        return False
                    calc_results = await response.json()
                
                # Get policy recommendation
                policy_data = {
                    "battleState": calc_data["battleState"],
                    "calcResults": calc_results
                }
                
                async with session.post(f"{self.policy_url}/policy", json=policy_data) as response:
                    if response.status != 200:
                        logger.error("Policy service failed in pipeline test")
                        return False
                    policy_result = await response.json()
                
                total_latency = time.time() - start_time
                
                logger.info(f"Full pipeline test passed (total latency: {total_latency:.3f}s)")
                
                # Check if latency is within requirements (<500ms)
                if total_latency > 0.5:
                    logger.warning(f"Latency exceeds requirement: {total_latency:.3f}s > 0.5s")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Full pipeline test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests"""
        logger.info("Running PokéAI integration tests...")
        
        # Start services
        await self.start_services()
        
        # Run tests
        tests = [
            ("Calculation Service", self.test_calc_service),
            ("Policy Service", self.test_policy_service),
            ("Team Builder Service", self.test_teambuilder_service),
            ("Full Pipeline", self.test_full_pipeline)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"Running {test_name} test...")
            result = await test_func()
            results.append((test_name, result))
            
            if not result:
                logger.error(f"{test_name} test failed!")
            else:
                logger.info(f"{test_name} test passed!")
        
        # Summary
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        logger.info(f"Integration tests completed: {passed}/{total} passed")
        
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            logger.info(f"  {test_name}: {status}")
        
        return passed == total
    
    def cleanup(self):
        """Clean up services"""
        logger.info("Cleaning up services...")
        for process in self.services:
            try:
                process.terminate()
            except:
                pass

async def main():
    """Main test function"""
    tester = IntegrationTester()
    
    try:
        success = await tester.run_all_tests()
        if success:
            logger.info("All integration tests passed!")
            sys.exit(0)
        else:
            logger.error("Some integration tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
