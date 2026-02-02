#!/usr/bin/env python3
"""
Enhanced version with artistic Chinese text support
为 engaging clips 添加中文标题字幕 - 支持艺术字效果
Based on add_titles_engaging_clips.py but with artistic text options
"""
import json
import os
from pathlib import Path
from moviepy import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, ColorClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import argparse


class ArtisticTextRenderer:
    """艺术字渲染器"""
    
    def __init__(self):
        self.font_path = self._find_chinese_font()
        self.font_cache = {}  # Cache fonts to avoid reloading
    
    def _find_chinese_font(self):
        """查找中文字体"""
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
        """获取缓存的字体"""
        if font_size not in self.font_cache:
            if self.font_path:
                try:
                    self.font_cache[font_size] = ImageFont.truetype(self.font_path, font_size)
                except:
                    self.font_cache[font_size] = ImageFont.load_default()
            else:
                self.font_cache[font_size] = ImageFont.load_default()
        return self.font_cache[font_size]
    
    def create_gradient_text(self, text, font_size=35, style='gradient_3d'):
        """创建艺术字文本"""
        
        font = self._get_font(font_size)
        
        # 计算文字尺寸
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 创建画布
        margin = 30
        img_width = text_width + margin * 2
        img_height = text_height + margin * 2
        
        x_pos = margin
        y_pos = margin
        
        if style == 'gradient_3d':
            return self._create_gradient_3d(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'neon_glow':
            return self._create_neon_glow(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'metallic_gold':
            return self._create_metallic_gold(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'rainbow_3d':
            return self._create_rainbow_3d(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'crystal_ice':
            return self._create_crystal_ice(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'fire_flame':
            return self._create_fire_flame(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'metallic_silver':
            return self._create_metallic_silver(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'glowing_plasma':
            return self._create_glowing_plasma(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'stone_carved':
            return self._create_stone_carved(text, font, img_width, img_height, x_pos, y_pos)
        elif style == 'glass_transparent':
            return self._create_glass_transparent(text, font, img_width, img_height, x_pos, y_pos)
        else:
            return self._create_gradient_3d(text, font, img_width, img_height, x_pos, y_pos)
    
    def _create_gradient_3d(self, text, font, img_width, img_height, x_pos, y_pos):
        """渐变3D效果 - 优化版"""
        # 3D阴影层
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        # 简化阴影层数
        for depth in range(4, 0, -1):
            shadow_alpha = max(50 - depth * 8, 20)
            shadow_draw.text((x_pos + depth, y_pos + depth), text,
                           font=font, fill=(0, 0, 0, shadow_alpha))
        
        # 使用NumPy创建渐变 - 快速！
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        x_gradient = np.linspace(0, 1, img_width)
        
        gradient_array[:, :, 0] = (255 * (1 - x_gradient) + 100 * x_gradient).astype(np.uint8)  # R
        gradient_array[:, :, 1] = (100 * (1 - x_gradient) + 150 * x_gradient).astype(np.uint8)  # G
        gradient_array[:, :, 2] = (150 * (1 - x_gradient) + 255 * x_gradient).astype(np.uint8)  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 合成阴影和文字
        final_img = Image.alpha_composite(shadow_img, gradient_img)
        
        # 简化描边
        outline_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline_img)
        
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            outline_draw.text((x_pos + dx, y_pos + dy), text,
                            font=font, fill=(255, 255, 255, 150))
        
        final_img = Image.alpha_composite(outline_img, final_img)
        
        return np.array(final_img)
    
    def _create_neon_glow(self, text, font, img_width, img_height, x_pos, y_pos):
        """霓虹发光效果 - 优化版"""
        glow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        
        # 减少发光层数
        glow_layers = [
            (4, (0, 255, 255, 40)),
            (2, (0, 255, 255, 120)),
            (0, (0, 255, 255, 255))
        ]
        
        for size, color in glow_layers:
            layer_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer_img)
            
            if size > 0:
                for dx in range(-size, size + 1, 2):  # 步长2，减少迭代
                    for dy in range(-size, size + 1, 2):
                        if dx*dx + dy*dy <= size*size:
                            layer_draw.text((x_pos + dx, y_pos + dy), text, font=font, fill=color)
                layer_img = layer_img.filter(ImageFilter.GaussianBlur(size/2))
            else:
                layer_draw.text((x_pos, y_pos), text, font=font, fill=color)
            
            glow_img = Image.alpha_composite(glow_img, layer_img)
        
        return np.array(glow_img)
    
    def _create_metallic_gold(self, text, font, img_width, img_height, x_pos, y_pos):
        """金属质感效果 - 优化版"""
        # 使用NumPy创建金色渐变
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        y_gradient = np.linspace(0.8, 1.0, img_height).reshape(-1, 1)
        
        gradient_array[:, :, 0] = (255 * y_gradient).astype(np.uint8)  # R
        gradient_array[:, :, 1] = (215 * y_gradient).astype(np.uint8)  # G
        gradient_array[:, :, 2] = 0  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 添加高光
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-1, y_pos-1), text, font=font, fill=(255, 255, 200, 180))
        
        final_img = Image.alpha_composite(gradient_img, highlight_img)
        return np.array(final_img)
    
    def _create_rainbow_3d(self, text, font, img_width, img_height, x_pos, y_pos):
        """彩虹3D效果 - 优化版"""
        # 3D阴影
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        
        for depth in range(3, 0, -1):
            shadow_alpha = max(60 - depth * 15, 30)
            shadow_draw.text((x_pos + depth, y_pos + depth), text,
                           font=font, fill=(0, 0, 0, shadow_alpha))
        
        # 使用NumPy创建彩虹渐变
        import colorsys
        rainbow_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        
        for x in range(img_width):
            hue = (x / img_width) * 0.8
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            rainbow_array[:, x, 0] = int(rgb[0] * 255)
            rainbow_array[:, x, 1] = int(rgb[1] * 255)
            rainbow_array[:, x, 2] = int(rgb[2] * 255)
            rainbow_array[:, x, 3] = 255
        
        rainbow_img = Image.fromarray(rainbow_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        rainbow_img.putalpha(text_mask)
        
        final_img = Image.alpha_composite(shadow_img, rainbow_img)
        return np.array(final_img)
    
    def _create_crystal_ice(self, text, font, img_width, img_height, x_pos, y_pos):
        """水晶冰霜效果 - 优化版"""
        # 使用NumPy创建冰蓝色渐变
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        x_gradient = np.linspace(0, 1, img_width)
        y_gradient = np.linspace(0, 1, img_height).reshape(-1, 1)
        
        gradient_array[:, :, 0] = (200 + 55 * x_gradient).astype(np.uint8)  # R
        gradient_array[:, :, 1] = (230 + 25 * y_gradient).astype(np.uint8)  # G
        gradient_array[:, :, 2] = 255  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 添加高光和阴影
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
        """火焰效果 - 优化版"""
        # 使用NumPy创建火焰渐变
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        y_gradient = np.linspace(0, 1, img_height).reshape(-1, 1)
        
        gradient_array[:, :, 0] = 255  # R
        gradient_array[:, :, 1] = (255 * (1 - y_gradient * 0.7)).astype(np.uint8)  # G
        gradient_array[:, :, 2] = (50 * (1 - y_gradient)).astype(np.uint8)  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 简化发光效果
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
        """银色金属效果 - 优化版"""
        # 使用NumPy创建银色渐变
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        y_gradient = np.linspace(0, 1, img_height).reshape(-1, 1)
        
        base_color = (180 + 75 * (0.5 + 0.5 * np.sin(y_gradient * np.pi * 2))).astype(np.uint8)
        gradient_array[:, :, 0] = base_color  # R
        gradient_array[:, :, 1] = base_color  # G
        gradient_array[:, :, 2] = base_color  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 添加高光和阴影
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
        """发光等离子效果 - 优化版"""
        # 使用NumPy创建等离子渐变
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
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 简化外发光
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
        """石刻雕刻效果 - 优化版"""
        # 使用NumPy创建石质纹理
        np.random.seed(42)
        noise = np.random.uniform(0.8, 1.2, (img_height, img_width))
        
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        base_gray = (120 * noise).astype(np.uint8)
        
        gradient_array[:, :, 0] = base_gray  # R
        gradient_array[:, :, 1] = base_gray  # G
        gradient_array[:, :, 2] = base_gray  # B
        gradient_array[:, :, 3] = 255  # A
        
        gradient_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        gradient_img.putalpha(text_mask)
        
        # 添加凹陷阴影
        shadow_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text((x_pos+1, y_pos+1), text, font=font, fill=(50, 50, 50, 180))
        shadow_draw.text((x_pos+2, y_pos+2), text, font=font, fill=(30, 30, 30, 120))
        
        # 浅色高光
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-1, y_pos-1), text, font=font, fill=(180, 180, 180, 100))
        
        final_img = Image.alpha_composite(shadow_img, gradient_img)
        final_img = Image.alpha_composite(final_img, highlight_img)
        
        return np.array(final_img)
    
    def _create_glass_transparent(self, text, font, img_width, img_height, x_pos, y_pos):
        """玻璃透明效果 - 优化版"""
        # 使用NumPy创建透明玻璃
        gradient_array = np.zeros((img_height, img_width, 4), dtype=np.uint8)
        gradient_array[:, :, 0] = 200  # R
        gradient_array[:, :, 1] = 220  # G
        gradient_array[:, :, 2] = 255  # B
        gradient_array[:, :, 3] = 120  # A (半透明)
        
        glass_img = Image.fromarray(gradient_array, 'RGBA')
        
        # 文字掩码
        text_mask = Image.new('L', (img_width, img_height), 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text((x_pos, y_pos), text, font=font, fill=255)
        
        glass_img.putalpha(text_mask)
        
        # 添加玻璃高光
        highlight_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        highlight_draw = ImageDraw.Draw(highlight_img)
        highlight_draw.text((x_pos-2, y_pos-2), text, font=font, fill=(255, 255, 255, 200))
        
        # 边框效果
        outline_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline_img)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            outline_draw.text((x_pos + dx, y_pos + dy), text,
                            font=font, fill=(100, 150, 200, 180))
        
        final_img = Image.alpha_composite(outline_img, glass_img)
        final_img = Image.alpha_composite(final_img, highlight_img)
        
        return np.array(final_img)


def add_title_overlay(input_video, title, output_video, mode='basic', artistic_style='gradient_3d'):
    """添加标题字幕 - 支持基础和艺术字模式"""
    try:
        print(f"正在处理: {Path(input_video).name} (模式: {mode})")
        video = VideoFileClip(input_video)
        
        if mode == 'artistic':
            return add_artistic_title_overlay(video, title, output_video, artistic_style)
        else:
            return add_basic_title_overlay(video, title, output_video)
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def add_basic_title_overlay(video, title, output_video):
    """基础标题模式 - 原有功能"""
    # 计算新的视频尺寸 (添加上下黑边)
    original_width = video.w
    original_height = video.h
    top_bar_height = 120
    bottom_bar_height = 60
    new_height = original_height + top_bar_height + bottom_bar_height
    
    # 创建黑色背景
    black_bg = ColorClip(size=(original_width, new_height), color=(0, 0, 0), duration=video.duration)
    
    # 将原视频放置在中间位置
    video_positioned = video.with_position(('center', top_bar_height))
    
    # 计算标题垂直居中位置
    title_y_position = top_bar_height // 2
    
    # 创建标题文字 - 尝试中文字体
    try:
        title_clip = TextClip(
            text=title,
            font_size=28,
            color='white',
            font='STHeiti'
        ).with_position(('center', title_y_position)).with_duration(video.duration)
    except:
        try:
            title_clip = TextClip(
                text=title,
                font_size=28,
                color='white',
                font='PingFang SC'
            ).with_position(('center', title_y_position)).with_duration(video.duration)
        except:
            title_clip = TextClip(
                text=title,
                font_size=28,
                color='white'
            ).with_position(('center', title_y_position)).with_duration(video.duration)
    
    # 合成
    final_video = CompositeVideoClip([black_bg, video_positioned, title_clip])
    
    # 输出
    final_video.write_videofile(
        output_video,
        codec='libx264',
        audio_codec='aac',
        fps=24,
        preset='ultrafast',  # 快速编码
        threads=4  # 多线程
    )
    
    # 清理
    video.close()
    final_video.close()
    title_clip.close()
    black_bg.close()
    
    print(f"✓ 完成: {Path(output_video).name}")
    return True


def add_artistic_title_overlay(video, title, output_video, artistic_style='gradient_3d'):
    """艺术字标题模式 - 保持黑色横条布局"""
    
    # 计算新的视频尺寸 (添加上下黑边 - 与原版相同)
    original_width = video.w
    original_height = video.h
    top_bar_height = 120  # 上方黑条高度
    bottom_bar_height = 60  # 下方黑条高度
    new_height = original_height + top_bar_height + bottom_bar_height
    
    # 创建黑色背景
    black_bg = ColorClip(size=(original_width, new_height), color=(0, 0, 0), duration=video.duration)
    
    # 将原视频放置在中间位置
    video_positioned = video.with_position(('center', top_bar_height))
    
    # 创建艺术字渲染器
    renderer = ArtisticTextRenderer()
    
    # 生成艺术字图像
    print(f"🎨 创建艺术字: {title} (样式: {artistic_style})")
    artistic_img = renderer.create_gradient_text(title, font_size=40, style=artistic_style)
    
    # 计算艺术字在顶部黑条的居中位置
    title_y_position = (top_bar_height - artistic_img.shape[0]) // 2
    
    # 创建艺术字片段 - 放置在顶部黑条中央
    artistic_clip = ImageClip(artistic_img, duration=video.duration).with_position(('center', title_y_position))
    
    # 合成所有元素: 黑色背景 + 视频 + 艺术字
    final_video = CompositeVideoClip([black_bg, video_positioned, artistic_clip])
    
    # 输出
    final_video.write_videofile(
        output_video,
        codec='libx264',
        audio_codec='aac', 
        fps=24,
        preset='ultrafast',  # 快速编码
        threads=4  # 多线程
    )
    
    # 清理
    video.close()
    final_video.close()
    artistic_clip.close()
    black_bg.close()
    
    print(f"✓ 完成艺术字处理: {Path(output_video).name}")
    return True


def main():
    # 命令行参数
    parser = argparse.ArgumentParser(description='为 engaging clips 添加标题字幕')
    parser.add_argument('--mode', choices=['basic', 'artistic'], default='basic', 
                       help='标题模式: basic (基础白字) 或 artistic (艺术字)')
    parser.add_argument('--style', choices=['gradient_3d', 'neon_glow', 'metallic_gold', 'rainbow_3d', 
                                          'crystal_ice', 'fire_flame', 'metallic_silver', 'glowing_plasma',
                                          'stone_carved', 'glass_transparent'], 
                       default='gradient_3d', help='艺术字样式 (仅在 artistic 模式下使用)')
    
    args = parser.parse_args()
    
    # 路径设置
    json_file = Path("processed_videos/splits/旭旭宝宝1月27日直播回放_split/top_engaging_moments.json")
    input_dir = Path("engaging_clips")
    
    if args.mode == 'artistic':
        output_dir = Path("engaging_clips_with_artistic_titles")
        mode_desc = f"艺术字模式 ({args.style})"
    else:
        output_dir = Path("engaging_clips_with_titles")
        mode_desc = "基础模式"
    
    output_dir.mkdir(exist_ok=True)
    
    # 检查输入目录
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        print("💡 请先运行 generate_engaging_clips.py 生成视频片段")
        return
    
    # 加载数据
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON文件不存在: {json_file}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return
    
    print("🎬 为 Engaging Clips 添加标题字幕")
    print(f"📊 视频标题: {data['analysis_info']['video_title']}")
    print(f"🎨 处理模式: {mode_desc}")
    print(f"📁 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print("-" * 60)
    
    successful_count = 0
    clips_data = []
    
    # 构建视频数据
    for moment in data['top_engaging_moments']:
        rank = moment['rank']
        title = moment['title']
        
        # 清理标题用于文件名
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[\s\-]+', '_', safe_title)
        safe_title = re.sub(r'_+', '_', safe_title)
        safe_title = safe_title.strip('_')
        
        input_filename = f"rank_{rank:02d}_{safe_title}.mp4"
        
        # 为长标题添加换行
        display_title = title
        if len(title) > 20 and args.mode == 'basic':  # 艺术字模式处理较短文字效果更好
            mid_point = len(title) // 2
            for i in range(mid_point - 5, mid_point + 6):
                if i < len(title) and title[i] in ['！', '？', '，', '、', ' ']:
                    display_title = title[:i+1] + '\n' + title[i+1:]
                    break
        elif len(title) > 30 and args.mode == 'artistic':
            # 艺术字模式适当缩短显示文字
            mid_point = len(title) // 2
            for i in range(mid_point - 3, mid_point + 4):
                if i < len(title) and title[i] in ['！', '？', '，', '、', ' ']:
                    display_title = title[:i+1] + '\n' + title[i+1:]
                    break
        
        clips_data.append({
            "filename": input_filename,
            "title": display_title,
            "rank": rank,
            "original_title": title
        })
    
    # 处理视频
    for i, clip in enumerate(clips_data, 1):
        print(f"\n[{i}/{len(clips_data)}] 处理 Rank {clip['rank']} 视频...")
        
        input_path = input_dir / clip["filename"]
        
        if args.mode == 'artistic':
            output_filename = f"artistic_{args.style}_{clip['filename']}"
        else:
            output_filename = f"titled_{clip['filename']}"
            
        output_path = output_dir / output_filename
        
        if not input_path.exists():
            print(f"✗ 文件不存在: {input_path}")
            continue
        
        success = add_title_overlay(
            str(input_path),
            clip["title"],
            str(output_path),
            mode=args.mode,
            artistic_style=args.style
        )
        
        if success:
            successful_count += 1
        
        print("-" * 40)
    
    # 创建说明文件
    if successful_count > 0:
        readme_path = output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🎬 带标题的 Engaging Clips ({mode_desc})\n\n")
            f.write(f"**原视频**: {data['analysis_info']['video_title']}\n")
            f.write(f"**生成日期**: {data['analysis_info']['analysis_date']}\n")
            f.write(f"**处理模式**: {mode_desc}\n")
            f.write(f"**成功处理**: {successful_count}/{len(clips_data)} 个视频\n\n")
            
            if args.mode == 'artistic':
                f.write("## 🎨 艺术字效果说明\n\n")
                if args.style == 'gradient_3d':
                    f.write("- **样式**: 渐变3D效果\n")
                    f.write("- **特色**: 粉色到蓝色渐变 + 3D立体阴影 + 白色描边\n")
                elif args.style == 'neon_glow':
                    f.write("- **样式**: 霓虹发光效果\n")
                    f.write("- **特色**: 青色霓虹灯发光 + 多层光晕效果\n")
                elif args.style == 'metallic_gold':
                    f.write("- **样式**: 金属质感效果\n")
                    f.write("- **特色**: 黄金色泽 + 高光效果 + 金属质感\n")
                elif args.style == 'rainbow_3d':
                    f.write("- **样式**: 彩虹3D效果\n")
                    f.write("- **特色**: 七彩渐变 + 3D立体阴影\n")
                f.write("- **字体**: 自动检测系统中文字体 (STHeiti/PingFang等)\n")
                f.write("- **位置**: 顶部黑色横条中央 (保持原版布局)\n\n")
            else:
                f.write("## 💡 基础模式说明\n\n")
                f.write("- **样式**: 白色文字 + 黑色背景条\n") 
                f.write("- **位置**: 顶部黑色横条上\n\n")
            
            f.write("## 📝 视频列表\n\n")
            f.write("| Rank | 标题 | 文件名 |\n")
            f.write("|------|------|--------|\n")
            
            for clip in clips_data:
                if args.mode == 'artistic':
                    expected_filename = f"artistic_{args.style}_{clip['filename']}"
                else:
                    expected_filename = f"titled_{clip['filename']}"
                    
                if Path(output_dir / expected_filename).exists():
                    f.write(f"| {clip['rank']} | {clip['original_title']} | `{expected_filename}` |\n")
            
            f.write(f"\n## 💡 使用说明\n")
            if args.mode == 'artistic':
                f.write("- 这些视频使用了真正的中文艺术字效果\n")
                f.write("- 艺术字显示在顶部黑色横条上，保持原版布局\n")
                f.write("- 包含渐变色彩、3D阴影、发光等专业视觉效果\n")
            else:
                f.write("- 这些视频已经添加了基础标题字幕\n")
                f.write("- 标题显示在视频顶部的黑色横条上\n")
            f.write("- 适合直接用于社交媒体发布或其他用途\n")
        
        print(f"\n📄 说明文件已创建: {readme_path}")
    
    print(f"\n🎯 处理结果:")
    print(f"✓ 成功处理: {successful_count}/{len(clips_data)} 个视频")
    print(f"📁 输出目录: {output_dir}")
    
    if successful_count > 0:
        if args.mode == 'artistic':
            print(f"\n🎨 所有视频已添加 {args.style} 艺术字效果！")
            print("💡 艺术字包含渐变色彩、3D阴影等专业视觉效果")
        else:
            print("\n💡 所有视频已添加基础标题字幕！")
        
        print("\n🚀 使用方法:")
        print("  python add_titles_engaging_clips_artistic.py --mode basic     # 基础白字模式")
        print("  python add_titles_engaging_clips_artistic.py --mode artistic  # 艺术字模式")
        print("  python add_titles_engaging_clips_artistic.py --mode artistic --style neon_glow    # 霓虹发光")
        print("  python add_titles_engaging_clips_artistic.py --mode artistic --style metallic_gold # 金属质感")
        print("  python add_titles_engaging_clips_artistic.py --mode artistic --style rainbow_3d    # 彩虹3D")
    else:
        print("\n❌ 没有成功处理任何视频，请检查输入文件是否存在")


if __name__ == "__main__":
    main()
