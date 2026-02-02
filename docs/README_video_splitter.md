# Video and Subtitle Splitter

A Python script that splits video files and their corresponding subtitle files into multiple parts. Supports two splitting methods: by time duration or by number of subtitle segments.

## Features

🎬 **Video Splitting**: Uses ffmpeg to split video files efficiently without re-encoding  
📝 **Subtitle Synchronization**: Automatically adjusts subtitle timing for each part  
⏰ **Time-based Splitting**: Split by duration (e.g., 2-minute parts)  
📊 **Segment-based Splitting**: Split by number of subtitles (e.g., 20 subtitles per part)  
🎯 **Smart Timing**: Ensures subtitle timing starts from 00:00:00 in each part  
📁 **Organized Output**: Creates organized output directories with sequential naming  

## Requirements

### System Requirements
- **Python 3.6+**
- **ffmpeg** (for video processing)

### Installing ffmpeg
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## Usage

### Basic Commands

1. **Split by time duration (minutes)**:
   ```bash
   python video_splitter.py time video.mp4 subtitles.srt 2.0
   ```
   Creates 2-minute video parts

2. **Split by subtitle segments**:
   ```bash
   python video_splitter.py segments video.mp4 subtitles.srt 20
   ```
   Creates parts with 20 subtitles each

3. **Quick test with sample files**:
   ```bash
   python video_splitter.py test
   ```
   Tests with `video_sample.mp4` and `video_sample.srt`

### Advanced Usage

**Custom output directory**:
```bash
python video_splitter.py time video.mp4 subtitles.srt 1.5 my_output_folder
python video_splitter.py segments video.mp4 subtitles.srt 15 my_parts
```

## Examples

### Example 1: Educational Content
Split a 10-minute tutorial into 2-minute segments:
```bash
python video_splitter.py time tutorial.mp4 tutorial.srt 2.0
```

### Example 2: Language Learning
Split by subtitle count for bite-sized learning:
```bash
python video_splitter.py segments lesson.mp4 lesson.srt 10
```

### Example 3: Social Media Content
Create short clips for platforms:
```bash
python video_splitter.py time long_video.mp4 subtitles.srt 0.5
```

## Output Structure

The script creates an output directory with numbered parts:

```
output_parts/
├── video_sample_part01.mp4
├── video_sample_part01.srt
├── video_sample_part02.mp4
├── video_sample_part02.srt
└── ...
```

### File Naming Convention
- Videos: `{original_name}_part{number:02d}.mp4`
- Subtitles: `{original_name}_part{number:02d}.srt`

## How It Works

### Subtitle Processing
1. **Parse SRT File**: Extracts timing and text information
2. **Calculate Split Points**: Determines where to split based on chosen method
3. **Adjust Timing**: Recalculates subtitle timing to start from 00:00:00 for each part
4. **Generate New SRT**: Creates synchronized subtitle files for each part

### Video Processing
1. **ffmpeg Integration**: Uses ffmpeg with stream copying (no re-encoding)
2. **Precise Timing**: Splits at exact timestamps for perfect synchronization
3. **Quality Preservation**: Maintains original video quality and format

### Splitting Methods

#### Time-based Splitting
- Splits video into fixed duration parts
- Finds subtitles within each time range
- Handles partial subtitles at boundaries intelligently

#### Segment-based Splitting
- Groups subtitles into fixed-size chunks
- Calculates video timing based on subtitle timestamps
- Ensures natural content breaks

## Technical Details

### Subtitle Format Support
- **SRT Format**: Standard SubRip subtitle format
- **Encoding**: UTF-8 encoding for international characters
- **Timing**: Supports millisecond precision

### Video Format Support
- **Input**: Any format supported by ffmpeg (MP4, AVI, MOV, etc.)
- **Output**: Maintains original container format
- **Codecs**: Preserves original video and audio codecs

### Performance
- **Fast Processing**: Uses stream copying instead of re-encoding
- **Memory Efficient**: Processes subtitles in chunks
- **Batch Processing**: Handles multiple parts automatically

## Error Handling

The script includes comprehensive error handling:
- ✅ File existence validation
- ✅ SRT format validation
- ✅ ffmpeg error reporting
- ✅ Timing consistency checks

## Example Output

```
🎬 Video and Subtitle Splitter
========================================
🎯 Splitting by segments: 20 subtitles per part
✅ Parsed 60 subtitle segments from video_sample.srt
📁 Output directory: output_parts
🎬 Will create 3 parts

--- Part 1/3 ---
📝 Subtitles: 1-20 (20 segments)
⏰ Time: 00:00:00,000 - 00:00:37,000
⏱️  Duration: 37.0 seconds
🎬 Creating video part: output_parts/video_sample_part01.mp4
📝 Created subtitle part: video_sample_part01.srt
✅ Part 1 completed successfully

🏁 Completed: 3/3 parts successful
```

## Use Cases

### Content Creation
- **YouTube Shorts**: Create short-form content from long videos
- **Social Media**: Generate clips for Instagram, TikTok
- **Tutorials**: Break down long tutorials into digestible parts

### Language Learning
- **Bite-sized Lessons**: Split language content by subtitle count
- **Practice Sessions**: Create focused practice materials
- **Vocabulary Building**: Isolate specific conversation segments

### Education
- **Lecture Segments**: Break lectures into topic-based parts
- **Review Materials**: Create focused study segments
- **Assignment Preparation**: Extract specific content sections

## Troubleshooting

### Common Issues

**ffmpeg not found**:
```bash
# Install ffmpeg first
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

**Encoding errors**:
- Ensure subtitle files are UTF-8 encoded
- Check for malformed SRT format

**Video processing fails**:
- Verify video file is not corrupted
- Check available disk space for output

### Getting Help
```bash
# Show usage help
python video_splitter.py

# Test with sample files
python video_splitter.py test
```

## Integration with Whisper

This script works perfectly with the existing Whisper workflow:

1. **Generate subtitles** with Whisper:
   ```bash
   python main.py video.mp4 base
   ```

2. **Split the video** and subtitles:
   ```bash
   python video_splitter.py segments video.mp4 video.srt 15
   ```

3. **Add subtitles** to parts (optional):
   ```bash
   python subtitle_helper.py add video_part01.mp4 video_part01.srt
   ```

---

**Created by**: Video Processing Toolkit  
**Compatible with**: Python 3.6+, ffmpeg 4.0+  
**License**: Open source for educational and commercial use
