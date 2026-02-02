# Skip Analysis Feature

## Overview

Added `--skip-analysis` flag to allow skipping the AI engaging moments analysis step while still being able to generate clips from an existing `top_engaging_moments.json` file.

## Use Cases

1. **Reprocess with different clip settings**: Skip analysis but regenerate clips with different parameters
2. **Save API costs**: Reuse existing analysis without calling the Qwen API again
3. **Faster iteration**: Quickly test different artistic styles without re-analyzing
4. **Offline processing**: Generate clips when API is unavailable but analysis file exists

## Usage

### Skip analysis and use existing analysis file

```bash
# Will look for existing top_engaging_moments.json and generate clips
uv run python video_orchestrator.py --skip-analysis "https://www.bilibili.com/video/BV1234567890"
```

### Skip analysis with custom artistic style

```bash
# Reuse analysis, generate clips with neon glow titles
uv run python video_orchestrator.py --skip-analysis --artistic-style neon_glow "URL"
```

### Skip analysis, clips only (no titles)

```bash
# Just regenerate clips without titles
uv run python video_orchestrator.py --skip-analysis --no-titles "URL"
```

## How It Works

### 1. Initialization

When `--skip-analysis` is set:
- Engaging moments analyzer is NOT initialized
- Clip generator and title adder remain enabled (if not explicitly disabled)
- Logs: "🧠 Engaging moments analysis: skipped (--skip-analysis)"

### 2. Processing Pipeline

During video processing:

**Step 4: Analysis**
- If `--skip-analysis`: Calls `_find_existing_analysis()` to locate existing analysis file
- Searches in the transcript directory for `top_engaging_moments.json`
- If found: Uses it for clip generation
- If not found: Logs warning and skips clip generation

**Step 5: Clip Generation**
- Proceeds if analysis file is available (either from analysis or existing file)
- Uses the same logic regardless of analysis source

**Step 6: Title Addition**
- Proceeds if clips were successfully generated

### 3. Finding Existing Analysis

The `_find_existing_analysis()` method:
1. Determines search directory based on video structure:
   - For split videos: Uses transcript parts directory
   - For single videos: Uses transcript directory
2. Looks for `top_engaging_moments.json`
3. Returns analysis metadata if found

## Examples

### Example 1: Reprocess with different style

```bash
# First run: Full analysis
export QWEN_API_KEY=your_key
uv run python video_orchestrator.py "URL"

# Second run: Skip analysis, use crystal_ice style
uv run python video_orchestrator.py --skip-analysis --artistic-style crystal_ice "URL"

# Third run: Skip analysis, use neon_glow style
uv run python video_orchestrator.py --skip-analysis --artistic-style neon_glow "URL"
```

### Example 2: Regenerate clips only

```bash
# Regenerate clips without re-analyzing or adding titles
uv run python video_orchestrator.py --skip-analysis --no-titles "URL"
```

### Example 3: Offline processing

```bash
# When API is unavailable but you have existing analysis
uv run python video_orchestrator.py --skip-analysis "URL"
```

## Configuration

### CLI Arguments

- `--skip-analysis`: Skip engaging moments analysis step
- Works with: `--no-clips`, `--no-titles`, `--artistic-style`
- Independent of: `QWEN_API_KEY` (not required when skipping)

### Programmatic Usage

```python
orchestrator = VideoOrchestrator(
    skip_analysis=True,      # Skip analysis
    generate_clips=True,     # Still generate clips
    add_titles=True,         # Still add titles
    artistic_style="neon_glow"
)
```

## Behavior Matrix

| Flag Combination | Analysis | Clips | Titles | Notes |
|-----------------|----------|-------|--------|-------|
| (none) | ✅ | ✅ | ✅ | Full pipeline |
| `--skip-analysis` | ❌ | ✅* | ✅* | *If existing file found |
| `--no-clips` | ✅ | ❌ | ❌ | Analysis only |
| `--no-titles` | ✅ | ✅ | ❌ | Clips without titles |
| `--skip-analysis --no-clips` | ❌ | ❌ | ❌ | Download/transcribe only |
| `--skip-analysis --no-titles` | ❌ | ✅* | ❌ | Clips only from existing |

## Logging

### When analysis is skipped:

```
🧠 Engaging moments analysis: skipped (--skip-analysis)
🎬 Clip generation: enabled
🎨 Title adding: enabled (style: crystal_ice)
...
🧠 Step 4: Skipping engaging moments analysis (--skip-analysis)
   Found existing analysis file: top_engaging_moments.json
🎬 Step 5: Generating clips from engaging moments...
```

### When no existing file found:

```
🧠 Step 4: Skipping engaging moments analysis (--skip-analysis)
   No existing analysis file found in: processed_videos/splits/video_split
⚠️  Clip generation enabled but no analysis file found
```

## Error Handling

- **No existing file**: Logs warning, skips clip generation gracefully
- **Invalid analysis file**: Error caught and logged, processing continues
- **Missing video files**: Handled by clip generator (skips individual clips)

## Benefits

1. **Cost savings**: Avoid repeated API calls for same video
2. **Time savings**: Skip 2-3 minute analysis step
3. **Flexibility**: Try different clip/title settings quickly
4. **Offline capability**: Work without API access
5. **Debugging**: Isolate clip generation issues

## Limitations

- Requires existing `top_engaging_moments.json` file
- Cannot modify analysis results (use existing as-is)
- File must be in expected location (transcript directory)

## Future Enhancements

Potential improvements:
1. Allow specifying custom analysis file path
2. Support partial re-analysis (specific segments only)
3. Cache analysis results with versioning
4. Merge multiple analysis files
5. Analysis file validation before use
