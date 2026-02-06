#!/usr/bin/env python3
"""
Video Processing Utilities
Common utility functions for video file handling, metadata extraction, and file management
"""

import os
import json
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

logger = logging.getLogger(__name__)


# ============================================================================
# RESULT CLASSES
# ============================================================================

class ProcessingResult:
    """Result container for video processing"""
    def __init__(self):
        self.success = False
        self.video_path = ""
        self.transcript_path = ""
        self.video_parts = []  # List of video part paths if split
        self.transcript_parts = []  # List of transcript part paths if split
        self.video_info = {}
        self.processing_time = 0
        self.transcript_source = ""  # "bilibili" or "whisper"
        self.was_split = False
        self.error_message = ""
        self.engaging_moments_analysis = {}  # Results from engaging moments analysis
        self.clip_generation = {}  # Results from clip generation
        self.title_addition = {}  # Results from title addition
        self.cover_generation = {}  # Results from cover image generation


class ResultsFormatter:
    """Formats and displays processing results"""
    
    @staticmethod
    def print_results(result: ProcessingResult):
        """Print processing results in a nice format"""
        print("\n" + "="*60)
        print("🎬 VIDEO PROCESSING RESULTS")
        print("="*60)
        
        if result.success:
            print("✅ Status: SUCCESS")
        else:
            print("❌ Status: FAILED")
            print(f"   Error: {result.error_message}")
            return
        
        print(f"⏱️  Processing time: {result.processing_time:.1f} seconds")
        print(f"📝 Transcript source: {result.transcript_source}")
        print(f"🔧 Was split: {'Yes' if result.was_split else 'No'}")
        
        if result.video_info:
            video_info = result.video_info
            print(f"📺 Title: {video_info.get('title', 'Unknown')}")
            print(f"👤 Uploader: {video_info.get('uploader', 'Unknown')}")
            if 'duration' in video_info:
                duration_min = video_info['duration'] / 60
                print(f"⏱️  Duration: {duration_min:.1f} minutes")
        
        print("\n📁 OUTPUT FILES:")
        
        if not result.was_split:
            print(f"   Video: {result.video_path}")
            if result.transcript_path:
                print(f"   Transcript: {result.transcript_path}")
        else:
            print(f"   Video parts ({len(result.video_parts)}):")
            for i, part in enumerate(result.video_parts, 1):
                print(f"     Part {i}: {Path(part).name}")
            
            print(f"   Transcript parts ({len(result.transcript_parts)}):")
            for i, part in enumerate(result.transcript_parts, 1):
                print(f"     Part {i}: {Path(part).name}")
        
        # Display engaging moments analysis results
        if result.engaging_moments_analysis:
            analysis = result.engaging_moments_analysis
            if 'error' not in analysis:
                print(f"\n🧠 ENGAGING MOMENTS ANALYSIS:")
                print(f"   Parts analyzed: {analysis.get('total_parts_analyzed', 0)}")
                if analysis.get('highlights_files'):
                    print(f"   Highlights files: {len(analysis['highlights_files'])}")
                if analysis.get('aggregated_file'):
                    print(f"   Top moments file: {Path(analysis['aggregated_file']).name}")
                if analysis.get('top_moments') and analysis['top_moments'].get('top_engaging_moments'):
                    top_moments = analysis['top_moments']['top_engaging_moments']
                    print(f"   Top engaging moments found: {len(top_moments)}")
                    for moment in top_moments:  # Show all
                        print(f"     • {moment.get('title', 'No title')} ({moment.get('duration_seconds', 0)}s)")
            else:
                print(f"\n🧠 ENGAGING MOMENTS ANALYSIS: Failed - {analysis['error']}")
        
        # Display clip generation results
        if result.clip_generation:
            clip_gen = result.clip_generation
            if clip_gen.get('success'):
                print(f"\n🎬 CLIP GENERATION:")
                print(f"   Clips generated: {clip_gen.get('successful_clips', 0)}/{clip_gen.get('total_clips', 0)}")
                print(f"   Output directory: {clip_gen.get('output_dir', 'N/A')}")
                if clip_gen.get('clips_info'):
                    print(f"   Generated clips:")
                    for clip in clip_gen['clips_info']:
                        print(f"     • {clip.get('filename', 'N/A')}")
            else:
                error = clip_gen.get('error', 'Unknown error')
                print(f"\n🎬 CLIP GENERATION: Failed - {error}")
        
        # Display title addition results
        if result.title_addition:
            title_add = result.title_addition
            if title_add.get('success'):
                print(f"\n🎨 TITLE ADDITION:")
                print(f"   Titles added: {title_add.get('successful_clips', 0)}/{title_add.get('total_clips', 0)}")
                print(f"   Artistic style: {title_add.get('artistic_style', 'N/A')}")
                print(f"   Output directory: {title_add.get('output_dir', 'N/A')}")
                if title_add.get('processed_clips'):
                    print(f"   Processed clips:")
                    for clip in title_add['processed_clips']:
                        print(f"     • {clip.get('filename', 'N/A')}")
            else:
                error = title_add.get('error', 'Unknown error')
                print(f"\n🎨 TITLE ADDITION: Failed - {error}")
        
        # Display cover generation results
        if result.cover_generation:
            cover_gen = result.cover_generation
            if cover_gen.get('success'):
                print(f"\n🖼️  COVER GENERATION:")
                print(f"   Covers generated: {cover_gen.get('total_covers', 0)}")
                print(f"   Output directory: {cover_gen.get('output_dir', 'N/A')}")
                if cover_gen.get('covers'):
                    print(f"   Generated covers:")
                    for cover in cover_gen['covers']:
                        print(f"     • [{cover.get('rank')}] {cover.get('filename', 'N/A')}")
            else:
                error = cover_gen.get('error', 'Unknown error')
                print(f"\n🖼️  COVER GENERATION: Failed - {error}")
        
        print("\n" + "="*60)


# ============================================================================
# VALIDATOR CLASSES
# ============================================================================


class VideoFileValidator:
    """Validates and processes video files"""
    
    # Supported video file extensions
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp'}
    
    # Supported subtitle extensions
    SUBTITLE_EXTENSIONS = ['.srt', '.vtt', '.ass']
    
    @classmethod
    def is_local_video_file(cls, source: str) -> bool:
        """Check if source is a local video file or URL"""
        # Check if it's a URL
        if source.startswith(('http://', 'https://', 'ftp://')):
            return False
        
        # Check if it's a valid file path
        path = Path(source)
        if not path.exists():
            return False
        
        # Check if it's a video file by extension
        return path.suffix.lower() in cls.VIDEO_EXTENSIONS
    
    @classmethod
    def is_video_file(cls, file_path: str) -> bool:
        """Check if file is a video file by extension"""
        return Path(file_path).suffix.lower() in cls.VIDEO_EXTENSIONS


class VideoMetadataExtractor:
    """Extracts video metadata using ffprobe"""
    
    @staticmethod
    async def get_video_info_ffprobe(video_path: str) -> Dict[str, Any]:
        """Get video information using ffprobe"""
        try:
            # Use ffprobe to get video information
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"ffprobe failed: {stderr.decode()}")
            
            probe_data = json.loads(stdout.decode())
            
            # Extract relevant information
            format_info = probe_data.get('format', {})
            video_stream = None
            
            # Find the first video stream
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            duration = float(format_info.get('duration', 0))
            title = Path(video_path).stem
            
            video_info = {
                'title': title,
                'duration': duration,
                'uploader': 'Local File',
                'description': f'Local video file: {Path(video_path).name}',
                'view_count': 0,
                'upload_date': datetime.now().strftime('%Y%m%d'),
                'webpage_url': f'file://{video_path}',
                'width': video_stream.get('width', 0) if video_stream else 0,
                'height': video_stream.get('height', 0) if video_stream else 0,
                'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0
            }
            
            logger.info(f"📊 Video info: {title}, {duration:.1f}s, {video_info.get('width')}x{video_info.get('height')}")
            
            return video_info
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to get video info with ffprobe: {e}")
            # Fallback to basic info
            return VideoMetadataExtractor._get_fallback_video_info(video_path)
    
    @staticmethod
    def _get_fallback_video_info(video_path: str) -> Dict[str, Any]:
        """Fallback video info when ffprobe fails"""
        return {
            'title': Path(video_path).stem,
            'duration': 0,  # Will be treated as unknown
            'uploader': 'Local File',
            'description': f'Local video file: {Path(video_path).name}',
            'view_count': 0,
            'upload_date': datetime.now().strftime('%Y%m%d'),
            'webpage_url': f'file://{video_path}'
        }


class VideoFileManager:
    """Manages video file operations like copying, organizing, and finding files"""
    
    @staticmethod
    def copy_video_to_output(video_path: str, output_dir: Path) -> Path:
        """Copy video file to output directory"""
        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create local videos directory
        local_videos_dir = output_dir / "local_videos"
        local_videos_dir.mkdir(exist_ok=True)
        
        processed_video_path = local_videos_dir / video_file.name
        
        if not processed_video_path.exists():
            # Copy the video to our output directory
            shutil.copy2(video_path, processed_video_path)
            logger.info(f"📋 Copied video to: {processed_video_path}")
        else:
            logger.info(f"📁 Using existing copy: {processed_video_path}")
        
        return processed_video_path
    
    @staticmethod
    def find_existing_subtitle(video_path: str, output_dir: Path) -> str:
        """Find existing subtitle file for a video"""
        video_file = Path(video_path)
        subtitle_path = ''
        
        for ext in VideoFileValidator.SUBTITLE_EXTENSIONS:
            potential_subtitle = video_file.parent / f"{video_file.stem}{ext}"
            if potential_subtitle.exists():
                # Copy subtitle to output directory
                subtitle_dest = output_dir / "local_videos" / f"{video_file.stem}{ext}"
                shutil.copy2(potential_subtitle, subtitle_dest)
                subtitle_path = str(subtitle_dest)
                logger.info(f"📝 Found existing subtitle: {potential_subtitle.name}")
                break
        
        return subtitle_path
    
    @staticmethod
    def find_downloaded_video(output_dir: Path, title: str) -> Optional[Path]:
        """Find downloaded video file"""
        possible_extensions = ['.mp4', '.mkv', '.webm', '.flv']
        
        for ext in possible_extensions:
            video_path = output_dir / f"{title}{ext}"
            if video_path.exists():
                return video_path
        
        # Fuzzy matching
        for file_path in output_dir.glob(f"{title}*"):
            if file_path.suffix.lower() in possible_extensions:
                return file_path
        
        return None
    
    @staticmethod
    def find_downloaded_subtitle(output_dir: Path, title: str) -> Optional[Path]:
        """Find downloaded subtitle file with AI subtitle priority"""
        logger.info(f"Looking for subtitle file with title: {title}")
        
        # Check for AI subtitle first
        ai_subtitle_path = output_dir / f"{title}.ai-zh.srt"
        if ai_subtitle_path.exists():
            # Rename to standard format
            standard_path = output_dir / f"{title}.srt"
            if not standard_path.exists():
                ai_subtitle_path.rename(standard_path)
                logger.info(f"Renamed AI subtitle: {title}.ai-zh.srt -> {title}.srt")
                return standard_path
            return ai_subtitle_path
        
        # Check standard format
        standard_path = output_dir / f"{title}.srt"
        if standard_path.exists():
            logger.info(f"Found standard subtitle: {title}.srt")
            return standard_path
        
        # Fuzzy matching for subtitle files
        for file_path in output_dir.glob(f"{title}*.srt"):
            logger.info(f"Found subtitle file: {file_path.name}")
            return file_path
        
        logger.warning(f"No subtitle file found for title: {title}")
        return None
    
    @staticmethod
    def find_video_parts(splits_dir: Path, base_name: str) -> tuple[List[str], List[str]]:
        """Find all video and transcript parts after splitting"""
        split_output_dir = splits_dir / f"{base_name}_split"
        
        video_parts = []
        transcript_parts = []
        
        for file_path in split_output_dir.glob(f"{base_name}_part*.mp4"):
            video_parts.append(str(file_path))
        
        for file_path in split_output_dir.glob(f"{base_name}_part*.srt"):
            transcript_parts.append(str(file_path))
        
        video_parts.sort()
        transcript_parts.sort()
        
        return video_parts, transcript_parts


class ProgressCallbackManager:
    """Manages progress callback creation and mapping"""
    
    @staticmethod
    def create_download_progress_callback(progress_callback: Optional[callable], 
                                        start_percent: float = 0, 
                                        end_percent: float = 25) -> Optional[callable]:
        """Create progress callback for download phase"""
        if not progress_callback:
            return None
        
        def download_progress(status: str, progress: float):
            # Map download progress to specified range of total
            total_progress = start_percent + (progress * (end_percent - start_percent) / 100)
            progress_callback(f"Downloading: {status}", total_progress)
        
        return download_progress
    
    @staticmethod
    def create_whisper_progress_callback(progress_callback: Optional[callable],
                                       current_file: int,
                                       total_files: int,
                                       start_percent: float = 60,
                                       end_percent: float = 95) -> float:
        """Create progress update for Whisper transcription"""
        if not progress_callback:
            return 0
        
        progress = start_percent + (current_file / total_files) * (end_percent - start_percent)
        progress_callback(f"Generating transcript for part {current_file + 1}/{total_files}...", progress)
        return progress


class FileNameSanitizer:
    """Utilities for sanitizing and managing file names"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing unsafe characters"""
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit filename length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip()


class VideoDirectoryProcessor:
    """Utilities for batch processing video directories"""
    
    @staticmethod
    def find_videos_in_directory(directory: Path, 
                                recursive: bool = False) -> List[Path]:
        """Find all video files in a directory"""
        video_files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for ext in VideoFileValidator.VIDEO_EXTENSIONS:
            video_files.extend(directory.glob(f"{pattern}{ext}"))
        
        return sorted(video_files)
    
    @staticmethod
    def get_video_file_info(video_path: Path) -> Dict[str, Any]:
        """Get basic info about a video file"""
        try:
            stat = video_path.stat()
            return {
                'name': video_path.name,
                'path': str(video_path),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': video_path.suffix.lower()
            }
        except Exception as e:
            logger.warning(f"Could not get info for {video_path}: {e}")
            return {
                'name': video_path.name,
                'path': str(video_path),
                'size': 0,
                'modified': datetime.now(),
                'extension': video_path.suffix.lower()
            }


# Convenience functions for common operations
async def process_local_video_file(video_path: str, output_dir: Path) -> Dict[str, Any]:
    """Complete local video processing workflow"""
    # Copy video to output directory
    processed_video_path = VideoFileManager.copy_video_to_output(video_path, output_dir)
    
    # Get video information using ffprobe
    video_info = await VideoMetadataExtractor.get_video_info_ffprobe(str(processed_video_path))
    
    # Look for existing subtitle file
    subtitle_path = VideoFileManager.find_existing_subtitle(video_path, output_dir)
    
    return {
        'video_path': str(processed_video_path),
        'video_info': video_info,
        'subtitle_path': subtitle_path
    }


def validate_video_source(source: str) -> tuple[bool, str]:
    """Validate and classify video source"""
    if VideoFileValidator.is_local_video_file(source):
        return True, "local_file"
    elif source.startswith(('http://', 'https://')):
        return True, "url"
    else:
        return False, "unknown"


async def find_existing_download(url: str, 
                               output_dir: Path, 
                               progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """
    Find existing downloaded video for a URL (supports Bilibili and YouTube)
    
    Args:
        url: Video URL (Bilibili or YouTube)
        output_dir: Base output directory
        progress_callback: Progress callback function
        
    Returns:
        Dictionary with video path, info, and subtitle path
    """
    if progress_callback:
        progress_callback("Looking for existing download...", 10)
    
    try:
        # Extract video ID from URL to find the dedicated directory
        import re
        
        # Try Bilibili pattern
        bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
        if bv_match:
            video_id = bv_match.group()
        else:
            # Try YouTube patterns
            yt_patterns = [
                r'youtube\.com/watch\?v=([\w-]+)',
                r'youtu\.be/([\w-]+)',
                r'youtube\.com/shorts/([\w-]+)',
                r'youtube\.com/embed/([\w-]+)',
            ]
            video_id = None
            for pattern in yt_patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
            
            if not video_id:
                raise Exception("Could not extract video ID from URL")
        
        # Look for dedicated directory in downloads
        downloads_dir = output_dir / "downloads"
        video_dir = None
        
        # Find directory that starts with the video ID
        for dir_path in downloads_dir.glob(f"{video_id}*"):
            if dir_path.is_dir():
                video_dir = dir_path
                break
        
        if not video_dir:
            raise Exception(f"No existing download directory found for {video_id}")
        
        logger.info(f"📁 Found existing download directory: {video_dir.name}")
        
        # Find video and subtitle files in the directory
        video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.mkv")) + list(video_dir.glob("*.webm"))
        if not video_files:
            raise Exception(f"No video files found in {video_dir}")
        
        video_path = str(video_files[0])  # Take the first video file
        
        # Look for subtitle file
        subtitle_files = list(video_dir.glob("*.srt"))
        subtitle_path = str(subtitle_files[0]) if subtitle_files else ""
        
        # Look for info file to get video metadata
        info_files = list(video_dir.glob("*.info.json"))
        video_info = {}
        if info_files:
            try:
                with open(info_files[0], 'r', encoding='utf-8') as f:
                    video_info = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load video info: {e}")
                video_info = {'title': video_dir.name, 'duration': 0}
        else:
            video_info = {'title': video_dir.name, 'duration': 0}
        
        if progress_callback:
            progress_callback("Found existing download", 25)
        
        return {
            'video_path': video_path,
            'video_info': video_info,
            'subtitle_path': subtitle_path
        }
        
    except Exception as e:
        logger.error(f"Error finding existing download: {e}")
        return {
            'video_path': None,
            'video_info': {},
            'subtitle_path': ""
        }


async def export_agent_prompts(result: 'ProcessingResult', 
                              output_dir: Path, 
                              use_background: bool = False, 
                              language: str = "zh", 
                              custom_prompt_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Export analysis prompts for agent step. Creates prompt files and a manifest
    so an external agent can perform the analysis and write results.

    Args:
        result: ProcessingResult with transcript information
        output_dir: Base output directory
        use_background: Whether to include background information in analysis prompts
        language: Language for output ("zh" for Chinese, "en" for English)
        custom_prompt_file: Path to custom prompt file (optional)

    Returns:
        Dictionary with manifest data including file paths
    """
    import json as json_module

    # Create a prompt-only analyzer (no API key needed)
    analyzer = EngagingMomentsAnalyzer(
        api_key=None,
        provider="agent",
        use_background=use_background,
        language=language,
        debug=False,
        custom_prompt_file=custom_prompt_file
    )

    manifest = {
        'mode': 'agent_analysis',
        'source': str(result.video_path),
        'prompts': [],
        'aggregation_prompt': None,
        'aggregation_output': None,
    }

    transcript_dir = None

    if result.was_split and result.transcript_parts:
        transcript_dir = Path(result.transcript_parts[0]).parent

        for i, transcript_path in enumerate(result.transcript_parts):
            part_name = f"part{i+1:02d}"
            prompt_content = analyzer.build_part_analysis_prompt(transcript_path, part_name)

            if not prompt_content:
                logger.warning(f"Empty prompt for {part_name}, skipping")
                continue

            prompt_file = transcript_dir / f"agent_prompt_{part_name}.md"
            prompt_file.write_text(prompt_content, encoding='utf-8')

            expected_output = transcript_dir / f"highlights_{part_name}.json"

            manifest['prompts'].append({
                'part_name': part_name,
                'prompt_file': str(prompt_file),
                'transcript_file': str(transcript_path),
                'expected_output': str(expected_output),
            })
            logger.info(f"   Exported prompt for {part_name}: {prompt_file}")

        manifest['aggregation_output'] = str(transcript_dir / "top_engaging_moments.json")

        # Note: aggregation prompt can't be fully built until per-part analysis is done.
        # Export the aggregation prompt template for reference.
        agg_prompt_template = analyzer.load_prompt_template("engaging_moments_agg_requirement")
        agg_prompt_file = transcript_dir / "agent_prompt_aggregation.md"
        agg_prompt_file.write_text(agg_prompt_template, encoding='utf-8')
        manifest['aggregation_prompt'] = str(agg_prompt_file)
        logger.info(f"   Exported aggregation prompt template: {agg_prompt_file}")

    elif result.transcript_path:
        transcript_dir = Path(result.transcript_path).parent
        prompt_content = analyzer.build_part_analysis_prompt(result.transcript_path, "full_video")

        if prompt_content:
            prompt_file = transcript_dir / "agent_prompt_full_video.md"
            prompt_file.write_text(prompt_content, encoding='utf-8')

            expected_output = transcript_dir / "top_engaging_moments.json"

            manifest['prompts'].append({
                'part_name': 'full_video',
                'prompt_file': str(prompt_file),
                'transcript_file': str(result.transcript_path),
                'expected_output': str(expected_output),
            })
            manifest['aggregation_output'] = str(expected_output)
            logger.info(f"   Exported prompt for full_video: {prompt_file}")
    else:
        logger.warning("No transcripts available for agent prompt export")
        return manifest

    # Write manifest
    manifest_dir = transcript_dir if transcript_dir else output_dir
    manifest_path = manifest_dir / "agent_analysis_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json_module.dump(manifest, f, ensure_ascii=False, indent=2)
    manifest['manifest_path'] = str(manifest_path)

    return manifest