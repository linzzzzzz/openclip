#!/usr/bin/env python3
"""
Improved Bilibili Video Downloader using yt-dlp
Combines automatic browser cookie extraction with advanced subtitle strategies
"""

import os
import sys
import argparse
import json
import re
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Any
from datetime import datetime

import yt_dlp
from yt_dlp.utils import sanitize_filename

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BilibiliVideoInfo:
    """Bilibili video information class"""
    
    def __init__(self, info_dict: Dict[str, Any]):
        self.bvid = info_dict.get('id', '')
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
            'bvid': self.bvid,
            'title': self.title,
            'duration': self.duration,
            'uploader': self.uploader,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'view_count': self.view_count,
            'upload_date': self.upload_date,
            'webpage_url': self.webpage_url
        }


class ImprovedBilibiliDownloader:
    """
    Improved Bilibili video downloader with automatic cookie handling and advanced subtitle strategies
    """
    
    def __init__(self, output_dir: str = "downloads", quality: str = "best", browser: str = "chrome"):
        """
        Initialize the improved Bilibili downloader
        
        Args:
            output_dir: Base directory to save downloaded videos (each video gets its own subdirectory)
            quality: Video quality preference (best, worst, or specific format)
            browser: Browser to extract cookies from (chrome, firefox, edge, safari)
        """
        self.base_output_dir = Path(output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.quality = quality
        self.browser = browser.lower()
        
        # Base yt-dlp options with improved anti-detection
        # Note: outtmpl will be set per video in create_video_directory
        self.base_opts = {
            'format': self._get_format_selector(),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['ai-zh', 'zh-Hans', 'zh-Hant', 'zh', 'en'],
            'subtitlesformat': 'srt',
            'extractflat': False,
            'writethumbnail': True,
            'writeinfojson': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'noplaylist': True,
            # Automatic cookie extraction from browser
            'cookiesfrombrowser': (self.browser, None, None, None),
            # Enhanced headers to better mimic real browser requests
            'http_headers': self._get_browser_headers(),
            # Enhanced retry configuration with delays
            'retries': 5,
            'fragment_retries': 5,
            'retry_sleep_functions': {
                'http': lambda n: min(4 ** n, 30),
                'fragment': lambda n: min(2 ** n, 30),
            },
        }
    
    def _get_format_selector(self) -> str:
        """Get format selector based on quality preference"""
        if self.quality == "best":
            # Prefer H.264 codec for better compatibility with QuickTime Player
            # Avoid AV1 codec which QuickTime doesn't support well
            return "bestvideo[vcodec^=avc1][ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[vcodec^=h264][ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        elif self.quality == "worst":
            return "worst"
        elif self.quality == "audio":
            return "bestaudio/best"
        else:
            return self.quality
    
    def _get_browser_headers(self) -> Dict[str, str]:
        """Get browser-specific headers to better mimic real requests"""
        if self.browser == 'chrome':
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Chromium";v="131", "Google Chrome";v="131", "Not_A Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.bilibili.com/',
            }
        elif self.browser == 'firefox':
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate, br',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
        elif self.browser == 'edge':
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }
        elif self.browser == 'safari':
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Upgrade-Insecure-Requests': '1',
            }
        else:
            # Default to Chrome headers
            return {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.bilibili.com/',
            }
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is a valid Bilibili URL"""
        bilibili_patterns = [
            r'https?://(?:www\.)?bilibili\.com/video/[Bb][Vv][0-9A-Za-z]+',
            r'https?://(?:www\.)?bilibili\.com/bangumi/',
            r'https?://(?:www\.)?b23\.tv/',
            r'https?://(?:m\.)?bilibili\.com/video/',
        ]
        
        return any(re.match(pattern, url) for pattern in bilibili_patterns)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing unsafe characters"""
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit filename length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip()
    
    def create_video_directory(self, video_info: 'BilibiliVideoInfo') -> Path:
        """
        Create a dedicated directory for a video
        
        Args:
            video_info: BilibiliVideoInfo object
            
        Returns:
            Path to the created video directory
        """
        # Create directory name with video ID and sanitized title
        safe_title = self._sanitize_filename(video_info.title)
        dir_name = f"{video_info.bvid}_{safe_title}"
        
        # Limit directory name length
        if len(dir_name) > 150:
            dir_name = f"{video_info.bvid}_{safe_title[:100]}"
        
        video_dir = self.base_output_dir / dir_name
        video_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Created video directory: {video_dir.name}")
        return video_dir
    
    async def get_video_info(self, url: str) -> BilibiliVideoInfo:
        """Extract video information without downloading"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid Bilibili URL: {url}")
        
        # Try multiple strategies to get video info
        strategies = [
            self._get_info_with_cookies,
            self._get_info_without_cookies,
            self._get_info_with_different_browser
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logger.info(f"Trying video info extraction strategy {i+1}/{len(strategies)}")
                info_dict = await strategy(url)
                return BilibiliVideoInfo(info_dict)
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed: {str(e)}")
                if i == len(strategies) - 1:  # Last strategy
                    logger.error(f"All video info extraction strategies failed")
                    raise
                continue
        
        raise Exception("Failed to extract video information with all strategies")
    
    async def _get_info_with_cookies(self, url: str) -> Dict[str, Any]:
        """Get video info with browser cookies"""
        info_opts = self.base_opts.copy()
        info_opts.update({
            'quiet': True,
            'no_warnings': True,
        })
        
        # Add delay to appear more human-like
        await asyncio.sleep(1)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._extract_info_sync, url, info_opts)
    
    async def _get_info_without_cookies(self, url: str) -> Dict[str, Any]:
        """Get video info without cookies"""
        info_opts = self.base_opts.copy()
        info_opts.update({
            'quiet': True,
            'no_warnings': True,
        })
        # Remove cookies
        if 'cookiesfrombrowser' in info_opts:
            del info_opts['cookiesfrombrowser']
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._extract_info_sync, url, info_opts)
    
    async def _get_info_with_different_browser(self, url: str) -> Dict[str, Any]:
        """Get video info with different browser cookies"""
        browsers = ['firefox', 'edge', 'safari'] if self.browser == 'chrome' else ['chrome']
        
        for browser in browsers:
            try:
                info_opts = self.base_opts.copy()
                info_opts.update({
                    'quiet': True,
                    'no_warnings': True,
                    'cookiesfrombrowser': (browser, None, None, None),
                })
                
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self._extract_info_sync, url, info_opts)
            except Exception as e:
                logger.debug(f"Browser {browser} failed: {e}")
                continue
        
        raise Exception("All browser cookie strategies failed")
    
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
        Download video and subtitles with multiple fallback strategies
        
        Args:
            url: Bilibili video URL
            custom_filename: Custom filename template
            progress_callback: Progress callback function
            
        Returns:
            Dictionary containing video_path, subtitle_path, and video_info
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid Bilibili URL: {url}")
        
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
            
            # First attempt: Full download with all options
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_sync, url, download_opts)
            
            # Find downloaded files in the video directory
            video_path = self._find_downloaded_video_in_dir(video_dir, safe_title)
            subtitle_path = self._find_downloaded_subtitle_in_dir(video_dir, safe_title)
            
            # If subtitle not found, try alternative strategies
            if not subtitle_path:
                logger.info("Primary subtitle download failed, trying alternative strategies...")
                subtitle_path = await self._try_alternative_subtitle_strategies(url, safe_title, video_dir, progress_callback)
            
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
            
            # Try fallback without cookies if initial attempt fails
            logger.info("Trying fallback download without cookies...")
            return await self._try_fallback_download(url, safe_title, custom_filename, video_dir, progress_callback)
    
    async def _try_fallback_download(
        self, 
        url: str, 
        safe_title: str, 
        custom_filename: Optional[str],
        video_dir: Path,
        progress_callback: Optional[Callable[[str, float], None]]
    ) -> Dict[str, str]:
        """Try download without cookies as fallback"""
        try:
            fallback_opts = self.base_opts.copy()
            # Remove cookies for fallback
            del fallback_opts['cookiesfrombrowser']
            
            if custom_filename:
                fallback_opts['outtmpl'] = str(video_dir / custom_filename)
            else:
                fallback_opts['outtmpl'] = str(video_dir / f'{safe_title}_fallback.%(ext)s')
            
            if progress_callback:
                fallback_opts['progress_hooks'] = [self._create_progress_hook(progress_callback)]
                progress_callback("Trying fallback download...", 0)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_sync, url, fallback_opts)
            
            # Find downloaded files in video directory
            search_title = safe_title + "_fallback" if not custom_filename else safe_title
            video_path = self._find_downloaded_video_in_dir(video_dir, search_title)
            subtitle_path = self._find_downloaded_subtitle_in_dir(video_dir, search_title)
            
            if progress_callback:
                progress_callback("Fallback download completed", 100)
            
            return {
                'video_path': str(video_path) if video_path else '',
                'subtitle_path': str(subtitle_path) if subtitle_path else '',
                'video_info': {}
            }
            
        except Exception as e:
            logger.error(f"Fallback download also failed: {str(e)}")
            raise
    
    async def _try_alternative_subtitle_strategies(
        self, 
        url: str, 
        safe_title: str,
        video_dir: Path,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Optional[Path]:
        """Try multiple subtitle acquisition strategies"""
        strategies = [
            self._try_subtitle_only_download,
            self._try_different_subtitle_langs,
            self._try_subtitle_without_cookies
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                if progress_callback:
                    progress_callback(f"Trying subtitle strategy {i+1}/{len(strategies)}", 50 + (i * 10))
                
                subtitle_path = await strategy(url, safe_title, video_dir)
                if subtitle_path:
                    logger.info(f"Subtitle strategy successful: {strategy.__name__}")
                    return subtitle_path
            except Exception as e:
                logger.warning(f"Subtitle strategy failed {strategy.__name__}: {e}")
                continue
        
        logger.warning("All subtitle strategies failed")
        return None
    
    async def _try_subtitle_only_download(self, url: str, safe_title: str, video_dir: Path) -> Optional[Path]:
        """Try downloading only subtitles"""
        try:
            subtitle_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ai-zh', 'zh-Hans', 'zh'],
                'subtitlesformat': 'srt',
                'outtmpl': str(video_dir / f'{safe_title}_sub.%(ext)s'),
                'cookiesfrombrowser': (self.browser, None, None, None),
                'quiet': True,
            }
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_sync, url, subtitle_opts)
            
            return self._find_downloaded_subtitle_in_dir(video_dir, safe_title + "_sub")
            
        except Exception as e:
            logger.debug(f"Subtitle-only download failed: {e}")
            return None
    
    async def _try_different_subtitle_langs(self, url: str, safe_title: str, video_dir: Path) -> Optional[Path]:
        """Try different subtitle language combinations"""
        lang_combinations = [
            ['ai-zh'],
            ['zh-Hans', 'zh'],
            ['en'],
            ['auto']
        ]
        
        for langs in lang_combinations:
            try:
                subtitle_opts = {
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': langs,
                    'subtitlesformat': 'srt',
                    'outtmpl': str(video_dir / f'{safe_title}_lang.%(ext)s'),
                    'cookiesfrombrowser': (self.browser, None, None, None),
                    'quiet': True,
                }
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._download_sync, url, subtitle_opts)
                
                subtitle_path = self._find_downloaded_subtitle_in_dir(video_dir, safe_title + "_lang")
                if subtitle_path:
                    return subtitle_path
                    
            except Exception as e:
                logger.debug(f"Language {langs} failed: {e}")
                continue
        
        return None
    
    async def _try_subtitle_without_cookies(self, url: str, safe_title: str, video_dir: Path) -> Optional[Path]:
        """Try downloading subtitles without cookies"""
        try:
            subtitle_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['ai-zh', 'zh-Hans', 'zh'],
                'subtitlesformat': 'srt',
                'outtmpl': str(video_dir / f'{safe_title}_nocookie.%(ext)s'),
                'quiet': True,
            }
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download_sync, url, subtitle_opts)
            
            return self._find_downloaded_subtitle_in_dir(video_dir, safe_title + "_nocookie")
            
        except Exception as e:
            logger.debug(f"No-cookie subtitle download failed: {e}")
            return None
    
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
        possible_extensions = ['.mp4', '.mkv', '.webm', '.flv']
        
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
        """Find downloaded subtitle file in specific directory with AI subtitle priority"""
        logger.info(f"Looking for subtitle file with title: {title} in {video_dir}")
        
        # Check for AI subtitle first
        ai_subtitle_path = video_dir / f"{title}.ai-zh.srt"
        if ai_subtitle_path.exists():
            # Rename to standard format
            standard_path = video_dir / f"{title}.srt"
            if not standard_path.exists():
                ai_subtitle_path.rename(standard_path)
                logger.info(f"Renamed AI subtitle: {title}.ai-zh.srt -> {title}.srt")
                return standard_path
            return ai_subtitle_path
        
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
    
    def _find_downloaded_video(self, title: str) -> Optional[Path]:
        """Find downloaded video file (legacy method for compatibility)"""
        possible_extensions = ['.mp4', '.mkv', '.webm', '.flv']
        
        for ext in possible_extensions:
            video_path = self.base_output_dir / f"{title}{ext}"
            if video_path.exists():
                return video_path
        
        # Fuzzy matching
        for file_path in self.base_output_dir.glob(f"{title}*"):
            if file_path.suffix.lower() in possible_extensions:
                return file_path
        
        return None
    
    def _find_downloaded_subtitle(self, title: str) -> Optional[Path]:
        """Find downloaded subtitle file with AI subtitle priority (legacy method for compatibility)"""
        logger.info(f"Looking for subtitle file with title: {title}")
        
        # Check for AI subtitle first
        ai_subtitle_path = self.base_output_dir / f"{title}.ai-zh.srt"
        if ai_subtitle_path.exists():
            # Rename to standard format
            standard_path = self.base_output_dir / f"{title}.srt"
            if not standard_path.exists():
                ai_subtitle_path.rename(standard_path)
                logger.info(f"Renamed AI subtitle: {title}.ai-zh.srt -> {title}.srt")
                return standard_path
            return ai_subtitle_path
        
        # Check standard format
        standard_path = self.base_output_dir / f"{title}.srt"
        if standard_path.exists():
            logger.info(f"Found standard subtitle: {title}.srt")
            return standard_path
        
        # Fuzzy matching for subtitle files
        for file_path in self.base_output_dir.glob(f"{title}*.srt"):
            logger.info(f"Found subtitle file: {file_path.name}")
            return file_path
        
        logger.warning(f"No subtitle file found for title: {title}")
        return None


class DownloadProcessor:
    """Handles video downloading operations"""
    
    def __init__(self, downloader):
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


async def main():
    """Main async function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="Improved Bilibili Video Downloader with automatic cookie handling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download with automatic cookie extraction (no manual browser interaction)
  python bilibili_downloader_improved.py "https://www.bilibili.com/video/BV1234567890"
  
  # Use Firefox cookies instead of Chrome
  python bilibili_downloader_improved.py --browser firefox "https://www.bilibili.com/video/BV1234567890"
  
  # Download with specific quality
  python bilibili_downloader_improved.py -q "720p" "https://www.bilibili.com/video/BV1234567890"
  
  # Get video info only
  python bilibili_downloader_improved.py -i "https://www.bilibili.com/video/BV1234567890"
        """
    )
    
    parser.add_argument('url', help='Bilibili video URL')
    parser.add_argument('-o', '--output', default='downloads', 
                       help='Output directory (default: downloads)')
    parser.add_argument('-q', '--quality', default='best',
                       help='Video quality (best, worst, 720p, 480p, etc.)')
    parser.add_argument('-b', '--browser', default='firefox',
                       choices=['chrome', 'firefox', 'edge', 'safari'],
                       help='Browser to extract cookies from (default: firefox)')
    parser.add_argument('-f', '--filename',
                       help='Custom filename template')
    parser.add_argument('-i', '--info', action='store_true',
                       help='Show video information only')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = ImprovedBilibiliDownloader(
        output_dir=args.output, 
        quality=args.quality, 
        browser=args.browser
    )
    
    def progress_callback(status: str, progress: float):
        print(f"\r{status} ({progress:.1f}%)", end='', flush=True)
    
    try:
        if args.info:
            # Get video info only
            info = await downloader.get_video_info(args.url)
            print(f"Title: {info.title}")
            print(f"Uploader: {info.uploader}")
            print(f"Duration: {info.duration} seconds")
            print(f"View Count: {info.view_count}")
            print(f"Upload Date: {info.upload_date}")
            print(f"Description: {info.description[:200]}...")
        else:
            # Download video
            result = await downloader.download_video(
                args.url, 
                args.filename, 
                progress_callback
            )
            print("\n")
            print(f"Video: {result['video_path']}")
            print(f"Subtitle: {result['subtitle_path']}")
            print("Download completed successfully!")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Run async main
    import sys
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
