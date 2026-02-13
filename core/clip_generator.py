#!/usr/bin/env python3
"""
Clip Generator - Extract engaging video clips from analyzed moments
"""
import json
import subprocess
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ClipGenerator:
    """Generate video clips from engaging moments analysis"""
    
    def __init__(self, output_dir: str = "engaging_clips"):
        """
        Initialize clip generator
        
        Args:
            output_dir: Directory to save generated clips
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Clip output directory: {self.output_dir}")
    
    def generate_clips_from_analysis(self, 
                                    analysis_file: str,
                                    video_dir: str,
                                    subtitle_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate clips from engaging moments analysis
        
        Args:
            analysis_file: Path to top_engaging_moments.json
            video_dir: Directory containing source video files
            subtitle_dir: Directory containing subtitle files (optional)
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Load analysis data
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            video_dir = Path(video_dir)
            subtitle_dir = Path(subtitle_dir) if subtitle_dir else video_dir
            
            logger.info("🎬 Generating clips from Top Engaging Moments")
            logger.info(f"📁 Output: {self.output_dir}")
            logger.info(f"📝 Subtitle directory: {subtitle_dir}")
            
            clips_info = []
            successful_clips = 0
            
            # Process each engaging moment
            for moment in data['top_engaging_moments']:
                rank = moment['rank']
                title = moment['title']
                video_part = moment['timing']['video_part']
                start_time = moment['timing']['start_time']
                end_time = moment['timing']['end_time']
                duration = moment['timing']['duration']
                
                logger.info(f"[Rank {rank}] Processing: {title}")
                
                # Get source video file
                input_video = self._find_video_file(video_part, video_dir)
                if not input_video:
                    logger.warning(f"✗ Skipping rank {rank}: Video file not found")
                    continue
                
                # Create output filename
                safe_title = self._sanitize_filename(title)
                output_filename = f"rank_{rank:02d}_{safe_title}.mp4"
                output_path = self.output_dir / output_filename
                
                # Create the clip
                success = self._create_clip(
                    input_video,
                    start_time,
                    end_time,
                    str(output_path),
                    title
                )
                
                if success:
                    # Generate subtitle file for the clip
                    subtitle_filename = f"rank_{rank:02d}_{safe_title}.srt"
                    subtitle_path = self.output_dir / subtitle_filename
                    subtitle_generated = self._extract_subtitle_for_clip(
                        video_part,
                        start_time,
                        end_time,
                        str(subtitle_path),
                        subtitle_dir
                    )
                    
                    successful_clips += 1
                    clips_info.append({
                        'rank': rank,
                        'title': title,
                        'filename': output_filename,
                        'subtitle_filename': subtitle_filename if subtitle_generated else None,
                        'duration': duration,
                        'video_part': video_part,
                        'time_range': f"{start_time} - {end_time}",
                        'engagement_level': moment['engagement_details'].get('engagement_level', 'N/A'),
                        'why_engaging': moment['why_engaging']
                    })
                    logger.info(f"✓ Saved: {output_filename}")
                    if subtitle_generated:
                        logger.info(f"✓ Subtitle: {subtitle_filename}")
                    else:
                        logger.info(f"⚠ No subtitle generated for this clip")
                else:
                    logger.error(f"✗ Failed: {output_filename}")
            
            # Create summary
            if clips_info:
                self._create_summary(clips_info, data)
            
            result = {
                'success': successful_clips > 0,
                'total_clips': len(data['top_engaging_moments']),
                'successful_clips': successful_clips,
                'clips_info': clips_info,
                'output_dir': str(self.output_dir)
            }
            
            logger.info(f"🎯 Generated {successful_clips}/{len(data['top_engaging_moments'])} clips")
            return result
            
        except Exception as e:
            logger.error(f"Error generating clips: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_clips': 0,
                'successful_clips': 0,
                'clips_info': []
            }
    
    def _find_video_file(self, video_part: str, video_dir: Path) -> Optional[str]:
        """Find video file for a given part"""
        # Try common patterns
        patterns = [
            f"*_{video_part}.mp4",
            f"{video_part}.mp4",
            "*.mp4"  # Fallback for single video
        ]
        
        for pattern in patterns:
            matches = list(video_dir.glob(pattern))
            if matches:
                return str(matches[0])
        
        return None
    
    def _find_subtitle_file(self, video_part: str, subtitle_dir: Path) -> Optional[str]:
        """Find subtitle file for a given part"""
        # Try common patterns
        patterns = [
            f"*_{video_part}.srt",
            f"{video_part}.srt",
            "*.srt"  # Fallback for single subtitle
        ]
        
        for pattern in patterns:
            matches = list(subtitle_dir.glob(pattern))
            if matches:
                return str(matches[0])
        
        return None
    
    def _parse_srt_file(self, srt_path: str) -> List[Dict]:
        """Parse SRT file and extract subtitle segments"""
        segments = []
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
                        segments.append({
                            'index': index,
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text
                        })
            
            logger.info(f"📝 Parsed {len(segments)} subtitle segments from {srt_path}")
            return segments
            
        except Exception as e:
            logger.warning(f"⚠ Error parsing SRT file: {e}")
            return []
    
    def _time_to_seconds_srt(self, time_str: str) -> float:
        """Convert SRT time format (HH:MM:SS,mmm) to seconds"""
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        return h * 3600 + m * 60 + s + ms / 1000.0
    
    def _seconds_to_time_srt(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        ms = int((seconds % 1) * 1000)
        seconds = int(seconds)
        
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    def _extract_subtitle_for_clip(self, video_part: str, start_time: str, 
                                    end_time: str, output_path: str, 
                                    subtitle_dir: Path) -> bool:
        """Extract subtitle segments for a clip's time range and save to file"""
        try:
            # Find subtitle file
            subtitle_file = self._find_subtitle_file(video_part, subtitle_dir)
            if not subtitle_file:
                logger.info(f"⚠ No subtitle file found for {video_part}")
                return False
            
            # Parse subtitle file
            segments = self._parse_srt_file(subtitle_file)
            if not segments:
                logger.info(f"⚠ No subtitle segments found in {subtitle_file}")
                return False
            
            # Convert clip time range to seconds
            clip_start = self._time_to_seconds(start_time)
            clip_end = self._time_to_seconds(end_time)
            
            # Filter segments that overlap with clip time range
            clip_segments = []
            for seg in segments:
                seg_start = self._time_to_seconds_srt(seg['start_time'])
                seg_end = self._time_to_seconds_srt(seg['end_time'])
                
                # Check if segment overlaps with clip time range
                if seg_end > clip_start and seg_start < clip_end:
                    # Adjust segment timing to start from 0 for the clip
                    new_start = max(0.0, seg_start - clip_start)
                    new_end = max(new_start + 0.1, seg_end - clip_start)
                    
                    clip_segments.append({
                        'index': len(clip_segments) + 1,
                        'start_time': self._seconds_to_time_srt(new_start),
                        'end_time': self._seconds_to_time_srt(new_end),
                        'text': seg['text']
                    })
            
            if not clip_segments:
                logger.info(f"⚠ No subtitle segments overlap with clip time range")
                return False
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                for seg in clip_segments:
                    f.write(f"{seg['index']}\n")
                    f.write(f"{seg['start_time']} --> {seg['end_time']}\n")
                    f.write(f"{seg['text']}\n\n")
            
            logger.info(f"✓ Generated subtitle file with {len(clip_segments)} segments")
            return True
            
        except Exception as e:
            logger.warning(f"⚠ Error extracting subtitle for clip: {e}")
            return False
    
    def _sanitize_filename(self, title: str) -> str:
        """Clean title for use as filename"""
        # Remove emojis and special characters
        title = re.sub(r'[^\w\s-]', '', title)
        # Replace spaces with underscores
        title = re.sub(r'[\s\-]+', '_', title)
        # Remove multiple underscores
        title = re.sub(r'_+', '_', title)
        # Trim underscores
        return title.strip('_')
    
    def _time_to_seconds(self, time_str: str) -> int:
        """Convert MM:SS or HH:MM:SS to seconds"""
        parts = time_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    
    def _create_clip(self, input_video: str, start_time: str, 
                    end_time: str, output_path: str, title: str) -> bool:
        """Create a video clip using ffmpeg"""
        try:
            start_seconds = self._time_to_seconds(start_time)
            end_seconds = self._time_to_seconds(end_time)
            duration = end_seconds - start_seconds
            
            # Use ffmpeg to extract clip
            cmd = [
                'ffmpeg',
                '-ss', start_time,
                '-i', input_video,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-avoid_negative_ts', 'make_zero',
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error creating clip: {e}")
            return False
    
    def _create_summary(self, clips_info: List[Dict], data: Dict):
        """Create markdown summary of generated clips"""
        summary_path = self.output_dir / "engaging_moments_summary.md"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# 🔥 Top Engaging Moments - Video Clips\n\n")
            f.write(f"**Total Clips**: {len(clips_info)}\n\n")
            
            if 'analysis_summary' in data:
                f.write("## 📊 Analysis Summary\n")
                f.write(f"**Highest Engagement Themes**: {', '.join(data['analysis_summary']['highest_engagement_themes'])}\n")
                f.write(f"**Total Engaging Content Time**: {data['analysis_summary']['total_engaging_content_time']}\n")
                f.write(f"**Recommendation**: {data['analysis_summary']['recommendation']}\n\n")
            
            f.write("## 🎬 Generated Clips\n\n")
            f.write("| Rank | Title | Video File | Subtitle File | Duration | Engagement |\n")
            f.write("|------|-------|------------|----------------|----------|------------|\n")
            
            for clip in clips_info:
                subtitle_file = clip.get('subtitle_filename', 'N/A')
                if subtitle_file:
                    subtitle_file = f"`{subtitle_file}`"
                else:
                    subtitle_file = "N/A"
                f.write(f"| {clip['rank']} | {clip['title']} | `{clip['filename']}` | "
                       f"{subtitle_file} | {clip['duration']} | {clip['engagement_level']} |\n")
            
            f.write("\n## 📝 Detailed Descriptions\n\n")
            for clip in clips_info:
                f.write(f"### Rank {clip['rank']}: {clip['title']}\n")
                f.write(f"**Time Range**: {clip['time_range']}\n")
                f.write(f"**Duration**: {clip['duration']}\n")
                f.write(f"**Video File**: `{clip['filename']}`\n")
                if clip.get('subtitle_filename'):
                    f.write(f"**Subtitle File**: `{clip['subtitle_filename']}`\n")
                f.write(f"**Why Engaging**: {clip['why_engaging']}\n\n")
        
        logger.info(f"📄 Summary created: {summary_path}")
