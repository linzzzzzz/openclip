# Video Processing Directory Structure

## Overview

The video orchestrator organizes all outputs in a clean, hierarchical directory structure under the main output directory (default: `processed_videos`).

## Directory Layout

```
processed_videos/
├── downloads/              # Downloaded videos and metadata
│   ├── BV1234567890_video_title/
│   │   ├── video_title.mp4
│   │   ├── video_title.srt
│   │   ├── video_title.ai-zh.srt
│   │   ├── video_title.info.json
│   │   └── video_title.jpg
│   └── ...
│
├── splits/                 # Split video parts (for videos > 20 min)
│   ├── video_title_split/
│   │   ├── video_title_part01.mp4
│   │   ├── video_title_part01.srt
│   │   ├── video_title_part02.mp4
│   │   ├── video_title_part02.srt
│   │   ├── highlights_part01.json
│   │   ├── highlights_part02.json
│   │   └── top_engaging_moments.json
│   └── ...
│
├── clips/                  # Generated clips from engaging moments
│   ├── rank_01_clip_title.mp4
│   ├── rank_02_clip_title.mp4
│   ├── rank_03_clip_title.mp4
│   ├── rank_04_clip_title.mp4
│   ├── rank_05_clip_title.mp4
│   └── engaging_moments_summary.md
│
└── clips_with_titles/      # Clips with artistic titles added
    ├── artistic_fire_flame_rank_01_clip_title.mp4
    ├── artistic_fire_flame_rank_02_clip_title.mp4
    ├── artistic_fire_flame_rank_03_clip_title.mp4
    ├── artistic_fire_flame_rank_04_clip_title.mp4
    ├── artistic_fire_flame_rank_05_clip_title.mp4
    └── README.md
```

## Directory Descriptions

### downloads/
- Contains original downloaded videos from Bilibili
- Includes video files, subtitles, metadata, and thumbnails
- Organized by video BV ID and title
- Preserves all original content for reference

### splits/
- Created when videos exceed 20 minutes duration
- Contains video parts split at 20-minute intervals
- Includes corresponding subtitle files for each part
- Stores analysis results (highlights and top moments)
- Each video gets its own subdirectory

### clips/
- **NEW LOCATION**: Now under `processed_videos/clips/`
- Contains short clips extracted from engaging moments
- Clips are ranked by engagement level (rank_01 to rank_05)
- Includes a summary markdown file with clip details
- Ready for sharing on social media

### clips_with_titles/
- **NEW LOCATION**: Now under `processed_videos/clips_with_titles/`
- Contains clips with artistic titles overlaid
- Title style prefix indicates the artistic style used
- Same ranking system as clips directory
- Includes README with style information

## Custom Output Directory

You can specify a custom output directory:

```bash
# Use custom directory
uv run python video_orchestrator.py -o my_videos "https://..."

# Results in:
my_videos/
├── downloads/
├── splits/
├── clips/
└── clips_with_titles/
```

## Benefits of This Structure

1. **Organization**: All outputs for a project in one place
2. **Clarity**: Clear separation between different processing stages
3. **Portability**: Easy to move or backup entire project
4. **Scalability**: Can process multiple videos without conflicts
5. **Clean Workspace**: No scattered directories in project root

## Migration from Old Structure

If you have existing clips in the old locations:
- Old: `engaging_clips/` → New: `processed_videos/clips/`
- Old: `engaging_clips_with_titles/` → New: `processed_videos/clips_with_titles/`

The orchestrator will automatically use the new structure for all new processing.

## Example Usage

```bash
# Process video with full pipeline
export QWEN_API_KEY=your_key
uv run python video_orchestrator.py \
  --use-background \
  --artistic-style fire_flame \
  "https://www.bilibili.com/video/BV1234567890"

# Results will be organized in:
# processed_videos/downloads/BV1234567890_title/
# processed_videos/splits/title_split/
# processed_videos/clips/
# processed_videos/clips_with_titles/
```

## Notes

- Directories are created automatically as needed
- Empty directories are not created if features are disabled
- All paths are relative to the output directory
- Directory structure is consistent across all processing modes
