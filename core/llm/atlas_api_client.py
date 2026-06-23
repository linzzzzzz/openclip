"""
Atlas Cloud API Client - Implementation for interacting with the Atlas Cloud
OpenAI-compatible LLM API (https://www.atlascloud.ai).
"""

import logging
import time
import requests
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)
from dataclasses import dataclass

from core.config import LLM_CONFIG, API_KEY_ENV_VARS


@dataclass
class AtlasMessage:
    """Represents a message in the conversation"""
    role: str  # "system", "user", or "assistant"
    content: str


class AtlasAPIClient:
    """Client for interacting with the Atlas Cloud OpenAI-compatible LLM API"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Atlas Cloud API client

        Args:
            api_key: Your Atlas Cloud API key (can also be set via ATLAS_API_KEY env var)
            base_url: Base URL for the Atlas Cloud API (optional, uses config value if not provided)
        """
        self.api_key = api_key or os.getenv(API_KEY_ENV_VARS["atlas"])
        self.base_url = base_url or LLM_CONFIG["atlas"]["base_url"]

        if not self.api_key:
            raise ValueError(f"API key is required. Set {API_KEY_ENV_VARS['atlas']} environment variable or pass api_key parameter.")

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Atlas Cloud API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(self.base_url, headers=headers, json=payload, timeout=240)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                if attempt < max_attempts:
                    logger.warning(f"API request timed out (attempt {attempt}/{max_attempts}), retrying...")
                    continue
                raise Exception(f"API request failed: {e}")
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429 and attempt < max_attempts:
                    wait = 5 * attempt
                    logger.warning(f"Rate limited (429), waiting {wait}s before retry {attempt}/{max_attempts}...")
                    time.sleep(wait)
                    continue
                if response.status_code >= 500 and attempt < max_attempts:
                    wait = 3 * attempt
                    logger.warning(f"Server error ({response.status_code}), waiting {wait}s before retry {attempt}/{max_attempts}...")
                    time.sleep(wait)
                    continue
                raise Exception(f"API request failed: {e}")
            except requests.exceptions.RequestException as e:
                raise Exception(f"API request failed: {e}")

    def chat_completion(
        self,
        messages: List[AtlasMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion using the Atlas Cloud API

        Args:
            messages: List of conversation messages
            model: Model to use (e.g., deepseek-ai/deepseek-v4-pro, zai-org/glm-5)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            stream: Whether to stream the response

        Returns:
            API response dictionary
        """
        model = model or LLM_CONFIG["atlas"]["default_model"]
        max_tokens = max_tokens or LLM_CONFIG["atlas"]["default_params"]["max_tokens"]
        temperature = temperature if temperature is not None else LLM_CONFIG["atlas"]["default_params"]["temperature"]
        top_p = top_p or LLM_CONFIG["atlas"]["default_params"]["top_p"]
        stream = stream if stream is not None else LLM_CONFIG["atlas"]["default_params"]["stream"]

        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream
        }

        return self._make_request(payload)

    def simple_chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Simple chat interface - send a prompt and get response

        Args:
            prompt: User prompt/question
            model: Model to use (optional, uses config value if not provided)

        Returns:
            Generated response text
        """
        model = model or LLM_CONFIG["atlas"]["default_model"]

        messages = [AtlasMessage(role="user", content=prompt)]
        response = self.chat_completion(messages, model=model, temperature=temperature)

        try:
            message = response["choices"][0]["message"]
            content = message.get("content")
        except (KeyError, IndexError):
            raise Exception(f"Unexpected response format: {response}")
        # Atlas reasoning models (e.g. deepseek-v4-pro, glm-5) may return empty
        # content when max_tokens is exhausted by reasoning_content. Treat as a
        # truncation error so callers can raise max_tokens.
        if not content:
            reasoning = message.get("reasoning_content", "")
            if reasoning:
                raise Exception(
                    f"Model exhausted max_tokens on reasoning without producing content. "
                    f"Consider increasing max_tokens. Partial reasoning: {reasoning[:200]}..."
                )
            raise Exception(f"Model returned null content (possible content filter or empty response). Response: {response}")
        return content

    def conversation_chat(
        self,
        messages: List[AtlasMessage],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Multi-turn conversation chat

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt to set context
            model: Model to use (optional, uses config value if not provided)

        Returns:
            Generated response text
        """
        model = model or LLM_CONFIG["atlas"]["default_model"]

        conversation = []

        if system_prompt:
            conversation.append(AtlasMessage(role="system", content=system_prompt))

        conversation.extend(messages)

        response = self.chat_completion(conversation, model=model)

        try:
            message = response["choices"][0]["message"]
            content = message.get("content")
        except (KeyError, IndexError):
            raise Exception(f"Unexpected response format: {response}")
        if not content:
            reasoning = message.get("reasoning_content", "")
            if reasoning:
                raise Exception(
                    f"Model exhausted max_tokens on reasoning without producing content. "
                    f"Consider increasing max_tokens. Partial reasoning: {reasoning[:200]}..."
                )
            raise Exception(f"Model returned null content. Response: {response}")
        return content
