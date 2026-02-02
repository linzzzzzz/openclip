"""
Example workflow integrating Qwen API with video processing
"""

import os
from qwen_video_assistant import QwenVideoAssistant
from typing import Dict, List, Optional


def process_video_with_qwen(video_path: str, transcript_path: Optional[str] = None) -> Dict:
    """
    Complete video processing workflow using Qwen API
    
    Args:
        video_path: Path to video file
        transcript_path: Optional path to existing transcript file
        
    Returns:
        Dictionary with all generated content
    """
    
    # Initialize Qwen assistant
    try:
        assistant = QwenVideoAssistant()
    except ValueError as e:
        return {"error": f"Failed to initialize Qwen client: {e}"}
    
    # Load or generate transcript
    if transcript_path and os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        print(f"Loaded transcript from {transcript_path}")
    else:
        # In a real scenario, you'd generate this with Whisper
        print("No transcript provided. In a real workflow, you'd generate this with Whisper.")
        transcript = """
        Sample transcript content. In your actual workflow, this would be 
        generated from your video using Whisper or another speech-to-text service.
        """
    
    print("Processing video with Qwen AI...")
    
    results = {
        "video_path": video_path,
        "transcript": transcript
    }
    
    # 1. Analyze transcript
    print("1. Analyzing transcript...")
    analysis = assistant.analyze_transcript(transcript)
    results["analysis"] = analysis
    
    # 2. Generate titles
    print("2. Generating engaging titles...")
    titles = assistant.generate_engaging_titles(transcript, count=5)
    results["titles"] = titles
    
    # 3. Suggest clip segments
    print("3. Suggesting clip segments...")
    clips = assistant.suggest_clip_segments(transcript, duration_seconds=60)
    results["suggested_clips"] = clips
    
    # 4. Generate description using best title
    if titles and len(titles) > 0:
        print("4. Generating video description...")
        description = assistant.generate_description(transcript, titles[0])
        results["description"] = description
    
    # 5. Improve subtitles (if you have raw subtitle data)
    print("5. Improving subtitle formatting...")
    improved_subtitles = assistant.improve_subtitles(transcript)
    results["improved_subtitles"] = improved_subtitles
    
    return results


def save_results(results: Dict, output_dir: str = "qwen_output"):
    """Save processing results to files"""
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    video_name = os.path.splitext(os.path.basename(results["video_path"]))[0]
    
    # Save analysis
    if "analysis" in results:
        with open(f"{output_dir}/{video_name}_analysis.json", 'w') as f:
            import json
            json.dump(results["analysis"], f, indent=2)
    
    # Save titles
    if "titles" in results:
        with open(f"{output_dir}/{video_name}_titles.txt", 'w') as f:
            for i, title in enumerate(results["titles"], 1):
                f.write(f"{i}. {title}\n")
    
    # Save description
    if "description" in results:
        with open(f"{output_dir}/{video_name}_description.txt", 'w') as f:
            f.write(results["description"])
    
    # Save improved subtitles
    if "improved_subtitles" in results:
        with open(f"{output_dir}/{video_name}_improved_subtitles.srt", 'w') as f:
            f.write(results["improved_subtitles"])
    
    # Save suggested clips
    if "suggested_clips" in results:
        with open(f"{output_dir}/{video_name}_clip_suggestions.json", 'w') as f:
            import json
            json.dump(results["suggested_clips"], f, indent=2)
    
    print(f"Results saved to {output_dir}/")


def batch_process_videos(video_directory: str, transcript_directory: Optional[str] = None):
    """Process multiple videos in batch"""
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    
    for file in os.listdir(video_directory):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(video_directory, file))
    
    print(f"Found {len(video_files)} video files to process")
    
    for video_path in video_files:
        print(f"\n=== Processing {os.path.basename(video_path)} ===")
        
        # Look for corresponding transcript
        transcript_path = None
        if transcript_directory:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            potential_transcript = os.path.join(transcript_directory, f"{video_name}.txt")
            if os.path.exists(potential_transcript):
                transcript_path = potential_transcript
        
        # Process video
        results = process_video_with_qwen(video_path, transcript_path)
        
        if "error" in results:
            print(f"Error processing {video_path}: {results['error']}")
            continue
        
        # Save results
        save_results(results)
        
        print(f"Completed processing {os.path.basename(video_path)}")


def main():
    """Example usage"""
    
    print("=== Qwen Video Processing Workflow ===\n")
    
    # Check if API key is set
    if not os.getenv("QWEN_API_KEY"):
        print("Error: QWEN_API_KEY environment variable not set")
        print("Please set it with: export QWEN_API_KEY='your-api-key'")
        return
    
    # Example 1: Process single video
    print("Example 1: Single video processing")
    sample_video = "test_output.mp4"  # This file exists in your directory
    
    if os.path.exists(sample_video):
        results = process_video_with_qwen(sample_video)
        
        if "error" not in results:
            print("\n=== Results ===")
            
            if "titles" in results:
                print("\nGenerated Titles:")
                for i, title in enumerate(results["titles"], 1):
                    print(f"{i}. {title}")
            
            if "analysis" in results and isinstance(results["analysis"], dict):
                print(f"\nSummary: {results['analysis'].get('summary', 'N/A')}")
                print(f"Tone: {results['analysis'].get('tone', 'N/A')}")
            
            # Save results
            save_results(results)
        else:
            print(f"Error: {results['error']}")
    else:
        print(f"Sample video {sample_video} not found")
    
    # Example 2: Batch processing (commented out)
    # print("\nExample 2: Batch processing")
    # batch_process_videos("./", "./transcripts")


if __name__ == "__main__":
    main()