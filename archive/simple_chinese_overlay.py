#!/usr/bin/env python3
"""
简单的中文艺术字叠加示例
Simple Chinese Artistic Text Overlay Example
"""

import os
from chinese_text_overlay import ChineseTextOverlay
from moviepy import CompositeVideoClip


def add_simple_title(video_path, title_text, output_path, style='stroke'):
    """
    简单添加中文标题到视频
    
    Args:
        video_path: 输入视频路径
        title_text: 标题文字
        output_path: 输出视频路径  
        style: 样式类型 ('basic', 'stroke', 'shadow', 'title_bar')
    """
    
    print(f"正在处理视频: {video_path}")
    print(f"添加标题: {title_text}")
    print(f"使用样式: {style}")
    
    try:
        # 创建叠加器
        overlay = ChineseTextOverlay(video_path)
        
        if style == 'basic':
            # 基础白色文字，居中显示
            text_clip = overlay.create_basic_text(
                text=title_text,
                font_size=56,
                color='white',
                position='center'
            )
            final_video = CompositeVideoClip([overlay.video, text_clip])
            
        elif style == 'stroke':
            # 黄色文字 + 黑色描边
            text_clip = overlay.create_stroke_text(
                text=title_text,
                font_size=56,
                text_color='yellow',
                stroke_color='black',
                stroke_width=4,
                position='center'
            )
            final_video = CompositeVideoClip([overlay.video, text_clip])
            
        elif style == 'shadow':
            # 白色文字 + 红色阴影
            text_clip = overlay.create_shadow_text(
                text=title_text,
                font_size=56,
                text_color='white',
                shadow_color='red',
                shadow_offset=(4, 4),
                position='center'
            )
            final_video = CompositeVideoClip([overlay.video, text_clip])
            
        elif style == 'title_bar':
            # 顶部黑条 + 标题
            final_video = overlay.create_title_overlay(
                title=title_text,
                style='stroke',
                font_size=42
            )
            
        else:
            raise ValueError(f"不支持的样式: {style}")
        
        # 输出视频
        print("开始渲染...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24
        )
        
        # 清理资源
        final_video.close()
        overlay.close()
        
        print(f"✓ 完成！输出文件: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ 处理失败: {e}")
        return False


def add_watermark_only(video_path, watermark_text, output_path):
    """只添加水印"""
    
    print(f"为视频添加水印: {watermark_text}")
    
    try:
        overlay = ChineseTextOverlay(video_path)
        
        # 添加右下角水印
        final_video = overlay.add_watermark(
            text=watermark_text,
            position='bottom_right',
            font_size=24,
            opacity=0.8
        )
        
        print("开始渲染...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24
        )
        
        final_video.close()
        overlay.close()
        
        print(f"✓ 完成！输出文件: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ 处理失败: {e}")
        return False


def main():
    """演示各种使用方法"""
    
    # 输入视频
    input_video = "adhoc/video_sample.mp4"
    
    if not os.path.exists(input_video):
        print(f"错误: 找不到视频文件 {input_video}")
        return
    
    print("🎨 中文艺术字叠加工具 - 简单版")
    print("=" * 50)
    
    # 创建输出目录
    os.makedirs("overlay_output", exist_ok=True)
    
    # 示例1: 基础样式
    print("\n📝 示例1: 基础白色文字")
    add_simple_title(
        input_video,
        "史上最壮观30美女主播集体亮相",
        "overlay_output/basic_title.mp4",
        style='basic'
    )
    
    # 示例2: 描边样式  
    print("\n🖍️ 示例2: 黄色描边文字")
    add_simple_title(
        input_video,
        "史上最壮观30美女主播集体亮相",
        "overlay_output/stroke_title.mp4",
        style='stroke'
    )
    
    # 示例3: 阴影样式
    print("\n🌑 示例3: 白色文字红色阴影")
    add_simple_title(
        input_video,
        "史上最壮观30美女主播集体亮相",
        "overlay_output/shadow_title.mp4",
        style='shadow'
    )
    
    # 示例4: 标题条样式
    print("\n📺 示例4: 顶部标题条")
    add_simple_title(
        input_video,
        "史上最壮观30美女主播集体亮相大型见面会",
        "overlay_output/title_bar.mp4",
        style='title_bar'
    )
    
    # 示例5: 只添加水印
    print("\n💧 示例5: 添加水印")
    add_watermark_only(
        input_video,
        "@直播频道",
        "overlay_output/watermark_only.mp4"
    )
    
    print("\n🎬 所有示例处理完成！")
    print("📁 输出目录: overlay_output/")


if __name__ == "__main__":
    main()
