#!/usr/bin/env python3
"""
Test script for cover image generation
"""
import sys
from pathlib import Path
from core.cover_image_generator import CoverImageGenerator

def main():
    """Test cover image generation"""
    
    # Check if video file exists
    test_videos = [
        "processed_videos/downloads/旭旭宝宝1月27日直播回放.mp4",
        "test_final/豪弟：这不对呀，11.5个W就买了个手机.mp4"
    ]
    
    video_path = None
    for path in test_videos:
        if Path(path).exists():
            video_path = path
            break
    
    if not video_path:
        print("❌ No test video found")
        print("Available test videos:")
        for path in test_videos:
            print(f"  - {path}")
        return 1
    
    print(f"🎬 Testing cover generation with: {video_path}")
    
    # Initialize generator
    generator = CoverImageGenerator()
    
    # Generate cover
    output_path = "test_output/test_cover.jpg"
    Path("test_output").mkdir(exist_ok=True)
    
    title_text = "宝哥与大斌子洗脚梗爆笑互动全场沸腾"
    
    print(f"📝 Title: {title_text}")
    print(f"💾 Output: {output_path}")
    
    success = generator.generate_cover(
        video_path,
        title_text,
        output_path,
        frame_time=5.0
    )
    
    if success:
        print(f"✅ Cover generated successfully!")
        print(f"📁 Saved to: {output_path}")
        return 0
    else:
        print(f"❌ Cover generation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
