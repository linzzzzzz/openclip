#!/usr/bin/env python3
"""
Title Adder - Add artistic titles to video clips
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

logger = logging.getLogger(__name__)


class ArtisticTextRenderer:
    """Artistic text renderer for Chinese and other languages"""
    
    def __init__(self):
        self.font_path = self._find_chinese_font()
        self.font_cache = {}
    
    def _find_chinese_font(self):
        """Find available Chinese font"""
        fonts = [
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in fonts:
            if os.path.exists(font_path):
                return font_path
        return None
    
    def _get_font(self, font_size):
        """Get cached font"""
        if font_size not in self.font_cache:
            if self.font_path:
                try:
                    self.font_cache[font_size] = ImageFont.truetype(self.font_path, font_size)
                except:
                    self.font_cache[font_size] = ImageFont.load_default()
            else:
                self.font_cache[font_size] = ImageFont.load_default()
        return self.font_cache[font_size]
    
    def create_artistic_text(self, text, font_size=35, style='gradient_3d'):
        """Create artistic text image"""
        font = self._get_font(font_size)
        
        # Calculate text size
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Create canvas
        margin = 30
        img_width = text_width + margin * 2
        img_height = text_height + margin * 2
        
        x_pos = margin
        y_pos = margin
        
        # Render based on style
        style_methods = {
            'gradient_3d': self._create_gradient_3d,
            'neon_glow': self._create_neon_glow,
            'metallic_gold': self._create_metallic_gold,
            'rainbow_3d': self._create_rainbow_3d,
            'crystal_ice': self._create_crystal_ice,
            'fire_flame': self._create_fire_flame,
            'metallic_silver': self._create_metallic_silver,
            'glowing_plasma': self._create_glowing_plasma,
            'stone_carved': self._create_stone_carved,
            'glass_transparent': self._create_glass_transparent,
        }
        
        method = style_methods.get(style, self._create_gradient_3d)
        return method(text, font, img_width, img_height, x_pos, y_pos)
    
    def _create_gradient_3d(self, text, font, img_width, img_height, x_pos, y_pos):
        """Gradient 3D effect"""
        # Shadow layer
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        for depth in range(4, 0, -1):
            shadow_alpha = max(50 - depth * 8, 20)
            shadow_draw.text((x_pos + depth, y_pos + depth), text,
                           font=font, fill=(0, 0, 0, shadow_alpha))
        
        # Gradient using NumPy
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        x_gradient = np.linspace(0, 1, img_width)
        
        gradient_array[:, :, 0] = (255 * (1 - x_gradient) + 100 * x_gradient).astype(np.uint8)
        gradient_array[:, :, 1] = (100 * (1 - x_gradient) + 150 * x_gradient).astype(np.uint8)
        gradient_array[:, :, 2] = (150 * (1 - x_gradient) + 255 * x_gradient).astype(np.uint8)
        gradient_array[:, :, 3] = 255
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # Text mask
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        final_img = Image.alpha_composite(shadow_img, gradient_img)
        
        return np.array(final_img)
    
    def _create_neon_glow(self, text, font, img_width, img_height, x_pos, y_pos):
        """Neon glow effect"""
        glow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        
        glow_layers = [
            (4, (0, 255, 255, 40)),
            (2, (0, 255, 255, 120)),
            (0, (0, 255, 255, 255))
        ]
        
        for size, color in glow_layers:
            layer_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer_img)
            
            if size > 0:
                for dx in range(-size, size + 1, 2):
                    for dy in range(-size, size + 1, 2):
                        if dx*dx + dy*dy <= size*size:
                            layer_draw.text((x_pos + dx, y_pos + dy), text, font=font, fill=color)
                layer_img = layer_img.filter(ImageFilter.GaussianBlur(size/2))
            else:
                layer_draw.text((x_pos, y_pos), text, font=font, fill=color)
            
            glow_img = Image.alpha_composite(glow_img, layer_img)
        
        return np.array(glow_img)
    
    def _create_metallic_gold(self, text, font, img_width, img_height, x_pos, y_pos):
        """Metallic gold effect"""
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        y_gradient = np.linspace(0.8, 1.0, img_height).reshape(-1, 1)
        
        gradient_array[:, :, 0] = (255 * y_gradient).astype(np.uint8)
        gradient_array[:, :, 1] = (215 * y_gradient).astype(np.uint8)
        gradient_array[:, :, 2] = 0
        gradient_array[:, :, 3] = 255
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-1, y_pos-1), text, font=font, fill=(255, 255, 200, 180))
        
        final_img = Image.alpha_composite(gradient_img, highlight_img)
        return np.array(final_img)
    
    def _create_rainbow_3d(self, text, font, img_width, img_height, x_pos, y_pos):
        """Rainbow 3D effect"""
        import colorsys
        
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        for depth in range(3, 0, -1):
            shadow_alpha = max(60 - depth * 15, 30)
            shadow_draw.text((x_pos + depth, y_pos + depth), text,
                           font=font, fill=(0, 0, 0, shadow_alpha))
        
        rainbow_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        
        for x in range(img_width):
            hue = (x / img_width) * 0.8
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            rainbow_array[:, x, 0] = int(rgb[0] * 255)
            rainbow_array[:, x, 1] = int(rgb[1] * 255)
            rainbow_array[:, x, 2] = int(rgb[2] * 255)
            rainbow_array[:, x, 3] = 255
        
        rainbow_img = Image.fromarray(rainbow_array, 'RGBA')
        
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        rainbow_img.putalpha(text_mask)
        final_img = Image.alpha_composite(shadow_img, rainbow_img)
        
        return np.array(final_img)
    
    def _create_crystal_ice(self, text, font, img_width, img_height, x_pos, y_pos):
        """Crystal ice effect"""
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        x_gradient = np.linspace(0, 1, img_width)
        y_gradient = np.linspace(0, 1, img_height).reshape(-1, 1)
        
        gradient_array[:, :, 0] = (200 + 55 * x_gradient).astype(np.uint8)
        gradient_array[:, :, 1] = (230 + 25 * y_gradient).astype(np.uint8)
        gradient_array[:, :, 2] = 255
        gradient_array[:, :, 3] = 255
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-2, y_pos-2), text, font=font, fill=(255, 255, 255, 120))
        
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text((x_pos+2, y_pos+2), text, font=font, fill=(0, 50, 100, 150))
        
        final_img = Image.alpha_composite(shadow_img, gradient_img)
        final_img = Image.alpha_composite(final_img, highlight_img)
        
        return np.array(final_img)
    
    def _create_fire_flame(self, text, font, img_width, img_height, x_pos, y_pos):
        """Fire flame effect"""
        # Create flame gradient using NumPy
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        y_gradient = np.linspace(0, 1, img_height).reshape(-1, 1)
        
        gradient_array[:, :, 0] = 255  # R
        gradient_array[:, :, 1] = (255 * (1 - y_gradient * 0.7)).astype(np.uint8)  # G
        gradient_array[:, :, 2] = (50 * (1 - y_gradient)).astype(np.uint8)  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # Text mask
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # Add glow effect
        glow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        
        for size in [3, 1]:
            alpha = 40 + size * 20
            for dx in range(-size, size + 1, 2):
                for dy in range(-size, size + 1, 2):
                    if dx*dx + dy*dy <= size*size:
                        glow_draw.text((x_pos + dx, y_pos + dy), text, font=font, fill=(255, 100, 0, alpha))
        
        final_img = Image.alpha_composite(glow_img, gradient_img)
        return np.array(final_img)
    
    def _create_metallic_silver(self, text, font, img_width, img_height, x_pos, y_pos):
        """Metallic silver effect"""
        # Create silver gradient using NumPy
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        y_gradient = np.linspace(0, 1, img_height).reshape(-1, 1)
        
        base_color = (180 + 75 * (0.5 + 0.5 * np.sin(y_gradient * np.pi * 2))).astype(np.uint8)
        gradient_array[:, :, 0] = base_color  # R
        gradient_array[:, :, 1] = base_color  # G
        gradient_array[:, :, 2] = base_color  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # Text mask
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # Add highlights and shadows
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-1, y_pos-1), text, font=font, fill=(255, 255, 255, 180))
        
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text((x_pos+2, y_pos+2), text, font=font, fill=(80, 80, 80, 120))
        
        final_img = Image.alpha_composite(shadow_img, gradient_img)
        final_img = Image.alpha_composite(final_img, highlight_img)
        
        return np.array(final_img)
    
    def _create_glowing_plasma(self, text, font, img_width, img_height, x_pos, y_pos):
        """Glowing plasma effect"""
        # Create plasma gradient using NumPy
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        
        x_coords = np.arange(img_width)
        y_coords = np.arange(img_height).reshape(-1, 1)
        
        wave1 = np.sin(x_coords * 0.1) * 0.5 + 0.5
        wave2 = np.cos(y_coords * 0.1) * 0.5 + 0.5
        combined = (wave1 + wave2) / 2
        
        gradient_array[:, :, 0] = (150 + 105 * combined).astype(np.uint8)  # R
        gradient_array[:, :, 1] = (50 + 100 * (1 - combined)).astype(np.uint8)  # G
        gradient_array[:, :, 2] = (200 + 55 * combined).astype(np.uint8)  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # Text mask
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # Add outer glow
        glow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        
        glow_layers = [(4, (255, 0, 255, 30)), (2, (200, 50, 255, 60))]
        
        for size, color in glow_layers:
            for dx in range(-size, size + 1, 2):
                for dy in range(-size, size + 1, 2):
                    if dx*dx + dy*dy <= size*size:
                        glow_draw.text((x_pos + dx, y_pos + dy), text, font=font, fill=color)
        
        final_img = Image.alpha_composite(glow_img, gradient_img)
        return np.array(final_img)
    
    def _create_stone_carved(self, text, font, img_width, img_height, x_pos, y_pos):
        """Stone carved effect"""
        # Create stone texture using NumPy
        np.random.seed(42)
        noise = np.random.uniform(0.8, 1.2, (img_height, img_width))
        
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        base_gray = (120 * noise).astype(np.uint8)
        
        gradient_array[:, :, 0] = base_gray  # R
        gradient_array[:, :, 1] = base_gray  # G
        gradient_array[:, :, 2] = base_gray  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # Text mask
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # Add carved shadow
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text((x_pos+1, y_pos+1), text, font=font, fill=(50, 50, 50, 180))
        shadow_draw.text((x_pos+2, y_pos+2), text, font=font, fill=(30, 30, 30, 120))
        
        # Add highlight
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-1, y_pos-1), text, font=font, fill=(180, 180, 180, 100))
        
        final_img = Image.alpha_composite(shadow_img, gradient_img)
        final_img = Image.alpha_composite(final_img, highlight_img)
        
        return np.array(final_img)
    
    def _create_glass_transparent(self, text, font, img_width, img_height, x_pos, y_pos):
        """Glass transparent effect"""
        # Create transparent glass using NumPy
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        gradient_array[:, :, 0] = 200  # R
        gradient_array[:, :, 1] = 220  # G
        gradient_array[:, :, 2] = 255  # B
        gradient_array[:, :, 3] = 120  # A (semi-transparent)
        
        glass_img = Image.fromarray(gradient_array, 'RGBA')
        
        # Text mask
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        glass_img.putalpha(text_mask)
        
        # Add glass highlight
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-2, y_pos-2), text, font=font, fill=(255, 255, 255, 200))
        
        # Add border effect
        outline_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline_img)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            outline_draw.text((x_pos + dx, y_pos + dy), text,
                            font=font, fill=(100, 150, 200, 180))
        
        final_img = Image.alpha_composite(outline_img, glass_img)
        final_img = Image.alpha_composite(final_img, highlight_img)
        
        return np.array(final_img)


class TitleAdder:
    """Add artistic titles to video clips"""
    
    def __init__(self, output_dir: str = "engaging_clips_with_titles"):
        """
        Initialize title adder
        
        Args:
            output_dir: Directory to save videos with titles
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.renderer = ArtisticTextRenderer()
        logger.info(f"📁 Title output directory: {self.output_dir}")
    
    def add_titles_to_clips(self,
                           clips_dir: str,
                           analysis_file: str,
                           title_style: str = 'crystal_ice') -> Dict[str, Any]:
        """
        Add titles to generated clips
        
        Args:
            clips_dir: Directory containing clips without titles
            analysis_file: Path to top_engaging_moments.json
            title_style: Style for artistic text rendering
            
        Returns:
            Dictionary with processing results
        """
        try:
            clips_dir = Path(clips_dir)
            
            if not clips_dir.exists():
                raise FileNotFoundError(f"Clips directory not found: {clips_dir}")
            
            # Load analysis data
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info("🎨 Adding artistic titles to clips")
            logger.info(f"🎨 Style: {title_style}")
            logger.info(f"📁 Output: {self.output_dir}")
            
            successful_count = 0
            processed_clips = []
            
            # Process each engaging moment
            for moment in data['top_engaging_moments']:
                rank = moment['rank']
                title = moment['title']
                
                # Find input clip
                safe_title = self._sanitize_filename(title)
                input_filename = f"rank_{rank:02d}_{safe_title}.mp4"
                input_path = clips_dir / input_filename
                
                if not input_path.exists():
                    logger.warning(f"✗ Clip not found: {input_filename}")
                    continue
                
                # Create output filename
                output_filename = f"artistic_{title_style}_rank_{rank:02d}_{safe_title}.mp4"
                output_path = self.output_dir / output_filename
                
                logger.info(f"[{rank}] Processing: {title}")
                
                # Add title overlay
                success = self._add_artistic_title(
                    str(input_path),
                    title,
                    str(output_path),
                    title_style
                )
                
                if success:
                    successful_count += 1
                    processed_clips.append({
                        'rank': rank,
                        'title': title,
                        'filename': output_filename
                    })
                    logger.info(f"✓ Saved: {output_filename}")
                else:
                    logger.error(f"✗ Failed: {output_filename}")
            
            # Create README
            if processed_clips:
                self._create_readme(processed_clips, data, title_style)
            
            result = {
                'success': successful_count > 0,
                'total_clips': len(data['top_engaging_moments']),
                'successful_clips': successful_count,
                'processed_clips': processed_clips,
                'output_dir': str(self.output_dir),
                'title_style': title_style
            }
            
            logger.info(f"🎯 Added titles to {successful_count}/{len(data['top_engaging_moments'])} clips")
            return result
            
        except Exception as e:
            logger.error(f"Error adding titles: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_clips': 0,
                'successful_clips': 0,
                'processed_clips': []
            }
    
    def _sanitize_filename(self, title: str) -> str:
        """Clean title for filename"""
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'[\s\-]+', '_', title)
        title = re.sub(r'_+', '_', title)
        return title.strip('_')
    
    def _add_artistic_title(self, input_video: str, title: str,
                           output_video: str, title_style: str) -> bool:
        """Add artistic title overlay to video"""
        try:
            video = VideoFileClip(input_video)
            
            # Calculate dimensions
            original_width = video.w
            original_height = video.h
            top_bar_height = 120
            bottom_bar_height = 60
            new_height = original_height + top_bar_height + bottom_bar_height
            
            # Create black background
            black_bg = ColorClip(
                size=(original_width, new_height),
                color=(0, 0, 0),
                duration=video.duration
            )
            
            # Position video
            video_positioned = video.with_position(('center', top_bar_height))
            
            # Create artistic text
            artistic_img = self.renderer.create_artistic_text(
                title,
                font_size=40,
                style=title_style
            )
            
            # Position title
            title_y_position = (top_bar_height - artistic_img.shape[0]) // 2
            artistic_clip = ImageClip(artistic_img, duration=video.duration).with_position(
                ('center', title_y_position)
            )
            
            # Composite
            final_video = CompositeVideoClip([black_bg, video_positioned, artistic_clip])
            
            # Write output
            final_video.write_videofile(
                output_video,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='ultrafast',
                threads=4,
                logger=None  # Suppress moviepy logs
            )
            
            # Cleanup
            video.close()
            final_video.close()
            artistic_clip.close()
            black_bg.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding title: {e}")
            return False
    
    def _create_readme(self, processed_clips: List[Dict], data: Dict, title_style: str):
        """Create README for titled clips"""
        readme_path = self.output_dir / "README.md"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🎬 Engaging Clips with Artistic Titles\n\n")
            f.write(f"**Artistic Style**: {title_style}\n")
            f.write(f"**Total Clips**: {len(processed_clips)}\n\n")
            
            f.write("## 🎨 Artistic Style\n\n")
            f.write(f"All clips use the **{title_style}** artistic text effect.\n\n")
            
            f.write("## 📝 Clips List\n\n")
            f.write("| Rank | Title | Filename |\n")
            f.write("|------|-------|----------|\n")
            
            for clip in processed_clips:
                f.write(f"| {clip['rank']} | {clip['title']} | `{clip['filename']}` |\n")
        
        logger.info(f"📄 README created: {readme_path}")
