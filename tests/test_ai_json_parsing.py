#!/usr/bin/env python3
"""
Test script to verify AI-powered JSON parsing functionality
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

def test_ai_json_fixing():
    """Test the AI-powered JSON fixing functionality"""
    
    print("🧪 Testing AI-powered JSON fixing...")
    print()
    
    # Initialize analyzer
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    # Test case with malformed JSON (truncated)
    malformed_json = '''```json
{
  "video_part": "part01",
  "engaging_moments": [
    {
      "title": "测试标题",
      "start_time": "00:01:30",
      "end_time": "00:02:45",
      "duration_seconds": 75,
      "transcript": "测试内容",
      "engagement_score": 8.5,
      "engagement_details": {
        "engagement_level": "high"
      },
      "why_engaging": "测试原因",
      "tags": ["co-hosting", "interactive"'''
    
    print("Testing malformed JSON (truncated):")
    print(f"Input: {malformed_json[:100]}...")
    
    try:
        # Create dummy entries for validation
        dummy_entries = [{"start_time": "00:00:00,000", "end_time": "00:00:10,000", "text": "test"}]
        
        result = analyzer._extract_and_parse_json(malformed_json, "part01", dummy_entries)
        
        print(f"✅ Successfully parsed with AI fixing!")
        print(f"Result: {result.get('video_part', 'unknown')} with {result.get('total_moments', 0)} moments")
        return True
        
    except Exception as e:
        print(f"❌ AI JSON fixing failed: {e}")
        return False

def test_standard_json_parsing():
    """Test that standard JSON parsing still works"""
    
    print("🧪 Testing standard JSON parsing (should not use AI)...")
    print()
    
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    valid_json = '''```json
{
  "video_part": "part01",
  "engaging_moments": [],
  "total_moments": 0,
  "analysis_timestamp": "2024-01-01T12:00:00Z"
}
```'''
    
    try:
        dummy_entries = [{"start_time": "00:00:00,000", "end_time": "00:00:10,000", "text": "test"}]
        result = analyzer._extract_and_parse_json(valid_json, "part01", dummy_entries)
        
        print(f"✅ Standard parsing worked: {result.get('video_part', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Standard parsing failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running AI JSON parsing tests...")
    print("=" * 60)
    
    # Run tests
    standard_test = test_standard_json_parsing()
    print()
    ai_test = test_ai_json_fixing()
    
    print()
    print("=" * 60)
    if standard_test and ai_test:
        print("🎉 All AI JSON parsing tests passed!")
        print("✅ The system can now handle malformed JSON using AI!")
        sys.exit(0)
    else:
        print("❌ Some AI JSON parsing tests failed!")
        sys.exit(1)