#!/usr/bin/env python3
"""
Example Usage of Video Orchestrator
Demonstrates how to use the video orchestrator programmatically
"""

import asyncio
from video_orchestrator import VideoOrchestrator

async def example_basic_usage():
    """Example 1: Basic video processing"""
    print("🎬 Example 1: Basic Video Processing")
    print("=" * 50)
    
    # Initialize orchestrator with default settings
    orchestrator = VideoOrchestrator()
    
    # Example URL (replace with actual Bilibili URL)
    example_url = "https://www.bilibili.com/video/BV1234567890"
    
    print(f"🔗 Processing URL: {example_url}")
    print("📝 Using default settings:")
    print("   - Max duration: 20 minutes")
    print("   - Whisper model: base")
    print("   - Transcript source: auto (bilibili first, then whisper)")
    print("   - Output directory: processed_videos")
    
    # Note: This would actually process the video if the URL was valid
    # result = await orchestrator.process_video(example_url)
    print("\n✅ (This is just an example - replace with a real URL to test)")

async def example_custom_settings():
    """Example 2: Custom settings"""
    print("\n🎬 Example 2: Custom Settings")
    print("=" * 50)
    
    # Initialize orchestrator with custom settings
    orchestrator = VideoOrchestrator(
        output_dir="my_custom_output",
        max_duration_minutes=15.0,  # Split at 15 minutes
        whisper_model="small",      # Better accuracy
        browser="firefox"           # Use Firefox cookies
    )
    
    example_url = "https://www.bilibili.com/video/BV9999999999"
    
    print(f"🔗 Processing URL: {example_url}")
    print("📝 Using custom settings:")
    print("   - Max duration: 15 minutes")
    print("   - Whisper model: small (better accuracy)")
    print("   - Browser: firefox")
    print("   - Output directory: my_custom_output")
    
    # Force Whisper transcript generation
    # result = await orchestrator.process_video(
    #     example_url,
    #     force_whisper=True  # Force Whisper even if bilibili subtitles exist
    # )
    print("\n✅ (This is just an example - replace with a real URL to test)")

async def example_batch_processing():
    """Example 3: Batch processing multiple videos"""
    print("\n🎬 Example 3: Batch Processing")
    print("=" * 50)
    
    # List of example URLs (replace with actual URLs)
    video_urls = [
        "https://www.bilibili.com/video/BV1111111111",
        "https://www.bilibili.com/video/BV2222222222", 
        "https://www.bilibili.com/video/BV3333333333"
    ]
    
    orchestrator = VideoOrchestrator(
        output_dir="batch_output",
        max_duration_minutes=10.0,  # Shorter parts for batch processing
        whisper_model="tiny"        # Faster processing
    )
    
    print(f"🔗 Processing {len(video_urls)} videos:")
    for i, url in enumerate(video_urls, 1):
        print(f"   {i}. {url}")
    
    print("\n📝 Using batch-optimized settings:")
    print("   - Max duration: 10 minutes (smaller parts)")
    print("   - Whisper model: tiny (fastest)")
    print("   - Output directory: batch_output")
    
    # Process each video
    # for i, url in enumerate(video_urls, 1):
    #     print(f"\n🚀 Processing video {i}/{len(video_urls)}")
    #     result = await orchestrator.process_video(url)
    #     
    #     if result.success:
    #         print(f"✅ Success: {result.video_info.get('title', 'Unknown')}")
    #     else:
    #         print(f"❌ Failed: {result.error_message}")
    
    print("\n✅ (This is just an example - replace with real URLs to test)")

async def example_with_progress_callback():
    """Example 4: Using progress callback"""
    print("\n🎬 Example 4: Progress Tracking")
    print("=" * 50)
    
    def progress_callback(status: str, progress: float):
        # Custom progress display
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r🔄 [{bar}] {progress:.1f}% - {status}", end='', flush=True)
    
    orchestrator = VideoOrchestrator()
    example_url = "https://www.bilibili.com/video/BV5555555555"
    
    print(f"🔗 Processing URL: {example_url}")
    print("📊 With custom progress tracking:")
    
    # result = await orchestrator.process_video(
    #     example_url,
    #     progress_callback=progress_callback
    # )
    
    print("\n✅ (This is just an example - replace with a real URL to test)")

def example_cli_usage():
    """Example 5: Command line usage examples"""
    print("\n🎬 Example 5: Command Line Usage")
    print("=" * 50)
    
    print("📋 Here are some CLI examples you can try:")
    print()
    
    examples = [
        {
            "name": "Basic processing",
            "cmd": 'uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"'
        },
        {
            "name": "Force Whisper transcripts",
            "cmd": 'uv run python video_orchestrator.py --force-whisper "https://www.bilibili.com/video/BV1234567890"'
        },
        {
            "name": "Custom duration and model",
            "cmd": 'uv run python video_orchestrator.py --max-duration 15 --whisper-model small "https://www.bilibili.com/video/BV1234567890"'
        },
        {
            "name": "Custom output directory",
            "cmd": 'uv run python video_orchestrator.py -o "my_videos" "https://www.bilibili.com/video/BV1234567890"'
        },
        {
            "name": "Verbose logging",
            "cmd": 'uv run python video_orchestrator.py -v "https://www.bilibili.com/video/BV1234567890"'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['name']}:")
        print(f"   {example['cmd']}")
        print()

async def main():
    """Run all examples"""
    print("🎯 Video Orchestrator Examples")
    print("=" * 60)
    print("These examples demonstrate how to use the video orchestrator")
    print("Replace the example URLs with real Bilibili URLs to test")
    print("=" * 60)
    
    # Run async examples
    await example_basic_usage()
    await example_custom_settings()
    await example_batch_processing()
    await example_with_progress_callback()
    
    # Show CLI examples
    example_cli_usage()
    
    print("🚀 To test with real videos, replace the example URLs and run!")
    print("📚 For more information, see README_video_orchestrator.md")

if __name__ == "__main__":
    asyncio.run(main())
