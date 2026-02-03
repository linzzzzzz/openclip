"""
OpenClip Core Modules

This package contains all the core functionality for video processing,
analysis, and clip generation.
"""

from .downloaders import ImprovedBilibiliDownloader, DownloadProcessor, VideoDownloader, YouTubeDownloader
from .video_splitter import VideoSplitter
from .transcript_generation_whisper import TranscriptProcessor
from .engaging_moments_analyzer import EngagingMomentsAnalyzer
from .qwen_api_client import QwenAPIClient
from .clip_generator import ClipGenerator
from .title_adder import TitleAdder
from .cover_image_generator import CoverImageGenerator
from .video_utils import (
    VideoFileValidator,
    VideoFileManager,
    ProgressCallbackManager,
    ProcessingResult,
    ResultsFormatter,
    process_local_video_file,
    find_existing_download
)

__all__ = [
    'ImprovedBilibiliDownloader',
    'DownloadProcessor',
    'VideoDownloader',
    'YouTubeDownloader',
    'VideoSplitter',
    'TranscriptProcessor',
    'EngagingMomentsAnalyzer',
    'QwenAPIClient',
    'ClipGenerator',
    'TitleAdder',
    'CoverImageGenerator',
    'VideoFileValidator',
    'VideoFileManager',
    'ProgressCallbackManager',
    'ProcessingResult',
    'ResultsFormatter',
    'process_local_video_file',
    'find_existing_download',
]
