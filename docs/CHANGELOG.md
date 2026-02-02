# Changelog

## Recent Updates

### Directory Structure Reorganization (2026-02-02)

**Changed:**
- Clips are now organized under the main output directory
- `engaging_clips/` → `processed_videos/clips/`
- `engaging_clips_with_titles/` → `processed_videos/clips_with_titles/`

**Benefits:**
- All outputs consolidated under one directory
- Cleaner project structure
- Easier to manage and backup
- Better organization for multiple video processing

**Migration:**
- New processing automatically uses new structure
- Old directories remain unchanged
- No action needed for existing files

---

### Background Information Integration (2026-02-02)

**Added:**
- New `--use-background` CLI flag
- Background information loading from `prompts/background/background.md`
- Context-aware analysis with streamer names and nicknames

**Usage:**
```bash
uv run python video_orchestrator.py --use-background "https://..."
```

**Features:**
- Optional background context for AI analysis
- Better understanding of streamer names and terminology
- Improved engaging moment identification
- Graceful fallback if background file missing

---

### Template Code Cleanup (2026-02-02)

**Removed:**
- Unused `templates_dir` attribute from `EngagingMomentsAnalyzer`
- Legacy template references

**Impact:**
- Cleaner codebase
- No functional changes
- All prompts now use `prompts/` directory

---

## File Structure

### New Files
- `BACKGROUND_INTEGRATION_GUIDE.md` - Guide for using background information
- `DIRECTORY_STRUCTURE.md` - Documentation of output directory structure
- `CHANGELOG.md` - This file
- `test_background_integration.py` - Test script for background feature

### Modified Files
- `engaging_moments_analyzer.py` - Added background support, removed templates
- `video_orchestrator.py` - Updated directory structure, added background option

### Configuration Files
- `prompts/background/background.md` - Background information for analysis
- `prompts/reference/reference.md` - Reference information (placeholder)

---

## Usage Examples

### Basic Processing
```bash
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

### With Background Information
```bash
uv run python video_orchestrator.py --use-background "https://www.bilibili.com/video/BV1234567890"
```

### Full Pipeline with Custom Output
```bash
export QWEN_API_KEY=your_key
uv run python video_orchestrator.py \
  -o my_videos \
  --use-background \
  --artistic-style fire_flame \
  "https://www.bilibili.com/video/BV1234567890"
```

### Output Structure
```
my_videos/
├── downloads/          # Downloaded videos
├── splits/             # Split video parts
├── clips/              # Generated clips (NEW LOCATION)
└── clips_with_titles/  # Clips with titles (NEW LOCATION)
```

---

## Testing

### Test Background Integration
```bash
uv run python test_background_integration.py
```

### Test Directory Structure
```bash
uv run python -c "
from video_orchestrator import VideoOrchestrator
orch = VideoOrchestrator(output_dir='test_output')
print(f'Clips: {orch.clips_dir}')
print(f'Titles: {orch.clips_with_titles_dir}')
"
```

---

## Backward Compatibility

- All changes are backward compatible
- Default behavior unchanged (background disabled by default)
- Existing scripts work without modification
- Old clip directories remain untouched
- New processing uses new directory structure

---

## Future Enhancements

Potential improvements:
- [ ] Support for multiple background files
- [ ] Dynamic background loading based on video source
- [ ] Configurable clip directory names
- [ ] Batch processing with shared output directory
- [ ] Archive old clips automatically
