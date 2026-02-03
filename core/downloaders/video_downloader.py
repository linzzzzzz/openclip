#!/usr/bin/env python3
"""
Unified Video Downloader
Supports both Bilibili and YouTube platforms
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, Callable, Any

from .bilibili_downloader import ImprovedBilibiliDownloader
from .youtube_downloader import YouTubeDownloader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Unified video downloader that automatically detects platform and uses appropriate downloader
    """
    
    def __init__(self, output_dir: str = "downloads", quality: str = "best", browser: str = "firefox"):
        """
        Initialize the unified video downloader
        
        Args:
            output_dir: Base directory to save downloaded videos
            quality: Video quality preference (best, worst, or specific format)
            browser: Browser for cookie extraction (only used for Bilibili)
        """
        self.output_dir = output_dir
        self.quality = quality
        self.browser = browser
        
        # Initialize platform-specific downloaders
        self.bilibili_downloader = ImprovedBilibiliDownloader(
            output_dir=output_dir,
            quality=quality,
            browser=browser
        )
        
        self.youtube_downloader = YouTubeDownloader(
            output_dir=output_dir,
            # quality=quality,
            # browser=browser  # Pass browser to YouTube downloader too
        )
    
    def detect_platform(self, url: str) -> str:
        """
        Detect video platform from URL
        
        Args:
            url: Video URL
            
        Returns:
            Platform name: 'bilibili', 'youtube', or 'unknown'
        """
        # Bilibili patterns
        bilibili_patterns = [
            r'https?://(?:www\.)?bilibili\.com/video/[Bb][Vv][0-9A-Za-z]+',
            r'https?://(?:www\.)?bilibili\.com/bangumi/',
            r'https?://(?:www\.)?b23\.tv/',
            r'https?://(?:m\.)?bilibili\.com/video/',
        ]
        
        # YouTube patterns
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        ]
        
        if any(re.match(pattern, url) for pattern in bilibili_patterns):
            return 'bilibili'
        elif any(re.match(pattern, url) for pattern in youtube_patterns):
            return 'youtube'
        else:
            return 'unknown'
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get video information without downloading
        
        Args:
            url: Video URL
            
        Returns:
            Video information dictionary
        """
        platform = self.detect_platform(url)
        
        if platform == 'bilibili':
            logger.info("🎬 Detected platform: Bilibili")
            video_info = await self.bilibili_downloader.get_video_info(url)
            return video_info.to_dict()
        elif platform == 'youtube':
            logger.info("🎬 Detected platform: YouTube")
            video_info = await self.youtube_downloader.get_video_info(url)
            return video_info.to_dict()
        else:
            raise ValueError(f"Unsupported platform or invalid URL: {url}")
    
    async def download_video(
        self,
        url: str,
        custom_filename: Optional[str] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, str]:
        """
        Download video and subtitles from any supported platform
        
        Args:
            url: Video URL (Bilibili or YouTube)
            custom_filename: Custom filename template
            progress_callback: Progress callback function
            
        Returns:
            Dictionary containing video_path, subtitle_path, and video_info
        """
        platform = self.detect_platform(url)
        
        if platform == 'bilibili':
            logger.info("🎬 Downloading from Bilibili...")
            return await self.bilibili_downloader.download_video(
                url, custom_filename, progress_callback
            )
        elif platform == 'youtube':
            logger.info("🎬 Downloading from YouTube...")
            return await self.youtube_downloader.download_video(
                url, custom_filename, progress_callback
            )
        else:
            raise ValueError(f"Unsupported platform or invalid URL: {url}")


class DownloadProcessor:
    """Handles video downloading operations with unified downloader"""
    
    def __init__(self, downloader: VideoDownloader):
        self.downloader = downloader
    
    async def download_video(self, 
                           url: str, 
                           custom_filename: Optional[str],
                           progress_callback: Optional[Callable[[str, float], None]]) -> Dict[str, Any]:
        """Download video and subtitles with progress tracking"""
        
        # Create progress callback for download phase
        from core.video_utils import ProgressCallbackManager
        download_progress = ProgressCallbackManager.create_download_progress_callback(
            progress_callback, 0, 25
        )
        
        return await self.downloader.download_video(
            url, 
            custom_filename, 
            download_progress
        )
