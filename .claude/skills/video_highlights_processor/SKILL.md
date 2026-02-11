---
name: "video_highlights_processor"
description: "Processes videos to identify engaging moments, generate transcripts, and create highlight clips with artistic titles and custom cover images. Use when user needs to: extract highlights from long videos or livestreams, clip or cut best moments from videos, process Bilibili/YouTube URLs or local video files, generate transcripts via Whisper, analyze content for engaging moments, create short-form clips with styled titles and covers, adjust cover text position, or find and export memorable scenes from recordings."
---

# Video Highlights Processor Skill

Run the video orchestrator to process videos and extract engaging highlights.

## Execution

Run from the project root using `uv` (the project uses `uv` with `pyproject.toml` and `uv.lock`):

```bash
uv run python video_orchestrator.py [options] <source>
```

Where `<source>` is a video URL (Bilibili/YouTube) or local file path (MP4, WebM, AVI, MOV, MKV).

For local files with existing subtitles, place the `.srt` file in the same directory with the same filename (e.g. `video.mp4` → `video.srt`).

## CLI Reference

### Required

| Argument | Description |
|---|---|
| `source` | Video URL or local file path |

### Optional

| Flag | Default | Description |
|---|---|---|
| `-o`, `--output <dir>` | `processed_videos` | Output directory |
| `--max-duration <minutes>` | `20.0` | Max duration before auto-splitting |
| `--max-clips <n>` | `5` | Maximum number of highlight clips |
| `--browser <browser>` | `firefox` | Browser for cookies: `chrome`, `firefox`, `edge`, `safari` |
| `--title-style <style>` | `fire_flame` | Title style: `gradient_3d`, `neon_glow`, `metallic_gold`, `rainbow_3d`, `crystal_ice`, `fire_flame`, `metallic_silver`, `glowing_plasma`, `stone_carved`, `glass_transparent` |
| `--cover-text-location <loc>` | `center` | Cover text position: `top`, `upper_middle`, `bottom`, `center` |
| `--language <lang>` | `zh` | Output language: `zh` (Chinese), `en` (English) |
| `--llm-provider <provider>` | `qwen` | LLM provider: `qwen`, `openrouter` |
| `-f`, `--filename <template>` | — | yt-dlp template: `%(title)s`, `%(uploader)s`, `%(id)s`, etc. |

### Flags

| Flag | Description |
|---|---|
| `--force-whisper` | Ignore platform subtitles, use Whisper |
| `--skip-download` | Use existing downloaded video |
| `--skip-analysis` | Skip analysis, use existing analysis file for clip generation |
| `--use-background` | Include background info (streamer names/nicknames) in analysis prompts |
| `--skip-clips` | Skip clip generation |
| `--skip-titles` | Skip adding artistic titles to clips |
| `--skip-cover` | Skip cover image generation |
| `-v`, `--verbose` | Enable verbose logging |
| `--debug` | Export full prompts sent to LLM (saved to `debug_prompts/`) |

### Custom Filename Template (`-f`)

Uses yt-dlp template syntax. Common variables: `%(title)s`, `%(uploader)s`, `%(upload_date)s`, `%(id)s`, `%(ext)s`, `%(duration)s`.

Example: `-f "%(upload_date)s_%(title)s.%(ext)s"`

### Environment Variables

Set the appropriate API key for the chosen `--llm-provider`:

- `QWEN_API_KEY` — for `--llm-provider qwen`
- `OPENROUTER_API_KEY` — for `--llm-provider openrouter`

## Workflow

The orchestrator runs this pipeline automatically:

1. **Download** video and platform subtitles (Bilibili/YouTube) or accept local file
2. **Split** videos longer than `--max-duration` into segments
3. **Transcribe** using platform subtitles or Whisper AI (fallback or `--force-whisper`)
4. **Analyze** transcript for engaging moments via LLM
5. **Generate clips** from identified moments
6. **Add artistic titles** to clips using `--title-style`
7. **Generate cover images** for each highlight

Use `--skip-clips`, `--skip-titles`, `--skip-cover` to skip specific steps. Use `--skip-download` and `--skip-analysis` to resume from intermediate results.

## Output Structure

```
processed_videos/{video_name}/
├── downloads/            # Original video, subtitles, and metadata
├── splits/               # Split parts and AI analysis results
├── clips/                # Generated highlight clips and summary
└── clips_with_titles/    # Final clips with artistic titles and cover images
```

## Option Selection Guide

**Whisper model** — Default `base` works for clear audio. Use `small` for background noise, multiple speakers, or accents. Use `turbo` for speed + accuracy. Use `large`/`medium` only when transcript quality is critical.

**`--force-whisper`** — Use when platform subtitles are auto-generated (often inaccurate), when "no engaging moments found" occurs (better transcripts improve analysis), or for non-native language content where platform captions are unreliable.

**`--use-background`** — Use for content featuring recurring personalities (streamers, hosts) where nicknames and community references matter. Reads from `prompts/background/background.md`.

**`--max-duration`** — Default 20 min works for most videos. Decrease to 10-15 for very long livestreams (2+ hours) to keep segments manageable. Increase to 30-40 for shorter content to avoid unnecessary splits. Splitting happens at subtitle boundaries to preserve coherence.

**Multi-part analysis** — Videos that get split are analyzed per-segment, then aggregated to the top 5 engaging moments across all segments.

## Troubleshooting

| Error | Fix |
|---|---|
| "No API key provided" | Set `QWEN_API_KEY` or `OPENROUTER_API_KEY` env var |
| "Video download failed" | Check network/URL; try different `--browser`; or use local file |
| "Transcript generation failed" | Try larger `--whisper-model` or check audio quality |
| "No engaging moments found" | Try `--force-whisper` for better transcript accuracy |
| "Clip generation failed" | Ensure analysis completed; check for existing analysis file |

