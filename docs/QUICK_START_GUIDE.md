# Quick Start Guide - Video Orchestrator with Clip Generation

## Prerequisites

1. **Set up environment**:
   ```bash
   # Ensure uv is installed
   # All dependencies are managed via uv
   ```

2. **Set API key** (required for clip generation):
   ```bash
   export QWEN_API_KEY=your_api_key_here
   ```

3. **Verify FFmpeg** is installed:
   ```bash
   ffmpeg -version
   ```

## Basic Usage

### Full Pipeline (Recommended)

Process a video with all features enabled:

```bash
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

This will:
1. ✅ Download video from Bilibili
2. ✅ Split if longer than 20 minutes
3. ✅ Use Bilibili subtitles (or generate with Whisper)
4. ✅ Analyze engaging moments with AI
5. ✅ Generate clips from top moments
6. ✅ Add artistic titles to clips

### Custom Artistic Style

Choose from 5 artistic styles:

```bash
# Crystal ice effect (default)
uv run python video_orchestrator.py "URL"

# Neon glow effect
uv run python video_orchestrator.py --artistic-style neon_glow "URL"

# Metallic gold effect
uv run python video_orchestrator.py --artistic-style metallic_gold "URL"

# Rainbow 3D effect
uv run python video_orchestrator.py --artistic-style rainbow_3d "URL"

# Gradient 3D effect
uv run python video_orchestrator.py --artistic-style gradient_3d "URL"
```

### Selective Processing

```bash
# Analysis only (no clips or titles)
uv run python video_orchestrator.py --no-clips --no-titles "URL"

# Generate clips but skip titles
uv run python video_orchestrator.py --no-titles "URL"

# Skip clip generation
uv run python video_orchestrator.py --no-clips "URL"
```

### Process Local Video

```bash
uv run python video_orchestrator.py "/path/to/your/video.mp4"
```

### Advanced Options

```bash
# Force Whisper transcription (ignore Bilibili subtitles)
uv run python video_orchestrator.py --force-whisper "URL"

# Custom split duration (default: 20 minutes)
uv run python video_orchestrator.py --max-duration 15 "URL"

# Use different Whisper model
uv run python video_orchestrator.py --whisper-model small "URL"

# Custom output directory
uv run python video_orchestrator.py -o "my_output" "URL"

# Skip download (use existing video)
uv run python video_orchestrator.py --skip-download "URL"
```

## Output Structure

After processing, you'll find:

```
processed_videos/
├── downloads/
│   └── BV1234567890_video_title/
│       ├── video_title.mp4
│       └── video_title.srt
└── splits/
    └── video_title_split/
        ├── video_title_part01.mp4
        ├── video_title_part02.mp4
        ├── highlights_part01.json
        ├── highlights_part02.json
        └── top_engaging_moments.json

engaging_clips/
├── rank_01_moment_title.mp4
├── rank_02_moment_title.mp4
├── rank_03_moment_title.mp4
├── rank_04_moment_title.mp4
├── rank_05_moment_title.mp4
└── engaging_moments_summary.md

engaging_clips_with_titles/
├── artistic_crystal_ice_rank_01_moment_title.mp4
├── artistic_crystal_ice_rank_02_moment_title.mp4
├── artistic_crystal_ice_rank_03_moment_title.mp4
├── artistic_crystal_ice_rank_04_moment_title.mp4
├── artistic_crystal_ice_rank_05_moment_title.mp4
└── README.md
```

## Testing

Test the integration with existing data:

```bash
uv run python test_orchestrator_integration.py
```

This will:
- Test clip generation
- Test title addition
- Verify output files
- Create test outputs in `test_clips/` and `test_clips_with_titles/`

## Troubleshooting

### No clips generated

**Problem**: Orchestrator runs but no clips are created.

**Solutions**:
1. Check if `QWEN_API_KEY` is set:
   ```bash
   echo $QWEN_API_KEY
   ```
2. Verify engaging moments analysis completed:
   - Look for `top_engaging_moments.json` in splits directory
3. Check logs for errors

### Title addition fails

**Problem**: Clips are generated but titles fail to add.

**Solutions**:
1. Verify MoviePy is installed:
   ```bash
   uv run python -c "import moviepy; print('OK')"
   ```
2. Check if Chinese fonts are available:
   - macOS: Should auto-detect STHeiti or PingFang
   - Windows: Should auto-detect SimSun or Microsoft YaHei
3. Check disk space for video processing

### FFmpeg errors

**Problem**: Clip generation fails with FFmpeg errors.

**Solutions**:
1. Verify FFmpeg installation:
   ```bash
   which ffmpeg
   ffmpeg -version
   ```
2. Install FFmpeg if missing:
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`
   - Windows: Download from ffmpeg.org

### Memory issues

**Problem**: Process crashes or runs out of memory.

**Solutions**:
1. Reduce max duration for splits:
   ```bash
   uv run python video_orchestrator.py --max-duration 10 "URL"
   ```
2. Process clips in batches (disable titles first):
   ```bash
   uv run python video_orchestrator.py --no-titles "URL"
   # Then add titles separately
   ```

## Performance Tips

1. **Use ultrafast preset** (already default):
   - Faster encoding, slightly larger files
   
2. **Process shorter segments**:
   ```bash
   --max-duration 10  # Split into 10-minute chunks
   ```

3. **Skip unnecessary steps**:
   ```bash
   --no-titles  # If you don't need titles
   ```

4. **Use existing downloads**:
   ```bash
   --skip-download  # Reuse previously downloaded videos
   ```

## Examples

### Example 1: Quick test with local video

```bash
# Process a local video file
uv run python video_orchestrator.py ~/Videos/test.mp4
```

### Example 2: Full Bilibili video processing

```bash
# Set API key
export QWEN_API_KEY=sk-xxxxx

# Process with neon glow titles
uv run python video_orchestrator.py \
  --artistic-style neon_glow \
  "https://www.bilibili.com/video/BV1wT6GBBEPp"
```

### Example 3: Analysis only (no clips)

```bash
# Just analyze, don't generate clips
uv run python video_orchestrator.py \
  --no-clips \
  --no-titles \
  "https://www.bilibili.com/video/BV1234567890"
```

### Example 4: Reprocess with different style

```bash
# First run: generate clips
uv run python video_orchestrator.py --no-titles "URL"

# Second run: add titles with different style
# (manually run title_adder.py on existing clips)
```

## Next Steps

1. **Review outputs**: Check `engaging_clips_with_titles/` for final videos
2. **Customize styles**: Modify `title_adder.py` to add new artistic styles
3. **Batch process**: Create a script to process multiple videos
4. **Share clips**: Upload to social media or video platforms

## Support

For issues or questions:
1. Check logs in console output
2. Review error messages
3. Verify all dependencies are installed
4. Test with a short video first
