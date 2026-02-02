# Video Processing Orchestrator

A comprehensive video processing pipeline that orchestrates bilibili video downloading, video splitting, and transcript generation using either Bilibili subtitles or OpenAI Whisper.

## Overview

The Video Orchestrator (`video_orchestrator.py`) combines three powerful components:

1. **bilibili_downloader.py** - Downloads videos and subtitles from Bilibili
2. **video_splitter.py** - Splits long videos into manageable parts
3. **transcript_generation_whisper.py** - Generates transcripts using OpenAI Whisper

## Key Features

- 🎯 **Smart Transcript Selection**: Automatically uses Bilibili subtitles when available, falls back to Whisper generation
- ⏱️ **Intelligent Video Splitting**: Automatically splits videos longer than 20 minutes (configurable)
- 🔄 **Progress Tracking**: Real-time progress updates throughout the entire pipeline
- 🛡️ **Robust Error Handling**: Graceful failure handling with detailed error messages
- 📊 **Comprehensive Results**: Detailed processing reports with file locations and metadata

## Installation & Setup

### Prerequisites

1. **UV Environment**: This project uses `uv` for dependency management
2. **Python 3.8+**: Required for all components
3. **FFmpeg**: Required for video splitting functionality
4. **OpenAI Whisper**: Required for transcript generation (optional if using Bilibili subtitles)

### Installation

```bash
# Navigate to the whisper-env directory
cd whisper-env

# Sync dependencies with uv
uv sync

# Install Whisper (if not already installed)
pip install openai-whisper

# Verify FFmpeg is installed
ffmpeg -version
```

### Dependencies

The orchestrator depends on these packages (managed via `pyproject.toml`):
- `yt-dlp` - For video downloading
- `asyncio` - For asynchronous operations
- Built-in Python modules: `os`, `sys`, `logging`, `pathlib`, `datetime`

## Usage

### Basic Usage

```bash
# Basic processing (uses Bilibili subtitles if available)
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

### Advanced Usage

```bash
# Force Whisper transcript generation
uv run python video_orchestrator.py --force-whisper "https://www.bilibili.com/video/BV1234567890"

# Custom max duration (split videos longer than 15 minutes)
uv run python video_orchestrator.py --max-duration 15 "https://www.bilibili.com/video/BV1234567890"

# Use different Whisper model for better accuracy
uv run python video_orchestrator.py --whisper-model small "https://www.bilibili.com/video/BV1234567890"

# Specify custom output directory
uv run python video_orchestrator.py -o "my_videos" "https://www.bilibili.com/video/BV1234567890"

# Use different browser for cookie extraction
uv run python video_orchestrator.py --browser firefox "https://www.bilibili.com/video/BV1234567890"

# Custom filename template
uv run python video_orchestrator.py -f "%(title)s.%(ext)s" "https://www.bilibili.com/video/BV1234567890"

# Verbose logging for debugging
uv run python video_orchestrator.py -v "https://www.bilibili.com/video/BV1234567890"
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output directory | `processed_videos` |
| `--max-duration` | | Max duration before splitting (minutes) | `20.0` |
| `--whisper-model` | | Whisper model size | `base` |
| `--browser` | | Browser for cookie extraction | `chrome` |
| `--force-whisper` | | Force Whisper generation | `False` |
| `--filename` | `-f` | Custom filename template | Auto-generated |
| `--verbose` | `-v` | Enable verbose logging | `False` |

### Whisper Model Options

| Model | Speed | Accuracy | Memory |
|-------|-------|----------|---------|
| `tiny` | Fastest | Lowest | ~1GB |
| `base` | Fast | Good | ~1GB |
| `small` | Medium | Better | ~2GB |
| `medium` | Slow | High | ~5GB |
| `large` | Slowest | Best | ~10GB |
| `turbo` | Fast | High | ~6GB |

## Processing Pipeline

The orchestrator follows this processing pipeline:

```
1. Download Video & Subtitles
   ├── Extract video metadata
   ├── Download video file
   └── Download Bilibili subtitles (if available)

2. Check Duration & Split (if needed)
   ├── Check if video > max_duration_minutes
   ├── Split video into parts (if needed)
   └── Split subtitles accordingly

3. Process Transcripts
   ├── Use Bilibili subtitles (if available and not forced)
   └── Generate Whisper transcripts (if needed)

4. Generate Results Report
   ├── Processing time
   ├── File locations
   └── Metadata summary
```

## Output Structure

The orchestrator creates a well-organized output structure:

```
processed_videos/
├── downloads/                    # Downloaded videos and subtitles
│   ├── video_title.mp4
│   ├── video_title.srt          # Bilibili subtitles (if available)
│   ├── video_title.info.json    # Video metadata
│   └── video_title.jpg          # Thumbnail
└── splits/                      # Split videos (if applicable)
    └── video_title_split/
        ├── video_title_part01.mp4
        ├── video_title_part01.srt
        ├── video_title_part02.mp4
        ├── video_title_part02.srt
        └── ...
```

## Configuration Options

### Transcript Source Selection

The orchestrator intelligently selects transcript sources:

1. **Default Behavior**: 
   - Uses Bilibili subtitles if available and high quality
   - Falls back to Whisper generation if subtitles are missing or poor quality

2. **Force Whisper** (`--force-whisper`):
   - Always generates transcripts using Whisper
   - Ignores Bilibili subtitles even if available

### Video Splitting Behavior

Videos are automatically split when they exceed the maximum duration:

- **Default**: 20 minutes per part
- **Configurable**: Use `--max-duration` to set custom limit
- **Intelligent Splitting**: Splits at subtitle boundaries to maintain coherence
- **Synchronized Subtitles**: Automatically adjusts subtitle timing for each part

### Browser Cookie Selection

For accessing restricted content:

- **Chrome** (default): Most reliable for modern systems
- **Firefox**: Good alternative, often bypasses some restrictions
- **Edge**: Windows-specific optimizations
- **Safari**: macOS-specific optimizations

## Error Handling

The orchestrator includes comprehensive error handling:

- **Network Issues**: Automatic retries with exponential backoff
- **Missing Dependencies**: Clear error messages with installation instructions
- **Invalid URLs**: URL validation with helpful suggestions
- **Disk Space**: Checks available space before processing
- **Interrupted Processing**: Graceful cleanup of partial files

## Performance Considerations

### Memory Usage

- **Base Model**: ~1GB RAM for Whisper processing
- **Large Model**: ~10GB RAM for highest accuracy
- **Video Splitting**: Minimal RAM usage (stream processing)

### Processing Time

Typical processing times (varies by video length and system):

- **Download**: 1-5 minutes for 1-hour video
- **Splitting**: 30 seconds - 2 minutes
- **Whisper Transcription**: 5-15 minutes per hour of video

### Disk Space

- **Video Files**: Original size + split parts (if applicable)
- **Transcripts**: ~1MB per hour of video
- **Temporary Files**: Up to 2x video size during processing

## Troubleshooting

### Common Issues

**1. Module Not Found Error**
```bash
# Ensure uv environment is properly synced
cd whisper-env
uv sync
```

**2. FFmpeg Not Found**
```bash
# Install FFmpeg
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

**3. Browser Cookie Issues**
```bash
# Try different browser
uv run python video_orchestrator.py --browser firefox [URL]

# Or clear browser cookies and try again
```

**4. Whisper Model Download Issues**
```bash
# Pre-download Whisper models
python -c "import whisper; whisper.load_model('base')"
```

**5. Permission Issues**
```bash
# Ensure output directory is writable
chmod 755 processed_videos/
```

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
uv run python video_orchestrator.py -v [URL]
```

## Integration

### Programmatic Usage

You can also use the orchestrator programmatically:

```python
import asyncio
from video_orchestrator import VideoOrchestrator

async def process_video():
    orchestrator = VideoOrchestrator(
        output_dir="my_output",
        max_duration_minutes=15.0,
        whisper_model="small"
    )
    
    result = await orchestrator.process_video(
        "https://www.bilibili.com/video/BV1234567890",
        force_whisper=False
    )
    
    if result.success:
        print(f"✅ Processed successfully in {result.processing_time:.1f}s")
        print(f"📁 Video: {result.video_path}")
        print(f"📝 Transcript: {result.transcript_path}")
    else:
        print(f"❌ Failed: {result.error_message}")

# Run
asyncio.run(process_video())
```

### Batch Processing

For processing multiple videos (URLs, local files, or mixed):

```python
import asyncio
from pathlib import Path
from video_orchestrator import VideoOrchestrator

async def batch_process():
    # Mix of URLs and local files
    sources = [
        "https://www.bilibili.com/video/BV1111111111",
        "/path/to/local/video1.mp4",
        "https://www.bilibili.com/video/BV2222222222",
        "./my_videos/video2.mkv"
    ]
    
    orchestrator = VideoOrchestrator()
    
    for source in sources:
        print(f"🚀 Processing: {source}")
        result = await orchestrator.process_video(source)
        
        if result.success:
            title = result.video_info.get('title', Path(source).stem)
            print(f"✅ Success: {title}")
        else:
            print(f"❌ Failed: {result.error_message}")

async def batch_process_local_directory():
    """Process all videos in a directory"""
    video_dir = Path("/path/to/video/directory")
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
    
    orchestrator = VideoOrchestrator(
        max_duration_minutes=10.0,  # Shorter parts for batch processing
        whisper_model="tiny"        # Faster processing
    )
    
    video_files = []
    for ext in video_extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
    
    print(f"Found {len(video_files)} video files")
    
    for video_file in video_files:
        print(f"🚀 Processing: {video_file.name}")
        result = await orchestrator.process_video(str(video_file))
        
        if result.success:
            print(f"✅ Success: {video_file.name}")
        else:
            print(f"❌ Failed: {result.error_message}")

# Run examples
asyncio.run(batch_process())
asyncio.run(batch_process_local_directory())
```

## Best Practices

### For Quality

1. **Use appropriate Whisper model**:
   - `tiny`/`base`: For quick processing, acceptable quality
   - `small`/`medium`: For balanced speed/quality
   - `large`/`turbo`: For best quality, when time allows

2. **Leverage Bilibili subtitles when possible**:
   - Usually faster and more accurate for Chinese content
   - Use `--force-whisper` only when necessary

### For Performance

1. **Optimize splitting duration**:
   - Shorter parts: Faster parallel processing
   - Longer parts: Fewer files to manage
   - Default 20 minutes is usually optimal

2. **Choose appropriate browser**:
   - Use the browser you're actively logged into Bilibili with
   - Chrome generally has the best compatibility

### For Reliability

1. **Monitor disk space**:
   - Ensure 2-3x video size free space
   - Clean up old processed videos regularly

2. **Use verbose logging for debugging**:
   - Helps identify issues early
   - Useful for batch processing

## Contributing

To contribute to the Video Orchestrator:

1. Fork the repository
2. Create your feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **yt-dlp**: Powerful video downloading capabilities
- **OpenAI Whisper**: High-quality speech recognition
- **FFmpeg**: Video processing backbone
- **UV**: Modern Python dependency management
