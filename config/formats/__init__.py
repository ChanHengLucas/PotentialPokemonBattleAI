"""
Format configuration loader for PokéAI
"""

import yaml
import hashlib
from pathlib import Path
from typing import Dict, Any

def load_format_config(format_name: str) -> Dict[str, Any]:
    """Load format configuration from YAML file"""
    format_file = Path(__file__).parent / f"{format_name}.yaml"
    
    if not format_file.exists():
        raise ValueError(f"Format configuration not found: {format_name}")
    
    with open(format_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def get_format_version(format_name: str) -> str:
    """Get format version for a given format"""
    config = load_format_config(format_name)
    return config.get("version", "1.0.0")

def get_dex_version(format_name: str) -> str:
    """Get dex version for a given format"""
    config = load_format_config(format_name)
    return config.get("dex_version", "gen9")

def get_format_hash(format_name: str) -> str:
    """Get hash of format configuration for caching"""
    config = load_format_config(format_name)
    config_str = yaml.dump(config, sort_keys=True)
    return hashlib.md5(config_str.encode()).hexdigest()

def is_tera_allowed(format_name: str) -> bool:
    """Check if Tera is allowed for a format"""
    config = load_format_config(format_name)
    return config.get("tera_allowed", False)

def get_banned_pokemon(format_name: str) -> list:
    """Get banned Pokemon list for a format"""
    config = load_format_config(format_name)
    return config.get("banned_pokemon", [])

def get_banned_items(format_name: str) -> list:
    """Get banned items list for a format"""
    config = load_format_config(format_name)
    return config.get("banned_items", [])

def get_banned_abilities(format_name: str) -> list:
    """Get banned abilities list for a format"""
    config = load_format_config(format_name)
    return config.get("banned_abilities", [])

def get_banned_moves(format_name: str) -> list:
    """Get banned moves list for a format"""
    config = load_format_config(format_name)
    return config.get("banned_moves", [])

def get_clauses(format_name: str) -> Dict[str, bool]:
    """Get clauses for a format"""
    config = load_format_config(format_name)
    return config.get("clauses", {})

def validate_format(format_name: str) -> bool:
    """Validate that a format is supported"""
    try:
        load_format_config(format_name)
        return True
    except (ValueError, FileNotFoundError):
        return False
