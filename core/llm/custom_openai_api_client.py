"""
Custom OpenAI-compatible API client.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from core.config import API_KEY_ENV_VARS, LLM_CONFIG, _normalize_chat_completions_url

logger = logging.getLogger(__name__)


@dataclass
class CustomOpenAIMessage:
    """Represents a message in an OpenAI-compatible conversation."""

    role: str
    content: str


class CustomOpenAIAPIClient:
    """Client for arbitrary OpenAI-compatible chat completion endpoints."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv(API_KEY_ENV_VARS["custom_openai"])
        resolved_base_url = (
            base_url
            or os.getenv("CUSTOM_OPENAI_BASE_URL")
            or LLM_CONFIG["custom_openai"]["base_url"]
        )
        self.base_url = _normalize_chat_completions_url(resolved_base_url)
        self.default_model = (
            os.getenv("CUSTOM_OPENAI_MODEL")
            or LLM_CONFIG["custom_openai"]["default_model"]
        )

        if not self.base_url:
            raise ValueError(
                "Base URL is required for custom_openai. "
                "Set CUSTOM_OPENAI_BASE_URL or pass llm_base_url."
            )

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=float(os.getenv("CUSTOM_OPENAI_TIMEOUT", "240")),
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as exc:
                if attempt < max_attempts:
                    logger.warning(
                        "API request timed out (attempt %s/%s), retrying...",
                        attempt,
                        max_attempts,
                    )
                    continue
                raise Exception(f"API request failed: {exc}") from exc
            except requests.exceptions.HTTPError as exc:
                if response.status_code == 429 and attempt < max_attempts:
                    wait = 5 * attempt
                    logger.warning(
                        "Rate limited (429), waiting %ss before retry %s/%s...",
                        wait,
                        attempt,
                        max_attempts,
                    )
                    time.sleep(wait)
                    continue
                if response.status_code >= 500 and attempt < max_attempts:
                    wait = 3 * attempt
                    logger.warning(
                        "Server error (%s), waiting %ss before retry %s/%s...",
                        response.status_code,
                        wait,
                        attempt,
                        max_attempts,
                    )
                    time.sleep(wait)
                    continue
                response_details = self._format_error_response(response)
                raise Exception(
                    f"API request failed: {exc}. Response body: {response_details}"
                ) from exc
            except requests.exceptions.RequestException as exc:
                raise Exception(f"API request failed: {exc}") from exc

    @staticmethod
    def _format_error_response(response: requests.Response) -> str:
        """Return a compact error payload for HTTP failures."""
        try:
            payload = response.json()
        except ValueError:
            payload = response.text.strip()
        return str(payload) if payload else "<empty>"

    @staticmethod
    def _extract_content(message: Dict[str, Any]) -> str:
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)
                elif item is not None:
                    parts.append(str(item))
            return "".join(parts)
        return ""

    def chat_completion(
        self,
        messages: List[CustomOpenAIMessage],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: Optional[bool] = None,
    ) -> Dict[str, Any]:
        model = model or self.default_model
        if not model:
            raise ValueError(
                "Model is required for custom_openai. "
                "Set CUSTOM_OPENAI_MODEL or pass llm_model."
            )
        max_tokens = max_tokens or LLM_CONFIG["custom_openai"]["default_params"]["max_tokens"]
        temperature = temperature if temperature is not None else LLM_CONFIG["custom_openai"]["default_params"]["temperature"]
        top_p = top_p or LLM_CONFIG["custom_openai"]["default_params"]["top_p"]
        stream = (
            stream
            if stream is not None
            else LLM_CONFIG["custom_openai"]["default_params"]["stream"]
        )

        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
        }
        return self._make_request(payload)

    def simple_chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        messages = [CustomOpenAIMessage(role="user", content=prompt)]
        response = self.chat_completion(messages, model=model, temperature=temperature)

        try:
            message = response["choices"][0]["message"]
            content = self._extract_content(message)
        except (KeyError, IndexError) as exc:
            raise Exception(f"Unexpected response format: {response}") from exc

        if not content:
            raise Exception(
                f"Model returned empty content (possible content filter or malformed response). "
                f"Response: {response}"
            )
        return content

    def conversation_chat(
        self,
        messages: List[CustomOpenAIMessage],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        conversation = []
        if system_prompt:
            conversation.append(CustomOpenAIMessage(role="system", content=system_prompt))
        conversation.extend(messages)

        response = self.chat_completion(conversation, model=model)
        try:
            message = response["choices"][0]["message"]
            content = self._extract_content(message)
        except (KeyError, IndexError) as exc:
            raise Exception(f"Unexpected response format: {response}") from exc

        if not content:
            raise Exception(f"Model returned empty content. Response: {response}")
        return content
