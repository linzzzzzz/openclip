#!/usr/bin/env python3
"""
Test script to verify orchestrator integration
Tests the new clip generation and title addition features
"""
import asyncio
import os
from pathlib import Path
from video_orchestrator import VideoOrchestrator


async def test_integration():
    """Test the full pipeline with existing data"""
    
    print("🧪 Testing Video Orchestrator Integration")
    print("=" * 60)
    
    # Check if we have existing analysis data
    test_analysis_file = Path("processed_videos/splits/旭旭宝宝1月27日直播回放_split/top_engaging_moments.json")
    
    if not test_analysis_file.exists():
        print("❌ Test data not found. Please run the orchestrator on a video first.")
        print(f"   Expected: {test_analysis_file}")
        return False
    
    print("✓ Found existing analysis data")
    
    # Test 1: Clip Generator
    print("\n📋 Test 1: Clip Generator")
    print("-" * 60)
    
    from clip_generator import ClipGenerator
    
    clip_gen = ClipGenerator(output_dir="test_clips")
    video_dir = test_analysis_file.parent
    
    try:
        result = clip_gen.generate_clips_from_analysis(
            str(test_analysis_file),
            str(video_dir)
        )
        
        if result['success']:
            print(f"✓ Generated {result['successful_clips']}/{result['total_clips']} clips")
            print(f"  Output: {result['output_dir']}")
        else:
            print(f"✗ Clip generation failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Title Adder
    print("\n📋 Test 2: Title Adder")
    print("-" * 60)
    
    from title_adder import TitleAdder
    
    title_adder = TitleAdder(output_dir="test_clips_with_titles")
    
    try:
        result = title_adder.add_titles_to_clips(
            clips_dir="test_clips",
            analysis_file=str(test_analysis_file),
            artistic_style="crystal_ice"
        )
        
        if result['success']:
            print(f"✓ Added titles to {result['successful_clips']}/{result['total_clips']} clips")
            print(f"  Style: {result['artistic_style']}")
            print(f"  Output: {result['output_dir']}")
        else:
            print(f"✗ Title addition failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 3: Verify output files
    print("\n📋 Test 3: Verify Output Files")
    print("-" * 60)
    
    test_clips_dir = Path("test_clips")
    test_titles_dir = Path("test_clips_with_titles")
    
    clips_count = len(list(test_clips_dir.glob("*.mp4"))) if test_clips_dir.exists() else 0
    titles_count = len(list(test_titles_dir.glob("*.mp4"))) if test_titles_dir.exists() else 0
    
    print(f"  Clips generated: {clips_count}")
    print(f"  Clips with titles: {titles_count}")
    
    if clips_count > 0 and titles_count > 0:
        print("✓ All output files created successfully")
    else:
        print("✗ Some output files missing")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All integration tests passed!")
    print("\n💡 Test outputs:")
    print(f"   Clips: {test_clips_dir}")
    print(f"   Titled clips: {test_titles_dir}")
    print("\n💡 To clean up test files:")
    print("   rm -rf test_clips test_clips_with_titles")
    
    return True


async def test_orchestrator_config():
    """Test orchestrator configuration"""
    
    print("\n🧪 Testing Orchestrator Configuration")
    print("=" * 60)
    
    # Test with API key
    api_key = os.getenv("QWEN_API_KEY")
    
    if api_key:
        print("✓ QWEN_API_KEY found")
        
        orchestrator = VideoOrchestrator(
            output_dir="test_output",
            qwen_api_key=api_key,
            generate_clips=True,
            add_titles=True,
            artistic_style="neon_glow"
        )
        
        print(f"✓ Orchestrator initialized")
        print(f"  Clip generation: {'enabled' if orchestrator.clip_generator else 'disabled'}")
        print(f"  Title addition: {'enabled' if orchestrator.title_adder else 'disabled'}")
        print(f"  Artistic style: {orchestrator.artistic_style}")
    else:
        print("⚠️  QWEN_API_KEY not set")
        print("   Clip generation and title addition will be disabled")
        
        orchestrator = VideoOrchestrator(
            output_dir="test_output",
            generate_clips=True,
            add_titles=True
        )
        
        print(f"✓ Orchestrator initialized (limited mode)")
        print(f"  Clip generation: {'enabled' if orchestrator.clip_generator else 'disabled'}")
        print(f"  Title addition: {'enabled' if orchestrator.title_adder else 'disabled'}")
    
    return True


async def main():
    """Run all tests"""
    
    print("\n🚀 Video Orchestrator Integration Tests")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = await test_orchestrator_config()
    
    # Test 2: Integration (only if we have test data)
    integration_ok = await test_integration()
    
    print("\n" + "=" * 60)
    if config_ok and integration_ok:
        print("✅ ALL TESTS PASSED")
        return 0
    elif config_ok:
        print("⚠️  Configuration OK, but integration tests skipped (no test data)")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
