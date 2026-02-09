# OpenClip

English | [简体中文](./README.md)

A lightweight automated video processing pipeline that identifies and extracts the most engaging moments from long-form videos (especially talk-to-camera and livestream recordings). Uses AI-powered analysis to find highlights, generates clips, and adds titles and covers.

## 🎯 What It Does

Give it a video URL or local file, and it handles the full pipeline: **Download → Transcribe → Split → AI Analysis → Clip Generation → Titles and Covers** — outputting the most engaging moments. Great for quickly extracting highlights from long livestreams or videos.

> 💡 **How is it different from AutoClip?** See the [comparison section](#-comparison-with-autoclip) to learn about OpenClip's lightweight design philosophy.

## ✨ Features

- **Flexible Input**: Bilibili/YouTube URLs or local video files
- **Smart Transcription**: Uses platform subtitles when available, falls back to Whisper
- **Automatic Splitting**: Handles videos of any length by splitting into 20-minute parts
- **AI Analysis**: Identifies engaging moments based on content, interaction, and entertainment value
- **Clip Generation**: Extracts the most engaging moments as standalone video clips
- **Titles and Covers**: Adds custom titles and cover images to videos
- **Background Context**: Optionally add background information (e.g., streamer names) for better analysis
- **Triple Interface Support**: Streamlit web interface, Agent Skills, and command-line interface for different user needs
- **Real-time Preview**: Streamlit interface provides real-time preview of generated content
- **Agent Skills**: Built-in [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [TRAE](https://www.trae.ai/) agent skills for processing videos with natural language

## 📋 Prerequisites

### Required

- **Python 3.11+**
- **uv** (Python package manager) - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- **FFmpeg** - For video processing
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org)

- **LLM API Key** (choose one)
  - **Qwen API Key** - Get your key from [Alibaba Cloud](https://dashscope.aliyun.com/)
  - **OpenRouter API Key** - Get your key from [OpenRouter](https://openrouter.ai/)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/linzzzzzz/openclip.git
cd openclip

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

#### Option A: Using Streamlit Web Interface

**Start Streamlit app:**
```bash
uv run streamlit run streamlit_app.py
```

Once the app starts, open your browser and visit the displayed URL (typically `http://localhost:8501`).

**Usage Flow:**
1. Select input type (Video URL or Local File) in the sidebar
2. Configure processing options (LLM provider, etc.)
3. Click "Process Video" button to start processing
4. View real-time progress and final results
5. Preview generated clips and covers in the results section

**Advantages:** No need to remember command-line parameters, provides visual operation interface, suitable for all users.

#### Option B: Using AI Agent Skills

If you use [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or [TRAE](https://www.trae.ai/), you can process videos using natural language without manually typing commands:

```
"Extract highlights from this video: https://www.bilibili.com/video/BV1234567890"
"Process ~/Downloads/livestream.mp4 with English as output language"
```

The agent automatically invokes the built-in skill to handle the full pipeline: downloading, transcription, analysis, clip generation, and title styling.

Skill definitions are located in `.claude/skills/` and `.trae/skills/`.

#### Option C: Using Command Line Interface

```bash
# Process a Bilibili video
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"

# Process a YouTube video
uv run python video_orchestrator.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Process a local video
uv run python video_orchestrator.py "/path/to/video.mp4"
```

## 📖 CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `VIDEO_URL_OR_PATH` | Video URL or local file path (positional) | Required |
| `-o`, `--output-dir` | Custom output directory | `processed_videos` |
| `--llm-provider` | LLM provider (`qwen` or `openrouter`) | `qwen` |
| `--language` | Output language (`zh` or `en`) | `zh` |
| `--artistic-style` | Banner Title artistic style (see list below) | `fire_flame` |
| `--max-duration` | Split duration in minutes | `20` |
| `--browser` | Browser for cookies (`chrome`/`firefox`/`edge`/`safari`) | `firefox` |
| `--force-whisper` | Force Whisper transcription (ignore platform subtitles) | Off |
| `--use-background` | Use background info for analysis | Off |
| `--skip-download` | Skip download, use existing video | Off |
| `--skip-analysis` | Skip analysis, use existing results | Off |
| `--no-clips` | Don't generate clips | Off |
| `--no-titles` | Don't add artistic titles | Off |
| `--no-cover` | Don't generate cover images | Off |

<details>
<summary>🎨 Banner Title Artistic Styles</summary>

| Style | Effect |
|-------|--------|
| `fire_flame` | Fire flame effect (default) |
| `gradient_3d` | Gradient 3D effect |
| `neon_glow` | Neon glow effect |
| `metallic_gold` | Metallic gold effect |
| `rainbow_3d` | Rainbow 3D effect |
| `crystal_ice` | Crystal ice effect |
| `metallic_silver` | Metallic silver effect |
| `glowing_plasma` | Glowing plasma effect |
| `stone_carved` | Stone carved effect |
| `glass_transparent` | Glass transparent effect |

</details>

## 🔍 Command Line Examples

**Process a Bilibili video with background info and neon glow style banner title:**
```bash
uv run python video_orchestrator.py \
  --artistic-style neon_glow \
  --use-background \
  "https://www.bilibili.com/video/BV1wT6GBBEPp"
```

**Analysis only, no clip generation:**
```bash
uv run python video_orchestrator.py --no-clips --no-titles "VIDEO_URL"
```

**Skip download, reprocess existing video:**
```bash
uv run python video_orchestrator.py --skip-download --artistic-style crystal_ice "VIDEO_URL"
```

## 📁 Output Structure

After processing, the output directory is structured as follows:

```
processed_videos/{video_name}/
├── downloads/            # Original video, subtitles, and metadata
├── splits/               # Split parts and AI analysis results
├── clips/                # Generated highlight clips and summary
└── clips_with_titles/    # Final clips with artistic titles and cover images
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

Then use the `--use-background` flag:
```bash
uv run python video_orchestrator.py --use-background "VIDEO_URL"
```

### Customizing Analysis Prompts

Edit prompt templates in `prompts/`:
- `engaging_moments_part_requirement.md` - Analysis criteria for each part
- `engaging_moments_agg_requirement.md` - Aggregation criteria for top moments

### Adding New Artistic Styles

Edit `title_adder.py` to add new visual effects.

## 📎 Others

<details>
<summary>🔧 Workflow</summary>

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

</details>

<details>
<summary>🐛 Troubleshooting</summary>

### Download fails
**Cause**: 
- yt-dlp version is too old. Try updating dependencies: `uv sync`.
- Cookie/authentication issues. Try `--browser firefox` to switch browsers, or login to Bilibili in your browser first.

### No clips generated
**Cause**: Missing API key or analysis failed. Check `echo $QWEN_API_KEY` or `echo $OPENROUTER_API_KEY`, and verify analysis files exist.

### FFmpeg errors
**Cause**: FFmpeg not installed or not in PATH. Run `ffmpeg -version` to check, install if missing (macOS: `brew install ffmpeg`).

### Memory issues
**Cause**: Very long video. Try `--max-duration 10` for shorter splits, or `--no-titles` to process in stages.

### Chinese text not displaying
**Cause**: Missing Chinese fonts. macOS auto-detects (STHeiti, PingFang), Windows needs SimSun or Microsoft YaHei, Linux needs `fonts-wqy-zenhei`.

</details>

## 🔄 Comparison with AutoClip

OpenClip is inspired by [AutoClip](https://github.com/zhouxiaoka/autoclip) but takes a different approach:

| Feature | OpenClip | AutoClip |
|---------|----------|----------|
| **Code Size** | ~5K lines | ~2M lines (with frontend deps) |
| **Dependencies** | Python + FFmpeg | Docker + Redis + PostgreSQL + Celery |
| **Customization** | Editable prompt templates | Configuration files |
| **Interface** | Web UI + Agent Skills + Command-line | Web UI |
| **Deployment** | `uv sync` and go | Docker containerized |

**OpenClip Features:** Lightweight (5K lines), fast startup, customizable prompts, 10 artistic title styles, easy to maintain and extend

Thanks to [AutoClip](https://github.com/zhouxiaoka/autoclip) for their contributions to video automation.

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

- **AutoClip** - Contributions to video automation
- **OpenAI Whisper** - Speech recognition
- **Alibaba Qwen** - AI analysis
- **yt-dlp** - Video downloading
- **MoviePy** - Video processing
- **FFmpeg** - Video encoding

## 📞 Support

For issues or questions:
1. Review error messages in console output
2. Test with a short video first
3. Open an issue on GitHub
4. Join our [Discord community](https://discord.gg/KsC4Keaq) for discussions
