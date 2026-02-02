#!/usr/bin/env python3
"""
Test script to verify improved JSON parsing functionality
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

def test_json_extraction():
    """Test the improved JSON extraction methods"""
    
    print("🧪 Testing improved JSON extraction...")
    print()
    
    # Initialize analyzer
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    # Test cases with different JSON formats
    test_cases = [
        {
            "name": "Clean JSON",
            "response": '{"video_part": "part01", "engaging_moments": [], "total_moments": 0}',
            "should_work": True
        },
        {
            "name": "JSON with markdown code block",
            "response": '''Here's the analysis:

```json
{
  "video_part": "part01",
  "engaging_moments": [],
  "total_moments": 0
}
```

That's the result.''',
            "should_work": True
        },
        {
            "name": "JSON with trailing comma",
            "response": '{"video_part": "part01", "engaging_moments": [], "total_moments": 0,}',
            "should_work": True
        },
        {
            "name": "JSON wrapped in text",
            "response": '''Based on the analysis, here is the result:

{
  "video_part": "part01",
  "engaging_moments": [],
  "total_moments": 0
}

This completes the analysis.''',
            "should_work": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        
        try:
            # Create dummy entries for validation
            dummy_entries = [{"start_time": "00:00:00,000", "end_time": "00:00:10,000", "text": "test"}]
            
            result = analyzer._extract_and_parse_json(test_case['response'], "part01", dummy_entries)
            
            if test_case['should_work']:
                print(f"  ✅ Successfully parsed: {result.get('video_part', 'unknown')}")
                passed += 1
            else:
                print(f"  ❌ Should have failed but didn't")
                failed += 1
                
        except Exception as e:
            if test_case['should_work']:
                print(f"  ❌ Failed to parse: {e}")
                failed += 1
            else:
                print(f"  ✅ Correctly failed: {e}")
                passed += 1
        
        print()
    
    print(f"🎯 Results: {passed} passed, {failed} failed")
    return failed == 0

def test_json_cleaning():
    """Test the JSON cleaning functionality"""
    
    print("🧪 Testing JSON cleaning...")
    print()
    
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    test_cases = [
        {
            "input": '```json\n{"test": "value"}\n```',
            "expected_contains": '"test": "value"',
            "name": "Remove markdown markers"
        },
        {
            "input": '{"test": "value",}',
            "expected_contains": '"test": "value"}',
            "name": "Remove trailing comma"
        },
        {
            "input": '  \n  {"test": "value"}  \n  ',
            "expected_contains": '{"test": "value"}',
            "name": "Trim whitespace"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        
        try:
            result = analyzer._clean_json_text(test_case['input'])
            
            if test_case['expected_contains'] in result:
                print(f"  ✅ Correctly cleaned")
                passed += 1
            else:
                print(f"  ❌ Cleaning failed")
                print(f"    Input: {repr(test_case['input'])}")
                print(f"    Output: {repr(result)}")
                print(f"    Expected to contain: {repr(test_case['expected_contains'])}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error during cleaning: {e}")
            failed += 1
        
        print()
    
    print(f"🎯 Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("🚀 Running JSON parsing tests...")
    print("=" * 60)
    
    # Run tests
    extraction_test = test_json_extraction()
    print()
    cleaning_test = test_json_cleaning()
    
    print()
    print("=" * 60)
    if extraction_test and cleaning_test:
        print("🎉 All JSON parsing tests passed!")
        print("✅ The improved parsing should handle malformed JSON better!")
        sys.exit(0)
    else:
        print("❌ Some JSON parsing tests failed!")
        sys.exit(1)