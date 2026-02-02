#!/usr/bin/env python3
"""
Test artistic mode with black banner layout
测试艺术字模式 - 黑色横条布局
"""
import os
import sys
from pathlib import Path
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# Import the ArtisticTextRenderer class from our enhanced script
sys.path.append('.')
from add_titles_engaging_clips_artistic import ArtisticTextRenderer

def test_artistic_with_banner(video_path, output_path, title="测试艺术字标题效果", style='gradient_3d'):
    """测试艺术字 + 黑色横条布局"""
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return False
    
    print(f"🧪 测试艺术字黑条布局")
    print(f"📹 输入视频: {video_path}")
    print(f"🎨 艺术字样式: {style}")
    print(f"📝 标题文字: {title}")
    
    try:
        # 加载视频
        video = VideoFileClip(video_path)
        print(f"📐 视频信息: {video.w}x{video.h}, {video.duration:.1f}秒")
        
        # 只处理前5秒
        test_duration = min(5, video.duration)
        
        # 计算新的视频尺寸 (添加上下黑边 - 与原版相同)
        original_width = video.w
        original_height = video.h
        top_bar_height = 120  # 上方黑条高度
        bottom_bar_height = 60  # 下方黑条高度
        new_height = original_height + top_bar_height + bottom_bar_height
        
        print(f"📏 新尺寸: {original_width}x{new_height} (添加黑条)")
        
        # 创建黑色背景
        black_bg = ColorClip(size=(original_width, new_height), color=(0, 0, 0), duration=test_duration)
        
        # 将原视频放置在中间位置 (前5秒)
        video_segment = video.subclipped(0, test_duration) if hasattr(video, 'subclipped') else video.with_duration(test_duration)
        video_positioned = video_segment.with_position(('center', top_bar_height))
        
        # 创建艺术字渲染器
        renderer = ArtisticTextRenderer()
        
        # 生成艺术字图像
        print(f"🎨 创建艺术字...")
        artistic_img = renderer.create_gradient_text(title, font_size=36, style=style)
        print(f"🖼️ 艺术字尺寸: {artistic_img.shape[1]}x{artistic_img.shape[0]}")
        
        # 计算艺术字在顶部黑条的居中位置
        title_y_position = (top_bar_height - artistic_img.shape[0]) // 2
        print(f"📍 艺术字位置: 中心, Y={title_y_position}")
        
        # 创建艺术字片段 - 放置在顶部黑条中央
        artistic_clip = ImageClip(artistic_img, duration=test_duration).with_position(('center', title_y_position))
        
        # 合成所有元素: 黑色背景 + 视频 + 艺术字
        print(f"🎬 合成视频...")
        final_video = CompositeVideoClip([black_bg, video_positioned, artistic_clip])
        
        # 输出
        print(f"💾 渲染到: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac', 
            fps=24
        )
        
        # 清理
        video.close()
        video_segment.close()
        final_video.close()
        artistic_clip.close()
        black_bg.close()
        
        print(f"✅ 成功: {output_path}")
        print(f"💡 效果说明:")
        print(f"   - 艺术字显示在顶部黑色横条上")
        print(f"   - 原视频内容在中间区域")
        print(f"   - 底部有黑色横条")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return False

def main():
    # 测试参数
    video_path = "adhoc/video_sample.mp4"
    output_dir = Path("artistic_banner_test")
    output_dir.mkdir(exist_ok=True)
    
    # 测试所有样式
    styles = ['gradient_3d', 'neon_glow', 'metallic_gold', 'rainbow_3d']
    titles = ['渐变3D横条测试', '霓虹发光横条测试', '金属质感横条测试', '彩虹3D横条测试']
    
    print("🎨 测试艺术字黑条布局 - 所有样式")
    print("=" * 50)
    
    success_count = 0
    
    for style, title in zip(styles, titles):
        print(f"\n🎭 测试: {style}")
        output_path = output_dir / f"banner_{style}_test.mp4"
        
        success = test_artistic_with_banner(video_path, str(output_path), title, style)
        if success:
            success_count += 1
        
        print("-" * 40)
    
    print(f"\n🎯 测试结果: {success_count}/{len(styles)} 成功")
    
    if success_count > 0:
        print(f"📁 输出目录: {output_dir}")
        print("🎉 艺术字黑条布局测试成功!")
        print("💡 现在艺术字会显示在顶部黑色横条上，保持原版布局")

if __name__ == "__main__":
    main()
