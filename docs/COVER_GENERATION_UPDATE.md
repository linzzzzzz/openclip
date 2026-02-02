# Cover Generation Update - Multiple Covers per Engaging Moment

## ✅ Implementation Complete

Successfully updated the cover generation feature to create **one cover image for each engaging moment** instead of just one cover for the entire video.

## What Changed

### Previous Behavior
- Generated **1 cover** for the entire video
- Used video title as main text
- Used top engaging moment as subtitle
- Saved in video directory

### New Behavior
- Generates **multiple covers** - one for each engaging moment
- Uses video title as main text
- Uses **each moment's title** as subtitle
- Extracts frame from the **specific timestamp** of each moment
- Saves all covers in `processed_videos/clips_with_titles/` directory
- Naming format: `cover_rank_{rank:02d}_{moment_title}.jpg`

## Cover Image Details

### For Each Engaging Moment:
1. **Extracts frame** from the correct video part at the moment's start time
2. **Main text (red)**: Video title (e.g., "旭旭宝宝1月31日直播回放")
3. **Subtitle (yellow)**: Engaging moment title (e.g., "宝哥与大斌子洗脚梗爆笑互动全场沸腾")
4. **Filename**: `cover_rank_02_宝哥与大斌子洗脚梗爆笑互动全场沸腾.jpg`

## Example Output

From the test run:
```
🖼️  COVER GENERATION:
   Covers generated: 1
   Output directory: processed_videos/clips_with_titles
   Generated covers:
     • [2] cover_rank_02_宝哥与大斌子洗脚梗爆笑互动全场沸腾.jpg
```

File created:
```
processed_videos/clips_with_titles/cover_rank_02_宝哥与大斌子洗脚梗爆笑互动全场沸腾.jpg (293KB)
```

## Technical Implementation

### Frame Extraction Logic
```python
# Parse start time from moment timing
start_time = timing.get('start_time', '00:00:05')  # e.g., "00:13:59"
time_parts = start_time.split(':')
frame_time = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
```

### Video Part Selection
```python
# Find the correct video part based on timing
video_part_name = timing.get('video_part', 'part01')  # e.g., "part04"

# Match against result.video_parts
for part_path in result.video_parts:
    if video_part_name in Path(part_path).stem:
        video_path = part_path
        break
```

### Filename Sanitization
```python
# Clean moment title for filesystem
safe_moment_title = re.sub(r'[^\w\s-]', '', moment_title)
safe_moment_title = re.sub(r'[\s\-]+', '_', safe_moment_title)
safe_moment_title = re.sub(r'_+', '_', safe_moment_title).strip('_')

# Generate filename
cover_filename = f"cover_rank_{rank:02d}_{safe_moment_title}.jpg"
```

## Files Modified

1. **video_orchestrator.py**
   - Updated `_generate_cover_image()` to loop through all engaging moments
   - Added frame time calculation from moment timing
   - Added video part selection logic
   - Added filename sanitization

2. **video_utils.py**
   - Changed `cover_image_path` (string) to `cover_generation` (dict)
   - Updated `ResultsFormatter` to display multiple covers

## Data Flow

```
top_engaging_moments.json
  ↓
For each moment:
  - rank: 2
  - title: "宝哥与大斌子洗脚梗爆笑互动全场沸腾"
  - timing:
      video_part: "part04"
      start_time: "00:13:59"
  ↓
Extract frame from part04 at 13:59
  ↓
Add text overlay:
  - Main: "旭旭宝宝1月31日直播回放" (red)
  - Subtitle: "宝哥与大斌子洗脚梗爆笑互动全场沸腾" (yellow)
  ↓
Save as: cover_rank_02_宝哥与大斌子洗脚梗爆笑互动全场沸腾.jpg
```

## Output Structure

```
processed_videos/
└── clips_with_titles/
    ├── artistic_fire_flame_rank_02_宝哥与大斌子洗脚梗爆笑互动全场沸腾.mp4
    ├── cover_rank_02_宝哥与大斌子洗脚梗爆笑互动全场沸腾.jpg  ← NEW
    └── README.md
```

## Benefits

1. **One cover per moment** - Each engaging moment gets its own thumbnail
2. **Accurate frame extraction** - Uses the exact timestamp from the moment
3. **Correct video part** - Extracts from the right video segment
4. **Descriptive filenames** - Easy to identify which moment each cover represents
5. **Organized output** - All covers in the same directory as titled clips

## Usage

No changes to CLI - works automatically:

```bash
# Generate covers for all engaging moments (default)
uv run python video_orchestrator.py --skip-download --skip-analysis "URL"

# Disable cover generation
uv run python video_orchestrator.py --no-cover "URL"
```

## Test Results

✅ Successfully generated cover for rank 2 moment
✅ Extracted frame from correct video part (part04)
✅ Used correct timestamp (00:13:59 = 839 seconds)
✅ Applied styled text overlay
✅ Saved in clips_with_titles directory
✅ File size: 293KB (high quality)

## Next Steps

If you have a full analysis with 5 engaging moments, the system will generate 5 cover images:
- `cover_rank_01_{title}.jpg`
- `cover_rank_02_{title}.jpg`
- `cover_rank_03_{title}.jpg`
- `cover_rank_04_{title}.jpg`
- `cover_rank_05_{title}.jpg`

All covers will be in `processed_videos/clips_with_titles/` alongside the video clips.
