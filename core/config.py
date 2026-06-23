"""
Configuration file for LLM clients and other components
"""

import os
from pathlib import Path
from typing import Dict, Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def _normalize_chat_completions_url(url: str) -> str:
    """Accept either a full endpoint or an OpenAI-compatible API root."""
    normalized = url.rstrip("/")
    if normalized.endswith("/chat/completions") or normalized.endswith("/generation"):
        return normalized
    if normalized.endswith("/v1") or normalized.endswith("/v4") or normalized.endswith("/compatible-mode/v1"):
        return f"{normalized}/chat/completions"
    return normalized


def _env_llm_base_url(provider: str, default: str) -> str:
    env_value = os.getenv(f"{provider.upper()}_BASE_URL")
    if not env_value:
        return default
    return _normalize_chat_completions_url(env_value)


def _env_llm_model(provider: str, default: str) -> str:
    return os.getenv(f"{provider.upper()}_MODEL", default)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


SUPPORTED_LLM_PROVIDERS = (
    "qwen",
    "openrouter",
    "glm",
    "minimax",
    "atlas",
    "custom_openai",
)


# LLM Client configurations
LLM_CONFIG: Dict[str, Dict[str, Any]] = {
    "qwen": {
        # New models (qwen3.5, qwen3, etc.) use OpenAI-compatible endpoint
        "base_url": _env_llm_base_url("qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"),
        # Old models (qwen-turbo, qwen-plus, qwen-max) use DashScope endpoint
        "legacy_base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "default_model": _env_llm_model("qwen", "qwen3.6-plus"),
        "default_params": {
            "max_tokens": 16384,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        },
        # Models that use the legacy endpoint
        "legacy_models": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-long"]
    },
    "openrouter": {
        "base_url": _env_llm_base_url("openrouter", "https://openrouter.ai/api/v1/chat/completions"),
        "default_model": _env_llm_model("openrouter", "stepfun/step-3.5-flash:free"),
        "default_params": {
            "max_tokens": 32768,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        }
    },
    "glm": {
        "base_url": _env_llm_base_url("glm", "https://open.bigmodel.cn/api/paas/v4/chat/completions"),
        "default_model": _env_llm_model("glm", "glm-4.7"),
        "default_params": {
            "max_tokens": 32768,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        }
    },
    "minimax": {
        "base_url": _env_llm_base_url("minimax", "https://api.minimaxi.com/v1/chat/completions"),
        "default_model": _env_llm_model("minimax", "MiniMax-M2.7"),
        "default_params": {
            "max_tokens": 32768,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        }
    },
    "atlas": {
        # Atlas Cloud — single OpenAI-compatible API for LLM / image / video.
        # https://www.atlascloud.ai
        "base_url": _env_llm_base_url("atlas", "https://api.atlascloud.ai/v1/chat/completions"),
        # deepseek-v4-pro is a reasoning model; keep max_tokens high so the
        # answer is not exhausted by the chain-of-thought (reasoning_content).
        "default_model": _env_llm_model("atlas", "deepseek-ai/deepseek-v4-pro"),
        "default_params": {
            "max_tokens": 32768,
            "temperature": 0.7,
            "top_p": 0.8,
            "stream": False
        }
    },
    "custom_openai": {
        "base_url": _env_llm_base_url("custom_openai", "https://api.openai.com/v1/chat/completions"),
        "default_model": _env_llm_model("custom_openai", ""),
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
    "openrouter": "OPENROUTER_API_KEY",
    "glm": "GLM_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "atlas": "ATLAS_API_KEY",
    "custom_openai": "CUSTOM_OPENAI_API_KEY",
}


# Default LLM provider
DEFAULT_LLM_PROVIDER: str = "qwen"

# Video splitting
MAX_DURATION_MINUTES: float = 20.0

# Whisper model for transcript generation
# Options: tiny, base, small, medium, large, turbo
WHISPER_MODEL: str = "base"

# Lightweight Whisper model used only for transcript language detection.
# Keep this small because the full transcript backend is selected after detection.
TRANSCRIPT_LANGUAGE_DETECT_MODEL: str = os.getenv("TRANSCRIPT_LANGUAGE_DETECT_MODEL", "tiny")

# Local FunASR Paraformer project used for Chinese ASR.
# Default to a repo-relative vendored checkout so the config is portable.
PARAFORMER_PROJECT_DIR: str = os.getenv(
    "PARAFORMER_PROJECT_DIR",
    str(REPO_ROOT / "third_party" / "funasr-paraformer"),
)
PARAFORMER_DEVICE: str = os.getenv("PARAFORMER_DEVICE", "auto")

# Title style for artistic text overlay
# Options: gradient_3d, neon_glow, metallic_gold, rainbow_3d, crystal_ice,
#          fire_flame, metallic_silver, glowing_plasma, stone_carved, glass_transparent
DEFAULT_TITLE_STYLE: str = "fire_flame"

# Maximum number of highlight clips to generate
MAX_CLIPS: int = 5

# Subtitle translation post-processing
SUBTITLE_TRANSLATION_MAX_WORKERS: int = max(
    1,
    _env_int("SUBTITLE_TRANSLATION_MAX_WORKERS", 3),
)
SUBTITLE_TRANSLATION_LAUNCH_STAGGER_SECONDS: float = max(
    0.0,
    _env_float("SUBTITLE_TRANSLATION_LAUNCH_STAGGER_SECONDS", 0.25),
)

# Skip download by default (use existing files if available)
SKIP_DOWNLOAD: bool = False

# Skip transcript generation (use existing transcript files if available)
SKIP_TRANSCRIPT: bool = False
