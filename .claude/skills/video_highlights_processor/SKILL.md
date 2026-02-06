---
name: "video_highlights_processor"
description: "Processes videos to identify engaging moments, generate transcripts, and create highlight clips with artistic titles. Use when user needs to extract highlights from long videos or livestreams, process Bilibili/YouTube URLs or local video files, generate transcripts via Whisper, analyze content for engaging moments, or create short-form clips with styled titles and cover images."
---

# Video Highlights Processor Skill

Run the video orchestrator to process videos and extract engaging highlights.

## Execution

Run from the project root using `uv` (the project uses `uv` with `pyproject.toml` and `uv.lock`):

```bash
uv run python video_orchestrator.py [options] <source>
```

Where `<source>` is a video URL (Bilibili/YouTube) or local file path (MP4, WebM, AVI, MOV, MKV).

## CLI Reference

### Required

| Argument | Description |
|---|---|
| `source` | Video URL or local file path |

### Optional

| Flag | Default | Description |
|---|---|---|
| `-o`, `--output <dir>` | `processed_videos` | Output directory |
| `--whisper-model <model>` | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large`, `turbo` |
| `--max-duration <minutes>` | `20.0` | Max duration before auto-splitting |
| `--browser <browser>` | `firefox` | Browser for cookie extraction: `chrome`, `firefox`, `edge`, `safari` |
| `--artistic-style <style>` | `fire_flame` | Title style: `gradient_3d`, `neon_glow`, `metallic_gold`, `rainbow_3d`, `crystal_ice`, `fire_flame`, `metallic_silver`, `glowing_plasma`, `stone_carved`, `glass_transparent` |
| `--language <lang>` | `zh` | Output language: `zh` (Chinese), `en` (English) |
| `--llm-provider <provider>` | `qwen` | LLM provider: `qwen`, `openrouter` |
| `-f`, `--filename <template>` | — | Custom filename template |

### Flags

| Flag | Description |
|---|---|
| `--force-whisper` | Ignore platform subtitles, use Whisper |
| `--skip-download` | Use existing downloaded video |
| `--skip-analysis` | Skip analysis, use existing analysis file for clip generation |
| `--use-background` | Include background info (streamer names/nicknames) in analysis prompts |
| `--no-clips` | Disable clip generation |
| `--no-titles` | Disable adding artistic titles to clips |
| `--no-cover` | Disable cover image generation |
| `-v`, `--verbose` | Enable verbose logging |
| `--debug` | Export full prompts sent to LLM (saved to `debug_prompts/`) |
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
6. **Add artistic titles** to clips using `--artistic-style`
7. **Generate cover images** for each highlight

Use `--no-clips`, `--no-titles`, `--no-cover` to skip specific steps. Use `--skip-download` and `--skip-analysis` to resume from intermediate results.

## Output Structure

```
processed_videos/
├── downloads/            # Downloaded videos
├── splits/               # Split video segments
├── clips/                # Highlight clips
│   └── [video_title]/
├── clips_with_titles/    # Clips with artistic titles
│   └── [video_title]/
└── transcripts/          # Generated transcripts
```

## Troubleshooting

| Error | Fix |
|---|---|
| "No API key provided" | Set `QWEN_API_KEY` or `OPENROUTER_API_KEY` env var |
| "Video download failed" | Check network/URL; try different `--browser`; or use local file |
| "Transcript generation failed" | Try larger `--whisper-model` or check audio quality |
| "No engaging moments found" | Try `--force-whisper` for better transcript accuracy |
| "Clip generation failed" | Ensure analysis completed; check for existing analysis file |

