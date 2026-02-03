"""
Video Downloaders Package

This package contains video downloaders for different platforms:
- Bilibili
- YouTube
- Unified downloader (auto-detects platform)
"""

from .bilibili_downloader import ImprovedBilibiliDownloader
from .youtube_downloader import YouTubeDownloader
from .video_downloader import VideoDownloader, DownloadProcessor

__all__ = [
    'ImprovedBilibiliDownloader',
    'YouTubeDownloader',
    'VideoDownloader',
    'DownloadProcessor',
]
