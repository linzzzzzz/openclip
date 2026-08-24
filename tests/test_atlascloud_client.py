from core.engaging_moments_analyzer import EngagingMomentsAnalyzer
from core.insights_analyzer import InsightsAnalyzer
from core.llm.atlascloud_api_client import AtlasCloudAPIClient
from core.subtitle_burner import SubtitleBurner


def test_atlascloud_client_uses_provider_defaults(monkeypatch):
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "atlas-key")

    client = AtlasCloudAPIClient()

    assert client.api_key == "atlas-key"
    assert client.base_url == "https://api.atlascloud.ai/v1/chat/completions"
    assert client.default_model == "deepseek-ai/deepseek-v4-pro"


def test_atlascloud_provider_is_used_by_analysis_and_subtitles():
    analyzer = EngagingMomentsAnalyzer(provider="atlascloud", api_key="atlas-key")
    insights = InsightsAnalyzer(provider="atlascloud", api_key="atlas-key")
    burner = SubtitleBurner(provider="atlascloud", api_key="atlas-key", enable_llm=True)

    assert isinstance(analyzer.llm_client, AtlasCloudAPIClient)
    assert isinstance(insights.llm_client, AtlasCloudAPIClient)
    assert isinstance(burner.client, AtlasCloudAPIClient)
