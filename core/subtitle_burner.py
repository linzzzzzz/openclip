#!/usr/bin/env python3
"""
SubtitleBurner — burn subtitles into video clips, with optional translation.

Reads paired .mp4 + .srt files from a clips directory, optionally translates
the SRT to a target language via Qwen API, generates an ASS subtitle file,
then burns it into the output video with ffmpeg.

Usage (standalone):
    from core.subtitle_burner import SubtitleBurner

    # Burn original subtitles only (no API key needed):
    burner = SubtitleBurner()
    result = burner.burn_subtitles_for_clips("clips/", "clips_post_processed/")

    # Burn original + translated subtitles:
    burner = SubtitleBurner(api_key=os.environ["QWEN_API_KEY"])
    result = burner.burn_subtitles_for_clips(
        "clips/", "clips_post_processed/", subtitle_translation="Simplified Chinese"
    )
"""

import json
import logging
import os
import re
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageDraw

from core.config import (
    API_KEY_ENV_VARS,
    SUBTITLE_TRANSLATION_LAUNCH_STAGGER_SECONDS,
    SUBTITLE_TRANSLATION_MAX_WORKERS,
)
from core.font_utils import build_missing_font_message, find_best_font

logger = logging.getLogger(__name__)

# Matches diarization speaker tags at the start of a subtitle line, e.g.:
#   "[Sam Altman] text"  →  "text"
#   "[SPEAKER_01] >> text"  →  "text"
_SPEAKER_TAG_RE = re.compile(r"^\[.*?\]\s*(?:>>\s*)?", re.UNICODE)
_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


ASS_PLAY_RES_X = 1920
ASS_PLAY_RES_Y = 1080
ASS_ALIGNMENT_BOTTOM_CENTER = 2

SUBTITLE_FONT_SIZE_PRESETS = {
    "small": 64,
    "medium": 80,
    "large": 96,
}

SUBTITLE_VERTICAL_POSITION_PRESETS = {
    "bottom": 150,
    "lower_middle": 260,
    "middle": 390,
}

SUBTITLE_BILINGUAL_LAYOUT_OPTIONS = {"auto", "original_only", "bilingual"}
SUBTITLE_BACKGROUND_STYLE_OPTIONS = {"none", "light_box", "solid_box"}


@dataclass(frozen=True)
class SubtitleStylePreset:
    original_color: str
    translation_color: str
    outline_color: str
    shadow_color: str
    outline: int
    shadow: int
    bold: int = -1
    font_name: str = "Arial"


SUBTITLE_STYLE_PRESETS = {
    "default": SubtitleStylePreset(
        original_color="&H00FFFFFF",
        translation_color="&H0000FFFF",
        outline_color="&H00000000",
        shadow_color="&H80000000",
        outline=2,
        shadow=1,
    ),
    "clean": SubtitleStylePreset(
        original_color="&H00F5F5F5",
        translation_color="&H00D7F3FF",
        outline_color="&H00313131",
        shadow_color="&H50000000",
        outline=1,
        shadow=1,
        bold=0,
    ),
    "high_contrast": SubtitleStylePreset(
        original_color="&H00FFFFFF",
        translation_color="&H0000FFFF",
        outline_color="&H00000000",
        shadow_color="&HC0000000",
        outline=3,
        shadow=2,
    ),
    "stream": SubtitleStylePreset(
        original_color="&H00FFFFFF",
        translation_color="&H0057D8FF",
        outline_color="&H000B0B0B",
        shadow_color="&H90000000",
        outline=2,
        shadow=2,
    ),
}


@dataclass(frozen=True)
class SubtitleStyleConfig:
    preset: str = "default"
    font_size: str = "medium"
    vertical_position: str = "bottom"
    bilingual_layout: str = "auto"
    background_style: str = "none"

    def normalized(self) -> "SubtitleStyleConfig":
        return SubtitleStyleConfig(
            preset=self.preset if self.preset in SUBTITLE_STYLE_PRESETS else "default",
            font_size=self.font_size if self.font_size in SUBTITLE_FONT_SIZE_PRESETS else "medium",
            vertical_position=(
                self.vertical_position
                if self.vertical_position in SUBTITLE_VERTICAL_POSITION_PRESETS
                else "bottom"
            ),
            bilingual_layout=(
                self.bilingual_layout
                if self.bilingual_layout in SUBTITLE_BILINGUAL_LAYOUT_OPTIONS
                else "auto"
            ),
            background_style=(
                self.background_style
                if self.background_style in SUBTITLE_BACKGROUND_STYLE_OPTIONS
                else "none"
            ),
        )

    @classmethod
    def from_dict(cls, payload: dict | None) -> "SubtitleStyleConfig":
        if not payload:
            return cls()
        return cls(
            preset=payload.get("preset", "default"),
            font_size=payload.get("font_size", "medium"),
            vertical_position=payload.get("vertical_position", "bottom"),
            bilingual_layout=payload.get("bilingual_layout", "auto"),
            background_style=payload.get("background_style", "none"),
        ).normalized()

    def to_dict(self) -> dict:
        normalized = self.normalized()
        return {
            "preset": normalized.preset,
            "font_size": normalized.font_size,
            "vertical_position": normalized.vertical_position,
            "bilingual_layout": normalized.bilingual_layout,
            "background_style": normalized.background_style,
        }


@dataclass(frozen=True)
class SubtitlePreparationJob:
    mp4: Path
    srt: Path
    ass_path: Path
    translated_srt_path: Path | None = None
    translated_output_path: Path | None = None


@dataclass(frozen=True)
class SubtitlePreparationResult:
    job: SubtitlePreparationJob
    ok: bool


class SubtitleBurner:
    """Burn SRT subtitles into video clips, with optional LLM-powered translation."""

    def __init__(
        self,
        api_key: str = None,
        provider: str = "qwen",
        model: str = None,
        base_url: str = None,
        enable_llm: bool = False,
        subtitle_style_config: SubtitleStyleConfig | None = None,
        subtitle_translation_max_workers: int = SUBTITLE_TRANSLATION_MAX_WORKERS,
        subtitle_translation_launch_stagger_seconds: float = SUBTITLE_TRANSLATION_LAUNCH_STAGGER_SECONDS,
    ):
        self.model = model  # None → each client uses its config default
        self.subtitle_style_config = (subtitle_style_config or SubtitleStyleConfig()).normalized()
        self.subtitle_translation_max_workers = max(1, int(subtitle_translation_max_workers))
        self.subtitle_translation_launch_stagger_seconds = max(
            0.0,
            float(subtitle_translation_launch_stagger_seconds),
        )
        if enable_llm:
            provider = provider.lower()
            if provider == "openrouter":
                from core.llm.openrouter_api_client import OpenRouterAPIClient
                self.client = OpenRouterAPIClient(api_key=api_key, base_url=base_url)
            elif provider == "atlascloud":
                from core.llm.atlascloud_api_client import AtlasCloudAPIClient
                self.client = AtlasCloudAPIClient(api_key=api_key, base_url=base_url)
            elif provider == "glm":
                from core.llm.glm_api_client import GLMAPIClient
                self.client = GLMAPIClient(api_key=api_key, base_url=base_url)
            elif provider == "minimax":
                from core.llm.minimax_api_client import MiniMaxAPIClient
                self.client = MiniMaxAPIClient(api_key=api_key, base_url=base_url)
            elif provider == "custom_openai":
                from core.llm.custom_openai_api_client import CustomOpenAIAPIClient
                self.client = CustomOpenAIAPIClient(api_key=api_key, base_url=base_url)
            else:
                from core.llm.qwen_api_client import QwenAPIClient
                self.client = QwenAPIClient(api_key=api_key, base_url=base_url)
        else:
            self.client = None

    @staticmethod
    def _contains_cjk(text: str) -> bool:
        return bool(_CJK_RE.search(text or ""))

    @staticmethod
    def _font_family_from_path(font_path: str) -> str:
        try:
            result = subprocess.run(
                ["fc-scan", "--format", "%{family}\n", font_path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            family = (result.stdout or "").strip().splitlines()
            if result.returncode == 0 and family and family[0].strip():
                primary_family = family[0].split(",", 1)[0].strip()
                if primary_family:
                    return primary_family
        except (FileNotFoundError, OSError):
            pass

        return Path(font_path).stem

    @classmethod
    def _resolve_ass_font(cls, language: str) -> tuple[str, str | None]:
        font_path = find_best_font(language, prefer_bold=False, allow_generic_fallback=True)
        if not font_path:
            if language == "zh":
                logger.warning(build_missing_font_message(language))
            return "Arial", None

        return cls._font_family_from_path(font_path), str(Path(font_path).resolve().parent)

    @classmethod
    def build_ass_filter_value(cls, ass_path: str | Path, language: str = "zh") -> str:
        ass_path = Path(ass_path)
        _, font_dir = cls._resolve_ass_font(language)
        filter_value = f"ass={cls._escape_ffmpeg_filter_value(ass_path)}"
        if font_dir:
            filter_value += f":fontsdir={cls._escape_ffmpeg_filter_value(font_dir)}"
        return filter_value

    @staticmethod
    def _escape_ffmpeg_filter_value(value: str | Path) -> str:
        escaped = str(value).replace("\\", "/")
        for char in (":", "'", "[", "]", ",", ";"):
            escaped = escaped.replace(char, f"\\{char}")
        return escaped

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def burn_subtitles_for_clips(
        self, clips_dir, output_dir, subtitle_translation: str = None,
        clip_filenames=None, clip_titles: dict = None,
    ) -> dict:
        """
        Process MP4+subtitle pairs in clips_dir and write subtitle-burned
        versions to output_dir.

        Args:
            clips_dir: Directory containing .mp4 files and subtitle sidecars.
            output_dir: Directory to write burned clips to.
            subtitle_translation: If set (e.g. "Simplified Chinese"), translate
                the SRT to that language and burn both tracks. Requires api_key.
            clip_filenames: If provided, only process these filenames (scopes
                processing to the current run's clips).
            clip_titles: Optional dict mapping filename → display title. When
                provided, used instead of deriving the title from the filename.

        Returns a summary dict with success, total_clips, successful_clips,
        failed_clips, and output_dir.
        """
        clips_dir = Path(clips_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if clip_filenames is not None:
            mp4_files = sorted(
                clips_dir / name for name in clip_filenames
                if (clips_dir / name).exists()
            )
        else:
            mp4_files = sorted(clips_dir.glob("*.mp4"))

        processed_clips = []
        jobs = []
        total = 0
        for mp4 in mp4_files:
            srt = self.preferred_subtitle_path_for_clip(mp4)
            if not srt.exists():
                logger.warning(f"No SRT for {mp4.name}, skipping subtitle burn")
                continue
            total += 1
            subtitle_source = "whisper" if srt.name.endswith(".whisper.srt") else "original"
            logger.info(f"  Burning subtitles: {mp4.name} ({subtitle_source})")
            jobs.append(
                SubtitlePreparationJob(
                    mp4=mp4,
                    srt=srt,
                    ass_path=(output_dir / mp4.name).with_suffix(".ass"),
                    translated_output_path=(
                        mp4.with_suffix(".translated.srt")
                        if subtitle_translation and self.client
                        else None
                    ),
                )
            )

        if self._should_prepare_translations_in_parallel(subtitle_translation):
            preparation_results = self.prepare_ass_for_clips(jobs, subtitle_translation)
            for result in preparation_results:
                job = result.job
                output = output_dir / job.mp4.name
                try:
                    if result.ok and self._burn_ass(job.mp4, job.ass_path, output):
                        title = (clip_titles or {}).get(job.mp4.name) or job.mp4.stem.replace("_", " ")
                        processed = {"filename": job.mp4.name, "title": title}
                        if job.translated_output_path and Path(job.translated_output_path).exists():
                            processed["translated_subtitle_filename"] = Path(job.translated_output_path).name
                        processed_clips.append(processed)
                finally:
                    job.ass_path.unlink(missing_ok=True)
        else:
            for job in jobs:
                ok = self._process_clip(
                    job.mp4,
                    job.srt,
                    output_dir / job.mp4.name,
                    subtitle_translation,
                    translated_output_path=job.translated_output_path,
                )
                if ok:
                    title = (clip_titles or {}).get(job.mp4.name) or job.mp4.stem.replace("_", " ")
                    processed = {"filename": job.mp4.name, "title": title}
                    if job.translated_output_path and Path(job.translated_output_path).exists():
                        processed["translated_subtitle_filename"] = Path(job.translated_output_path).name
                    processed_clips.append(processed)

        successful = len(processed_clips)
        logger.info(f"  Subtitle burning complete: {successful}/{total} clips")
        return {
            "success": successful > 0,
            "output_dir": str(output_dir),
            "total_clips": total,
            "successful_clips": successful,
            "failed_clips": total - successful,
            "processed_clips": processed_clips,
        }

    @staticmethod
    def preferred_subtitle_path_for_clip(mp4: Path) -> Path:
        """Prefer a Whisper sidecar when present, otherwise fall back to the default SRT."""
        whisper_srt = mp4.with_suffix(".whisper.srt")
        if whisper_srt.exists():
            return whisper_srt
        return mp4.with_suffix(".srt")

    def _should_prepare_translations_in_parallel(self, subtitle_translation: str | None) -> bool:
        return bool(
            subtitle_translation
            and self.client
            and self.subtitle_translation_max_workers > 1
        )

    def _prepare_ass_job(
        self,
        job: SubtitlePreparationJob,
        subtitle_translation: str | None,
    ) -> SubtitlePreparationResult:
        try:
            job.ass_path.parent.mkdir(parents=True, exist_ok=True)
            ok = self.prepare_ass_for_clip(
                job.srt,
                job.ass_path,
                subtitle_translation,
                translated_srt_path=job.translated_srt_path,
                translated_output_path=job.translated_output_path,
            )
            return SubtitlePreparationResult(job=job, ok=ok)
        except Exception as exc:
            logger.warning(f"  Failed to prepare subtitles for {job.mp4.name}: {exc}")
            return SubtitlePreparationResult(job=job, ok=False)

    def prepare_ass_for_clips(
        self,
        jobs: list[SubtitlePreparationJob],
        subtitle_translation: str | None = None,
    ) -> list[SubtitlePreparationResult]:
        """
        Prepare ASS subtitle files for multiple clips, preserving input order.

        When translation is enabled, this can run the per-clip LLM work in
        parallel while leaving video rendering to the caller.
        """
        if not jobs:
            return []

        max_workers = min(self.subtitle_translation_max_workers, len(jobs))
        if not self._should_prepare_translations_in_parallel(subtitle_translation) or max_workers <= 1:
            return [
                self._prepare_ass_job(job, subtitle_translation)
                for job in jobs
            ]

        logger.info(
            "  Preparing translated subtitles for %s clips with %s workers",
            len(jobs),
            max_workers,
        )
        results: list[SubtitlePreparationResult | None] = [None] * len(jobs)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            started_at = {}
            for index, job in enumerate(jobs):
                logger.info(
                    "  Translation prep task %s/%s launched: %s",
                    index + 1,
                    len(jobs),
                    job.mp4.name,
                )
                launched_at = perf_counter()
                future = executor.submit(self._prepare_ass_job, job, subtitle_translation)
                futures[future] = index
                started_at[future] = launched_at
                if index < len(jobs) - 1 and self.subtitle_translation_launch_stagger_seconds > 0:
                    time.sleep(self.subtitle_translation_launch_stagger_seconds)

            for future in as_completed(futures):
                index = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    job = jobs[index]
                    logger.warning(f"  Translation prep task failed for {job.mp4.name}: {exc}")
                    result = SubtitlePreparationResult(job=job, ok=False)
                elapsed = perf_counter() - started_at[future]
                logger.info(
                    "  Translation prep task %s/%s completed in %.1fs: %s",
                    index + 1,
                    len(jobs),
                    elapsed,
                    result.job.mp4.name,
                )
                results[index] = result

        return [
            result if result is not None else SubtitlePreparationResult(job=jobs[index], ok=False)
            for index, result in enumerate(results)
        ]

    def _write_srt_segments(self, srt_path: Path, segments: list[dict[str, str]]) -> None:
        blocks = []
        for index, segment in enumerate(segments, start=1):
            blocks.append(
                "\n".join(
                    [
                        str(index),
                        f"{segment['start']} --> {segment['end']}",
                        segment["text"],
                    ]
                )
            )
        srt_path.write_text("\n\n".join(blocks).strip() + "\n", encoding="utf-8")

    def prepare_ass_for_clip(
        self,
        srt_path: Path,
        ass_path: Path,
        subtitle_translation: str = None,
        translated_srt_path: Path | None = None,
        translated_output_path: Path | None = None,
    ) -> bool:
        """
        Write an ASS subtitle file for a single clip.
        Used by TitleAdder for single-pass title+subtitle burns.

        Args:
            srt_path: Source SRT file.
            ass_path: Destination ASS file to write.
            subtitle_translation: If set, translate and include a second track.
            translated_srt_path: Existing translated sidecar to use if available.
            translated_output_path: Destination to persist newly generated translated subtitles.

        Returns True on success, False if the SRT is empty.
        """
        segments = self._parse_srt(srt_path)
        if not segments:
            return False
        translated = None
        if translated_srt_path and Path(translated_srt_path).exists():
            translated = self._parse_srt(Path(translated_srt_path))
        elif subtitle_translation and self.client:
            translated = self._translate_srt(segments, subtitle_translation)
            if translated and translated_output_path:
                self._write_srt_segments(Path(translated_output_path), translated)
        ass_path.write_text(self._generate_ass(segments, translated), encoding="utf-8")
        return True

    def generate_preview_image(
        self,
        output_path: Path,
        subtitle_translation: str = None,
        original_text: str = "This is how the original subtitle will look.",
        translated_text: str = "这是翻译字幕的预览效果。",
    ) -> bool:
        """
        Render a static subtitle style preview image using the same ASS path
        as final subtitle burning.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        segments = [
            {
                "start": "00:00:00,000",
                "end": "00:00:06,000",
                "text": original_text,
            }
        ]

        translated = None
        layout = self.subtitle_style_config.bilingual_layout
        if layout == "bilingual":
            translated = [
                {
                    "start": "00:00:00,000",
                    "end": "00:00:06,000",
                    "text": translated_text,
                }
            ]
        elif layout == "auto" and subtitle_translation:
            translated = [
                {
                    "start": "00:00:00,000",
                    "end": "00:00:06,000",
                    "text": translated_text,
                }
            ]

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            background_path = tmpdir_path / "preview_background.png"
            ass_path = tmpdir_path / "preview.ass"
            self._create_preview_background(background_path)
            ass_path.write_text(self._generate_ass(segments, translated), encoding="utf-8")
            return self._render_ass_preview(background_path, ass_path, output_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_clip(
        self,
        mp4: Path,
        srt: Path,
        output: Path,
        subtitle_translation: str = None,
        translated_srt_path: Path | None = None,
        translated_output_path: Path | None = None,
    ) -> bool:
        """Generate ASS + burn into output MP4."""
        ass_path = output.with_suffix(".ass")
        ok = self.prepare_ass_for_clip(
            srt,
            ass_path,
            subtitle_translation,
            translated_srt_path=translated_srt_path,
            translated_output_path=translated_output_path,
        )
        if not ok:
            logger.warning(f"  Skipping {mp4.name}: no subtitle segments found")
            return False
        success = self._burn_ass(mp4, ass_path, output)
        ass_path.unlink(missing_ok=True)
        return success

    def _parse_srt(self, srt_path: Path) -> list:
        """Parse SRT file into list of {start, end, text} dicts."""
        return self._parse_srt_text(srt_path.read_text(encoding="utf-8"))

    def _parse_srt_text(self, text: str) -> list:
        """Parse SRT text into list of {start, end, text} dicts.

        Clips each segment's end to the next segment's start to prevent
        overlapping subtitle entries (common in Whisper-generated SRTs).
        """
        segments = []
        for block in re.split(r"\n\s*\n", text.strip()):
            lines = block.strip().splitlines()
            if len(lines) < 3:
                continue
            m = re.match(
                r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})",
                lines[1],
            )
            if not m:
                continue
            segments.append(
                {
                    "start": m.group(1),
                    "end": m.group(2),
                    "text": " ".join(lines[2:]),
                }
            )
        # Clip each segment's end to the start of the next to remove overlaps
        for i in range(len(segments) - 1):
            if segments[i]["end"] > segments[i + 1]["start"]:
                segments[i]["end"] = segments[i + 1]["start"]
        return segments

    def _extract_json_array(self, text: str) -> list | None:
        cleaned = text.strip()
        candidates = [cleaned]

        fenced_json = re.search(r"```json\s*(\[.*?\])\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if fenced_json:
            candidates.append(fenced_json.group(1))

        fenced = re.search(r"```\s*(\[.*?\])\s*```", cleaned, re.DOTALL)
        if fenced:
            candidates.append(fenced.group(1))

        for candidate in candidates:
            try:
                payload = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, list):
                return payload

        decoder = json.JSONDecoder()
        start = cleaned.find("[")
        if start != -1:
            try:
                payload, _ = decoder.raw_decode(cleaned[start:])
            except json.JSONDecodeError:
                return None
            if isinstance(payload, list):
                return payload

        return None

    def _parse_translation_json(self, text: str, expected_count: int) -> list[str] | None:
        """
        Parse translation output in the form:
          [{"id": 1, "translation": "..."}, ...]
        Returns a list of translated strings ordered by id, or None on failure.
        """
        payload = self._extract_json_array(text)
        if payload is None or len(payload) != expected_count:
            return None

        translations_by_id = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            if "id" not in item or "translation" not in item:
                return None
            line_id = item["id"]
            translated_text = item["translation"]
            if not isinstance(line_id, int):
                return None
            if not isinstance(translated_text, str):
                return None
            idx = line_id
            if idx < 1 or idx > expected_count:
                return None
            translations_by_id[idx] = translated_text.strip()

        if len(translations_by_id) != expected_count:
            return None

        return [translations_by_id[i] for i in range(1, expected_count + 1)]

    def _translate_srt(self, segments: list, target_lang: str) -> list | None:
        """
        Translate subtitle text lines via LLM while keeping SRT timing/structure local.
        Returns translated segments on success, None on failure (caller burns original-only).
        """
        numbered_lines = [
            {
                "id": i,
                "text": seg["text"].replace(chr(10), " ").strip(),
            }
            for i, seg in enumerate(segments, 1)
        ]
        n = len(segments)
        prompt = (
            f"Translate the following subtitle lines to {target_lang}.\n"
            f"The input contains exactly {n} subtitle lines.\n"
            "Input JSON:\n"
            f"{json.dumps(numbered_lines, ensure_ascii=False)}\n\n"
            "Rules:\n"
            "- Return valid JSON only.\n"
            "- Return exactly one object per input line.\n"
            "- Keep every numeric id exactly the same.\n"
            '- Use this schema exactly: [{"id": 1, "translation": "..."}]\n'
            "- Translate only the text field.\n"
            "- Keep each translation on a single line.\n"
            "- Do not merge lines, split lines, add commentary, add markdown, or return timestamps."
        )
        try:
            response = self.client.simple_chat(prompt, model=self.model, temperature=0)
            translated_texts = self._parse_translation_json(response, len(segments))
            if translated_texts is None:
                logger.warning(
                    "Translation returned malformed JSON payload; burning original subtitles only."
                )
                return None

            return [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": translated_texts[i],
                }
                for i, seg in enumerate(segments)
            ]
        except Exception as e:
            logger.warning(f"Translation failed ({e}); burning original subtitles only.")
            return None

    def _srt_time_to_ass(self, t: str) -> str:
        """Convert SRT time 'HH:MM:SS,mmm' to ASS time 'H:MM:SS.cc'."""
        h, m, s_ms = t.split(":")
        s, ms = s_ms.split(",")
        cc = int(ms) // 10
        return f"{int(h)}:{m}:{s}.{cc:02d}"

    def _resolve_ass_layout(self, translated: list | None) -> tuple[dict, bool]:
        config = self.subtitle_style_config.normalized()
        preset = SUBTITLE_STYLE_PRESETS[config.preset]
        font_size = SUBTITLE_FONT_SIZE_PRESETS[config.font_size]
        translation_margin = SUBTITLE_VERTICAL_POSITION_PRESETS[config.vertical_position]
        original_margin = max(40, translation_margin - 100)
        has_translation = bool(translated)

        if config.bilingual_layout == "bilingual":
            show_translation = has_translation
        elif config.bilingual_layout == "original_only":
            show_translation = False
        else:
            show_translation = has_translation

        if config.background_style == "none":
            border_style = 1
            shadow = preset.shadow
            outline_color = preset.outline_color
            back_color = "&H00000000"
        elif config.background_style == "light_box":
            border_style = 3
            shadow = 0
            outline_color = "&H80606060"
            back_color = "&H80606060"
        else:
            border_style = 3
            shadow = 0
            outline_color = "&H00000000"
            back_color = "&H00000000"

        return (
            {
                "preset": preset,
                "font_size": font_size,
                "original_margin": original_margin,
                "translation_margin": translation_margin,
                "border_style": border_style,
                "shadow": shadow,
                "outline_color": outline_color,
                "back_color": back_color,
            },
            show_translation,
        )

    def _build_ass_header(self, segments: list, translated: list | None) -> tuple[str, bool]:
        layout, show_translation = self._resolve_ass_layout(translated)
        preset = layout["preset"]
        font_size = layout["font_size"]
        border_style = layout["border_style"]
        shadow = layout["shadow"]
        outline_color = layout["outline_color"]
        back_color = layout["back_color"]
        use_cjk_font = any(self._contains_cjk(seg["text"]) for seg in segments)
        if translated:
            use_cjk_font = use_cjk_font or any(self._contains_cjk(seg["text"]) for seg in translated)
        font_language = "zh" if use_cjk_font else "default"
        font_name, _ = self._resolve_ass_font(font_language)

        if show_translation:
            original_color = preset.original_color
            original_margin = layout["original_margin"]
        else:
            # Preserve the current single-language behavior: one subtitle line
            # using the translation slot/color for better vertical balance.
            original_color = preset.translation_color
            original_margin = layout["translation_margin"]

        original_style = (
            "Style: Original,"
            f"{font_name},{font_size},{original_color},&H000000FF,"
            f"{outline_color},{back_color},{preset.bold},0,0,0,"
            f"100,100,0,0,{border_style},"
            f"{preset.outline},{shadow},{ASS_ALIGNMENT_BOTTOM_CENTER},10,10,{original_margin},1"
        )
        translation_style = (
            "Style: Translation,"
            f"{font_name},{font_size},{preset.translation_color},&H000000FF,"
            f"{outline_color},{back_color},{preset.bold},0,0,0,"
            f"100,100,0,0,{border_style},"
            f"{preset.outline},{shadow},{ASS_ALIGNMENT_BOTTOM_CENTER},10,10,{layout['translation_margin']},1"
        )

        header = "\n".join(
            [
                "[Script Info]",
                "ScriptType: v4.00+",
                f"PlayResX: {ASS_PLAY_RES_X}",
                f"PlayResY: {ASS_PLAY_RES_Y}",
                "ScaledBorderAndShadow: yes",
                "",
                "[V4+ Styles]",
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
                original_style,
                translation_style,
                "",
                "[Events]",
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
            ]
        )
        return header, show_translation

    def _generate_ass(self, segments: list, translated: list = None) -> str:
        """Build full ASS file content. Includes translation track if provided."""
        header, show_translation = self._build_ass_header(segments, translated)
        layout, _ = self._resolve_ass_layout(translated)
        boxed_style = layout["border_style"] == 3
        lines = [header]
        for i, seg in enumerate(segments):
            start = self._srt_time_to_ass(seg["start"])
            end = self._srt_time_to_ass(seg["end"])
            text = _SPEAKER_TAG_RE.sub("", seg["text"].replace("\n", " "))
            if boxed_style:
                text = rf"\h{text}\h"
            lines.append(f"Dialogue: 0,{start},{end},Original,,0,0,0,,{text}")
            if show_translation and translated and i < len(translated):
                tr_text = _SPEAKER_TAG_RE.sub("", translated[i]["text"].replace("\n", " "))
                if tr_text:
                    if boxed_style:
                        tr_text = rf"\h{tr_text}\h"
                    lines.append(f"Dialogue: 0,{start},{end},Translation,,0,0,0,,{tr_text}")
        return "\n".join(lines) + "\n"

    def _create_preview_background(self, output_path: Path) -> None:
        """Create a built-in 1920x1080 sample background for subtitle previews."""
        img = Image.new("RGB", (ASS_PLAY_RES_X, ASS_PLAY_RES_Y), "#12161d")
        draw = ImageDraw.Draw(img)

        for y in range(ASS_PLAY_RES_Y):
            mix = y / max(1, ASS_PLAY_RES_Y - 1)
            r = int(18 + 20 * mix)
            g = int(22 + 38 * mix)
            b = int(29 + 72 * mix)
            draw.line((0, y, ASS_PLAY_RES_X, y), fill=(r, g, b))

        draw.rounded_rectangle((90, 90, 700, 410), radius=40, fill=(28, 37, 52))
        draw.rounded_rectangle((1230, 160, 1830, 470), radius=36, fill=(55, 37, 77))
        draw.rounded_rectangle((180, 620, 1760, 880), radius=46, fill=(24, 29, 34))
        draw.ellipse((1450, 620, 1830, 1000), fill=(219, 116, 44))
        draw.ellipse((120, 700, 380, 960), fill=(76, 145, 255))
        draw.rectangle((0, 930, ASS_PLAY_RES_X, ASS_PLAY_RES_Y), fill=(10, 12, 16))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)

    def _render_ass_preview(self, background: Path, ass: Path, output: Path) -> bool:
        """Render a static preview image with ffmpeg using the generated ASS."""
        tmp_fd, tmp_ass_str = tempfile.mkstemp(suffix=".ass")
        os.close(tmp_fd)
        tmp_ass = Path(tmp_ass_str)
        tmp_bg_video = tmp_ass.with_suffix(".mp4")
        tmp_burned_video = tmp_ass.with_name(f"{tmp_ass.stem}_burned.mp4")
        try:
            tmp_ass.write_bytes(ass.read_bytes())

            background_cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", str(background.resolve()),
                "-t", "2",
                "-pix_fmt", "yuv420p",
                "-an",
                "-y", str(tmp_bg_video.resolve()),
            ]
            background_result = subprocess.run(
                background_cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if background_result.returncode != 0:
                stderr_tail = (background_result.stderr or "")[-500:]
                logger.error(f"ffmpeg preview background video error: {stderr_tail}")
                return False

            burn_cmd = [
                "ffmpeg",
                "-i", str(tmp_bg_video.resolve()),
                "-vf", self.build_ass_filter_value(tmp_ass.name, language="zh"),
                "-pix_fmt", "yuv420p",
                "-an",
                "-y", str(tmp_burned_video.resolve()),
            ]
            burn_result = subprocess.run(
                burn_cmd,
                cwd=str(tmp_ass.parent),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if burn_result.returncode != 0:
                stderr_tail = (burn_result.stderr or "")[-500:]
                logger.error(f"ffmpeg preview subtitle error: {stderr_tail}")
                return False

            frame_cmd = [
                "ffmpeg",
                "-ss", "0.5",
                "-i", str(tmp_burned_video.resolve()),
                "-frames:v", "1",
                "-update", "1",
                "-y", str(output.resolve()),
            ]
            frame_result = subprocess.run(
                frame_cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if frame_result.returncode != 0:
                stderr_tail = (frame_result.stderr or "")[-500:]
                logger.error(f"ffmpeg preview frame extraction error: {stderr_tail}")
            return frame_result.returncode == 0
        finally:
            tmp_ass.unlink(missing_ok=True)
            tmp_bg_video.unlink(missing_ok=True)
            tmp_burned_video.unlink(missing_ok=True)

    def _burn_ass(self, mp4: Path, ass: Path, output: Path) -> bool:
        """Run ffmpeg to burn the ASS subtitle file into the video."""
        # ffmpeg's ass= filter struggles with long paths — copy to a short /tmp path
        tmp_fd, tmp_ass_str = tempfile.mkstemp(suffix=".ass")
        os.close(tmp_fd)
        tmp_ass = Path(tmp_ass_str)
        try:
            tmp_ass.write_bytes(ass.read_bytes())
            cmd = [
                "ffmpeg",
                "-i", str(mp4.resolve()),
                "-vf", self.build_ass_filter_value(tmp_ass.name, language="zh"),
                "-c:a", "copy",
                "-y", str(output.resolve()),
            ]
            r = subprocess.run(
                cmd,
                cwd=str(tmp_ass.parent),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if r.returncode != 0:
                stderr_tail = (r.stderr or "")[-500:]
                logger.error(f"ffmpeg subtitle error for {mp4.name}: {stderr_tail}")
            return r.returncode == 0
        finally:
            tmp_ass.unlink(missing_ok=True)
