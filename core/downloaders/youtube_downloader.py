#!/usr/bin/env python3
"""
YouTube Video Downloader using yt-dlp
Follows the same pattern as bilibili_downloader.py for consistency
"""

import os
import asyncio
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Any

import yt_dlp

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeVideoInfo:
    """YouTube video information class"""
    
    def __init__(self, info_dict: Dict[str, Any]):
        self.video_id = info_dict.get('id', '')
        self.title = info_dict.get('title', 'unknown_video')
        self.duration = info_dict.get('duration', 0)
        self.uploader = info_dict.get('uploader', 'unknown')
        self.description = info_dict.get('description', '')
        self.thumbnail_url = info_dict.get('thumbnail', '')
        self.view_count = info_dict.get('view_count', 0)
        self.upload_date = info_dict.get('upload_date', '')
        self.webpage_url = info_dict.get('webpage_url', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'video_id': self.video_id,
            'title': self.title,
            'duration': self.duration,
            'uploader': self.uploader,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'view_count': self.view_count,
            'upload_date': self.upload_date,
            'webpage_url': self.webpage_url
        }


class YouTubeDownloader:
    """
    YouTube video downloader with subtitle support
    """
    
    def __init__(self, output_dir: str = "downloads", quality: str = "best", browser: Optional[str] = None):
        """
        Initialize the YouTube downloader
        
        Args:
            output_dir: Base directory to save downloaded videos (each video gets its own subdirectory)
            quality: Video quality preference (best, worst, or specific format)
            browser: Optional browser to extract cookies from (chrome, firefox, edge, safari)
        """
        self.base_output_dir = Path(output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.quality = quality
        self.browser = browser.lower() if browser else None
        
        # Base yt-dlp options - keep it simple and let yt-dlp handle YouTube
        self.base_opts = {
            'format': self._get_format_selector(),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            # 'subtitleslangs': ['en', 'zh-Hans', 'zh-Hant', 'zh', 'ja', 'ko'],
            'subtitlesformat': 'srt',
            'extractflat': False,
            'writethumbnail': True,
            'writeinfojson': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'noplaylist': True,
            'retries': 10,
            'fragment_retries': 10,
        }
        
        # Add browser cookies if specified (helps with restricted content)
        if self.browser:
            self.base_opts['cookiesfrombrowser'] = (self.browser, None, None, None)
            logger.info(f"🍪 Using cookies from {self.browser} browser")
    
    def _get_format_selector(self) -> str:
        """Get format selector based on quality preference"""
        if self.quality == "best":
            # Prefer H.264 codec for better compatibility
            return "bestvideo[vcodec^=avc1][ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        elif self.quality == "worst":
            return "worst"
        elif self.quality == "audio":
            return "bestaudio/best"
        else:
            return self.quality
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is a valid YouTube URL"""
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing unsafe characters"""
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit filename length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip()
    
    def create_video_directory(self, video_info: 'YouTubeVideoInfo') -> Path:
        """
        Create a dedicated directory for a video
        
        Args:
            video_info: YouTubeVideoInfo object
            
        Returns:
            Path to the created video directory
        """
        # Create directory name with video ID and sanitized title
        safe_title = self._sanitize_filename(video_info.title)
        dir_name = f"{video_info.video_id}_{safe_title}"
        
        # Limit directory name length
        if len(dir_name) > 150:
            dir_name = f"{video_info.video_id}_{safe_title[:100]}"
        
        video_dir = self.base_output_dir / dir_name
        video_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Created video directory: {video_dir.name}")
        return video_dir
    
    async def get_video_info(self, url: str) -> YouTubeVideoInfo:
        """Extract video information without downloading"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        info_opts = self.base_opts.copy()
        info_opts.update({
            'quiet': True,
            'no_warnings': True,
        })
        
        loop = asyncio.get_event_loop()
        info_dict = await loop.run_in_executor(None, self._extract_info_sync, url, info_opts)
        return YouTubeVideoInfo(info_dict)
    
    def _extract_info_sync(self, url: str, ydl_opts: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously extract video information"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    
    async def download_video(
        self, 
        url: str, 
        custom_filename: Optional[str] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, str]:
        """
        Download video and subtitles
        
        Args:
            url: YouTube video URL
            custom_filename: Custom filename template
            progress_callback: Progress callback function
            
        Returns:
            Dictionary containing video_path, subtitle_path, and video_info
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        # Get video information
        video_info = await self.get_video_info(url)
        safe_title = self._sanitize_filename(video_info.title)
        
        # Create dedicated directory for this video
        video_dir = self.create_video_directory(video_info)
        
        download_opts = self.base_opts.copy()
        
        if custom_filename:
            download_opts['outtmpl'] = str(video_dir / custom_filename)
        else:
            # Use simple filename since we're already in a dedicated directory
            download_opts['outtmpl'] = str(video_dir / f'{safe_title}.%(ext)s')
        
        # Add progress hook
        if progress_callback:
            download_opts['progress_hooks'] = [self._create_progress_hook(progress_callback)]
        
        try:
            logger.info(f"Starting download: {video_info.title}")
            logger.info(f"Download directory: {video_dir}")
            if progress_callback:
                progress_callback("Starting download...", 0)
            
            # Download video
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_sync, url, download_opts)
            
            # Find downloaded files in the video directory
            video_path = self._find_downloaded_video_in_dir(video_dir, safe_title)
            subtitle_path = self._find_downloaded_subtitle_in_dir(video_dir, safe_title)
            
            if progress_callback:
                progress_callback("Download completed", 100)
            
            result = {
                'video_path': str(video_path) if video_path else '',
                'subtitle_path': str(subtitle_path) if subtitle_path else '',
                'video_info': video_info.to_dict()
            }
            
            logger.info(f"Download completed: {video_info.title}")
            return result
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(error_msg, 0)
            raise
    
    def _download_sync(self, url: str, ydl_opts: Dict[str, Any]):
        """Synchronous download execution"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    def _create_progress_hook(self, progress_callback: Callable[[str, float], None]):
        """Create progress callback hook"""
        def progress_hook(d):
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif '_percent_str' in d:
                    percent_str = d['_percent_str'].strip().rstrip('%')
                    try:
                        progress = float(percent_str)
                    except ValueError:
                        progress = 0
                else:
                    progress = 0
                
                speed = d.get('_speed_str', '')
                eta = d.get('_eta_str', '')
                status = f"Downloading... {speed} ETA: {eta}"
                progress_callback(status, progress)
            elif d['status'] == 'finished':
                progress_callback("Processing...", 95)
        
        return progress_hook
    
    def _find_downloaded_video_in_dir(self, video_dir: Path, title: str) -> Optional[Path]:
        """Find downloaded video file in specific directory"""
        possible_extensions = ['.mp4', '.mkv', '.webm']
        
        for ext in possible_extensions:
            video_path = video_dir / f"{title}{ext}"
            if video_path.exists():
                return video_path
        
        # Fuzzy matching within the directory
        for file_path in video_dir.glob(f"{title}*"):
            if file_path.suffix.lower() in possible_extensions:
                return file_path
        
        # If exact match not found, try any video file in the directory
        for ext in possible_extensions:
            for file_path in video_dir.glob(f"*{ext}"):
                return file_path
        
        return None
    
    def _find_downloaded_subtitle_in_dir(self, video_dir: Path, title: str) -> Optional[Path]:
        """Find downloaded subtitle file in specific directory"""
        logger.info(f"Looking for subtitle file with title: {title} in {video_dir}")
        
        # Check for English subtitle first (most common)
        en_subtitle_path = video_dir / f"{title}.en.srt"
        if en_subtitle_path.exists():
            # Rename to standard format
            standard_path = video_dir / f"{title}.srt"
            if not standard_path.exists():
                en_subtitle_path.rename(standard_path)
                logger.info(f"Renamed English subtitle: {title}.en.srt -> {title}.srt")
                return standard_path
            return en_subtitle_path
        
        # Check standard format
        standard_path = video_dir / f"{title}.srt"
        if standard_path.exists():
            logger.info(f"Found standard subtitle: {title}.srt")
            return standard_path
        
        # Fuzzy matching for subtitle files within directory
        for file_path in video_dir.glob(f"{title}*.srt"):
            logger.info(f"Found subtitle file: {file_path.name}")
            return file_path
        
        # If exact match not found, try any .srt file in the directory
        for file_path in video_dir.glob("*.srt"):
            logger.info(f"Found subtitle file: {file_path.name}")
            return file_path
        
        logger.warning(f"No subtitle file found for title: {title} in {video_dir}")
        return None
