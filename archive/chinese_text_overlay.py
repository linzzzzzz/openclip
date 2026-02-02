#!/usr/bin/env python3
"""
中文艺术字视频叠加工具
Chinese Artistic Text Overlay Tool for Videos

功能特点:
- 多种艺术字样式 (描边、阴影、渐变、发光)
- 灵活的位置控制
- 动画效果支持
- 多行文本支持
- 自定义字体和颜色
"""

import os
from pathlib import Path
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import math


class ChineseTextOverlay:
    def __init__(self, video_path):
        """初始化视频叠加器"""
        self.video = VideoFileClip(video_path)
        self.width = self.video.w
        self.height = self.video.h
        self.duration = self.video.duration
        
        # 常用中文字体列表 (macOS)
        self.chinese_fonts = [
            'PingFang SC',          # 苹方
            'STHeiti',              # 黑体
            'Hiragino Sans GB',     # 冬青黑体
            'STKaiti',              # 楷体
            'STSong',               # 宋体
            'Yuanti SC',            # 圆体
            'Baoli SC',             # 报隶
            'Hannotate SC',         # 手札体
            'Hanzipen SC',          # 钢笔字
            'Wawati SC',            # 娃娃体
            'Weibei SC',            # 魏碑
            'Xingkai SC',           # 行楷
            'Yuppy SC',             # 雅痞
        ]
    
    def get_safe_font(self, preferred_font='PingFang SC'):
        """获取安全的中文字体"""
        fonts_to_try = [preferred_font] + self.chinese_fonts
        
        for font in fonts_to_try:
            try:
                # 测试字体是否可用
                test_clip = TextClip("测试", font=font, font_size=20)
                test_clip.close()
                return font
            except:
                continue
        
        return None  # 使用默认字体
    
    def create_basic_text(self, text, font_size=48, color='white', font='PingFang SC', 
                         position='center', duration=None):
        """创建基础文本"""
        if duration is None:
            duration = self.duration
            
        safe_font = self.get_safe_font(font)
        
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            font=safe_font
        ).with_position(position).with_duration(duration)
        
        return text_clip
    
    def create_stroke_text(self, text, font_size=48, text_color='white', 
                          stroke_color='black', stroke_width=3, font='PingFang SC',
                          position='center', duration=None):
        """创建描边文字"""
        if duration is None:
            duration = self.duration
            
        safe_font = self.get_safe_font(font)
        
        # 创建描边效果
        stroke_clip = TextClip(
            text=text,
            font_size=font_size,
            color=stroke_color,
            font=safe_font,
            stroke_color=stroke_color,
            stroke_width=stroke_width
        ).with_position(position).with_duration(duration)
        
        # 创建主文字
        main_clip = TextClip(
            text=text,
            font_size=font_size,
            color=text_color,
            font=safe_font
        ).with_position(position).with_duration(duration)
        
        return CompositeVideoClip([stroke_clip, main_clip])
    
    def create_shadow_text(self, text, font_size=48, text_color='white',
                          shadow_color='black', shadow_offset=(5, 5), font='PingFang SC',
                          position='center', duration=None):
        """创建阴影文字"""
        if duration is None:
            duration = self.duration
            
        safe_font = self.get_safe_font(font)
        
        # 计算阴影位置
        if isinstance(position, tuple):
            shadow_pos = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
        else:
            shadow_pos = position  # 如果是字符串位置，保持相同
        
        # 创建阴影
        shadow_clip = TextClip(
            text=text,
            font_size=font_size,
            color=shadow_color,
            font=safe_font
        ).with_position(shadow_pos).with_duration(duration)
        
        # 创建主文字
        main_clip = TextClip(
            text=text,
            font_size=font_size,
            color=text_color,
            font=safe_font
        ).with_position(position).with_duration(duration)
        
        return CompositeVideoClip([shadow_clip, main_clip])
    
    def create_gradient_background_text(self, text, font_size=48, text_color='white',
                                       bg_color1='red', bg_color2='blue', font='PingFang SC',
                                       position='center', padding=20, duration=None):
        """创建带渐变背景的文字"""
        if duration is None:
            duration = self.duration
            
        safe_font = self.get_safe_font(font)
        
        # 先创建文字以获取尺寸
        temp_text = TextClip(
            text=text,
            font_size=font_size,
            color=text_color,
            font=safe_font
        )
        
        text_w, text_h = temp_text.w, temp_text.h
        temp_text.close()
        
        # 创建渐变背景 (简化版，使用单色背景)
        bg_clip = ColorClip(
            size=(text_w + padding * 2, text_h + padding * 2),
            color=bg_color1,
            duration=duration
        )
        
        # 创建文字
        text_clip = TextClip(
            text=text,
            font_size=font_size,
            color=text_color,
            font=safe_font
        ).with_position('center').with_duration(duration)
        
        # 合成
        result = CompositeVideoClip([bg_clip, text_clip])
        
        if position == 'center':
            result = result.with_position('center')
        else:
            result = result.with_position(position)
            
        return result
    
    def create_animated_text(self, text, font_size=48, color='white', font='PingFang SC',
                           animation_type='fade_in', animation_duration=1.0, 
                           start_time=0, text_duration=None):
        """创建动画文字"""
        if text_duration is None:
            text_duration = self.duration - start_time
            
        safe_font = self.get_safe_font(font)
        
        base_clip = TextClip(
            text=text,
            font_size=font_size,
            color=color,
            font=safe_font
        ).with_position('center')
        
        if animation_type == 'fade_in':
            text_clip = base_clip.with_duration(text_duration).with_start(start_time).crossfadein(animation_duration)
        elif animation_type == 'fade_out':
            text_clip = base_clip.with_duration(text_duration).with_start(start_time).crossfadeout(animation_duration)
        elif animation_type == 'slide_in_left':
            # 从左侧滑入
            def slide_func(t):
                if t < animation_duration:
                    progress = t / animation_duration
                    x = -base_clip.w + (progress * (self.width/2 + base_clip.w/2))
                    return (x, 'center')
                return 'center'
            text_clip = base_clip.with_duration(text_duration).with_start(start_time).with_position(slide_func)
        elif animation_type == 'bounce_in':
            # 弹跳进入效果
            def bounce_func(t):
                if t < animation_duration:
                    progress = t / animation_duration
                    # 简单的弹跳效果
                    scale = 0.5 + 0.5 * progress
                    return 'center'
                return 'center'
            text_clip = base_clip.with_duration(text_duration).with_start(start_time).with_position(bounce_func)
        else:
            text_clip = base_clip.with_duration(text_duration).with_start(start_time)
        
        return text_clip
    
    def create_multiline_text(self, lines, font_size=48, color='white', font='PingFang SC',
                             line_spacing=10, position='center', duration=None):
        """创建多行文字"""
        if duration is None:
            duration = self.duration
            
        text_clips = []
        safe_font = self.get_safe_font(font)
        
        # 计算总高度
        temp_clip = TextClip("测试", font_size=font_size, font=safe_font)
        line_height = temp_clip.h + line_spacing
        temp_clip.close()
        
        total_height = len(lines) * line_height - line_spacing
        
        for i, line in enumerate(lines):
            if isinstance(position, str) and position == 'center':
                y_offset = (i - (len(lines) - 1) / 2) * line_height
                clip_position = ('center', f'center+{int(y_offset)}')
            else:
                # 如果是具体坐标
                clip_position = (position[0], position[1] + i * line_height)
            
            line_clip = TextClip(
                text=line,
                font_size=font_size,
                color=color,
                font=safe_font
            ).with_position(clip_position).with_duration(duration)
            
            text_clips.append(line_clip)
        
        return text_clips
    
    def create_title_overlay(self, title, style='stroke', font_size=60, position='top',
                           bg_height=120, duration=None):
        """创建标题叠加 (在视频顶部添加黑条和标题)"""
        if duration is None:
            duration = self.duration
        
        # 创建新的视频尺寸
        new_height = self.height + bg_height
        
        # 创建黑色背景
        black_bg = ColorClip(
            size=(self.width, new_height),
            color=(0, 0, 0),
            duration=duration
        )
        
        # 将原视频放置在下方
        video_positioned = self.video.with_position(('center', bg_height))
        
        # 根据样式创建标题
        title_y = bg_height // 2
        
        if style == 'stroke':
            title_clip = self.create_stroke_text(
                text=title,
                font_size=font_size,
                position=('center', title_y),
                duration=duration
            )
        elif style == 'shadow':
            title_clip = self.create_shadow_text(
                text=title,
                font_size=font_size,
                position=('center', title_y),
                duration=duration
            )
        else:  # basic
            title_clip = self.create_basic_text(
                text=title,
                font_size=font_size,
                position=('center', title_y),
                duration=duration
            )
        
        # 合成视频
        final_video = CompositeVideoClip([black_bg, video_positioned, title_clip])
        return final_video
    
    def add_watermark(self, text, position='bottom_right', font_size=24, 
                     opacity=0.7, duration=None):
        """添加水印"""
        if duration is None:
            duration = self.duration
        
        # 计算位置
        positions = {
            'top_left': (20, 20),
            'top_right': (self.width - 20, 20),
            'bottom_left': (20, self.height - 40),
            'bottom_right': (self.width - 20, self.height - 40),
            'center': 'center'
        }
        
        watermark_pos = positions.get(position, position)
        
        watermark_clip = self.create_basic_text(
            text=text,
            font_size=font_size,
            color='white',
            position=watermark_pos,
            duration=duration
        ).with_opacity(opacity)
        
        return CompositeVideoClip([self.video, watermark_clip])
    
    def close(self):
        """清理资源"""
        if hasattr(self, 'video'):
            self.video.close()


def demo_overlay_styles(video_path, output_dir):
    """演示各种叠加样式"""
    overlay = ChineseTextOverlay(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    demos = [
        {
            'name': '基础文字',
            'method': 'basic_text',
            'params': {
                'text': '史上最壮观30美女主播\n集体亮相大型见面会',
                'font_size': 48,
                'color': 'white',
                'font': 'PingFang SC'
            }
        },
        {
            'name': '描边文字',
            'method': 'stroke_text',
            'params': {
                'text': '史上最壮观30美女主播\n集体亮相大型见面会',
                'font_size': 48,
                'text_color': 'yellow',
                'stroke_color': 'black',
                'stroke_width': 4
            }
        },
        {
            'name': '阴影文字',
            'method': 'shadow_text',
            'params': {
                'text': '史上最壮观30美女主播\n集体亮相大型见面会',
                'font_size': 48,
                'text_color': 'white',
                'shadow_color': 'red',
                'shadow_offset': (3, 3)
            }
        },
        {
            'name': '标题叠加',
            'method': 'title_overlay',
            'params': {
                'title': '史上最壮观30美女主播集体亮相大型见面会',
                'style': 'stroke',
                'font_size': 36
            }
        },
        {
            'name': '水印效果',
            'method': 'watermark',
            'params': {
                'text': '@主播频道',
                'position': 'bottom_right',
                'font_size': 20,
                'opacity': 0.8
            }
        }
    ]
    
    print("开始生成演示视频...")
    
    for i, demo in enumerate(demos):
        print(f"\n[{i+1}/{len(demos)}] 生成 {demo['name']} 效果...")
        
        try:
            if demo['method'] == 'basic_text':
                # 处理多行文本
                lines = demo['params']['text'].split('\n')
                text_clips = overlay.create_multiline_text(
                    lines=lines,
                    font_size=demo['params']['font_size'],
                    color=demo['params']['color'],
                    font=demo['params']['font']
                )
                final_video = CompositeVideoClip([overlay.video] + text_clips)
                
            elif demo['method'] == 'stroke_text':
                # 处理多行文本
                lines = demo['params']['text'].split('\n')
                text_clips = []
                for j, line in enumerate(lines):
                    y_offset = (j - (len(lines) - 1) / 2) * 60
                    clip = overlay.create_stroke_text(
                        text=line,
                        font_size=demo['params']['font_size'],
                        text_color=demo['params']['text_color'],
                        stroke_color=demo['params']['stroke_color'],
                        stroke_width=demo['params']['stroke_width'],
                        position=('center', f'center+{int(y_offset)}')
                    )
                    text_clips.append(clip)
                final_video = CompositeVideoClip([overlay.video] + text_clips)
                
            elif demo['method'] == 'shadow_text':
                # 处理多行文本
                lines = demo['params']['text'].split('\n')
                text_clips = []
                for j, line in enumerate(lines):
                    y_offset = (j - (len(lines) - 1) / 2) * 60
                    clip = overlay.create_shadow_text(
                        text=line,
                        font_size=demo['params']['font_size'],
                        text_color=demo['params']['text_color'],
                        shadow_color=demo['params']['shadow_color'],
                        shadow_offset=demo['params']['shadow_offset'],
                        position=('center', f'center+{int(y_offset)}')
                    )
                    text_clips.append(clip)
                final_video = CompositeVideoClip([overlay.video] + text_clips)
                
            elif demo['method'] == 'title_overlay':
                final_video = overlay.create_title_overlay(**demo['params'])
                
            elif demo['method'] == 'watermark':
                final_video = overlay.add_watermark(**demo['params'])
            
            # 输出文件
            output_file = output_dir / f"{demo['name']}_overlay.mp4"
            
            final_video.write_videofile(
                str(output_file),
                codec='libx264',
                audio_codec='aac',
                fps=24
            )
            
            final_video.close()
            print(f"✓ 完成: {output_file}")
            
        except Exception as e:
            print(f"✗ 错误: {e}")
    
    overlay.close()
    print(f"\n🎬 所有演示视频生成完成！")
    print(f"📁 输出目录: {output_dir}")


def main():
    """主函数 - 演示用法"""
    
    # 配置路径
    video_path = "adhoc/titled_rank_02_史上最壮观30美女主播集体亮相大型见面会.mp4"
    output_dir = "chinese_text_overlay_demos"
    
    if not os.path.exists(video_path):
        print(f"错误: 找不到视频文件 {video_path}")
        return
    
    print("🎥 中文艺术字视频叠加工具")
    print("=" * 50)
    print(f"输入视频: {video_path}")
    print(f"输出目录: {output_dir}")
    print("=" * 50)
    
    # 生成演示视频
    demo_overlay_styles(video_path, output_dir)


if __name__ == "__main__":
    main()
