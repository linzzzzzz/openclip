#!/usr/bin/env python3
"""
Test script to verify debug response export functionality
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from core.engaging_moments_analyzer import EngagingMomentsAnalyzer

def test_debug_export():
    """Test that failed responses are exported correctly"""
    
    print("🧪 Testing debug response export...")
    print()
    
    # Initialize analyzer
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    # Create a temporary directory for testing
    original_cwd = Path.cwd()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        temp_path = Path(temp_dir)
        import os
        os.chdir(temp_path)
        
        try:
            # Test export functionality
            raw_response = "This is a malformed JSON response that should be exported"
            fixed_response = "This is the AI-fixed response that also failed"
            test_error = Exception("Test parsing error")
            
            # Call the export method
            analyzer._export_failed_responses(raw_response, "part01", fixed_response, test_error)
            
            # Check if debug directory was created
            debug_dir = temp_path / "debug_responses"
            if not debug_dir.exists():
                print("❌ Debug directory was not created")
                return False
            
            # Check if files were created
            raw_files = list(debug_dir.glob("part01_raw_response_*.txt"))
            fixed_files = list(debug_dir.glob("part01_ai_fixed_response_*.txt"))
            
            if not raw_files:
                print("❌ Raw response file was not created")
                return False
            
            if not fixed_files:
                print("❌ AI-fixed response file was not created")
                return False
            
            # Check file contents
            with open(raw_files[0], 'r', encoding='utf-8') as f:
                raw_content = f.read()
                if raw_response not in raw_content:
                    print("❌ Raw response content not found in file")
                    return False
            
            with open(fixed_files[0], 'r', encoding='utf-8') as f:
                fixed_content = f.read()
                if fixed_response not in fixed_content:
                    print("❌ Fixed response content not found in file")
                    return False
            
            print("✅ Debug export functionality works correctly")
            print(f"   Created files: {len(raw_files)} raw, {len(fixed_files)} fixed")
            return True
            
        finally:
            # Change back to original directory
            os.chdir(original_cwd)

def test_aggregation_debug_export():
    """Test that failed aggregation responses are exported correctly"""
    
    print("🧪 Testing aggregation debug response export...")
    print()
    
    analyzer = EngagingMomentsAnalyzer("dummy_key_for_testing")
    
    # Create a temporary directory for testing
    original_cwd = Path.cwd()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        import os
        os.chdir(temp_path)
        
        try:
            # Test aggregation export functionality
            raw_response = "This is a malformed aggregation JSON response"
            fixed_response = "This is the AI-fixed aggregation response that also failed"
            test_error = Exception("Test aggregation parsing error")
            
            # Call the export method
            analyzer._export_failed_aggregation_responses(raw_response, fixed_response, test_error)
            
            # Check if debug directory was created
            debug_dir = temp_path / "debug_responses"
            if not debug_dir.exists():
                print("❌ Debug directory was not created")
                return False
            
            # Check if files were created
            raw_files = list(debug_dir.glob("aggregation_raw_response_*.txt"))
            fixed_files = list(debug_dir.glob("aggregation_ai_fixed_response_*.txt"))
            
            if not raw_files:
                print("❌ Aggregation raw response file was not created")
                return False
            
            if not fixed_files:
                print("❌ Aggregation AI-fixed response file was not created")
                return False
            
            print("✅ Aggregation debug export functionality works correctly")
            print(f"   Created files: {len(raw_files)} raw, {len(fixed_files)} fixed")
            return True
            
        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    print("🚀 Running debug export tests...")
    print("=" * 60)
    
    # Run tests
    part_test = test_debug_export()
    print()
    agg_test = test_aggregation_debug_export()
    
    print()
    print("=" * 60)
    if part_test and agg_test:
        print("🎉 All debug export tests passed!")
        print("✅ Failed responses will now be exported for debugging!")
        sys.exit(0)
    else:
        print("❌ Some debug export tests failed!")
        sys.exit(1)