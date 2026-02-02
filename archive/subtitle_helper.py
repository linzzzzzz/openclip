#!/usr/bin/env python3
"""
Subtitle Helper Script
Utilities for working with video subtitles using Whisper and ffmpeg
"""

import subprocess
import os
import sys

def add_subtitles_to_video(video_file, srt_file, output_file=None, hard_coded=False):
    """
    Add subtitles to a video file
    
    Args:
        video_file (str): Path to input video
        srt_file (str): Path to SRT subtitle file  
        output_file (str): Path to output video (optional)
        hard_coded (bool): If True, burn subtitles into video permanently
    
    Returns:
        bool: True if successful
    """
    if not output_file:
        name, ext = os.path.splitext(video_file)
        output_file = f"{name}_with_subtitles{ext}"
    
    print(f"🎬 Adding subtitles to: {video_file}")
    print(f"📝 Using subtitles: {srt_file}")
    print(f"💾 Output file: {output_file}")
    
    if hard_coded:
        print("🔥 Creating hard-coded subtitles (burned into video)")
        cmd = [
            "ffmpeg", "-i", video_file,
            "-vf", f"subtitles={srt_file}",
            "-c:a", "copy",
            output_file
        ]
    else:
        print("📄 Creating soft subtitles (can be toggled on/off)")
        cmd = [
            "ffmpeg", "-i", video_file, "-i", srt_file,
            "-c", "copy", "-c:s", "mov_text",
            "-metadata:s:s:0", "language=zh",
            output_file
        ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Subtitles added successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def transcribe_and_subtitle(video_file, model="base", output_format="srt"):
    """
    Transcribe video and create subtitled version in one step
    
    Args:
        video_file (str): Path to video file
        model (str): Whisper model to use
        output_format (str): Output format for transcription
    """
    print(f"🎵 Step 1: Transcribing {video_file} with model '{model}'")
    
    # Run whisper transcription
    cmd = ["whisper", video_file, "--model", model, "--output_format", output_format]
    try:
        subprocess.run(cmd, check=True)
        print("✅ Transcription completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Transcription failed: {e}")
        return False
    
    # Find the generated subtitle file
    base_name = os.path.splitext(video_file)[0]
    srt_file = f"{base_name}.{output_format}"
    
    if not os.path.exists(srt_file):
        print(f"❌ Subtitle file not found: {srt_file}")
        return False
    
    print(f"📝 Step 2: Adding subtitles to video")
    return add_subtitles_to_video(video_file, srt_file)

def main():
    """Main function with command line interface"""
    
    if len(sys.argv) < 2:
        print("🎬 Subtitle Helper Usage:")
        print("\n1. Transcribe and add subtitles:")
        print("   python subtitle_helper.py transcribe video.mp4 [model]")
        print("   Example: python subtitle_helper.py transcribe video.mp4 tiny")
        
        print("\n2. Add existing SRT to video:")
        print("   python subtitle_helper.py add video.mp4 subtitles.srt [output.mp4]")
        
        print("\n3. Create hard-coded subtitles:")
        print("   python subtitle_helper.py burn video.mp4 subtitles.srt [output.mp4]")
        
        print("\n📋 Available Whisper models: tiny, base, small, medium, large, turbo")
        return
    
    action = sys.argv[1].lower()
    
    if action == "transcribe":
        if len(sys.argv) < 3:
            print("❌ Please specify a video file")
            return
        
        video_file = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "base"
        transcribe_and_subtitle(video_file, model)
        
    elif action == "add":
        if len(sys.argv) < 4:
            print("❌ Please specify video and subtitle files")
            return
            
        video_file = sys.argv[2]
        srt_file = sys.argv[3]
        output_file = sys.argv[4] if len(sys.argv) > 4 else None
        add_subtitles_to_video(video_file, srt_file, output_file, hard_coded=False)
        
    elif action == "burn":
        if len(sys.argv) < 4:
            print("❌ Please specify video and subtitle files")
            return
            
        video_file = sys.argv[2]
        srt_file = sys.argv[3]
        output_file = sys.argv[4] if len(sys.argv) > 4 else None
        add_subtitles_to_video(video_file, srt_file, output_file, hard_coded=True)
        
    else:
        print(f"❌ Unknown action: {action}")
        print("Valid actions: transcribe, add, burn")

if __name__ == "__main__":
    main()
