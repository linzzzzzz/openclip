#!/usr/bin/env python3
"""
Video Processing Orchestrator
Orchestrates bilibili_downloader.py, video_splitter.py, and transcript_generation_whisper.py
"""

import sys
import asyncio
import argparse
import logging
import re
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import os

# Import our components from core package
from core.downloaders import VideoDownloader, DownloadProcessor
from core.video_splitter import VideoSplitter
from core.transcript_generation_whisper import TranscriptProcessor
from core.engaging_moments_analyzer import EngagingMomentsAnalyzer
from core.clip_generator import ClipGenerator
from core.title_adder import TitleAdder
from core.cover_image_generator import CoverImageGenerator

# Import our utilities (including processing result classes)
from core.video_utils import (
    VideoFileValidator, 
    process_local_video_file,
    ProcessingResult,
    ResultsFormatter,
    find_existing_download
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VideoOrchestrator:
    """
    Orchestrates video download, splitting, and transcript generation
    """
    
    def __init__(self, 
                 output_dir: str = "processed_videos",
                 max_duration_minutes: float = 20.0,
                 whisper_model: str = "base",
                 browser: str = "firefox",
                 qwen_api_key: Optional[str] = None,
                 skip_analysis: bool = False,
                 generate_clips: bool = True,
                 add_titles: bool = True,
                 artistic_style: str = "crystal_ice",
                 use_background: bool = False,
                 generate_cover: bool = True,
                 language: str = "zh",
                 debug: bool = False):
        """
        Initialize the video orchestrator
        
        Args:
            output_dir: Directory for all processed outputs
            max_duration_minutes: Maximum duration before splitting (default 20 minutes)
            whisper_model: Whisper model to use for transcript generation
            browser: Browser for cookie extraction
            qwen_api_key: Qwen API key for engaging moments analysis
            skip_analysis: Skip engaging moments analysis (clips can still use existing analysis file)
            generate_clips: Whether to generate clips from engaging moments
            add_titles: Whether to add artistic titles to clips
            artistic_style: Style for artistic titles (crystal_ice, gradient_3d, neon_glow, etc.)
            use_background: Whether to include background information in analysis prompts
            generate_cover: Whether to generate cover images
            language: Language for output ("zh" for Chinese, "en" for English)
            debug: Enable debug mode to export full prompts sent to LLM
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.language = language
        self.debug = debug
        
        # Initialize processing components
        self.downloader = VideoDownloader(
            output_dir=str(self.output_dir / "downloads"),
            browser=browser
        )
        self.video_splitter = VideoSplitter(max_duration_minutes, self.output_dir)
        self.transcript_processor = TranscriptProcessor(whisper_model)
        self.download_processor = DownloadProcessor(self.downloader)
        
        # Initialize engaging moments analyzer only if not skipping and API key is available
        self.skip_analysis = skip_analysis
        self.engaging_moments_analyzer = None
        if not skip_analysis and qwen_api_key:
            try:
                self.engaging_moments_analyzer = EngagingMomentsAnalyzer(
                    qwen_api_key, 
                    use_background=use_background,
                    language=language,
                    debug=self.debug
                )
                logger.info(f"🧠 Engaging moments analysis: enabled (language: {language}, background: {'yes' if use_background else 'no'})")
            except ValueError as e:
                logger.warning(f"🔑 Engaging moments analysis disabled: {e}")
        elif skip_analysis:
            logger.info("🧠 Engaging moments analysis: skipped (--skip-analysis)")
        else:
            logger.info("🧠 Engaging moments analysis: disabled (no QWEN_API_KEY)")
        
        # Initialize clip generation and title adding components
        # These can work independently if analysis file already exists
        self.generate_clips_enabled = generate_clips
        self.add_titles_enabled = add_titles
        self.artistic_style = artistic_style
        
        # Set up clip directories under output_dir
        self.clips_dir = self.output_dir / "clips"
        self.clips_with_titles_dir = self.output_dir / "clips_with_titles"
        
        if self.generate_clips_enabled:
            self.clip_generator = ClipGenerator(output_dir=str(self.clips_dir))
            logger.info(f"🎬 Clip generation: enabled (output: {self.clips_dir})")
        else:
            self.clip_generator = None
            logger.info("🎬 Clip generation: disabled")
        
        if self.add_titles_enabled:
            self.title_adder = TitleAdder(output_dir=str(self.clips_with_titles_dir))
            logger.info(f"🎨 Title adding: enabled (style: {artistic_style}, output: {self.clips_with_titles_dir})")
        else:
            self.title_adder = None
            logger.info("🎨 Title adding: disabled")
        
        # Initialize cover image generator
        self.generate_cover_enabled = generate_cover
        if self.generate_cover_enabled:
            self.cover_generator = CoverImageGenerator()
            logger.info("🖼️  Cover generation: enabled")
        else:
            self.cover_generator = None
            logger.info("🖼️  Cover generation: disabled")
        
        logger.info(f"🎬 Video Orchestrator initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"⏱️  Max duration: {max_duration_minutes} minutes")
        logger.info(f"🤖 Whisper model: {whisper_model}")
    
    async def process_video(self, 
                          source: str, 
                          force_whisper: bool = False,
                          custom_filename: Optional[str] = None,
                          skip_download: bool = False,
                          progress_callback: Optional[Callable[[str, float], None]] = None) -> ProcessingResult:
        """
        Complete video processing pipeline
        
        Args:
            source: Video URL (Bilibili/YouTube) or local video file path
            force_whisper: Force transcript generation via Whisper (ignore platform subtitles)
            custom_filename: Custom filename template
            skip_download: Skip video download (use existing downloaded video)
            progress_callback: Progress callback function
            
        Returns:
            ProcessingResult object with all processing information
        """
        result = ProcessingResult()
        start_time = datetime.now()
        
        try:
            if progress_callback:
                progress_callback("Starting video processing...", 0)
            
            # Check if source is a local file or URL
            is_local_file = await self._is_local_video_file(source)
            
            if is_local_file:
                # Step 1: Process local video file
                logger.info("📁 Step 1: Processing local video file...")
                file_result = await self._process_local_video(source, progress_callback)
                result.video_path = file_result['video_path']
                result.video_info = file_result['video_info']
                subtitle_path = file_result.get('subtitle_path', '')
            else:
                if skip_download:
                    # Step 1: Find existing downloaded video
                    logger.info("🔍 Step 1: Looking for existing downloaded video...")
                    download_result = await self._find_existing_download(source, progress_callback)
                    
                    if not download_result['video_path']:
                        raise Exception("No existing download found. Remove --skip-download to download the video.")
                    
                    result.video_path = download_result['video_path']
                    result.video_info = download_result['video_info']
                    subtitle_path = download_result['subtitle_path']
                else:
                    # Step 1: Download video and get info
                    logger.info("📥 Step 1: Downloading video...")
                    download_result = await self._download_video(source, custom_filename, progress_callback)
                    
                    if not download_result['video_path']:
                        raise Exception("Video download failed")
                    
                    result.video_path = download_result['video_path']
                    result.video_info = download_result['video_info']
                    subtitle_path = download_result['subtitle_path']
            
            # Step 2: Check duration and split if needed
            logger.info("⏱️  Step 2: Checking video duration...")
            needs_splitting = self.video_splitter.check_duration_needs_splitting(result.video_info)
            
            if needs_splitting:
                logger.info(f"🔧 Video duration > 20 minutes, splitting required")
                split_result = await self.video_splitter.split_video_async(
                    result.video_path, 
                    subtitle_path,
                    progress_callback
                )
                result.was_split = True
                result.video_parts = split_result['video_parts']
                result.transcript_parts = split_result['transcript_parts']
            
            # Step 3: Handle transcript generation
            logger.info("📝 Step 3: Processing transcripts...")
            transcript_result = await self.transcript_processor.process_transcripts(
                subtitle_path,
                result.video_path if not result.was_split else result.video_parts,
                force_whisper,
                progress_callback
            )
            
            result.transcript_source = transcript_result['source']
            if not result.was_split:
                result.transcript_path = transcript_result['transcript_path']
            else:
                # Transcript parts were already set during splitting if bilibili subtitles used
                if transcript_result['source'] == 'whisper':
                    result.transcript_parts = transcript_result['transcript_parts']
            
            # Step 4: Analyze engaging moments (if not skipped and analyzer available)
            engaging_result = None
            if self.engaging_moments_analyzer and not self.skip_analysis:
                logger.info("🧠 Step 4: Analyzing engaging moments...")
                engaging_result = await self._analyze_engaging_moments(result, progress_callback)
                result.engaging_moments_analysis = engaging_result
            elif self.skip_analysis:
                logger.info("🧠 Step 4: Skipping engaging moments analysis (--skip-analysis)")
                # Try to find existing analysis file for clip generation
                engaging_result = self._find_existing_analysis(result)
                if engaging_result:
                    result.engaging_moments_analysis = engaging_result
                    logger.info(f"   Found existing analysis: {engaging_result.get('aggregated_file')}")
            
            # Step 5: Generate clips from engaging moments (if enabled and analysis available)
            if self.clip_generator and engaging_result and engaging_result.get('aggregated_file'):
                logger.info("🎬 Step 5: Generating clips from engaging moments...")
                if progress_callback:
                    progress_callback("Generating video clips...", 85)
                
                # Determine video directory
                if result.was_split and result.video_parts:
                    video_dir = Path(result.video_parts[0]).parent
                else:
                    video_dir = Path(result.video_path).parent
                
                # Create subfolder based on video name
                video_name = result.video_info.get('title', 'video')
                # Sanitize video name for folder
                safe_video_name = re.sub(r'[^\w\s-]', '', video_name)
                safe_video_name = re.sub(r'[\s\-]+', '_', safe_video_name)
                safe_video_name = re.sub(r'_+', '_', safe_video_name).strip('_')
                
                # Create video-specific subfolder
                video_clips_dir = self.clips_dir / safe_video_name
                video_clips_dir.mkdir(parents=True, exist_ok=True)
                
                # Update clip generator output dir
                self.clip_generator.output_dir = video_clips_dir
                
                clip_result = self.clip_generator.generate_clips_from_analysis(
                    engaging_result['aggregated_file'],
                    str(video_dir)
                )
                result.clip_generation = clip_result
                
                # Step 6: Add artistic titles to clips (if enabled)
                if self.title_adder and clip_result.get('success'):
                    logger.info("🎨 Step 6: Adding artistic titles to clips...")
                    if progress_callback:
                        progress_callback("Adding artistic titles...", 92)
                    
                    # Create video-specific subfolder for titles
                    video_titles_dir = self.clips_with_titles_dir / safe_video_name
                    video_titles_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Update title adder output dir
                    self.title_adder.output_dir = video_titles_dir
                    
                    title_result = self.title_adder.add_titles_to_clips(
                        clip_result['output_dir'],
                        engaging_result['aggregated_file'],
                        self.artistic_style
                    )
                    result.title_addition = title_result
            elif self.clip_generator and not engaging_result:
                logger.warning("⚠️  Clip generation enabled but no analysis file found")
            
            # Step 7: Generate cover images (if enabled and analysis available)
            if self.cover_generator and engaging_result and engaging_result.get('aggregated_file'):
                logger.info("🖼️  Step 7: Generating cover images...")
                if progress_callback:
                    progress_callback("Generating cover images...", 95)
                
                # Pass the video-specific clip directory to cover generation
                cover_result = self._generate_cover_image(result, engaging_result, video_clips_dir, video_titles_dir)
                result.cover_generation = cover_result
            
            result.success = True
            
            if progress_callback:
                progress_callback("Processing completed successfully!", 100)
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            logger.error(error_msg)
            result.error_message = error_msg
            if progress_callback:
                progress_callback(error_msg, 0)
        
        finally:
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()
        
        return result
    
    async def _is_local_video_file(self, source: str) -> bool:
        """Check if source is a local video file or URL"""
        return VideoFileValidator.is_local_video_file(source)
    
    async def _process_local_video(self, 
                                 video_path: str,
                                 progress_callback: Optional[Callable[[str, float], None]]) -> Dict[str, Any]:
        """Process local video file using utilities"""
        if progress_callback:
            progress_callback("Processing local video file...", 10)
        
        logger.info(f"📁 Processing local file: {Path(video_path).name}")
        
        # Use utility function for complete local video processing
        result = await process_local_video_file(video_path, self.output_dir)
        
        if progress_callback:
            progress_callback("Local video processed", 25)
        
        return result
    
    async def _download_video(self, 
                            url: str, 
                            custom_filename: Optional[str],
                            progress_callback: Optional[Callable[[str, float], None]]) -> dict:
        """Download video and subtitles using download processor"""
        return await self.download_processor.download_video(url, custom_filename, progress_callback)
    
    async def _find_existing_download(self,
                                    url: str,
                                    progress_callback: Optional[Callable[[str, float], None]]) -> dict:
        """Find existing downloaded video for a URL"""
        return await find_existing_download(url, self.output_dir, progress_callback)
    
    def _find_existing_analysis(self, result: ProcessingResult) -> Optional[Dict[str, Any]]:
        """
        Find existing engaging moments analysis file
        
        Args:
            result: ProcessingResult with video information
            
        Returns:
            Dictionary with analysis file path or None if not found
        """
        try:
            # Determine where to look for analysis file
            if result.was_split and result.transcript_parts:
                # Look in the splits directory
                search_dir = Path(result.transcript_parts[0]).parent
            elif result.transcript_path:
                search_dir = Path(result.transcript_path).parent
            else:
                return None
            
            # Look for top_engaging_moments.json
            analysis_file = search_dir / "top_engaging_moments.json"
            
            if analysis_file.exists():
                logger.info(f"   Found existing analysis file: {analysis_file}")
                return {
                    'aggregated_file': str(analysis_file),
                    'total_parts_analyzed': 0,
                    'from_existing': True
                }
            else:
                logger.warning(f"   No existing analysis file found in: {search_dir}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding existing analysis: {e}")
            return None
    
    async def _analyze_engaging_moments(self, 
                                      result: ProcessingResult,
                                      progress_callback: Optional[Callable[[str, float], None]]) -> Dict[str, Any]:
        """
        Analyze engaging moments from transcripts
        
        Args:
            result: ProcessingResult with transcript information
            progress_callback: Progress callback function
            
        Returns:
            Dictionary with engaging moments analysis results
        """
        try:
            if progress_callback:
                progress_callback("Analyzing engaging moments...", 75)
            
            highlights_files = []
            
            if result.was_split and result.transcript_parts:
                # Analyze each part separately
                logger.info(f"🔍 Analyzing {len(result.transcript_parts)} video parts...")
                
                for i, transcript_path in enumerate(result.transcript_parts):
                    part_name = f"part{i+1:02d}"
                    
                    # Analyze this part
                    highlights = await self.engaging_moments_analyzer.analyze_part_for_engaging_moments(
                        transcript_path, part_name
                    )
                    
                    # Save highlights for this part
                    transcript_dir = Path(transcript_path).parent
                    highlights_file = transcript_dir / f"highlights_{part_name}.json"
                    await self.engaging_moments_analyzer.save_highlights_to_file(highlights, str(highlights_file))
                    highlights_files.append(str(highlights_file))
                    
                    if progress_callback:
                        progress = 75 + (i + 1) * 15 / len(result.transcript_parts)
                        progress_callback(f"Analyzed part {i+1}/{len(result.transcript_parts)}", progress)
                
                # Aggregate top moments
                logger.info("🔄 Aggregating top 5 engaging moments...")
                top_moments = await self.engaging_moments_analyzer.aggregate_top_moments(
                    highlights_files, str(transcript_dir)
                )
                
                # Save aggregated results
                aggregated_file = transcript_dir / "top_engaging_moments.json"
                await self.engaging_moments_analyzer.save_highlights_to_file(top_moments, str(aggregated_file))
                
                return {
                    'highlights_files': highlights_files,
                    'aggregated_file': str(aggregated_file),
                    'top_moments': top_moments,
                    'total_parts_analyzed': len(result.transcript_parts)
                }
                
            elif result.transcript_path:
                # Single video analysis
                logger.info("🔍 Analyzing single video for engaging moments...")
                
                highlights = await self.engaging_moments_analyzer.analyze_part_for_engaging_moments(
                    result.transcript_path, "full_video"
                )
                
                # Save highlights
                transcript_dir = Path(result.transcript_path).parent
                highlights_file = transcript_dir / "highlights_full_video.json"
                await self.engaging_moments_analyzer.save_highlights_to_file(highlights, str(highlights_file))
                
                return {
                    'highlights_files': [str(highlights_file)],
                    'aggregated_file': str(highlights_file),
                    'top_moments': highlights,
                    'total_parts_analyzed': 1
                }
            
            else:
                logger.warning("No transcript available for engaging moments analysis")
                return {
                    'highlights_files': [],
                    'aggregated_file': None,
                    'top_moments': None,
                    'total_parts_analyzed': 0
                }
                
        except Exception as e:
            logger.error(f"Error in engaging moments analysis: {e}")
            return {
                'error': str(e),
                'highlights_files': [],
                'aggregated_file': None,
                'top_moments': None,
                'total_parts_analyzed': 0
            }
    
    def _generate_cover_image(self, result: ProcessingResult, engaging_result: Dict[str, Any], 
                             clips_dir: Path, covers_output_dir: Path) -> Dict[str, Any]:
        """
        Generate cover images for each engaging moment with styled text overlay
        
        Args:
            result: ProcessingResult with video information
            engaging_result: Dictionary with engaging moments analysis
            clips_dir: Directory containing the video clips
            covers_output_dir: Directory to save cover images
            
        Returns:
            Dictionary with cover generation results
        """
        try:
            import json
            import re
            
            # Load analysis data to get all engaging moments
            with open(engaging_result['aggregated_file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            generated_covers = []
            
            # Generate a cover for each engaging moment
            for moment in data['top_engaging_moments']:
                rank = moment['rank']
                moment_title = moment['title']
                
                # Find the corresponding clip file
                safe_moment_title = re.sub(r'[^\w\s-]', '', moment_title)
                safe_moment_title = re.sub(r'[\s\-]+', '_', safe_moment_title)
                safe_moment_title = re.sub(r'_+', '_', safe_moment_title).strip('_')
                
                # Look for the clip in the video-specific clips directory
                clip_filename = f"rank_{rank:02d}_{safe_moment_title}.mp4"
                clip_path = clips_dir / clip_filename
                
                if not clip_path.exists():
                    logger.warning(f"✗ Clip not found for rank {rank}: {clip_filename}")
                    continue
                
                # Generate cover filename
                cover_filename = f"cover_rank_{rank:02d}_{safe_moment_title}.jpg"
                cover_path = covers_output_dir / cover_filename
                
                logger.info(f"[{rank}] Generating cover from clip: {moment_title}")
                
                # Generate cover from first frame of the clip (frame_time=0.0)
                success = self.cover_generator.generate_cover(
                    str(clip_path),
                    moment_title,
                    str(cover_path),
                    frame_time=0.0  # Use first frame of the clip
                )
                
                if success:
                    generated_covers.append({
                        'rank': rank,
                        'title': moment_title,
                        'filename': cover_filename,
                        'path': str(cover_path)
                    })
                    logger.info(f"✓ Cover saved: {cover_filename}")
                else:
                    logger.warning(f"✗ Failed to generate cover for rank {rank}")
            
            if generated_covers:
                return {
                    'success': True,
                    'covers': generated_covers,
                    'total_covers': len(generated_covers),
                    'output_dir': str(covers_output_dir)
                }
            else:
                return {
                    'success': False,
                    'error': 'No covers generated'
                }
                
        except Exception as e:
            logger.error(f"Error generating cover images: {e}")
            return {
                'success': False,
                'error': str(e)
            }


async def main():
    """Main async function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="Video Processing Orchestrator - Download, split, and generate transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic processing (use platform subtitles if available)
  python video_orchestrator.py "https://www.bilibili.com/video/BV1wT6GBBEPp"
  python video_orchestrator.py "https://www.youtube.com/watch?v=5MWT_doo68k"
  
  # Full pipeline with engaging moments, clips, and titles (set QWEN_API_KEY)
  export QWEN_API_KEY=your_api_key
  python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
  python video_orchestrator.py "https://youtu.be/dQw4w9WgXcQ"
  
  # With English output
  python video_orchestrator.py --language en "https://www.youtube.com/watch?v=5MWT_doo68k"
  
  # With background information (streamer names/nicknames) for better analysis
  python video_orchestrator.py --use-background "https://www.bilibili.com/video/BV1ut6JBTEVK"
  
  # With custom artistic style for titles
  python video_orchestrator.py --artistic-style neon_glow "https://www.bilibili.com/video/BV1wT6GBBEPp"
  
  # Skip clip generation but add titles
  python video_orchestrator.py --no-clips "https://www.bilibili.com/video/BV1234567890"
  
  # Analysis only, no clips or titles
  python video_orchestrator.py --no-clips --no-titles "https://www.bilibili.com/video/BV1234567890"
  
  # Skip analysis but generate clips from existing analysis file
  python video_orchestrator.py --skip-download --skip-analysis "https://www.bilibili.com/video/BV1wT6GBBEPp"
  
  # Skip download and use existing video
  python video_orchestrator.py --skip-download "https://www.bilibili.com/video/BV1ut6JBTEVK"
  
  # Force Whisper transcript generation (ignore platform subtitles)
  python video_orchestrator.py --force-whisper "https://www.bilibili.com/video/BV1234567890"
  python video_orchestrator.py --force-whisper "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Custom max duration and whisper model
  python video_orchestrator.py --max-duration 15 --whisper-model small "https://www.bilibili.com/video/BV1234567890"
  
  # Process local video file
  python video_orchestrator.py "/path/to/video.mp4"
  
  # Specify output directory
  python video_orchestrator.py -o "my_outputs" "https://www.bilibili.com/video/BV1234567890"
  
Note: Set QWEN_API_KEY environment variable to enable engaging moments analysis, clip generation, and title addition
        """
    )
    
    parser.add_argument('source', help='Video URL (Bilibili/YouTube) or local video file path')
    parser.add_argument('-o', '--output', default='processed_videos',
                       help='Output directory (default: processed_videos)')
    parser.add_argument('--max-duration', type=float, default=20.0,
                       help='Maximum duration before splitting in minutes (default: 20.0)')
    parser.add_argument('--whisper-model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large', 'turbo'],
                       help='Whisper model to use (default: base)')
    parser.add_argument('--browser', default='firefox',
                       choices=['chrome', 'firefox', 'edge', 'safari'],
                       help='Browser for cookie extraction (default: firefox)')
    parser.add_argument('--force-whisper', action='store_true',
                       help='Force transcript generation via Whisper (ignore platform subtitles)')
    parser.add_argument('--skip-download', action='store_true',
                       help='Skip video download and use existing downloaded video')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Skip engaging moments analysis (can still generate clips from existing analysis file)')
    parser.add_argument('--use-background', action='store_true',
                       help='Include background information (streamer names, nicknames) in analysis prompts')
    parser.add_argument('--no-clips', action='store_true',
                       help='Disable clip generation from engaging moments')
    parser.add_argument('--no-titles', action='store_true',
                       help='Disable adding titles to clips')
    parser.add_argument('--no-cover', action='store_true',
                       help='Disable cover image generation')
    parser.add_argument('--artistic-style', default='fire_flame',
                       choices=['gradient_3d', 'neon_glow', 'metallic_gold', 'rainbow_3d', 'crystal_ice',
                               'fire_flame', 'metallic_silver', 'glowing_plasma', 'stone_carved', 'glass_transparent'],
                       help='Artistic style for titles (default: crystal_ice)')
    parser.add_argument('--language', default='zh',
                       choices=['zh', 'en'],
                       help='Language for output (zh: Chinese, en: English, default: zh)')
    parser.add_argument('-f', '--filename',
                       help='Custom filename template')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode to export full prompts sent to LLM')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get Qwen API key from environment
    qwen_api_key = os.getenv("QWEN_API_KEY")
    
    # Initialize orchestrator
    orchestrator = VideoOrchestrator(
        output_dir=args.output,
        max_duration_minutes=args.max_duration,
        whisper_model=args.whisper_model,
        browser=args.browser,
        qwen_api_key=qwen_api_key,
        skip_analysis=args.skip_analysis,
        generate_clips=not args.no_clips,
        add_titles=not args.no_titles,
        artistic_style=args.artistic_style,
        use_background=args.use_background,
        generate_cover=not args.no_cover,
        language=args.language,
        debug=args.debug
    )
    
    def progress_callback(status: str, progress: float):
        print(f"\r🔄 {status} ({progress:.1f}%)", end='', flush=True)
    
    try:
        print(f"🚀 Starting video processing...")
        print(f"🔗 Source: {args.source}")
        
        # Process video
        result = await orchestrator.process_video(
            args.source,
            force_whisper=args.force_whisper,
            custom_filename=args.filename,
            skip_download=args.skip_download,
            progress_callback=progress_callback
        )
        
        print()  # New line after progress
        
        # Print results using the ResultsFormatter
        ResultsFormatter.print_results(result)
        
        return 0 if result.success else 1
    
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    # Run async main
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
