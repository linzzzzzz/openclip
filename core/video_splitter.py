#!/usr/bin/env python3
"""
Video and Subtitle Splitter
Split videos and their corresponding subtitle files into multiple parts
"""

import os
import sys
import re
import subprocess
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Callable, Any
from core.config import MAX_DURATION_MINUTES

logger = logging.getLogger(__name__)

class SubtitleSegment:
    """Represents a single subtitle segment"""
    def __init__(self, index: int, start_time: str, end_time: str, text: str):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
    
    def to_srt_format(self) -> str:
        """Convert back to SRT format"""
        return f"{self.index}\n{self.start_time} --> {self.end_time}\n{self.text}\n"

class VideoSplitter:
    """Split videos and subtitles into multiple parts"""
    
    def __init__(self, max_duration_minutes: float = MAX_DURATION_MINUTES, output_dir: Optional[Path] = None):
        self.subtitles: List[SubtitleSegment] = []
        self.max_duration_minutes = max_duration_minutes
        self.max_duration_seconds = max_duration_minutes * 60
        self.output_dir = output_dir or Path("output_parts")
        
    def parse_srt_file(self, srt_path: str) -> bool:
        """Parse SRT file and extract subtitle segments"""
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Split by double newlines to get individual subtitle blocks
            blocks = re.split(r'\n\s*\n', content)
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    index = int(lines[0])
                    time_line = lines[1]
                    text = '\n'.join(lines[2:])
                    
                    # Parse time line "00:00:00,000 --> 00:00:00,800"
                    time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                        
                        segment = SubtitleSegment(index, start_time, end_time, text)
                        self.subtitles.append(segment)
            
            print(f"✅ Parsed {len(self.subtitles)} subtitle segments from {srt_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error parsing SRT file: {e}")
            return False
    
    def time_to_seconds(self, time_str: str) -> float:
        """Convert SRT time format to seconds"""
        # Format: "00:01:23,456"
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        
        return h * 3600 + m * 60 + s + ms / 1000.0
    
    def seconds_to_time(self, seconds: float) -> str:
        """Convert seconds back to SRT time format"""
        ms = int((seconds % 1) * 1000)
        seconds = int(seconds)
        
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    def split_by_duration(self, duration_seconds: float) -> List[Tuple[float, float]]:
        """Split video into parts by duration"""
        if not self.subtitles:
            return []
        
        # Get total duration from last subtitle
        total_duration = self.time_to_seconds(self.subtitles[-1].end_time)
        
        split_points = []
        current_start = 0.0
        
        while current_start < total_duration:
            end_time = min(current_start + duration_seconds, total_duration)
            split_points.append((current_start, end_time))
            current_start = end_time
        
        return split_points
    
    def split_by_segments(self, segments_per_part: int) -> List[Tuple[float, float, int, int]]:
        """Split video by number of subtitle segments"""
        if not self.subtitles:
            return []
        
        split_points = []
        total_segments = len(self.subtitles)
        
        for i in range(0, total_segments, segments_per_part):
            start_idx = i
            end_idx = min(i + segments_per_part - 1, total_segments - 1)
            
            start_time = self.time_to_seconds(self.subtitles[start_idx].start_time)
            end_time = self.time_to_seconds(self.subtitles[end_idx].end_time)
            
            split_points.append((start_time, end_time, start_idx, end_idx))
        
        return split_points
    
    def create_subtitle_part(self, start_idx: int, end_idx: int, part_num: int, 
                           output_dir: str, base_name: str, time_offset: float = 0.0) -> str:
        """Create a subtitle file for a specific part"""
        part_subtitles = self.subtitles[start_idx:end_idx + 1]
        
        # Adjust timing to start from 0 for each part
        adjusted_subtitles = []
        for i, subtitle in enumerate(part_subtitles):
            new_start = self.time_to_seconds(subtitle.start_time) - time_offset
            new_end = self.time_to_seconds(subtitle.end_time) - time_offset
            
            # Ensure times are not negative
            new_start = max(0.0, new_start)
            new_end = max(new_start + 0.1, new_end)
            
            adjusted_subtitle = SubtitleSegment(
                i + 1,
                self.seconds_to_time(new_start),
                self.seconds_to_time(new_end),
                subtitle.text
            )
            adjusted_subtitles.append(adjusted_subtitle)
        
        # Write to file
        output_path = os.path.join(output_dir, f"{base_name}_part{part_num:02d}.srt")
        with open(output_path, 'w', encoding='utf-8') as f:
            for subtitle in adjusted_subtitles:
                f.write(subtitle.to_srt_format() + '\n')
        
        return output_path
    
    def split_video_ffmpeg(self, video_path: str, start_time: float, duration: float, 
                          output_path: str) -> bool:
        """Split video using ffmpeg"""
        try:
            cmd = [
                "ffmpeg", "-y",  # -y to overwrite output files
                "-i", video_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",  # Copy streams without re-encoding for speed
                output_path
            ]
            
            print(f"🎬 Creating video part: {output_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                print(f"❌ ffmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error splitting video: {e}")
            return False
    
    def split_by_time_duration(self, video_path: str, srt_path: str, 
                              duration_minutes: float, output_dir: str = "output_parts"):
        """Split video and subtitles by time duration"""
        print(f"🎯 Splitting by duration: {duration_minutes} minutes per part")
        
        # Check if subtitles are available
        has_subtitles = bool(srt_path and os.path.exists(srt_path))
        split_points = []
        
        if has_subtitles:
            if not self.parse_srt_file(srt_path):
                return False
            
            duration_seconds = duration_minutes * 60
            split_points = self.split_by_duration(duration_seconds)
        else:
            # No subtitles, split based on time using ffprobe
            print("⚠️  No subtitles found, splitting based on time only")
            import subprocess
            import json
            
            # Get video duration using ffprobe
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                video_path
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                info = json.loads(result.stdout)
                total_duration = float(info['format']['duration'])
                print(f"📊 Video duration: {total_duration:.1f} seconds")
                
                # Generate split points
                duration_seconds = duration_minutes * 60
                current_start = 0.0
                while current_start < total_duration:
                    end_time = min(current_start + duration_seconds, total_duration)
                    split_points.append((current_start, end_time))
                    current_start = end_time
            except Exception as e:
                print(f"❌ Error getting video duration: {e}")
                return False
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        # Output directly to the provided output_dir
        os.makedirs(output_dir, exist_ok=True)

        print(f"📁 Output directory: {output_dir}")
        print(f"🎬 Will create {len(split_points)} parts")

        success_count = 0

        for i, (start_time, end_time) in enumerate(split_points, 1):
            duration = end_time - start_time

            print(f"\n--- Part {i}/{len(split_points)} ---")
            print(f"⏰ Time: {self.seconds_to_time(start_time)} - {self.seconds_to_time(end_time)}")
            print(f"⏱️  Duration: {duration:.1f} seconds")

            # Create video part
            video_output = os.path.join(output_dir, f"{base_name}_part{i:02d}.mp4")
            video_success = self.split_video_ffmpeg(video_path, start_time, duration, video_output)

            # Handle subtitles if available
            if has_subtitles:
                # Find subtitle segments for this time range
                start_idx = 0
                end_idx = len(self.subtitles) - 1

                for j, subtitle in enumerate(self.subtitles):
                    subtitle_start = self.time_to_seconds(subtitle.start_time)
                    if subtitle_start >= start_time:
                        start_idx = j
                        break

                for j, subtitle in enumerate(self.subtitles):
                    subtitle_end = self.time_to_seconds(subtitle.end_time)
                    if subtitle_end <= end_time:
                        end_idx = j

                # Create subtitle part
                if start_idx <= end_idx:
                    subtitle_output = self.create_subtitle_part(
                        start_idx, end_idx, i, output_dir, base_name, start_time
                    )
                    print(f"📝 Created subtitle part: {os.path.basename(subtitle_output)}")
            
            if video_success:
                success_count += 1
                print(f"✅ Part {i} completed successfully")
            else:
                print(f"❌ Part {i} failed")
        
        print(f"\n🏁 Completed: {success_count}/{len(split_points)} parts successful")
        return success_count == len(split_points)
    
    def split_by_segment_count(self, video_path: str, srt_path: str, 
                              segments_per_part: int, output_dir: str = "output_parts"):
        """Split video and subtitles by number of subtitle segments"""
        print(f"🎯 Splitting by segments: {segments_per_part} subtitles per part")
        
        if not self.parse_srt_file(srt_path):
            return False
        
        split_points = self.split_by_segments(segments_per_part)
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        # Output directly to the provided output_dir
        os.makedirs(output_dir, exist_ok=True)

        print(f"📁 Output directory: {output_dir}")
        print(f"🎬 Will create {len(split_points)} parts")

        success_count = 0

        for i, (start_time, end_time, start_idx, end_idx) in enumerate(split_points, 1):
            duration = end_time - start_time
            segment_count = end_idx - start_idx + 1

            print(f"\n--- Part {i}/{len(split_points)} ---")
            print(f"📝 Subtitles: {start_idx + 1}-{end_idx + 1} ({segment_count} segments)")
            print(f"⏰ Time: {self.seconds_to_time(start_time)} - {self.seconds_to_time(end_time)}")
            print(f"⏱️  Duration: {duration:.1f} seconds")

            # Create video part
            video_output = os.path.join(output_dir, f"{base_name}_part{i:02d}.mp4")
            video_success = self.split_video_ffmpeg(video_path, start_time, duration, video_output)

            # Create subtitle part
            subtitle_output = self.create_subtitle_part(
                start_idx, end_idx, i, output_dir, base_name, start_time
            )
            print(f"📝 Created subtitle part: {os.path.basename(subtitle_output)}")
            
            if video_success:
                success_count += 1
                print(f"✅ Part {i} completed successfully")
            else:
                print(f"❌ Part {i} failed")
        
        print(f"\n🏁 Completed: {success_count}/{len(split_points)} parts successful")
        return success_count == len(split_points)
    
    def check_duration_needs_splitting(self, video_info: Dict[str, Any]) -> bool:
        """Check if video needs splitting based on duration"""
        duration = video_info.get('duration', 0)
        
        if duration > self.max_duration_seconds:
            logger.info(f"📏 Video duration: {duration/60:.1f} minutes (> {self.max_duration_minutes} min limit)")
            return True
        else:
            logger.info(f"📏 Video duration: {duration/60:.1f} minutes (within {self.max_duration_minutes} min limit)")
            return False
    
    async def split_video_async(self,
                               video_path: str,
                               subtitle_path: str,
                               progress_callback: Optional[Callable[[str, float], None]],
                               splits_dir: Optional[Path] = None) -> Dict[str, List[str]]:
        """Async version of video splitting with progress tracking

        Args:
            video_path: Path to the video file
            subtitle_path: Path to the subtitle file
            progress_callback: Progress callback function
            splits_dir: Explicit output directory for split files. If None, falls back to
                       self.output_dir / base_name / "splits"
        """

        if progress_callback:
            progress_callback("Splitting video into parts...", 35)

        base_name = Path(video_path).stem

        # Use explicit splits_dir if provided, otherwise fall back to default
        if splits_dir is None:
            splits_dir = self.output_dir / base_name / "splits"
        splits_dir.mkdir(parents=True, exist_ok=True)

        # Use existing split_by_time_duration method
        success = self.split_by_time_duration(
            video_path,
            subtitle_path,
            self.max_duration_minutes,
            str(splits_dir)
        )

        if not success:
            raise Exception("Video splitting failed")

        # Find all created parts using utility function
        from core.video_utils import VideoFileManager
        video_parts, transcript_parts = VideoFileManager.find_video_parts(splits_dir, base_name)
        
        logger.info(f"✅ Split into {len(video_parts)} video parts and {len(transcript_parts)} transcript parts")
        
        return {
            'video_parts': video_parts,
            'transcript_parts': transcript_parts
        }


def main():
    """Main function with command line interface"""
    
    print("🎬 Video and Subtitle Splitter")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("\n📋 Usage:")
        print("1. Split by time duration (minutes):")
        print("   python video_splitter.py time video.mp4 subtitles.srt 2.0")
        print("   (Splits into 2-minute parts)")
        
        print("\n2. Split by subtitle segment count:")
        print("   python video_splitter.py segments video.mp4 subtitles.srt 20")
        print("   (20 subtitles per part)")
        
        print("\n3. Quick test with sample files:")
        print("   python video_splitter.py test")
        
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "test":
        # Test with sample files
        video_file = "video_sample.mp4"
        srt_file = "video_sample.srt"
        
        if not os.path.exists(video_file) or not os.path.exists(srt_file):
            print("❌ Sample files not found. Expected:")
            print(f"   - {video_file}")
            print(f"   - {srt_file}")
            return
        
        print("🧪 Testing with sample files...")
        splitter = VideoSplitter()
        
        # Split by 20 segments per part
        splitter.split_by_segment_count(video_file, srt_file, 20, "test_output")
        
    elif mode == "time":
        if len(sys.argv) < 5:
            print("❌ Usage: python video_splitter.py time video.mp4 subtitles.srt duration_minutes")
            return
        
        video_path = sys.argv[2]
        srt_path = sys.argv[3]
        duration_minutes = float(sys.argv[4])
        output_dir = sys.argv[5] if len(sys.argv) > 5 else "output_parts"
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return
        
        if not os.path.exists(srt_path):
            print(f"❌ Subtitle file not found: {srt_path}")
            return
        
        splitter = VideoSplitter()
        splitter.split_by_time_duration(video_path, srt_path, duration_minutes, output_dir)
        
    elif mode == "segments":
        if len(sys.argv) < 5:
            print("❌ Usage: python video_splitter.py segments video.mp4 subtitles.srt segments_per_part")
            return
        
        video_path = sys.argv[2]
        srt_path = sys.argv[3]
        segments_per_part = int(sys.argv[4])
        output_dir = sys.argv[5] if len(sys.argv) > 5 else "output_parts"
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return
        
        if not os.path.exists(srt_path):
            print(f"❌ Subtitle file not found: {srt_path}")
            return
        
        splitter = VideoSplitter()
        splitter.split_by_segment_count(video_path, srt_path, segments_per_part, output_dir)
        
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Valid modes: time, segments, test")

if __name__ == "__main__":
    main()
