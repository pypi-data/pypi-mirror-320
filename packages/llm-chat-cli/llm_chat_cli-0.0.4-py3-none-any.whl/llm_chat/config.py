"""
Configuration management for LLM Chat
"""

import json
from pathlib import Path
import os

def initialize():
    """
    Initialize the configuration and load API keys.
    
    Returns:
        dict: Dictionary containing API keys for different providers
    
    Raises:
        SystemExit: If config file is not found
    """
    config_file = Path.home() / ".llm_cli" / "config.json"
    if not config_file.exists():
        print("API keys not found. Please run 'lmci setup' first.")
        exit(1)

    with open(config_file, "r") as f:
        api_keys = json.load(f)

    for provider, key in api_keys.items():
        os.environ[provider] = key

    return api_keys