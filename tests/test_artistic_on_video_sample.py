#!/usr/bin/env python3
"""
Test the artistic text functionality on video_sample.mp4
使用 video_sample.mp4 测试艺术字功能
"""
import os
import sys
from pathlib import Path
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import argparse

# Import the ArtisticTextRenderer class from our enhanced script
sys.path.append('.')
from add_titles_engaging_clips_artistic import ArtisticTextRenderer

def test_artistic_styles_on_video(video_path, output_dir):
    """Test all artistic styles on a single video"""
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Load video
    print(f"📹 加载视频: {video_path}")
    video = VideoFileClip(video_path)
    print(f"📐 视频信息: {video.w}x{video.h}, {video.duration:.1f}秒")
    
    # Test duration (only first 5 seconds for speed)
    test_duration = min(5, video.duration)
    
    # Artistic styles to test
    styles = {
        'gradient_3d': '渐变3D效果测试',
        'neon_glow': '霓虹发光效果测试', 
        'metallic_gold': '金属质感效果测试',
        'rainbow_3d': '彩虹3D效果测试'
    }
    
    # Create renderer
    renderer = ArtisticTextRenderer()
    
    print(f"\n🎨 开始测试所有艺术字样式...")
    print(f"⏰ 处理时长: {test_duration}秒 (加速测试)")
    print("=" * 60)
    
    successful_count = 0
    
    for style, title in styles.items():
        print(f"\n🎭 测试样式: {style}")
        print(f"📝 标题文字: {title}")
        
        try:
            # Create artistic text
            print(f"🎨 生成艺术字图像...")
            artistic_img = renderer.create_gradient_text(title, font_size=36, style=style)
            
            # Create text clip
            artistic_clip = ImageClip(artistic_img, duration=test_duration).with_position('center')
            
            # Composite with video (only first 5 seconds)
            video_segment = video.subclipped(0, test_duration) if hasattr(video, 'subclipped') else video.with_duration(test_duration)
            final_video = CompositeVideoClip([video_segment, artistic_clip])
            
            # Output path
            output_path = output_dir / f"artistic_{style}_video_sample.mp4"
            
            print(f"🎬 渲染视频: {output_path.name}")
            
            # Render
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=24
            )
            
            # Cleanup
            final_video.close()
            artistic_clip.close()
            video_segment.close()
            
            print(f"✅ 成功: {style}")
            successful_count += 1
            
        except Exception as e:
            print(f"❌ 失败 {style}: {e}")
        
        print("-" * 40)
    
    # Cleanup
    video.close()
    
    # Create summary
    if successful_count > 0:
        readme_path = output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# 🎨 艺术字样式测试结果\n\n")
            f.write(f"**测试视频**: {video_path}\n")
            f.write(f"**处理时长**: {test_duration}秒\n")
            f.write(f"**成功样式**: {successful_count}/4\n\n")
            
            f.write("## 🎭 样式说明\n\n")
            f.write("| 样式 | 效果描述 | 文件名 |\n")
            f.write("|------|----------|--------|\n")
            
            for style, title in styles.items():
                output_file = f"artistic_{style}_video_sample.mp4"
                if (output_dir / output_file).exists():
                    if style == 'gradient_3d':
                        desc = "粉色到蓝色渐变 + 3D阴影"
                    elif style == 'neon_glow':
                        desc = "青色霓虹发光 + 光晕效果"
                    elif style == 'metallic_gold':
                        desc = "黄金质感 + 高光效果"
                    elif style == 'rainbow_3d':
                        desc = "七彩渐变 + 3D阴影"
                    else:
                        desc = "艺术字效果"
                    
                    f.write(f"| `{style}` | {desc} | `{output_file}` |\n")
            
            f.write("\n## 💡 效果特点\n")
            f.write("- **真正的艺术字**: 包含渐变色彩、3D阴影、发光等效果\n")
            f.write("- **高质量渲染**: 抗锯齿处理，边缘平滑\n")
            f.write("- **中文字体**: 自动检测系统中文字体\n")
            f.write("- **直接叠加**: 艺术字叠加在视频内容上\n")
        
        print(f"\n📄 测试报告已生成: {readme_path}")
    
    print(f"\n🎯 测试完成!")
    print(f"✅ 成功样式: {successful_count}/4")
    print(f"📁 输出目录: {output_dir}")
    
    if successful_count > 0:
        print(f"\n🎉 测试成功! 可以查看生成的艺术字视频:")
        for style in styles.keys():
            output_file = output_dir / f"artistic_{style}_video_sample.mp4"
            if output_file.exists():
                print(f"  🎨 {style}: {output_file}")
    else:
        print(f"\n❌ 所有测试都失败了，请检查错误信息")


def main():
    parser = argparse.ArgumentParser(description='测试艺术字功能')
    parser.add_argument('--video', default='adhoc/video_sample.mp4', help='测试视频路径')
    parser.add_argument('--output', default='artistic_test_results', help='输出目录')
    parser.add_argument('--style', choices=['gradient_3d', 'neon_glow', 'metallic_gold', 'rainbow_3d'], 
                       help='只测试指定样式')
    
    args = parser.parse_args()
    
    print("🧪 艺术字功能测试")
    print("=" * 40)
    
    if args.style:
        print(f"🎭 单独测试样式: {args.style}")
        # 这里可以添加单个样式的测试逻辑
    else:
        print("🎨 测试所有艺术字样式")
        test_artistic_styles_on_video(args.video, args.output)


if __name__ == "__main__":
    main()
