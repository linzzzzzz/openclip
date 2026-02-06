#!/usr/bin/env python3
"""
Clip Generator - Extract engaging video clips from analyzed moments
"""
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

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
                                    video_dir: str) -> Dict[str, Any]:
        """
        Generate clips from engaging moments analysis
        
        Args:
            analysis_file: Path to top_engaging_moments.json
            video_dir: Directory containing source video files
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Load analysis data
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            video_dir = Path(video_dir)
            
            logger.info("🎬 Generating clips from Top Engaging Moments")
            logger.info(f"📁 Output: {self.output_dir}")
            
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
                    successful_clips += 1
                    clips_info.append({
                        'rank': rank,
                        'title': title,
                        'filename': output_filename,
                        'duration': duration,
                        'video_part': video_part,
                        'time_range': f"{start_time} - {end_time}",
                        'engagement_level': moment['engagement_details'].get('engagement_level', 'N/A'),
                        'why_engaging': moment['why_engaging']
                    })
                    logger.info(f"✓ Saved: {output_filename}")
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
            f.write("| Rank | Title | File | Duration | Engagement |\n")
            f.write("|------|-------|------|----------|------------|\n")
            
            for clip in clips_info:
                f.write(f"| {clip['rank']} | {clip['title']} | `{clip['filename']}` | "
                       f"{clip['duration']} | {clip['engagement_level']} |\n")
            
            f.write("\n## 📝 Detailed Descriptions\n\n")
            for clip in clips_info:
                f.write(f"### Rank {clip['rank']}: {clip['title']}\n")
                f.write(f"**Time Range**: {clip['time_range']}\n")
                f.write(f"**Duration**: {clip['duration']}\n")
                f.write(f"**Why Engaging**: {clip['why_engaging']}\n\n")
        
        logger.info(f"📄 Summary created: {summary_path}")
