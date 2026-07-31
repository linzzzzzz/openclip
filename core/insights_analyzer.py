#!/usr/bin/env python3
"""
Insights Analyzer
Extracts intellectual insights from thought-leader video transcripts using LLM APIs.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import re

from core.config import LLM_CONFIG, MAX_CLIPS

logger = logging.getLogger(__name__)


class InsightsAnalyzer:
    """Analyzes video transcripts to extract intellectual insights using LLM APIs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider: str = "qwen",
        use_background: bool = False,
        language: str = "en",
        debug: bool = False,
        max_clips: int = MAX_CLIPS,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.max_clips = max_clips
        self.provider = provider.lower()
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.use_background = use_background
        self.background_content = None
        self.language = language
        self.debug = debug
        self.model = model.strip() if model else None
        self.base_url = base_url.strip() if base_url else None

        if self.provider == "custom_openai" and not (
            self.model or LLM_CONFIG["custom_openai"]["default_model"]
        ):
            raise ValueError(
                "custom_openai requires llm_model. Set CUSTOM_OPENAI_MODEL or provide llm_model."
            )

        if self.provider == "qwen":
            from core.llm.qwen_api_client import QwenAPIClient
            self.llm_client = QwenAPIClient(api_key, base_url=self.base_url)
        elif self.provider == "openrouter":
            from core.llm.openrouter_api_client import OpenRouterAPIClient
            self.llm_client = OpenRouterAPIClient(api_key, base_url=self.base_url)
        elif self.provider == "atlascloud":
            from core.llm.atlascloud_api_client import AtlasCloudAPIClient
            self.llm_client = AtlasCloudAPIClient(api_key, base_url=self.base_url)
        elif self.provider == "glm":
            from core.llm.glm_api_client import GLMAPIClient
            self.llm_client = GLMAPIClient(api_key, base_url=self.base_url)
        elif self.provider == "minimax":
            from core.llm.minimax_api_client import MiniMaxAPIClient
            self.llm_client = MiniMaxAPIClient(api_key, base_url=self.base_url)
        elif self.provider == "custom_openai":
            from core.llm.custom_openai_api_client import CustomOpenAIAPIClient
            self.llm_client = CustomOpenAIAPIClient(api_key, base_url=self.base_url)
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. Supported: {', '.join(LLM_CONFIG)}."
            )

        if self.use_background:
            self._load_background_info()

    # ── Shared utilities ───────────────────────────────────────────────────────

    def _load_background_info(self):
        """Load background information from prompts/background/background.md."""
        try:
            background_path = self.prompts_dir / "background" / "background.md"
            if background_path.exists():
                with open(background_path, "r", encoding="utf-8") as f:
                    self.background_content = f.read().strip()
                logger.info("📚 Background information loaded")
            else:
                logger.warning(f"Background file not found: {background_path}")
                self.use_background = False
        except Exception as e:
            logger.error(f"Error loading background information: {e}")
            self.use_background = False

    def _export_debug_prompt(
        self, prompt_content: str, prompt_type: str, part_name: Optional[str] = None
    ):
        """Export full prompt content to disk when debug mode is on."""
        if not self.debug:
            return
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_dir = Path("debug_prompts")
            debug_dir.mkdir(exist_ok=True)
            filename = (
                f"{prompt_type}_{part_name}_{timestamp}.txt"
                if part_name
                else f"{prompt_type}_{timestamp}.txt"
            )
            export_path = debug_dir / filename
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(f"=== DEBUG PROMPT - {prompt_type.upper()} ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Language: {self.language}\n")
                if part_name:
                    f.write(f"Video Part: {part_name}\n")
                f.write(f"Prompt Length: {len(prompt_content)} characters\n")
                f.write("=" * 60 + "\n\n")
                f.write(prompt_content)
            logger.info(f"🐛 Debug prompt exported: {export_path}")
        except Exception as e:
            logger.error(f"Error exporting debug prompt: {e}")

    def load_prompt_template(self, prompt_name: str) -> str:
        """Load a prompt template from the prompts directory (with language patch)."""
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        language_patch_path = self.prompts_dir / "language_patches" / f"{self.language}.md"
        if language_patch_path.exists():
            with open(language_patch_path, "r", encoding="utf-8") as f:
                content += "\n\n" + f.read().strip()
            logger.info(f"🌐 Language patch loaded for: {self.language}")
        else:
            logger.warning(f"Language patch not found: {language_patch_path}")

        return content

    def parse_srt_file(self, srt_path: str) -> List[Dict[str, Any]]:
        """Parse an SRT file into a list of subtitle entries."""
        entries = []
        try:
            with open(srt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            for block in content.split("\n\n"):
                lines = block.strip().split("\n")
                if len(lines) >= 3:
                    timing_match = re.match(
                        r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})",
                        lines[1],
                    )
                    if timing_match:
                        entries.append(
                            {
                                "start_time": timing_match.group(1),
                                "end_time": timing_match.group(2),
                                "text": " ".join(lines[2:]),
                            }
                        )
        except Exception as e:
            logger.error(f"Error parsing SRT file {srt_path}: {e}")
        return entries

    def time_to_seconds(self, time_str: str) -> float:
        """Convert HH:MM:SS[,mmm] or MM:SS to seconds."""
        if "," in time_str:
            time_part, ms_part = time_str.split(",")
            ms = int(ms_part)
        else:
            time_part = time_str
            ms = 0
        parts = time_part.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
        elif len(parts) == 2:
            h = 0
            m, s = map(int, parts)
        else:
            raise ValueError(f"Unexpected time format: {time_str}")
        return h * 3600 + m * 60 + s + ms / 1000

    def create_transcript_context(self, entries: List[Dict[str, Any]]) -> str:
        """Format SRT entries into a transcript string for the LLM."""
        return "\n".join(
            f"[{e['start_time']} --> {e['end_time']}] {e['text']}" for e in entries
        )

    async def save_highlights_to_file(self, highlights: Dict[str, Any], output_path: str):
        """Save a highlights/insights dict to a JSON file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(highlights, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving to {output_path}: {e}")
            raise

    # ── Per-part analysis ──────────────────────────────────────────────────────

    def _build_part_prompt(self, srt_path: str, part_name: str) -> str:
        """Build the per-part analysis prompt for insights extraction."""
        entries = self.parse_srt_file(srt_path)
        if not entries:
            return ""
        transcript_context = self.create_transcript_context(entries)
        prompt_template = self.load_prompt_template("insights_part_requirement")

        parts = []
        if self.use_background and self.background_content:
            parts.append("## Additional Background Information\n\n")
            parts.append(self.background_content)
            parts.append("\n\n")
        parts.append(prompt_template)
        parts.append(f"\n\n## Transcript Data for {part_name}\n\n")
        parts.append(transcript_context)
        parts.append(
            "\n\nPlease analyze this transcript and extract intellectual insights following the requirements above."
        )
        return "".join(parts)

    async def analyze_part(self, srt_path: str, part_name: str) -> Dict[str, Any]:
        """Analyze a single video part and return extracted insights."""
        logger.info(f"💡 Extracting insights from {part_name}...")
        entries = self.parse_srt_file(srt_path)
        if not entries:
            logger.warning(f"No entries found in {srt_path}")
            return self._empty_part_result(part_name)

        prompt = self._build_part_prompt(srt_path, part_name)
        self._export_debug_prompt(prompt, "insights_analysis", part_name)

        try:
            response = self.llm_client.simple_chat(prompt, model=self.model)
            return self._parse_part_response(response, part_name, entries)
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return self._empty_part_result(part_name)

    def _parse_part_response(
        self, response: str, part_name: str, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract and validate insights JSON from a per-part LLM response."""
        for extractor in [
            lambda r: json.loads(r.strip()),
            lambda r: json.loads(re.search(r"```json\s*(\{.*?\})\s*```", r, re.DOTALL).group(1)),
            lambda r: json.loads(re.search(r"\{.*\}", r, re.DOTALL).group()),
        ]:
            try:
                result = extractor(response)
                return self._validate_part_result(result, part_name, entries)
            except (json.JSONDecodeError, AttributeError):
                pass
        logger.error(f"Could not parse insights JSON for {part_name}")
        return self._empty_part_result(part_name)

    def _validate_part_result(
        self, result: Dict[str, Any], part_name: str, entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        result.setdefault("insights", [])
        result["video_part"] = part_name
        valid = [ins for ins in result["insights"] if self._validate_insight(ins, entries)]
        result["insights"] = valid
        result["total_insights"] = len(valid)
        return result

    def _validate_insight(self, insight: Dict[str, Any], entries: List[Dict[str, Any]]) -> bool:
        """Return True if the insight has required fields and a valid duration."""
        for field in ("claim", "start_time", "end_time"):
            if not insight.get(field):
                logger.warning(f"Insight missing required field: {field}")
                return False
        try:
            start = self.time_to_seconds(insight["start_time"])
            end = self.time_to_seconds(insight["end_time"])
            duration = end - start
            if duration < 30 or duration > 180:
                logger.warning(
                    f"Insight duration out of range ({duration}s): {insight['claim'][:60]}"
                )
                return False
            insight["duration_seconds"] = int(duration)
        except Exception as e:
            logger.warning(f"Invalid insight timestamps: {e}")
            return False
        insight.setdefault("quote", "")
        insight.setdefault("topic", "general")
        return True

    def _empty_part_result(self, part_name: str) -> Dict[str, Any]:
        return {
            "video_part": part_name,
            "insights": [],
            "total_insights": 0,
            "analysis_timestamp": datetime.now().isoformat() + "Z",
        }

    # ── Collection & aggregation ───────────────────────────────────────────────

    def collect_all_insights(self, insights_files: List[str]) -> Dict[str, Any]:
        """Merge per-part insights files into a single flat list (no LLM call)."""
        all_insights = []
        for file_path in insights_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                part_name = data.get("video_part", "unknown")
                for ins in data.get("insights", []):
                    ins["video_part"] = part_name
                    all_insights.append(ins)
            except Exception as e:
                logger.error(f"Error loading insights file {file_path}: {e}")
        logger.info(f"Collected {len(all_insights)} insights from {len(insights_files)} part(s)")
        return {
            "insights": all_insights,
            "total_insights": len(all_insights),
            "analysis_timestamp": datetime.now().isoformat() + "Z",
        }

    def _build_aggregation_prompt(self, insights_files: List[str]) -> str:
        """Build the LLM aggregation prompt from per-part insights files."""
        all_insights = []
        for file_path in insights_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                part_name = data.get("video_part", "unknown")
                for ins in data.get("insights", []):
                    ins["video_part"] = part_name
                    all_insights.append(ins)
            except Exception as e:
                logger.error(f"Error loading insights file {file_path}: {e}")

        context_lines = []
        for i, ins in enumerate(all_insights, 1):
            context_lines.append(
                f"\nInsight {i}:\n"
                f"- Part: {ins.get('video_part', 'unknown')}\n"
                f"- Claim: {ins.get('claim', '')}\n"
                f"- Quote: {ins.get('quote', '')[:300]}\n"
                f"- Topic: {ins.get('topic', '')}\n"
                f"- Time: {ins.get('start_time', '')} --> {ins.get('end_time', '')}\n"
                f"- Duration: {ins.get('duration_seconds', 0)}s\n"
            )
        insights_context = "\n".join(context_lines)

        prompt_template = self.load_prompt_template("insights_agg_requirement")
        parts = []
        if self.use_background and self.background_content:
            parts.append("## Background Information\n\n")
            parts.append(self.background_content)
            parts.append("\n\n")
        parts.append(prompt_template.replace("{max_clips}", str(self.max_clips)))
        parts.append("\n\n## All Extracted Insights\n\n")
        parts.append(insights_context)
        parts.append(
            f"\n\nPlease select and rank the top {self.max_clips} most valuable insights following the requirements above."
        )
        return "".join(parts)

    async def aggregate_top_insights(
        self, insights_files: List[str], output_dir: str
    ) -> Dict[str, Any]:
        """LLM-rank insights from all parts and return the top max_clips."""
        logger.info(f"🔄 Aggregating top {self.max_clips} insights...")

        all_insights = []
        for file_path in insights_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                part_name = data.get("video_part", "unknown")
                for ins in data.get("insights", []):
                    ins["video_part"] = part_name
                    all_insights.append(ins)
            except Exception as e:
                logger.error(f"Error loading insights file {file_path}: {e}")

        if not all_insights:
            logger.warning("No insights found to aggregate")
            return {"insights": [], "total_insights": 0,
                    "analysis_timestamp": datetime.now().isoformat() + "Z",
                    "aggregation_criteria": "No insights found"}

        if len(all_insights) <= self.max_clips:
            logger.info(
                f"  {len(all_insights)} insights ≤ {self.max_clips} cap — skipping LLM aggregation"
            )
            for i, ins in enumerate(all_insights):
                ins["rank"] = i + 1
            return {
                "insights": all_insights,
                "total_insights": len(all_insights),
                "analysis_timestamp": datetime.now().isoformat() + "Z",
                "aggregation_criteria": "All insights kept (under cap)",
            }

        prompt = self._build_aggregation_prompt(insights_files)
        self._export_debug_prompt(prompt, "insights_aggregation")

        try:
            response = self.llm_client.simple_chat(prompt, model=self.model)
            return self._parse_aggregation_response(response, all_insights)
        except Exception as e:
            logger.error(f"Error in insights aggregation API call: {e}")
            return self._fallback_aggregation(all_insights)

    def _parse_aggregation_response(
        self, response: str, all_insights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract and validate insights aggregation JSON from LLM response."""
        for extractor in [
            lambda r: json.loads(r.strip()),
            lambda r: json.loads(re.search(r"```json\s*(\{.*?\})\s*```", r, re.DOTALL).group(1)),
            lambda r: json.loads(re.search(r"\{.*\}", r, re.DOTALL).group()),
        ]:
            try:
                result = extractor(response)
                return self._validate_aggregation_result(result)
            except (json.JSONDecodeError, AttributeError):
                pass
        logger.error("Could not parse insights aggregation JSON — using fallback")
        return self._fallback_aggregation(all_insights)

    def _validate_aggregation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        result.setdefault("insights", [])
        for i, ins in enumerate(result["insights"]):
            ins["rank"] = i + 1
        result["total_insights"] = len(result["insights"])
        result["analysis_timestamp"] = datetime.now().isoformat() + "Z"
        result.setdefault("aggregation_criteria", "Selected by intellectual impact and non-redundancy")
        return result

    def _fallback_aggregation(self, all_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Take the first max_clips insights without LLM ranking."""
        top = all_insights[: self.max_clips]
        for i, ins in enumerate(top):
            ins["rank"] = i + 1
        return {
            "insights": top,
            "total_insights": len(top),
            "analysis_timestamp": datetime.now().isoformat() + "Z",
            "aggregation_criteria": f"Fallback selection — first {self.max_clips} insights",
        }
