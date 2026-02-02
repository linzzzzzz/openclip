# Background Information Integration Guide

## Overview

The video orchestrator now supports including background information (such as streamer names, nicknames, and context) in the AI analysis prompts. This helps the AI better understand the content and identify more relevant engaging moments.

## What's New

### 1. Background Information File
- Location: `prompts/background/background.md`
- Contains: Streamer names, nicknames, fan terminology, and other contextual information
- Format: Markdown file with structured information about content creators

### 2. Enhanced Analyzer
The `EngagingMomentsAnalyzer` class now supports:
- Optional background information loading
- Automatic integration into analysis prompts
- Graceful fallback if background file is missing

### 3. CLI Option
New command-line flag: `--use-background`

## Usage

### Basic Usage (Without Background)
```bash
# Standard analysis without background context
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

### With Background Information
```bash
# Include background information for better context-aware analysis
uv run python video_orchestrator.py --use-background "https://www.bilibili.com/video/BV1234567890"
```

### Combined with Other Options
```bash
# Full pipeline with background, custom style, and all features
export QWEN_API_KEY=your_api_key
uv run python video_orchestrator.py \
  --use-background \
  --artistic-style fire_flame \
  "https://www.bilibili.com/video/BV1234567890"

# With background but skip download (use existing)
uv run python video_orchestrator.py \
  --use-background \
  --skip-download \
  "https://www.bilibili.com/video/BV1234567890"
```

## How It Works

### 1. Initialization
When `use_background=True`:
- Analyzer loads `prompts/background/background.md`
- Content is stored in memory for prompt generation
- If file is missing, feature is automatically disabled

### 2. Prompt Construction
For each analysis (part analysis and aggregation):
```
[Background Information]  ← Added when use_background=True
↓
[Main Prompt Template]
↓
[Transcript/Moments Data]
```

### 3. Benefits
- AI understands streamer names and nicknames
- Better identification of co-hosting moments
- More accurate engagement level assessment
- Context-aware title generation

## Customizing Background Information

Edit `prompts/background/background.md` to include:
- Streamer names and aliases
- Fan community terminology
- Content themes and topics
- Any other relevant context

Example structure:
```markdown
## Streamers and Nicknames

主播: 旭旭宝宝
称呼: 宝哥、大马猴
特点: DNF 顶流主播

## Common Terms

- 800万勇士: DNF粉丝群体
- 大字辈: 核心主播团队
```

## Testing

Run the integration test:
```bash
uv run python test_background_integration.py
```

Expected output:
- Without background: `use_background=False`, `background_content=None`
- With background: `use_background=True`, content loaded successfully

## Code Changes

### engaging_moments_analyzer.py
- Added `use_background` parameter to `__init__`
- Added `_load_background_info()` method
- Updated prompt construction in:
  - `analyze_part_for_engaging_moments()`
  - `aggregate_top_moments()`

### video_orchestrator.py
- Added `use_background` parameter to `VideoOrchestrator.__init__`
- Passes parameter to `EngagingMomentsAnalyzer`
- Added `--use-background` CLI flag
- Updated help text and examples

## Backward Compatibility

- Default behavior unchanged (background disabled by default)
- Existing scripts work without modification
- Optional feature activated only with `--use-background` flag

## Performance Impact

- Minimal: Background file loaded once during initialization
- Slightly longer prompts sent to AI (negligible impact)
- No impact when feature is disabled

## Troubleshooting

### Background not loading
- Check file exists: `prompts/background/background.md`
- Verify file encoding is UTF-8
- Check logs for warning messages

### Feature not working
- Ensure `--use-background` flag is used
- Verify QWEN_API_KEY is set
- Check that analysis is not skipped (`--skip-analysis`)

## Future Enhancements

Potential improvements:
- Support for multiple background files
- Dynamic background loading based on video source
- Background information versioning
- Auto-detection of relevant background context
