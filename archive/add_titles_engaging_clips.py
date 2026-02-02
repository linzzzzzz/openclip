#!/usr/bin/env python3
"""
使用 MoviePy 为 engaging clips 添加中文标题字幕
Based on add_titles_moviepy.py but adapted for engaging moments clips
"""
import json
import os
from pathlib import Path
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

def add_title_overlay(input_video, title, output_video):
    """使用 MoviePy 添加标题字幕"""
    try:
        # 加载视频
        print(f"正在处理: {Path(input_video).name}")
        video = VideoFileClip(input_video)
        
        # 计算新的视频尺寸 (添加上下黑边)
        original_width = video.w
        original_height = video.h
        top_bar_height = 120  # 上方黑条高度
        bottom_bar_height = 60  # 下方黑条高度
        new_height = original_height + top_bar_height + bottom_bar_height
        
        # 创建黑色背景
        black_bg = ColorClip(size=(original_width, new_height), color=(0, 0, 0), duration=video.duration)
        
        # 将原视频放置在中间位置
        video_positioned = video.with_position(('center', top_bar_height))
        
        # 计算标题垂直居中位置 (在顶部黑条中央)
        title_y_position = top_bar_height // 2
        
        # 创建标题文字 - 使用macOS系统中文字体
        try:
            # 尝试使用STHeiti字体（macOS系统中文字体）
            title_clip = TextClip(
                text=title,
                font_size=28,
                color='white',
                font='STHeiti'
            ).with_position(('center', title_y_position)).with_duration(video.duration)
        except:
            try:
                # 尝试PingFang SC
                title_clip = TextClip(
                    text=title,
                    font_size=28,
                    color='white',
                    font='PingFang SC'
                ).with_position(('center', title_y_position)).with_duration(video.duration)
            except:
                try:
                    # 尝试Hiragino Sans GB
                    title_clip = TextClip(
                        text=title,
                        font_size=28,
                        color='white',
                        font='Hiragino Sans GB'
                    ).with_position(('center', title_y_position)).with_duration(video.duration)
                except:
                    # 最后使用默认字体
                    title_clip = TextClip(
                        text=title,
                        font_size=28,
                        color='white'
                    ).with_position(('center', title_y_position)).with_duration(video.duration)
        
        # 合成所有元素
        final_video = CompositeVideoClip([black_bg, video_positioned, title_clip])
        
        # 输出视频
        final_video.write_videofile(
            output_video,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=24
        )
        
        # 清理内存
        video.close()
        final_video.close()
        title_clip.close()
        black_bg.close()
        
        print(f"✓ 完成: {Path(output_video).name}")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def main():
    # 路径设置
    json_file = Path("output_parts/top5_engaging_moments_旭旭宝宝1月22日直播回放.json")
    input_dir = Path("engaging_clips")
    output_dir = Path("engaging_clips_with_titles")
    output_dir.mkdir(exist_ok=True)
    
    # 检查输入目录是否存在
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        print("💡 请先运行 generate_engaging_clips.py 生成视频片段")
        return
    
    # 加载 engaging moments 数据
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
    print(f"📁 输入目录: {input_dir}")
    print(f"📁 输出目录: {output_dir}")
    print("-" * 60)
    
    successful_count = 0
    clips_data = []
    
    # 构建视频数据
    for moment in data['top_engaging_moments']:
        rank = moment['rank']
        title = moment['title']
        
        # 清理标题中的emoji，用于文件名
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[\s\-]+', '_', safe_title)
        safe_title = re.sub(r'_+', '_', safe_title)
        safe_title = safe_title.strip('_')
        
        input_filename = f"rank_{rank:02d}_{safe_title}.mp4"
        
        # 为标题添加换行符以适应显示
        display_title = title
        if len(title) > 20:  # 如果标题太长，尝试在合适位置换行
            # 查找合适的换行位置
            mid_point = len(title) // 2
            for i in range(mid_point - 5, mid_point + 6):
                if i < len(title) and title[i] in ['！', '？', '，', '、', ' ']:
                    display_title = title[:i+1] + '\n' + title[i+1:]
                    break
        
        clips_data.append({
            "filename": input_filename,
            "title": display_title,
            "rank": rank,
            "original_title": title
        })
    
    for i, clip in enumerate(clips_data, 1):
        print(f"\n[{i}/{len(clips_data)}] 处理 Rank {clip['rank']} 视频...")
        
        input_path = input_dir / clip["filename"]
        output_filename = f"titled_{clip['filename']}"
        output_path = output_dir / output_filename
        
        if not input_path.exists():
            print(f"✗ 文件不存在: {input_path}")
            continue
            
        success = add_title_overlay(
            str(input_path),
            clip["title"],
            str(output_path)
        )
        
        if success:
            successful_count += 1
        
        print("-" * 40)
    
    # 创建说明文件
    if successful_count > 0:
        readme_path = output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# 🎬 带标题的 Engaging Clips\n\n")
            f.write(f"**原视频**: {data['analysis_info']['video_title']}\n")
            f.write(f"**生成日期**: {data['analysis_info']['analysis_date']}\n")
            f.write(f"**成功处理**: {successful_count}/{len(clips_data)} 个视频\n\n")
            
            f.write("## 📝 视频列表\n\n")
            f.write("| Rank | 标题 | 文件名 |\n")
            f.write("|------|------|--------|\n")
            
            for clip in clips_data:
                if Path(output_dir / f"titled_{clip['filename']}").exists():
                    f.write(f"| {clip['rank']} | {clip['original_title']} | `titled_{clip['filename']}` |\n")
            
            f.write("\n## 💡 使用说明\n")
            f.write("- 这些视频已经添加了标题字幕\n")
            f.write("- 标题显示在视频顶部的黑色横条上\n")
            f.write("- 适合直接用于社交媒体发布或其他用途\n")
        
        print(f"\n📄 说明文件已创建: {readme_path}")
    
    print(f"\n🎯 处理结果:")
    print(f"✓ 成功处理: {successful_count}/{len(clips_data)} 个视频")
    print(f"📁 带标题的视频保存在: {output_dir}")
    
    if successful_count > 0:
        print("\n💡 所有视频已添加标题字幕，可以直接使用！")
    else:
        print("\n❌ 没有成功处理任何视频，请检查输入文件是否存在")

if __name__ == "__main__":
    main()
