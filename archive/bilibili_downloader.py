#!/usr/bin/env python3
"""
Bilibili Video Downloader using yt-dlp
A comprehensive tool for downloading videos from Bilibili (bilibili.com)
"""

import os
import sys
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import yt_dlp
from yt_dlp.utils import sanitize_filename


class BilibiliDownloader:
    """
    A class for downloading Bilibili videos using yt-dlp
    """
    
    def __init__(self, output_dir: str = "downloads", quality: str = "best"):
        """
        Initialize the Bilibili downloader
        
        Args:
            output_dir: Directory to save downloaded videos
            quality: Video quality preference (best, worst, or specific format)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.quality = quality
        
        # Bilibili-specific yt-dlp options
        self.ydl_opts = {
            'format': self._get_format_selector(),
            'outtmpl': str(self.output_dir / '%(uploader)s_%(title)s_%(id)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['zh-Hans', 'zh-Hant', 'zh', 'en'],
            'extractflat': False,
            'writethumbnail': True,
            'writeinfojson': True,
            'ignoreerrors': False,
            'no_warnings': False,
            # Bilibili-specific headers to avoid 412 errors
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.bilibili.com/',
                'Origin': 'https://www.bilibili.com',
            },
            # Add cookies file support (optional)
            'cookiefile': None,  # User can set this if needed
            # Additional options for Bilibili
            'extractor_args': {
                'bilibili': {
                    'prefer_multi_page': True,
                }
            },
            # Retry configuration with delays
            'retries': 5,
            'fragment_retries': 5,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            # Add geo-bypass options
            'geo_bypass': True,
            'geo_bypass_country': 'CN',
        }
    
    def _get_format_selector(self) -> str:
        """
        Get format selector based on quality preference
        
        Returns:
            Format selector string for yt-dlp
        """
        if self.quality == "best":
            return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif self.quality == "worst":
            return "worst"
        elif self.quality == "audio":
            return "bestaudio/best"
        else:
            return self.quality
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is a valid Bilibili URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid Bilibili URL, False otherwise
        """
        bilibili_patterns = [
            r'https?://(?:www\.)?bilibili\.com/video/',
            r'https?://(?:www\.)?bilibili\.com/bangumi/',
            r'https?://(?:www\.)?b23\.tv/',
            r'https?://(?:m\.)?bilibili\.com/video/',
        ]
        
        return any(re.match(pattern, url) for pattern in bilibili_patterns)
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Extract video information without downloading
        
        Args:
            url: Bilibili video URL
            
        Returns:
            Dictionary containing video information or None if failed
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return None
        
        info_opts = self.ydl_opts.copy()
        info_opts['quiet'] = True
        info_opts['no_warnings'] = True
        
        try:
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"Error extracting info: {str(e)}")
            return None
    
    def list_formats(self, url: str) -> None:
        """
        List available formats for a Bilibili video
        
        Args:
            url: Bilibili video URL
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return
        
        list_opts = self.ydl_opts.copy()
        list_opts['listformats'] = True
        
        try:
            with yt_dlp.YoutubeDL(list_opts) as ydl:
                ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Error listing formats: {str(e)}")
    
    def download_video(self, url: str, custom_filename: Optional[str] = None) -> bool:
        """
        Download a Bilibili video
        
        Args:
            url: Bilibili video URL
            custom_filename: Custom filename template (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return False
        
        download_opts = self.ydl_opts.copy()
        
        if custom_filename:
            download_opts['outtmpl'] = str(self.output_dir / custom_filename)
        
        # Add progress hook
        download_opts['progress_hooks'] = [self._progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                print(f"Downloading video from: {url}")
                ydl.download([url])
                print("Download completed successfully!")
                return True
        except Exception as e:
            print(f"Download failed: {str(e)}")
            return False
    
    def download_playlist(self, url: str) -> bool:
        """
        Download a Bilibili playlist or series
        
        Args:
            url: Bilibili playlist/series URL
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return False
        
        playlist_opts = self.ydl_opts.copy()
        playlist_opts['outtmpl'] = str(self.output_dir / '%(playlist_title)s/%(playlist_index)02d_%(title)s_%(id)s.%(ext)s')
        playlist_opts['progress_hooks'] = [self._progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                print(f"Downloading playlist from: {url}")
                ydl.download([url])
                print("Playlist download completed!")
                return True
        except Exception as e:
            print(f"Playlist download failed: {str(e)}")
            return False
    
    def download_audio_only(self, url: str) -> bool:
        """
        Download audio only from Bilibili video
        
        Args:
            url: Bilibili video URL
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return False
        
        audio_opts = self.ydl_opts.copy()
        audio_opts['format'] = 'bestaudio/best'
        audio_opts['outtmpl'] = str(self.output_dir / 'audio/%(uploader)s_%(title)s_%(id)s.%(ext)s')
        audio_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        audio_opts['progress_hooks'] = [self._progress_hook]
        
        # Create audio directory
        (self.output_dir / 'audio').mkdir(exist_ok=True)
        
        try:
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                print(f"Downloading audio from: {url}")
                ydl.download([url])
                print("Audio download completed!")
                return True
        except Exception as e:
            print(f"Audio download failed: {str(e)}")
            return False
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                print(f"\rDownloading... {percent:.1f}%", end='', flush=True)
            elif '_percent_str' in d:
                print(f"\rDownloading... {d['_percent_str']}", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\nDownloaded: {d['filename']}")


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="Download videos from Bilibili using yt-dlp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download a video with best quality
  python bilibili_downloader.py "https://www.bilibili.com/video/BV1234567890"
  
  # Download audio only
  python bilibili_downloader.py -a "https://www.bilibili.com/video/BV1234567890"
  
  # Download with specific quality
  python bilibili_downloader.py -q "720p" "https://www.bilibili.com/video/BV1234567890"
  
  # List available formats
  python bilibili_downloader.py -l "https://www.bilibili.com/video/BV1234567890"
  
  # Get video info
  python bilibili_downloader.py -i "https://www.bilibili.com/video/BV1234567890"
        """
    )
    
    parser.add_argument('url', help='Bilibili video URL')
    parser.add_argument('-o', '--output', default='downloads', 
                       help='Output directory (default: downloads)')
    parser.add_argument('-q', '--quality', default='best',
                       help='Video quality (best, worst, 720p, 480p, etc.)')
    parser.add_argument('-f', '--filename',
                       help='Custom filename template')
    parser.add_argument('-a', '--audio-only', action='store_true',
                       help='Download audio only')
    parser.add_argument('-p', '--playlist', action='store_true',
                       help='Download as playlist/series')
    parser.add_argument('-l', '--list-formats', action='store_true',
                       help='List available formats')
    parser.add_argument('-i', '--info', action='store_true',
                       help='Show video information only')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = BilibiliDownloader(output_dir=args.output, quality=args.quality)
    
    # Handle different operations
    if args.info:
        info = downloader.get_video_info(args.url)
        if info:
            print(f"Title: {info.get('title', 'N/A')}")
            print(f"Uploader: {info.get('uploader', 'N/A')}")
            print(f"Duration: {info.get('duration', 'N/A')} seconds")
            print(f"View Count: {info.get('view_count', 'N/A')}")
            print(f"Upload Date: {info.get('upload_date', 'N/A')}")
            print(f"Description: {info.get('description', 'N/A')[:200]}...")
    
    elif args.list_formats:
        downloader.list_formats(args.url)
    
    elif args.audio_only:
        downloader.download_audio_only(args.url)
    
    elif args.playlist:
        downloader.download_playlist(args.url)
    
    else:
        downloader.download_video(args.url, args.filename)


if __name__ == "__main__":
    main()
