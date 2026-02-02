#!/usr/bin/env python3
"""
Test script to verify prompt loading functionality
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

def test_prompt_loading():
    """Test that prompts can be loaded correctly"""
    
    print("🧪 Testing prompt loading functionality...")
    print()
    
    # Initialize analyzer with a dummy API key for testing
    try:
        analyzer = EngagingMomentsAnalyzer("dummy_api_key_for_testing")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    try:
        # Test loading part requirement prompt
        part_prompt = analyzer.load_prompt_template("engaging_moments_part_requirement")
        print("✅ Successfully loaded part requirement prompt")
        print(f"📝 Part prompt length: {len(part_prompt)} characters")
        print(f"📄 First 100 characters: {part_prompt[:100]}...")
        print()
        
        # Test loading aggregation requirement prompt
        agg_prompt = analyzer.load_prompt_template("engaging_moments_agg_requirement")
        print("✅ Successfully loaded aggregation requirement prompt")
        print(f"📝 Aggregation prompt length: {len(agg_prompt)} characters")
        print(f"📄 First 100 characters: {agg_prompt[:100]}...")
        print()
        
        # Test that prompts contain expected content
        assert "engaging moments" in part_prompt.lower(), "Part prompt should contain 'engaging moments'"
        assert "json" in part_prompt.lower(), "Part prompt should mention JSON format"
        assert "top 5" in agg_prompt.lower(), "Aggregation prompt should mention 'top 5'"
        assert "rank" in agg_prompt.lower(), "Aggregation prompt should mention ranking"
        
        print("✅ Content validation passed")
        print("🎉 All prompt loading tests passed!")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Prompt file not found: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Content validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading prompts: {e}")
        return False

def test_prompt_file_structure():
    """Test that prompt files exist and have proper structure"""
    
    print("🧪 Testing prompt file structure...")
    print()
    
    prompts_dir = Path("prompts")
    
    # Check if prompts directory exists
    if not prompts_dir.exists():
        print("❌ Prompts directory does not exist")
        return False
    
    # Check required prompt files
    required_files = [
        "engaging_moments_part_requirement.md",
        "engaging_moments_agg_requirement.md"
    ]
    
    for filename in required_files:
        file_path = prompts_dir / filename
        if not file_path.exists():
            print(f"❌ Required prompt file missing: {filename}")
            return False
        
        # Check file is not empty
        content = file_path.read_text(encoding='utf-8')
        if len(content.strip()) == 0:
            print(f"❌ Prompt file is empty: {filename}")
            return False
        
        print(f"✅ Found and validated: {filename}")
    
    print("🎉 Prompt file structure tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Running prompt loading tests...")
    print("=" * 50)
    
    # Run tests
    structure_test = test_prompt_file_structure()
    print()
    loading_test = test_prompt_loading()
    
    print()
    print("=" * 50)
    if structure_test and loading_test:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)