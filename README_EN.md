# OpenClip

English | [简体中文](./README.md)

A lightweight automated video processing pipeline that identifies and extracts the most engaging moments from long-form videos (especially livestream recordings). Uses AI-powered analysis to find highlights, generates clips, and adds artistic titles.

## 🎯 What It Does

This project orchestrates a complete workflow to:

1. **Download** videos from Bilibili/YouTube or process local video files
2. **Extract** subtitles (from platform or generate with Whisper)
3. **Split** long videos (>20 minutes) into manageable parts
4. **Analyze** content using AI to identify engaging moments
5. **Generate** video clips of the top 5 most engaging moments
6. **Add** artistic titles with 10 different visual styles
7. **Create** cover images for each clip

Perfect for content creators who want to extract highlights from long livestreams or videos for social media sharing.

> 💡 **How is it different from AutoClip?** See the [comparison section](#-comparison-with-autoclip) to learn about OpenClip's lightweight design philosophy.

## ✨ Features

- **Flexible Input**: Bilibili/YouTube URLs or local video files
- **Smart Transcription**: Uses platform subtitles when available, falls back to Whisper
- **Automatic Splitting**: Handles videos of any length by splitting into 20-minute parts
- **AI Analysis**: Identifies engaging moments based on content, interaction, and entertainment value
- **Bilingual Support**: Generate output in Chinese or English
- **Clip Generation**: Extracts top 5 moments as standalone video clips
- **Artistic Titles**: 10 professional title styles (fire, neon, crystal, metallic, etc.)
- **Cover Images**: Auto-generates styled cover images for each clip
- **Background Context**: Optional streamer/context information for better analysis
- **Dual Interface Support**: Command-line interface and Streamlit web interface for different user needs
- **Real-time Preview**: Streamlit interface provides real-time preview of generated content

## 📋 Prerequisites

### Required

- **Python 3.11+**
- **uv** (Python package manager) - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- **FFmpeg** - For video processing
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org)

### Optional

- **LLM API Key** - Required for AI analysis and clip generation (choose one)
  - **Qwen API Key**
    - Get your key from [Alibaba Cloud](https://dashscope.aliyun.com/)
    - Set as environment variable: `export QWEN_API_KEY=your_key_here`
  - **OpenRouter API Key**
    - Get your key from [OpenRouter](https://openrouter.ai/)
    - Set as environment variable: `export OPENROUTER_API_KEY=your_key_here`

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd OpenClip

# Install dependencies with uv
uv sync
```

### 2. Set API Key (for AI features)

**Using Qwen:**
```bash
export QWEN_API_KEY=your_api_key_here
```

**Using OpenRouter:**
```bash
export OPENROUTER_API_KEY=your_api_key_here
```

### 3. Run the Pipeline

#### Option A: Using Streamlit Web Interface (Recommended)

**Start Streamlit app:**
```bash
uv run streamlit run streamlit_app.py
```

Once the app starts, open your browser and visit the displayed URL (typically `http://localhost:8501`).

**Streamlit Interface Features:**
- ✅ Support for video URLs (Bilibili, YouTube) and local file uploads
- ✅ Real-time progress bar and status updates
- ✅ Intuitive form interface for all configuration options
- ✅ Built-in API key management
- ✅ 10 artistic title style selections
- ✅ Real-time preview of generated clips and covers
- ✅ Persistent processing result storage

**Usage Flow:**
1. Select input type (Video URL or Local File) in the sidebar
2. Configure processing options (LLM provider, artistic style, etc.)
3. Click "Process Video" button to start processing
4. View real-time progress and final results
5. Preview generated clips and covers in the results section

**Advantages:** No need to remember command-line parameters, provides visual operation interface, suitable for all users.

#### Option B: Using Command Line Interface

**Process a Bilibili video:**
```bash
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

**Process a YouTube video:**
```bash
uv run python video_orchestrator.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Process a local video:**
```bash
uv run python video_orchestrator.py "/path/to/video.mp4"
```

## 📖 Usage Guide

### Basic Commands

```bash
# Full pipeline with all features
uv run python video_orchestrator.py "VIDEO_URL_OR_PATH"

# With custom artistic style for YouTube video
uv run python video_orchestrator.py --artistic-style neon_glow "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# With custom artistic style for Bilibili video
uv run python video_orchestrator.py --artistic-style neon_glow "https://www.bilibili.com/video/BV1234567890"

# Process local file
uv run python video_orchestrator.py ~/Videos/livestream.mp4

# Custom output directory
uv run python video_orchestrator.py -o my_output "VIDEO_URL"
```

### Transcript Options

```bash
# Use platform subtitles (default, supports Bilibili and YouTube)
uv run python video_orchestrator.py "VIDEO_URL"

# Force Whisper transcription
uv run python video_orchestrator.py --force-whisper "VIDEO_URL"

# Use different Whisper model (tiny, base, small, medium, large, turbo)
uv run python video_orchestrator.py --whisper-model small "VIDEO_URL"
```

### Video Splitting

```bash
# Default: split at 20 minutes
uv run python video_orchestrator.py "VIDEO_URL"

# Custom split duration (15 minutes)
uv run python video_orchestrator.py --max-duration 15 "VIDEO_URL"

# Videos under 20 minutes won't be split
```

### Analysis Options

```bash
# Include background information (streamer names, context)
uv run python video_orchestrator.py --use-background "VIDEO_URL"

# Use English output (default is Chinese)
uv run python video_orchestrator.py --language en "VIDEO_URL"

# Skip analysis (use existing analysis file)
uv run python video_orchestrator.py --skip-analysis "VIDEO_URL"

# Analysis only (no clips or titles)
uv run python video_orchestrator.py --no-clips --no-titles "VIDEO_URL"

# Use OpenRouter as LLM provider (default is Qwen)
uv run python video_orchestrator.py --llm-provider openrouter "VIDEO_URL"
```

### Clip Generation

```bash
# Generate clips with titles (default)
uv run python video_orchestrator.py "VIDEO_URL"

# Generate clips without titles
uv run python video_orchestrator.py --no-titles "VIDEO_URL"

# Skip clip generation
uv run python video_orchestrator.py --no-clips "VIDEO_URL"

# Disable cover image generation
uv run python video_orchestrator.py --no-cover "VIDEO_URL"
```

### Artistic Styles

Choose from 10 different title styles:

```bash
--artistic-style gradient_3d      # Gradient 3D effect
--artistic-style neon_glow         # Neon glow effect
--artistic-style metallic_gold     # Metallic gold effect
--artistic-style rainbow_3d        # Rainbow 3D effect
--artistic-style crystal_ice       # Crystal ice effect
--artistic-style fire_flame        # Fire flame effect (default)
--artistic-style metallic_silver   # Metallic silver effect
--artistic-style glowing_plasma    # Glowing plasma effect
--artistic-style stone_carved      # Stone carved effect
--artistic-style glass_transparent # Glass transparent effect
```

### Download Options

```bash
# Skip download (use existing downloaded video)
uv run python video_orchestrator.py --skip-download "VIDEO_URL"

# Use different browser for cookies (chrome, firefox, edge, safari)
uv run python video_orchestrator.py --browser firefox "VIDEO_URL"
```

## 📁 Output Structure

After processing, your output directory will contain:

```
processed_videos/
├── downloads/                          # Downloaded videos
│   └── BV1234567890_video_title/
│       ├── video_title.mp4            # Original video
│       ├── video_title.srt            # Subtitles
│       ├── video_title.info.json      # Video metadata
│       └── video_title.jpg            # Thumbnail
│
├── splits/                             # Split video parts (if >20 min)
│   └── video_title_split/
│       ├── video_title_part01.mp4     # Video part 1
│       ├── video_title_part01.srt     # Subtitles part 1
│       ├── video_title_part02.mp4     # Video part 2
│       ├── video_title_part02.srt     # Subtitles part 2
│       ├── highlights_part01.json     # AI analysis part 1
│       ├── highlights_part02.json     # AI analysis part 2
│       └── top_engaging_moments.json  # Top 5 aggregated moments
│
├── clips/                              # Generated clips
│   └── video_title/
│       ├── rank_01_moment_title.mp4   # Clip #1
│       ├── rank_02_moment_title.mp4   # Clip #2
│       ├── rank_03_moment_title.mp4   # Clip #3
│       ├── rank_04_moment_title.mp4   # Clip #4
│       ├── rank_05_moment_title.mp4   # Clip #5
│       └── engaging_moments_summary.md # Summary
│
└── clips_with_titles/                  # Clips with artistic titles
    └── video_title/
        ├── artistic_fire_flame_rank_01_moment_title.mp4
        ├── artistic_fire_flame_rank_02_moment_title.mp4
        ├── artistic_fire_flame_rank_03_moment_title.mp4
        ├── artistic_fire_flame_rank_04_moment_title.mp4
        ├── artistic_fire_flame_rank_05_moment_title.mp4
        ├── cover_rank_01_moment_title.jpg              # Cover images
        ├── cover_rank_02_moment_title.jpg
        ├── cover_rank_03_moment_title.jpg
        ├── cover_rank_04_moment_title.jpg
        ├── cover_rank_05_moment_title.jpg
        └── README.md
```

## 🔧 Architecture

The project consists of several modular components:

### Core Components

1. **video_orchestrator.py** - Main orchestration script
   - Coordinates all components
   - Manages workflow and progress
   - Handles command-line interface

2. **Video Download Components** - Video download
   - **bilibili_downloader.py** - Downloads from Bilibili with automatic cookie handling
   - **youtube_downloader.py** - Downloads from YouTube with video and subtitles
   - Extracts subtitles (platform-generated preferred)
   - Supports multiple browsers for authentication

3. **video_splitter.py** - Video splitting
   - Splits long videos into parts
   - Maintains subtitle synchronization
   - Configurable split duration

4. **transcript_generation_whisper.py** - Transcript generation
   - Uses OpenAI Whisper for speech-to-text
   - Fallback when Bilibili subtitles unavailable
   - Multiple model sizes available

5. **engaging_moments_analyzer.py** - AI analysis
   - Analyzes transcripts with LLM API (supports Qwen and OpenRouter)
   - Identifies engaging moments
   - Aggregates top moments across parts

6. **clip_generator.py** - Clip extraction
   - Generates video clips from timestamps
   - Preserves video quality
   - Creates summary documentation

7. **title_adder.py** - Title overlay
   - Adds artistic titles to clips
   - 10 different visual styles
   - Chinese text support

8. **cover_image_generator.py** - Cover generation
   - Extracts frames from clips
   - Adds styled text overlay
   - Creates thumbnail images

### Workflow

```
Input (URL or File)
    ↓
Download/Validate Video
    ↓
Extract/Generate Transcript
    ↓
Check Duration → Split if >20 min
    ↓
AI Analysis (per part)
    ↓
Aggregate Top 5 Moments
    ↓
Generate Clips
    ↓
Add Artistic Titles
    ↓
Generate Cover Images
    ↓
Output Ready!
```

## 🎨 Customization

### Adding Background Information

Create or edit `prompts/background/background.md` to provide context about streamers, nicknames, or recurring themes:

```markdown
# Background Information

## Streamer Information
- Main streamer: 旭旭宝宝 (Xu Xu Bao Bao)
- Nickname: 宝哥 (Bao Ge)
- Game: Dungeon Fighter Online (DNF)

## Common Terms
- 增幅: Equipment enhancement
- 鉴定: Item appraisal
```

Then use `--use-background` flag:
```bash
uv run python video_orchestrator.py --use-background "VIDEO_URL"
```

### Customizing Analysis Prompts

Edit prompt templates in `prompts/`:
- `engaging_moments_part_requirement.md` - Analysis criteria for each part
- `engaging_moments_agg_requirement.md` - Aggregation criteria for top moments

### Adding New Artistic Styles

Edit `title_adder.py` to add new visual effects. See `docs/ARTISTIC_TITLES_GUIDE.md` for details.

## 📚 Documentation

Detailed documentation available in `docs/`:

- **QUICK_START_GUIDE.md** - Quick start and examples
- **ARTISTIC_TITLES_GUIDE.md** - Title styles and customization
- **README_video_orchestrator.md** - Orchestrator details
- **README_bilibili_downloader.md** - Download component
- **README_qwen_integration.md** - AI analysis integration
- **SKIP_ANALYSIS_FEATURE.md** - Skip analysis workflow
- **DIRECTORY_STRUCTURE.md** - Project organization

## 🐛 Troubleshooting

### No clips generated

**Cause**: Missing API key or analysis failed

**Solution**:
```bash
# Check Qwen API key
echo $QWEN_API_KEY

# Or check OpenRouter API key
echo $OPENROUTER_API_KEY

# Verify analysis file exists
ls processed_videos/splits/*/top_engaging_moments.json
```

### FFmpeg errors

**Cause**: FFmpeg not installed or not in PATH

**Solution**:
```bash
# Check FFmpeg
ffmpeg -version

# Install if missing
brew install ffmpeg  # macOS
```

### Memory issues

**Cause**: Processing very long videos

**Solution**:
```bash
# Use shorter split duration
uv run python video_orchestrator.py --max-duration 10 "VIDEO_URL"

# Or process in stages
uv run python video_orchestrator.py --no-titles "VIDEO_URL"
```

### Chinese text not displaying

**Cause**: Missing Chinese fonts

**Solution**:
- macOS: Fonts auto-detected (STHeiti, PingFang)
- Windows: Install SimSun or Microsoft YaHei
- Linux: Install `fonts-wqy-zenhei` or similar

### Download fails

**Cause**: Cookie/authentication issues

**Solution**:
```bash
# Try different browser
uv run python video_orchestrator.py --browser firefox "VIDEO_URL"

# Or login to Bilibili in your browser first
```

## 🔍 Examples

### Example 1: Quick Local Video Processing

```bash
# Process a local video with default settings
uv run python video_orchestrator.py ~/Downloads/livestream.mp4
```

### Example 2: Full Bilibili Pipeline

```bash
# Set API key
export QWEN_API_KEY=sk-xxxxx

# Process with neon glow style
uv run python video_orchestrator.py \
  --artistic-style neon_glow \
  --use-background \
  "https://www.bilibili.com/video/BV1wT6GBBEPp"
```

### Example 3: Analysis Only

```bash
# Just analyze, don't generate clips
uv run python video_orchestrator.py \
  --no-clips \
  --no-titles \
  "https://www.bilibili.com/video/BV1234567890"
```

### Example 4: Reuse Existing Download

```bash
# Skip download, use existing video
uv run python video_orchestrator.py \
  --skip-download \
  --artistic-style crystal_ice \
  "https://www.bilibili.com/video/BV1234567890"
```

### Example 5: Custom Split Duration

```bash
# Split into 15-minute parts
uv run python video_orchestrator.py \
  --max-duration 15 \
  --whisper-model small \
  "VIDEO_URL"
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional artistic title styles
- Support for more video platforms
- Improved AI analysis prompts
- Performance optimizations
- Additional language support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **Alibaba Qwen** - AI analysis
- **yt-dlp** - Video downloading
- **MoviePy** - Video processing
- **FFmpeg** - Video encoding

## 🔄 Comparison with AutoClip

OpenClip is inspired by [AutoClip](https://github.com/zhouxiaoka/autoclip) but takes a different approach:

| Feature | OpenClip | AutoClip |
|---------|----------|----------|
| **Code Size** | ~5K lines | ~2M lines (with frontend deps) |
| **Architecture** | Lightweight CLI tool | Web app (FastAPI + React) |
| **Dependencies** | Python + FFmpeg | Docker + Redis + PostgreSQL + Celery |
| **Customization** | Editable prompt templates | Configuration files |
| **Interface** | Command-line | Web UI + Real-time monitoring |
| **Deployment** | `uv sync` and go | Docker containerized |

**OpenClip Features:** Lightweight (5K lines), fast startup, customizable prompts, 10 artistic title styles, easy to maintain and extend

Thanks to [AutoClip](https://github.com/zhouxiaoka/autoclip) for their contributions to video automation.

## 📞 Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review error messages in console output
3. Test with a short video first
4. Open an issue on GitHub
5. Join our [Discord community](https://discord.gg/KsC4Keaq) for discussions

---

**Made with ❤️ for content creators**
