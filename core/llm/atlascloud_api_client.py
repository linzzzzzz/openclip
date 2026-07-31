"""Atlas Cloud OpenAI-compatible API client."""

import os

from core.config import API_KEY_ENV_VARS, LLM_CONFIG
from core.llm.custom_openai_api_client import CustomOpenAIAPIClient


class AtlasCloudAPIClient(CustomOpenAIAPIClient):
    """Use Atlas Cloud defaults with the shared OpenAI-compatible client."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        super().__init__(
            api_key=api_key or os.getenv(API_KEY_ENV_VARS["atlascloud"]),
            base_url=base_url or LLM_CONFIG["atlascloud"]["base_url"],
        )
        self.default_model = LLM_CONFIG["atlascloud"]["default_model"]
