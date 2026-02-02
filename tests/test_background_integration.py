#!/usr/bin/env python3
"""
Test script to verify background information integration
"""

import os
from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

def test_background_integration():
    """Test that background information is properly loaded and integrated"""
    
    print("=" * 60)
    print("Testing Background Information Integration")
    print("=" * 60)
    
    # Use a dummy API key for testing (we won't make actual API calls)
    dummy_api_key = os.getenv("QWEN_API_KEY", "test_key_for_initialization")
    
    # Test 1: Without background
    print("\n1. Testing WITHOUT background information:")
    analyzer1 = EngagingMomentsAnalyzer(api_key=dummy_api_key, use_background=False)
    print(f"   use_background: {analyzer1.use_background}")
    print(f"   background_content: {analyzer1.background_content}")
    
    # Test 2: With background
    print("\n2. Testing WITH background information:")
    analyzer2 = EngagingMomentsAnalyzer(api_key=dummy_api_key, use_background=True)
    print(f"   use_background: {analyzer2.use_background}")
    print(f"   has_content: {analyzer2.background_content is not None}")
    
    if analyzer2.background_content:
        lines = analyzer2.background_content.split('\n')
        print(f"   content lines: {len(lines)}")
        print(f"   first line: {lines[0]}")
        print(f"   preview (first 150 chars): {analyzer2.background_content[:150]}...")
    
    print("\n" + "=" * 60)
    print("✅ Background integration test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_background_integration()
