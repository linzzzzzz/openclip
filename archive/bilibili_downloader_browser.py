#!/usr/bin/env python3
"""
Bilibili Video Downloader using Browser Automation + yt-dlp
Uses Chrome browser to bypass anti-bot protections and extract video URLs
"""

import os
import sys
import argparse
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import yt_dlp
from yt_dlp.utils import sanitize_filename


class BilibiliBrowserDownloader:
    """
    A class for downloading Bilibili videos using browser automation + yt-dlp
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
        
        # yt-dlp options with cookies support
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
            # Use cookies from browser
            'cookiesfrombrowser': ('chrome', None, None, None),
            # Headers to mimic browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.bilibili.com/',
                'Origin': 'https://www.bilibili.com',
            },
            # Retry configuration
            'retries': 3,
            'fragment_retries': 3,
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
    
    def browser_pre_visit(self, url: str) -> bool:
        """
        Use browser automation to visit the page and generate cookies
        
        Args:
            url: Bilibili video URL
            
        Returns:
            True if successful browser visit, False otherwise
        """
        try:
            import subprocess
            
            print("Opening Bilibili page in Chrome to generate cookies...")
            print("Please wait while the browser loads the page...")
            
            # Open the URL in Chrome and wait for it to load
            # This will generate the necessary cookies and session data
            subprocess.run([
                'open', '-a', 'Google Chrome', url
            ], check=False, capture_output=True)
            
            print("Chrome browser opened. Please:")
            print("1. Wait for the video page to fully load")
            print("2. Close the Chrome tab/window when ready")
            print("3. The cookies will be automatically used for download")
            
            input("Press Enter when you've closed the Chrome tab and are ready to download...")
            
            return True
            
        except Exception as e:
            print(f"Browser automation failed: {str(e)}")
            print("Continuing with direct yt-dlp download...")
            return False
    
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
        
        # Try browser pre-visit for better success rate
        self.browser_pre_visit(url)
        
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
        
        # Try browser pre-visit for better success rate
        self.browser_pre_visit(url)
        
        list_opts = self.ydl_opts.copy()
        list_opts['listformats'] = True
        
        try:
            with yt_dlp.YoutubeDL(list_opts) as ydl:
                ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Error listing formats: {str(e)}")
    
    def download_video(self, url: str, custom_filename: Optional[str] = None, use_browser: bool = True) -> bool:
        """
        Download a Bilibili video
        
        Args:
            url: Bilibili video URL
            custom_filename: Custom filename template (optional)
            use_browser: Whether to use browser pre-visit (default: True)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return False
        
        # Try browser pre-visit for better success rate
        if use_browser:
            self.browser_pre_visit(url)
        
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
            if use_browser:
                print("Retrying without browser pre-visit...")
                return self.download_video(url, custom_filename, use_browser=False)
            return False
    
    def download_playlist(self, url: str, use_browser: bool = True) -> bool:
        """
        Download a Bilibili playlist or series
        
        Args:
            url: Bilibili playlist/series URL
            use_browser: Whether to use browser pre-visit
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return False
        
        if use_browser:
            self.browser_pre_visit(url)
        
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
            if use_browser:
                print("Retrying without browser pre-visit...")
                return self.download_playlist(url, use_browser=False)
            return False
    
    def download_audio_only(self, url: str, use_browser: bool = True) -> bool:
        """
        Download audio only from Bilibili video
        
        Args:
            url: Bilibili video URL
            use_browser: Whether to use browser pre-visit
            
        Returns:
            True if successful, False otherwise
        """
        if not self.validate_url(url):
            print(f"Error: Invalid Bilibili URL: {url}")
            return False
        
        if use_browser:
            self.browser_pre_visit(url)
        
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
            if use_browser:
                print("Retrying without browser pre-visit...")
                return self.download_audio_only(url, use_browser=False)
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
        description="Download videos from Bilibili using Browser + yt-dlp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download a video with browser assistance (recommended)
  python bilibili_downloader_browser.py "https://www.bilibili.com/video/BV1234567890"
  
  # Download without browser (may fail with 412 errors)
  python bilibili_downloader_browser.py --no-browser "https://www.bilibili.com/video/BV1234567890"
  
  # Download audio only with browser assistance
  python bilibili_downloader_browser.py -a "https://www.bilibili.com/video/BV1234567890"
  
  # List available formats
  python bilibili_downloader_browser.py -l "https://www.bilibili.com/video/BV1234567890"
  
  # Get video info
  python bilibili_downloader_browser.py -i "https://www.bilibili.com/video/BV1234567890"
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
    parser.add_argument('--no-browser', action='store_true',
                       help='Skip browser pre-visit (not recommended)')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = BilibiliBrowserDownloader(output_dir=args.output, quality=args.quality)
    use_browser = not args.no_browser
    
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
        downloader.download_audio_only(args.url, use_browser)
    
    elif args.playlist:
        downloader.download_playlist(args.url, use_browser)
    
    else:
        downloader.download_video(args.url, args.filename, use_browser)


if __name__ == "__main__":
    main()
