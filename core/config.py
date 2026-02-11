"""
Configuration file for LLM clients and other components
"""

from typing import Dict, Any


# LLM Client configurations
LLM_CONFIG: Dict[str, Dict[str, Any]] = {
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "default_model": "qwen-turbo",
        "default_params": {
            "max_tokens": 8192,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        }
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "openrouter/free",
        "default_params": {
            "max_tokens": 8192,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        }
    }
}


# Environment variable names for API keys
API_KEY_ENV_VARS: Dict[str, str] = {
    "qwen": "QWEN_API_KEY",
    "openrouter": "OPENROUTER_API_KEY"
}


# Default LLM provider
DEFAULT_LLM_PROVIDER: str = "qwen"

# Video splitting
MAX_DURATION_MINUTES: float = 20.0

# Whisper model for transcript generation
# Options: tiny, base, small, medium, large, turbo
WHISPER_MODEL: str = "base"

# Title style for artistic text overlay
# Options: gradient_3d, neon_glow, metallic_gold, rainbow_3d, crystal_ice,
#          fire_flame, metallic_silver, glowing_plasma, stone_carved, glass_transparent
DEFAULT_TITLE_STYLE: str = "fire_flame"

# Maximum number of highlight clips to generate
MAX_CLIPS: int = 5

# Skip download by default (use existing files if available)
SKIP_DOWNLOAD: bool = False

# Skip transcript generation (use existing transcript files if available)
SKIP_TRANSCRIPT: bool = False
