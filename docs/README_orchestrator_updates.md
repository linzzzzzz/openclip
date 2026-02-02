# Video Orchestrator Updates

## New Features

The video orchestrator now includes two additional processing steps:

### 1. Clip Generation (Step 5)
Automatically generates video clips from the top engaging moments identified by the AI analysis.

**Module**: `clip_generator.py`
**Class**: `ClipGenerator`

**Features**:
- Extracts clips based on timestamps from engaging moments analysis
- Uses FFmpeg for fast, high-quality clip extraction
- Generates descriptive filenames based on moment titles
- Creates a summary markdown file with clip details

### 2. Title Addition (Step 6)
Adds artistic Chinese text titles to the generated clips.

**Module**: `title_adder.py`
**Class**: `TitleAdder`

**Features**:
- Multiple artistic styles: gradient_3d, neon_glow, metallic_gold, rainbow_3d, crystal_ice
- Automatic Chinese font detection
- Professional visual effects (gradients, shadows, glows)
- Maintains original video layout with black bars for titles

## Usage

### Basic Usage (Full Pipeline)
```bash
export QWEN_API_KEY=your_api_key
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

This will:
1. Download the video
2. Split if > 20 minutes
3. Generate/use transcripts
4. Analyze engaging moments
5. Generate clips from top moments
6. Add artistic titles to clips

### Custom Artistic Style
```bash
uv run python video_orchestrator.py --artistic-style neon_glow "URL"
```

Available styles:
- `gradient_3d` - Pink to blue gradient with 3D shadows
- `neon_glow` - Cyan neon light effect
- `metallic_gold` - Gold metallic finish
- `rainbow_3d` - Rainbow gradient with 3D depth
- `crystal_ice` - Ice blue crystal effect (default)

### Disable Specific Steps
```bash
# Analysis only, no clips
uv run python video_orchestrator.py --no-clips --no-titles "URL"

# Generate clips but no titles
uv run python video_orchestrator.py --no-titles "URL"

# Skip clip generation
uv run python video_orchestrator.py --no-clips "URL"
```

### Process Local Video
```bash
uv run python video_orchestrator.py "/path/to/video.mp4"
```

## Output Structure

```
processed_videos/
├── downloads/              # Downloaded videos
├── splits/                 # Split video parts
│   └── video_split/
│       ├── video_part01.mp4
│       ├── video_part02.mp4
│       ├── highlights_part01.json
│       ├── highlights_part02.json
│       └── top_engaging_moments.json
engaging_clips/             # Generated clips (Step 5)
├── rank_01_clip_title.mp4
├── rank_02_clip_title.mp4
└── engaging_moments_summary.md
engaging_clips_with_titles/ # Clips with titles (Step 6)
├── artistic_crystal_ice_rank_01_clip_title.mp4
├── artistic_crystal_ice_rank_02_clip_title.mp4
└── README.md
```

## Architecture

### New Modules

**clip_generator.py**
- `ClipGenerator` class handles clip extraction
- Uses FFmpeg subprocess for video processing
- Reads `top_engaging_moments.json` for timestamps
- Generates clips with sanitized filenames

**title_adder.py**
- `TitleAdder` class manages title overlay
- `ArtisticTextRenderer` creates styled text images
- Uses MoviePy for video composition
- Uses PIL/Pillow for text rendering with effects

### Integration Points

The orchestrator integrates these components in the `process_video()` method:

```python
# Step 4: Analyze engaging moments
engaging_result = await self._analyze_engaging_moments(...)

# Step 5: Generate clips (if enabled)
if self.clip_generator and engaging_result.get('aggregated_file'):
    clip_result = self.clip_generator.generate_clips_from_analysis(...)
    
# Step 6: Add titles (if enabled)
if self.title_adder and clip_result.get('success'):
    title_result = self.title_adder.add_titles_to_clips(...)
```

### Configuration

The orchestrator constructor now accepts:
- `generate_clips` (bool): Enable/disable clip generation
- `add_titles` (bool): Enable/disable title addition
- `artistic_style` (str): Style for artistic titles

## Dependencies

All dependencies are managed via `uv` and defined in `pyproject.toml`:
- `moviepy` - Video editing and composition
- `Pillow` - Image processing and text rendering
- `numpy` - Fast array operations for gradients
- `ffmpeg` - Video processing (system dependency)

## Error Handling

Both modules include comprehensive error handling:
- Missing video files are skipped with warnings
- FFmpeg errors are caught and logged
- MoviePy errors don't crash the pipeline
- Results include success/failure status

## Performance

**Optimizations**:
- Font caching to avoid reloading
- NumPy for fast gradient generation
- FFmpeg with ultrafast preset
- Parallel processing where possible

**Typical Processing Time**:
- Clip generation: ~2-5 seconds per clip
- Title addition: ~10-15 seconds per clip (depends on video length)

## Future Enhancements

Potential improvements:
- Batch processing multiple videos
- Custom title templates
- More artistic styles
- GPU acceleration for rendering
- Preview mode before final render
