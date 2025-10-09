#!/usr/bin/env python3
"""
PokéAI Team Builder CLI

Command-line interface for building teams.
"""

import argparse
import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any

def build_team(format_name: str, output_path: str, include_tera: bool = True, role_hints: list = None) -> bool:
    """Build a team using the team builder service"""
    try:
        # Prepare request data
        request_data = {
            "format": format_name,
            "includeTera": include_tera,
            "roleHints": role_hints or []
        }
        
        # Call team builder service
        response = requests.post(
            "http://localhost:8001/build",
            json=request_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Error: Team builder service returned {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        # Save team to output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Team built successfully!")
        print(f"Format: {result['team']['format']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Synergy: {result['synergy']:.2f}")
        print(f"Coverage: {', '.join(result['coverage'])}")
        print(f"Win Conditions: {', '.join(result['winConditions'])}")
        print(f"Team saved to: {output_path}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to team builder service. Make sure it's running on port 8001.")
        return False
    except Exception as e:
        print(f"Error building team: {e}")
        return False

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Build a competitive Pokémon team")
    parser.add_argument("--format", required=True, help="Format (e.g., gen9ou)")
    parser.add_argument("--out", required=True, help="Output file path")
    parser.add_argument("--include-tera", action="store_true", default=True, help="Include Tera types")
    parser.add_argument("--no-tera", action="store_true", help="Exclude Tera types")
    parser.add_argument("--role-hints", nargs="*", help="Role hints for team building")
    
    args = parser.parse_args()
    
    # Handle tera inclusion
    include_tera = args.include_tera and not args.no_tera
    
    # Build team
    success = build_team(
        format_name=args.format,
        output_path=args.out,
        include_tera=include_tera,
        role_hints=args.role_hints
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
