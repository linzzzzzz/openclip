"""
Qwen Video Assistant - Integration with video processing workflow
"""

from qwen_api_client import QwenAPIClient, QwenMessage
from typing import List, Dict, Optional
import json
import os


class QwenVideoAssistant:
    """Assistant that uses Qwen API for video-related tasks"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the video assistant with Qwen API client"""
        self.client = QwenAPIClient(api_key)
    
    def analyze_transcript(self, transcript: str) -> Dict[str, str]:
        """
        Analyze video transcript and extract insights
        
        Args:
            transcript: Video transcript text
            
        Returns:
            Dictionary with analysis results
        """
        system_prompt = """You are a video content analyst. Analyze the provided transcript and provide:
1. A brief summary (2-3 sentences)
2. Key topics discussed
3. Main speakers or characters mentioned
4. Emotional tone
5. Suggested video title
6. Recommended tags for SEO

Format your response as JSON with keys: summary, topics, speakers, tone, title, tags"""
        
        messages = [
            QwenMessage(role="user", content=f"Please analyze this video transcript:\n\n{transcript}")
        ]
        
        try:
            response = self.client.conversation_chat(messages, system_prompt=system_prompt)
            # Try to parse as JSON, fallback to structured text if needed
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"analysis": response}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_engaging_titles(self, transcript: str, count: int = 5) -> List[str]:
        """
        Generate engaging video titles based on transcript
        
        Args:
            transcript: Video transcript text
            count: Number of titles to generate
            
        Returns:
            List of suggested titles
        """
        prompt = f"""Based on this video transcript, generate {count} engaging, clickable video titles that would perform well on social media platforms like YouTube or TikTok. Make them attention-grabbing but accurate to the content.

Transcript:
{transcript[:1000]}...

Please provide exactly {count} titles, one per line."""
        
        try:
            response = self.client.simple_chat(prompt)
            titles = [line.strip() for line in response.split('\n') if line.strip()]
            return titles[:count]  # Ensure we don't return more than requested
        except Exception as e:
            return [f"Error generating titles: {e}"]
    
    def suggest_clip_segments(self, transcript: str, duration_seconds: int = 60) -> List[Dict[str, str]]:
        """
        Suggest interesting segments for short clips
        
        Args:
            transcript: Video transcript text
            duration_seconds: Target duration for clips
            
        Returns:
            List of suggested segments with timestamps and descriptions
        """
        prompt = f"""Analyze this video transcript and suggest 3-5 interesting segments that would make good {duration_seconds}-second clips for social media. For each segment, provide:
1. A brief description of why it's interesting
2. Approximate start time (if timestamps are available)
3. Key quote or moment
4. Suggested clip title

Transcript:
{transcript}

Format as JSON array with objects containing: description, start_time, key_quote, clip_title"""
        
        try:
            response = self.client.simple_chat(prompt)
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback to structured text parsing
                return [{"description": response}]
        except Exception as e:
            return [{"error": str(e)}]
    
    def improve_subtitles(self, subtitle_text: str) -> str:
        """
        Improve subtitle formatting and readability
        
        Args:
            subtitle_text: Raw subtitle text
            
        Returns:
            Improved subtitle text
        """
        prompt = f"""Please improve these subtitles for better readability and engagement:
1. Fix any grammar or spelling errors
2. Add appropriate punctuation
3. Break long sentences into shorter, more readable chunks
4. Maintain the original meaning and timing structure

Original subtitles:
{subtitle_text}

Please return the improved version maintaining any timestamp format if present."""
        
        try:
            return self.client.simple_chat(prompt)
        except Exception as e:
            return f"Error improving subtitles: {e}"
    
    def generate_description(self, transcript: str, title: str) -> str:
        """
        Generate video description based on transcript and title
        
        Args:
            transcript: Video transcript text
            title: Video title
            
        Returns:
            Generated description
        """
        prompt = f"""Create an engaging video description for a video with this title: "{title}"

Based on this transcript content:
{transcript[:800]}...

The description should:
1. Hook viewers in the first line
2. Summarize key points covered
3. Include relevant hashtags
4. Be optimized for search and engagement
5. Be around 150-200 words"""
        
        try:
            return self.client.simple_chat(prompt)
        except Exception as e:
            return f"Error generating description: {e}"


def demo_video_assistant():
    """Demo function showing how to use the video assistant"""
    
    # Sample transcript (you can replace with actual transcript)
    sample_transcript = """
    Hello everyone, welcome back to my channel. Today we're going to talk about 
    artificial intelligence and how it's changing the world. AI is everywhere now, 
    from our phones to our cars, and it's making our lives easier in so many ways.
    
    First, let's discuss machine learning. Machine learning is a subset of AI that 
    allows computers to learn and improve from experience without being explicitly 
    programmed. It's fascinating how these systems can recognize patterns and make 
    predictions.
    
    One of the most exciting applications is in healthcare, where AI is helping 
    doctors diagnose diseases faster and more accurately than ever before.
    """
    
    try:
        assistant = QwenVideoAssistant()
        
        print("=== Qwen Video Assistant Demo ===\n")
        
        # Analyze transcript
        print("1. Transcript Analysis:")
        analysis = assistant.analyze_transcript(sample_transcript)
        print(json.dumps(analysis, indent=2))
        print()
        
        # Generate titles
        print("2. Engaging Titles:")
        titles = assistant.generate_engaging_titles(sample_transcript, count=3)
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
        print()
        
        # Suggest clips
        print("3. Suggested Clip Segments:")
        clips = assistant.suggest_clip_segments(sample_transcript)
        print(json.dumps(clips, indent=2))
        print()
        
        # Generate description
        if titles:
            print("4. Video Description:")
            description = assistant.generate_description(sample_transcript, titles[0])
            print(description)
            print()
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your QWEN_API_KEY environment variable")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    demo_video_assistant()