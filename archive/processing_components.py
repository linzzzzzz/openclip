#!/usr/bin/env python3
"""
DEPRECATED: This module has been refactored.
All classes have been moved to video_utils.py for better organization.

This file now serves as a compatibility layer for existing code.
Please update your imports to use video_utils instead:
  
  OLD: from processing_components import ProcessingResult, ResultsFormatter
  NEW: from video_utils import ProcessingResult, ResultsFormatter
"""

import warnings

# Import everything from video_utils for backward compatibility
from video_utils import (
    ProcessingResult,
    ResultsFormatter
)

# Show deprecation warning when this module is imported
warnings.warn(
    "processing_components.py is deprecated. Please import from video_utils instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['ProcessingResult', 'ResultsFormatter']
