#!/usr/bin/env python3
import json
import subprocess
import os
from pathlib import Path

def run_ffmpeg_command(cmd):
    """Run ffmpeg command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✓ Command executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error executing command: {e}")
        print(f"stderr: {e.stderr}")
        return False

def time_to_seconds(time_str):
    """Convert MM:SS or HH:MM:SS to seconds"""
    parts = time_str.split(':')
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

def create_engaging_clip(input_video, start_time, end_time, output_filename, title):
    """Create a video clip without overlay from engaging moments data"""
    
    # Calculate duration
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    duration = end_seconds - start_seconds
    
    # Use the start time directly (no offset adjustment needed for part videos)
    start_time_formatted = start_time
    
    # Use re-encoding to ensure compatibility and avoid issues
    cmd = f'ffmpeg -ss {start_time_formatted} -i "{input_video}" -t {duration} -c:v libx264 -c:a aac -avoid_negative_ts make_zero "{output_filename}" -y'
    
    print(f"Creating clip: {Path(output_filename).name}")
    print(f"Title: {title}")
    print(f"Time range: {start_time} to {end_time} (Duration: {duration}s)")
    print(f"Source video: {Path(input_video).name}")
    
    return run_ffmpeg_command(cmd)

def get_video_filename(video_part, base_dir):
    """Map video_part to actual video filename"""
    video_filename = f"旭旭宝宝1月27日直播回放_{video_part}.mp4"
    video_path = base_dir / video_filename
    
    if video_path.exists():
        return str(video_path)
    else:
        print(f"Warning: Video file not found: {video_path}")
        return None

def sanitize_filename(title):
    """Clean title for use as filename"""
    # Remove emojis and special characters that might cause issues
    import re
    # Remove emojis
    title = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces and special chars with underscores
    title = re.sub(r'[\s\-]+', '_', title)
    # Remove multiple underscores
    title = re.sub(r'_+', '_', title)
    # Trim underscores from ends
    title = title.strip('_')
    return title

def main():
    # Paths
    json_file = Path("processed_videos/splits/旭旭宝宝1月27日直播回放_split/top_engaging_moments.json")
    video_dir = Path("processed_videos/splits/旭旭宝宝1月27日直播回放_split")
    output_dir = Path("engaging_clips")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Load engaging moments data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found: {json_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        return
    
    print("🎬 Generating clips from Top 5 Engaging Moments")
    print(f"📊 Analysis date: {data['analysis_info']['analysis_date']}")
    print(f"🎯 Video title: {data['analysis_info']['video_title']}")
    print(f"📁 Output directory: {output_dir}")
    print("-" * 60)
    
    # Process each engaging moment
    clips_info = []
    successful_clips = 0
    
    for moment in data['top_engaging_moments']:
        rank = moment['rank']
        title = moment['title']
        video_part = moment['timing']['video_part']
        start_time = moment['timing']['start_time']
        end_time = moment['timing']['end_time']
        duration = moment['timing']['duration']
        
        print(f"\n[Rank {rank}] Processing engaging moment...")
        
        # Get the correct video file
        input_video = get_video_filename(video_part, video_dir)
        if not input_video:
            print(f"✗ Skipping rank {rank}: Video file not found")
            continue
        
        # Create safe filename
        safe_title = sanitize_filename(title)
        output_filename = f"rank_{rank:02d}_{safe_title}.mp4"
        output_path = output_dir / output_filename
        
        # Create the clip
        success = create_engaging_clip(
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
            print(f"✓ Saved: {output_filename}")
        else:
            print(f"✗ Failed to create: {output_filename}")
        
        print("-" * 40)
    
    # Create summary file
    if clips_info:
        summary_path = output_dir / "engaging_moments_summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# 🔥 Top 5 Engaging Moments - Video Clips\n\n")
            f.write(f"**Video**: {data['analysis_info']['video_title']}\n")
            f.write(f"**Analysis Date**: {data['analysis_info']['analysis_date']}\n")
            f.write(f"**Total Clips**: {len(clips_info)}\n\n")
            
            f.write("## 📊 Analysis Summary\n")
            if 'analysis_summary' in data:
                f.write(f"**Highest Engagement Themes**: {', '.join(data['analysis_summary']['highest_engagement_themes'])}\n")
                f.write(f"**Total Engaging Content Time**: {data['analysis_summary']['total_engaging_content_time']}\n")
                f.write(f"**Recommendation**: {data['analysis_summary']['recommendation']}\n\n")
            
            f.write("## 🎬 Generated Clips\n\n")
            f.write("| Rank | Title | File | Duration | Engagement | Source |\n")
            f.write("|------|-------|------|----------|------------|--------|\n")
            
            for clip in clips_info:
                f.write(f"| {clip['rank']} | {clip['title']} | `{clip['filename']}` | {clip['duration']} | {clip['engagement_level']} | {clip['video_part']} |\n")
            
            f.write("\n## 📝 Detailed Descriptions\n\n")
            for clip in clips_info:
                f.write(f"### Rank {clip['rank']}: {clip['title']}\n")
                f.write(f"**Time Range**: {clip['time_range']}\n")
                f.write(f"**Duration**: {clip['duration']}\n")
                f.write(f"**Source**: {clip['video_part']}\n")
                f.write(f"**Why Engaging**: {clip['why_engaging']}\n\n")
        
        print(f"\n📄 Summary created: {summary_path}")
    
    # Print final summary
    print(f"\n🎯 Final Results:")
    print(f"✓ Successfully created: {successful_clips}/{len(data['top_engaging_moments'])} clips")
    print(f"📁 All clips saved in: {output_dir}")
    
    if successful_clips > 0:
        print(f"📝 Detailed summary: {output_dir}/engaging_moments_summary.md")
        print("\n💡 To add titles to the clips, you can use:")
        print("💡 1. Video editing software (Premiere, Final Cut, etc.)")
        print("💡 2. MoviePy script: python add_titles_engaging_clips.py")
        print("💡 3. Each clip corresponds to its title in the summary file")
        print("\n💡 These clips represent the most engaging moments from the livestream")
        print("💡 Perfect for highlights, social media posts, or promotional content")
    
    # Show honorable mentions
    if 'honorable_mentions' in data and data['honorable_mentions']:
        print(f"\n🏆 Honorable Mentions Available:")
        for mention in data['honorable_mentions'][:3]:  # Show first 3
            print(f"   - {mention.get('title', 'No title')}")
        print("💡 Consider creating clips for these moments too!")

if __name__ == "__main__":
    main()
