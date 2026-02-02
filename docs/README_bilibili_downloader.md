# Bilibili Video Downloader

A comprehensive Bilibili video downloader built on top of yt-dlp, designed specifically for downloading videos from Bilibili (bilibili.com) with Chinese subtitle support and optimized settings. **Now includes fully automated cookie extraction - no manual browser interaction required!**

## Features

- ✅ Download videos from Bilibili in various qualities
- ✅ Automatic subtitle download (Chinese and English)
- ✅ Audio-only extraction with MP3 conversion
- ✅ Playlist and series download support
- ✅ Video information extraction
- ✅ Progress tracking during downloads
- ✅ Thumbnail and metadata download
- ✅ Custom filename templates
- ✅ Format listing for quality selection

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed, then:

```bash
cd whisper-env
uv add yt-dlp
```

**Note:** The browser-assisted version requires Google Chrome to be installed on your system.

## Usage

### **NEW: Fully Automated Mode (Recommended - No Manual Interaction)**

```bash
# Download with automatic cookie extraction from Chrome (no browser interaction needed)
uv run python bilibili_downloader_improved.py "https://www.bilibili.com/video/BV1234567890"

# Use Firefox cookies instead of Chrome
uv run python bilibili_downloader_improved.py --browser firefox "https://www.bilibili.com/video/BV1234567890"

# Use custom output directory
uv run python bilibili_downloader_improved.py -o "my_downloads" "https://www.bilibili.com/video/BV1234567890"
```

### Browser-Assisted Mode (Manual interaction required)

```bash
# Download a video with browser assistance (requires manual interaction)
uv run python bilibili_downloader_browser.py "https://www.bilibili.com/video/BV1234567890"

# Use custom output directory
uv run python bilibili_downloader_browser.py -o "my_downloads" "https://www.bilibili.com/video/BV1234567890"
```

### Traditional Mode (May encounter 412 errors)

```bash
# Download a video with best available quality
uv run python bilibili_downloader.py "https://www.bilibili.com/video/BV1234567890"

# Use custom output directory
uv run python bilibili_downloader.py -o "my_downloads" "https://www.bilibili.com/video/BV1234567890"
```

### Quality Selection

```bash
# Fully automated (recommended)
uv run python bilibili_downloader_improved.py -q "best" "https://www.bilibili.com/video/BV1234567890"
uv run python bilibili_downloader_improved.py -q "720p" "https://www.bilibili.com/video/BV1234567890"
uv run python bilibili_downloader_improved.py -q "480p" "https://www.bilibili.com/video/BV1234567890"

# Browser-assisted (with manual interaction)
uv run python bilibili_downloader_browser.py -q "best" "https://www.bilibili.com/video/BV1234567890"
uv run python bilibili_downloader_browser.py -q "720p" "https://www.bilibili.com/video/BV1234567890"
```

### Audio-Only Downloads

```bash
# Download audio only and convert to MP3 (browser-assisted)
uv run python bilibili_downloader_browser.py -a "https://www.bilibili.com/video/BV1234567890"

# Traditional method
uv run python bilibili_downloader.py -a "https://www.bilibili.com/video/BV1234567890"
```

### Information and Format Listing

```bash
# Fully automated (recommended)
uv run python bilibili_downloader_improved.py -i "https://www.bilibili.com/video/BV1234567890"

# Browser-assisted (with manual interaction)
uv run python bilibili_downloader_browser.py -i "https://www.bilibili.com/video/BV1234567890"
uv run python bilibili_downloader_browser.py -l "https://www.bilibili.com/video/BV1234567890"

# Traditional method (may fail with 412 errors)
uv run python bilibili_downloader.py -i "https://www.bilibili.com/video/BV1234567890"
```

### Playlist Downloads

```bash
# Download entire playlist or series (browser-assisted)
uv run python bilibili_downloader_browser.py -p "https://www.bilibili.com/video/BV1234567890"

# Traditional method
uv run python bilibili_downloader.py -p "https://www.bilibili.com/video/BV1234567890"
```

### Custom Filename Templates

```bash
# Use custom filename template (browser-assisted)
uv run python bilibili_downloader_browser.py -f "%(title)s.%(ext)s" "https://www.bilibili.com/video/BV1234567890"

# More complex template with date and uploader
uv run python bilibili_downloader_browser.py -f "%(upload_date)s_%(uploader)s_%(title)s.%(ext)s" "https://www.bilibili.com/video/BV1234567890"
```

## Supported URL Formats

The downloader supports various Bilibili URL formats:

- `https://www.bilibili.com/video/BV...`
- `https://www.bilibili.com/bangumi/...`
- `https://b23.tv/...` (short URLs)
- `https://m.bilibili.com/video/...` (mobile URLs)

## Output Structure

### Default Video Downloads

Files are saved in the format: `{uploader}_{title}_{video_id}.{extension}`

Additional files include:
- `.srt` files for subtitles (Chinese and English when available)
- `.jpg` files for thumbnails
- `.info.json` files with video metadata

### Audio Downloads

Audio files are saved in: `downloads/audio/{uploader}_{title}_{video_id}.mp3`

### Playlist Downloads

Playlist videos are organized as: `downloads/{playlist_title}/{index:02d}_{title}_{video_id}.{extension}`

## Available Downloaders

### 1. `bilibili_downloader_improved.py` - **RECOMMENDED**
- ✅ **Fully automated** - no manual browser interaction
- ✅ Automatic cookie extraction from Chrome/Firefox/Edge/Safari
- ✅ Advanced subtitle strategies with multiple fallbacks
- ✅ Async architecture for better performance
- ✅ Comprehensive error handling and logging
- ✅ AI subtitle support (`ai-zh`) with priority handling

### 2. `bilibili_downloader_browser.py` - Manual Interaction
- ✅ Browser-assisted download with manual cookie generation
- ✅ Works when automated methods fail
- ⚠️ Requires manual browser interaction

### 3. `bilibili_downloader.py` - Traditional
- ⚠️ May encounter HTTP 412 errors
- ✅ Simple CLI interface
- ⚠️ Limited anti-bot protection

## Command Line Options

### Improved Downloader Options
| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output directory (default: downloads) |
| `--quality` | `-q` | Video quality preference |
| `--browser` | `-b` | Browser for cookies (chrome/firefox/edge/safari) |
| `--filename` | `-f` | Custom filename template |
| `--info` | `-i` | Show video information only |
| `--help` | `-h` | Show help message |

### Browser-Assisted & Traditional Options
| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output directory (default: downloads) |
| `--quality` | `-q` | Video quality preference |
| `--filename` | `-f` | Custom filename template |
| `--audio-only` | `-a` | Download audio only |
| `--playlist` | `-p` | Download as playlist/series |
| `--list-formats` | `-l` | List available formats |
| `--info` | `-i` | Show video information only |
| `--no-browser` | | Skip browser pre-visit (browser version only) |

## Programmatic Usage

You can also use the `BilibiliDownloader` class directly in your Python code:

```python
from bilibili_downloader import BilibiliDownloader

# Initialize downloader
downloader = BilibiliDownloader(output_dir="my_downloads", quality="720p")

# Download a video
success = downloader.download_video("https://www.bilibili.com/video/BV1234567890")

# Get video info
info = downloader.get_video_info("https://www.bilibili.com/video/BV1234567890")
if info:
    print(f"Title: {info['title']}")
    print(f"Duration: {info['duration']} seconds")

# Download audio only
downloader.download_audio_only("https://www.bilibili.com/video/BV1234567890")
```

## Quality Options

The downloader supports various quality settings:

- `best` - Best available quality (limited to 1080p max)
- `worst` - Lowest available quality
- `720p`, `480p`, `360p` - Specific resolutions
- `audio` - Audio only (equivalent to using `-a` flag)

## Subtitle Support

The downloader automatically downloads subtitles in multiple languages:

- Chinese Simplified (`zh-Hans`)
- Chinese Traditional (`zh-Hant`)
- Chinese (`zh`)
- English (`en`)

Subtitles are saved as `.srt` files alongside the video files.

## Error Handling

The downloader includes comprehensive error handling:

- URL validation for Bilibili domains
- Network error recovery
- Invalid video ID handling
- Missing format handling
- File system error handling

## Tips for Best Results

1. **Use specific quality settings** if you have bandwidth limitations
2. **Download subtitles separately** if needed for translation work
3. **Use playlist mode** for series or collections
4. **Check available formats** with `-l` flag before downloading
5. **Use custom filenames** to organize downloads better

## Troubleshooting

### Common Issues

1. **"No module named yt_dlp"**: Make sure to use `uv run` prefix
2. **Download fails**: Check if the URL is accessible and video is public
3. **No subtitles**: Not all videos have subtitles available
4. **Slow downloads**: Try lower quality settings or check your internet connection

### Getting Help

Run with `--help` flag for detailed usage information:

```bash
uv run python bilibili_downloader.py --help
```

## Examples

### Download a Popular Video

```bash
# Download with Chinese subtitles and metadata
uv run python bilibili_downloader.py "https://www.bilibili.com/video/BV1GJ411x7h7"
```

### Batch Download Script

Create a text file `urls.txt` with one URL per line, then:

```bash
# Simple batch download script
while IFS= read -r url; do
    uv run python bilibili_downloader.py "$url"
done < urls.txt
```

### Quality Comparison

```bash
# First, check available formats
uv run python bilibili_downloader.py -l "https://www.bilibili.com/video/BV1234567890"

# Then download specific quality
uv run python bilibili_downloader.py -q "720p" "https://www.bilibili.com/video/BV1234567890"
```

## Integration with Other Tools

This downloader works well with other video processing tools in this project:

- Use with `video_splitter.py` to create clips from downloaded videos
- Use with `subtitle_helper.py` for subtitle processing
- Use with `generate_clips.py` for automated highlight creation

## License

This tool is built on top of yt-dlp and respects its licensing terms. Use responsibly and in accordance with Bilibili's terms of service.
