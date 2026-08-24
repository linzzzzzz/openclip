import importlib

import core.config as config


def reload_config():
    return importlib.reload(config)


def test_normalize_chat_completions_url_accepts_api_roots_and_full_endpoints():
    assert config._normalize_chat_completions_url("https://example.com/v1") == "https://example.com/v1/chat/completions"
    assert config._normalize_chat_completions_url("https://example.com/api/v4/") == "https://example.com/api/v4/chat/completions"
    assert config._normalize_chat_completions_url("https://example.com/compatible-mode/v1") == "https://example.com/compatible-mode/v1/chat/completions"
    assert config._normalize_chat_completions_url("https://example.com/chat/completions") == "https://example.com/chat/completions"
    assert config._normalize_chat_completions_url("https://example.com/generation") == "https://example.com/generation"


def test_llm_config_uses_environment_overrides(monkeypatch):
    with monkeypatch.context() as env:
        env.setenv("QWEN_BASE_URL", "https://qwen.example/v1")
        env.setenv("QWEN_MODEL", "qwen-test")
        env.setenv("OPENROUTER_BASE_URL", "https://router.example/api/v1/")
        env.setenv("ATLASCLOUD_MODEL", "atlas-test")
        env.setenv("GLM_BASE_URL", "https://glm.example/api/paas/v4")
        env.setenv("MINIMAX_MODEL", "MiniMax-Test")
        env.setenv("CUSTOM_OPENAI_BASE_URL", "https://openai.example/v1/")
        env.setenv("CUSTOM_OPENAI_MODEL", "custom-model")

        reloaded = reload_config()

        assert reloaded.LLM_CONFIG["qwen"]["base_url"] == "https://qwen.example/v1/chat/completions"
        assert reloaded.LLM_CONFIG["qwen"]["default_model"] == "qwen-test"
        assert reloaded.LLM_CONFIG["openrouter"]["base_url"] == "https://router.example/api/v1/chat/completions"
        assert reloaded.LLM_CONFIG["atlascloud"]["base_url"] == "https://api.atlascloud.ai/v1/chat/completions"
        assert reloaded.LLM_CONFIG["atlascloud"]["default_model"] == "atlas-test"
        assert reloaded.LLM_CONFIG["glm"]["base_url"] == "https://glm.example/api/paas/v4/chat/completions"
        assert reloaded.LLM_CONFIG["minimax"]["default_model"] == "MiniMax-Test"
        assert reloaded.LLM_CONFIG["custom_openai"]["base_url"] == "https://openai.example/v1/chat/completions"
        assert reloaded.LLM_CONFIG["custom_openai"]["default_model"] == "custom-model"

    reload_config()


def test_paraformer_default_project_dir_is_repo_relative(monkeypatch):
    with monkeypatch.context() as env:
        env.delenv("PARAFORMER_PROJECT_DIR", raising=False)
        reloaded = reload_config()

        assert reloaded.PARAFORMER_PROJECT_DIR == str(
            reloaded.REPO_ROOT / "third_party" / "funasr-paraformer"
        )

    reload_config()
