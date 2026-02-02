#!/usr/bin/env python3
"""
Cover Image Generator - Create video cover images with styled text overlays
"""
import logging
from pathlib import Path
from typing import Tuple
import os

from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logger = logging.getLogger(__name__)


class CoverImageGenerator:
    """Generate cover images with styled text overlays from video frames"""
    
    def __init__(self):
        self.font_path = self._find_chinese_font()
    
    def _find_chinese_font(self):
        """Find available Chinese font (prefer bold variants)"""
        fonts = [
            # Bold variants first
            "/System/Library/Fonts/PingFang.ttc",  # Has bold weight
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "C:/Windows/Fonts/msyhbd.ttc",  # Microsoft YaHei Bold
            "C:/Windows/Fonts/simhei.ttf",  # SimHei (bold)
            # Regular variants as fallback
            "/System/Library/Fonts/STHeiti Light.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        
        for font_path in fonts:
            if os.path.exists(font_path):
                return font_path
        return None
    
    def generate_cover(self,
                      video_path: str,
                      title_text: str,
                      output_path: str,
                      frame_time: float = 5.0,
                      generate_vertical: bool = True) -> bool:
        """
        Generate cover image from video frame with styled text overlay
        
        Args:
            video_path: Path to video file
            title_text: Title text (large, red with outline)
            output_path: Path to save cover image
            frame_time: Time in seconds to extract frame (default: 5.0)
            generate_vertical: Also generate vertical 3:4 cover (default: True)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🖼️  Generating cover image from: {Path(video_path).name}")
            
            # Extract frame from video
            video = VideoFileClip(video_path)
            
            # Use specified time or middle of video
            extract_time = min(frame_time, video.duration / 2)
            frame = video.get_frame(extract_time)
            video.close()
            
            # Convert to PIL Image
            img = Image.fromarray(frame)
            
            # Generate horizontal cover (original aspect ratio) with 70% width
            img_horizontal = img.copy()  # Create a copy for horizontal cover
            img_with_text = self._add_text_overlay(img_horizontal, title_text, max_width_ratio=0.7)
            img_with_text.save(output_path, quality=95)
            logger.info(f"✓ Cover saved: {Path(output_path).name}")
            
            # Generate vertical 3:4 cover if requested (use original clean img) with 80% width
            if generate_vertical:
                vertical_output_path = output_path.replace('.jpg', '_vertical.jpg')
                img_vertical = self._create_vertical_cover(img, title_text)
                img_vertical.save(vertical_output_path, quality=95)
                logger.info(f"✓ Vertical cover saved: {Path(vertical_output_path).name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating cover: {e}")
            return False
    
    def _create_vertical_cover(self, img: Image.Image, title_text: str) -> Image.Image:
        """Create vertical 3:4 aspect ratio cover"""
        original_width, original_height = img.size
        
        # Calculate 3:4 dimensions (portrait)
        target_aspect = 3 / 4
        target_width = int(original_height * target_aspect)
        
        # Crop to center 3:4 portion
        if target_width < original_width:
            # Crop horizontally (center crop)
            left = (original_width - target_width) // 2
            right = left + target_width
            img_cropped = img.crop((left, 0, right, original_height))
        else:
            # If video is already narrower than 3:4, use as is
            img_cropped = img
        
        # Add text overlay with 80% width for vertical covers
        img_with_text = self._add_text_overlay(img_cropped, title_text, max_width_ratio=0.8)
        
        return img_with_text
    
    def _add_text_overlay(self, img: Image.Image, title_text: str, max_width_ratio: float = 0.6) -> Image.Image:
        """Add styled text overlay to image (single title only with text wrapping)
        
        Args:
            img: Image to add text to
            title_text: Text to overlay
            max_width_ratio: Ratio of image width to use for text (default: 0.6)
        """
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Start with initial font size
        title_font_size = int(height * 0.10)  # ~10% of height
        max_width = int(width * max_width_ratio)  # Use specified ratio of image width
        
        # Dynamically adjust font size to fit in at most 2 lines
        title_font = self._get_font_for_max_lines(title_text, title_font_size, max_width, draw, max_lines=2)
        
        # Wrap text with the adjusted font
        wrapped_lines = self._wrap_text(title_text, title_font, max_width, draw)
        
        # Calculate total height of text block
        line_height = title_font.size + 10
        total_text_height = len(wrapped_lines) * line_height
        
        # Position text in upper portion (centered vertically for the text block)
        start_y = int(height * 0.5)
        
        # Draw each line
        for i, line in enumerate(wrapped_lines):
            line_y = start_y + (i * line_height)
            
            # Draw line (yellow with black outline)
            self._draw_outlined_text(
                draw, line, title_font,
                width // 2, line_y,
                fill_color=(255, 220, 0),  # Yellow
                outline_color=(0, 0, 0),
                outline_width=8  # Increased from 6 to 8 for bolder text
            )
        
        return img
    
    def _get_font_for_max_lines(self, text: str, initial_size: int, max_width: int, 
                                draw: ImageDraw.Draw, max_lines: int = 2) -> ImageFont.FreeTypeFont:
        """Dynamically adjust font size to fit text in at most max_lines"""
        font_size = initial_size
        min_font_size = int(initial_size * 0.4)  # Don't go below 40% of initial size
        
        while font_size >= min_font_size:
            # Try current font size
            try:
                if self.font_path:
                    test_font = ImageFont.truetype(self.font_path, font_size)
                else:
                    test_font = ImageFont.load_default()
            except:
                test_font = ImageFont.load_default()
            
            # Check how many lines this would create
            wrapped_lines = self._wrap_text(text, test_font, max_width, draw)
            
            if len(wrapped_lines) <= max_lines:
                # Found a size that fits!
                return test_font
            
            # Try smaller font
            font_size -= 2
        
        # If we couldn't fit in max_lines, return the smallest font we tried
        try:
            if self.font_path:
                return ImageFont.truetype(self.font_path, min_font_size)
            else:
                return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw) -> list:
        """Wrap text to fit within max_width (handles Chinese text without spaces)"""
        lines = []
        
        # Check if text has spaces (English) or not (Chinese)
        has_spaces = ' ' in text
        
        if has_spaces:
            # English text - split by words
            words = text.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]
                
                if test_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
        else:
            # Chinese text - split by characters
            current_line = ""
            
            for char in text:
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]
                
                if test_width <= max_width:
                    current_line += char
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = char
                    else:
                        lines.append(char)
            
            if current_line:
                lines.append(current_line)
        
        return lines if lines else [text]
    
    def _draw_outlined_text(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                           x: int, y: int, fill_color: Tuple[int, int, int],
                           outline_color: Tuple[int, int, int], outline_width: int):
        """Draw text with outline effect"""
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = x - text_width // 2
        
        # Draw outline
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    draw.text((text_x + dx, y + dy), text, font=font, fill=outline_color)
        
        # Draw main text with multiple offsets for extra thickness (2px spread)
        for offset_x in [0, 1, 2]:
            for offset_y in [0, 1, 2]:
                if offset_x == 2 and offset_y == 2:
                    continue  # Skip the far diagonal to keep it at 8 draws
                draw.text((text_x + offset_x, y + offset_y), text, font=font, fill=fill_color)
