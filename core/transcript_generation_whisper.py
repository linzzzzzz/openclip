#!/usr/bin/env python3
"""
Whisper Transcript Generation
Complete transcript processing including CLI usage and orchestration functionality
"""

import subprocess
import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from core.config import WHISPER_MODEL

logger = logging.getLogger(__name__)

def run_whisper_cli(file_path, model_name=WHISPER_MODEL, language=None, output_format="srt", output_dir=None):
    """
    Transcribe audio/video file using OpenAI Whisper CLI

    Args:
        file_path (str): Path to audio/video file
        model_name (str): Whisper model to use (tiny, base, small, medium, large, turbo)
        language (str): Language code (e.g., 'en', 'zh', 'ja') or None for auto-detection
        output_format (str): Output format (txt, vtt, srt, tsv, json, all)
        output_dir (str): Directory to write output files to (defaults to current directory)

    Returns:
        bool: True if successful, False if failed
    """
    print(f"🎵 Transcribing: {file_path}")
    print(f"📊 Model: {model_name}")
    print(f"📝 Output format: {output_format}")

    # Build the whisper command
    cmd = ["whisper", file_path, "--model", model_name, "--output_format", output_format]

    if output_dir:
        cmd.extend(["--output_dir", str(output_dir)])
    
    if language:
        cmd.extend(["--language", language])
        print(f"🌍 Language: {language}")
    else:
        print("🔍 Language: Auto-detection")
    
    try:
        print("\n⏳ Running Whisper...")
        print("📋 Progress will be shown below:")
        print("-" * 50)
        
        # Run without capturing output to show real-time progress
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print("-" * 50)
            print("✅ Transcription completed successfully!")
            return True
        else:
            print("-" * 50)
            print(f"❌ Transcription failed with return code: {result.returncode}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Whisper CLI not found. Make sure it's installed and in your PATH.")
        return False

def demonstrate_whisper():
    """Demonstrate different Whisper usage examples"""
    
    print("=== OpenAI Whisper CLI Demo ===\n")
    
    # Check if we have a sample file
    sample_file = "../video_sample.mp4"
    
    if os.path.exists(sample_file):
        print("📁 Found sample video file!")
        
        print("\n--- Example 1: Basic transcription (tiny model, fast) ---")
        success = run_whisper_cli(sample_file, model_name="tiny")
        
        if success:
            # Look for output files
            base_name = os.path.splitext(os.path.basename(sample_file))[0]
            txt_file = f"{base_name}.txt"
            
            if os.path.exists(txt_file):
                print(f"\n📄 Transcript saved to: {txt_file}")
                # Show first few lines
                try:
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"Preview: {preview}")
                except Exception as e:
                    print(f"Could not read transcript: {e}")
        
        print("\n--- Example 2: Different formats ---")
        print("💡 You can also generate different output formats:")
        
    else:
        print("📂 No sample file found. Here are usage examples:")
    
    print("\n🎯 Usage Examples:")
    print("1. Basic transcription:")
    print("   whisper audio.mp3")
    
    print("\n2. Specify model size:")
    print("   whisper audio.mp3 --model small")
    
    print("\n3. Specify language:")
    print("   whisper audio.mp3 --language en")
    
    print("\n4. Multiple output formats:")
    print("   whisper audio.mp3 --output_format all")
    
    print("\n5. Subtitle format:")
    print("   whisper video.mp4 --output_format srt")
    
    print("\n📏 Available Models (speed vs accuracy):")
    models = [
        ("tiny", "Fastest, least accurate"),
        ("base", "Good balance"),
        ("small", "Better accuracy"),
        ("medium", "High accuracy"),
        ("large", "Best accuracy, slowest"),
        ("turbo", "Fast and accurate")
    ]
    
    for model, desc in models:
        print(f"   • {model}: {desc}")
    
    print("\n📋 Output Formats:")
    formats = ["txt", "vtt", "srt", "tsv", "json", "all"]
    for fmt in formats:
        print(f"   • {fmt}")

def simple_transcribe(audio_file, model="base"):
    """Simple function to transcribe an audio file"""
    if not os.path.exists(audio_file):
        print(f"❌ File not found: {audio_file}")
        return False
    
    return run_whisper_cli(audio_file, model_name=model)


class TranscriptProcessor:
    """Handles all transcript-related operations"""
    
    def __init__(self, whisper_model: str = WHISPER_MODEL):
        self.whisper_model = whisper_model
    
    async def process_transcripts(self, 
                                subtitle_path: str,
                                video_files: List[str] or str,
                                force_whisper: bool,
                                progress_callback: Optional[Callable[[str, float], None]]) -> Dict[str, Any]:
        """Process transcripts - either use existing subtitles or generate with whisper"""
        
        # Determine transcript source
        use_whisper = force_whisper or not subtitle_path or not os.path.exists(subtitle_path)
        
        if use_whisper:
            logger.info("🤖 Using Whisper for transcript generation")
            return await self._generate_whisper_transcripts(video_files, progress_callback)
        else:
            logger.info("📥 Using existing subtitles")
            return {
                'source': 'bilibili' if 'bilibili' in subtitle_path else 'existing',
                'transcript_path': subtitle_path if isinstance(video_files, str) else '',
                'transcript_parts': [] if isinstance(video_files, str) else self._get_existing_transcript_parts(video_files)
            }
    
    async def _generate_whisper_transcripts(self, 
                                          video_files: List[str] or str,
                                          progress_callback: Optional[Callable[[str, float], None]]) -> Dict[str, Any]:
        """Generate transcripts using Whisper"""
        
        if isinstance(video_files, str):
            video_files = [video_files]
        
        transcript_parts = []
        total_files = len(video_files)
        
        for i, video_file in enumerate(video_files):
            # Update progress
            if progress_callback:
                base_progress = 50 + (i / total_files) * 40  # 50-90% range
                progress_callback(f"Generating transcript {i+1}/{total_files}...", base_progress)
            
            logger.info(f"🎙️  Generating transcript for: {Path(video_file).name}")
            
            video_path = Path(video_file)
            video_dir = video_path.parent

            success = run_whisper_cli(
                str(video_path),
                model_name=self.whisper_model,
                language="zh",  # Assuming Chinese content
                output_format="srt",
                output_dir=str(video_dir)
            )

            if success:
                srt_path = video_dir / f"{video_path.stem}.srt"
                if srt_path.exists():
                    transcript_parts.append(str(srt_path))
                    logger.info(f"✅ Generated: {srt_path.name}")
                else:
                    logger.warning(f"⚠️  SRT file not found for {video_path.name}")
            else:
                logger.error(f"❌ Whisper failed for {video_path.name}")
        
        return {
            'source': 'whisper',
            'transcript_path': transcript_parts[0] if len(transcript_parts) == 1 else '',
            'transcript_parts': transcript_parts
        }
    
    def _get_existing_transcript_parts(self, video_files: List[str]) -> List[str]:
        """Get existing transcript parts (they should already exist from splitting)"""
        transcript_parts = []
        
        for video_file in video_files:
            video_path = Path(video_file)
            srt_path = video_path.parent / f"{video_path.stem}.srt"
            
            if srt_path.exists():
                transcript_parts.append(str(srt_path))
            else:
                logger.warning(f"⚠️  Expected transcript not found: {srt_path}")
        
        return transcript_parts


def main():
    """Main function"""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        model = sys.argv[2] if len(sys.argv) > 2 else "base"
        
        print(f"🎵 Transcribing file: {audio_file}")
        simple_transcribe(audio_file, model)
    else:
        # Run demonstration
        demonstrate_whisper()
    
    print("\n🚀 To transcribe your own file:")
    print("   python main.py your_audio_file.mp3 [model]")
    print("   Example: python main.py speech.wav tiny")

if __name__ == "__main__":
    main()
