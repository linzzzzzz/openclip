#!/usr/bin/env python3
"""
Test script to verify timestamp cleaning functionality
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

def test_timestamp_cleaning():
    """Test that SRT timestamps are converted to simple format"""
    
    print("🧪 Testing timestamp cleaning...")
    print()
    
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    test_cases = [
        {
            "name": "SRT timestamp format",
            "input": '"start_time": "00:01:30,500"',
            "expected": '"start_time": "00:01:30"',
        },
        {
            "name": "Multiple SRT timestamps",
            "input": '"start_time": "00:01:30,500", "end_time": "00:02:45,123"',
            "expected_contains": ['"start_time": "00:01:30"', '"end_time": "00:02:45"'],
        },
        {
            "name": "JSON with SRT timestamps",
            "input": '''```json
{
  "start_time": "00:02:06,920",
  "end_time": "00:04:38,519"
}
```''',
            "expected_contains": ['"start_time": "00:02:06"', '"end_time": "00:04:38"'],
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        
        try:
            result = analyzer._clean_json_text(test_case['input'])
            
            if 'expected' in test_case:
                if test_case['expected'] in result:
                    print(f"  ✅ Correctly cleaned")
                    passed += 1
                else:
                    print(f"  ❌ Cleaning failed")
                    print(f"    Expected: {test_case['expected']}")
                    print(f"    Got: {result}")
                    failed += 1
            elif 'expected_contains' in test_case:
                all_found = all(expected in result for expected in test_case['expected_contains'])
                if all_found:
                    print(f"  ✅ Correctly cleaned")
                    passed += 1
                else:
                    print(f"  ❌ Cleaning failed")
                    print(f"    Expected to contain: {test_case['expected_contains']}")
                    print(f"    Got: {result}")
                    failed += 1
                
        except Exception as e:
            print(f"  ❌ Error during cleaning: {e}")
            failed += 1
        
        print()
    
    print(f"🎯 Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("🚀 Running timestamp cleaning tests...")
    print("=" * 50)
    
    success = test_timestamp_cleaning()
    
    print("=" * 50)
    if success:
        print("🎉 All timestamp cleaning tests passed!")
        sys.exit(0)
    else:
        print("❌ Some timestamp cleaning tests failed!")
        sys.exit(1)