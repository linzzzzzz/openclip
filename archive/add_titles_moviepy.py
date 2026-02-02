#!/usr/bin/env python3
"""
使用 MoviePy 为视频添加中文标题字幕
"""
import os
from pathlib import Path
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

def add_title_overlay(input_video, title, output_video):
    """使用 MoviePy 添加标题字幕"""
    try:
        # 加载视频
        print(f"正在处理: {input_video}")
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
                font_size=24,
                color='white',
                font='STHeiti'
            ).with_position(('center', title_y_position)).with_duration(video.duration)
        except:
            try:
                # 尝试PingFang SC
                title_clip = TextClip(
                    text=title,
                    font_size=24,
                    color='white',
                    font='PingFang SC'
                ).with_position(('center', title_y_position)).with_duration(video.duration)
            except:
                try:
                    # 尝试Hiragino Sans GB
                    title_clip = TextClip(
                        text=title,
                        font_size=24,
                        color='white',
                        font='Hiragino Sans GB'
                    ).with_position(('center', title_y_position)).with_duration(video.duration)
                except:
                    try:
                        # 尝试使用字体文件路径
                        title_clip = TextClip(
                            text=title,
                            font_size=24,
                            color='white',
                            font='/System/Library/AssetsV2/com_apple_MobileAsset_Font7/eb257c12d1a51c8c661b89f30eec56cacf9b8987.asset/AssetData/STHEITI.ttf'
                        ).with_position(('center', title_y_position)).with_duration(video.duration)
                    except:
                        # 最后使用默认字体
                        title_clip = TextClip(
                            text=title,
                            font_size=24,
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
        
        print(f"✓ 完成: {output_video}")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def main():
    # 输入和输出目录
    input_dir = Path("highlight_clips")
    output_dir = Path("clips_with_titles")
    output_dir.mkdir(exist_ok=True)
    
    # 视频和标题对应关系
    clips_data = [
        {
            "filename": "01_撞脸游戏大神.mp4",
            "title": "主播偶遇神秘人，竟然长得和\n知名游戏选手一模一样！"
        },
        {
            "filename": "02_龙珠角色现实版.mp4",
            "title": "太像了！现实中遇到龙珠里的\n雅琴珠贝？胖胖的拿刀那个！"
        },
        {
            "filename": "03_追女神剧情.mp4",
            "title": "兄弟放话必须拿下！\n直播间见证追女神大戏！"
        },
        {
            "filename": "04_忠诚度大考验.mp4",
            "title": "谁是真兄弟？关键时刻看出人品，\n这个人没有同流合污！"
        },
        {
            "filename": "05_重磅官宣新队长.mp4",
            "title": "震撼！山东豪哥正式官宣\nGoGo飞鸟担任新队长，明年阵容曝光！"
        },
        {
            "filename": "06_富二代身份曝光.mp4",
            "title": "富二代身份曝光？\n家庭条件全市排名前列的神秘选手！"
        },
        {
            "filename": "07_背叛者名单大公开.mp4",
            "title": "手机里记录一万多个仇人！\n主播曝光背叛视频真相！"
        },
        {
            "filename": "08_审讯大戏即将开始.mp4",
            "title": "拿出神秘武器！10点准时开启\n审讯环节，今晚有人要遭殃了"
        },
        {
            "filename": "09_疯狂撒手机福利.mp4",
            "title": "壕气冲天！主播现场摆放5个\n手机盒子，最少送出10台手机！"
        },
        {
            "filename": "10_天价礼物开箱.mp4",
            "title": "秦风送的神秘金色礼物开箱！\n竟然是价值不菲的都彭打火机！"
        }
    ]
    
    print(f"开始处理 {len(clips_data)} 个视频片段...")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    successful_count = 0
    
    for i, clip in enumerate(clips_data, 1):
        print(f"\n[{i}/{len(clips_data)}] 处理中...")
        
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
        
        print("-" * 30)
    
    print(f"\n🎬 处理完成！成功: {successful_count}/{len(clips_data)}")
    print(f"📁 带标题的视频保存在: {output_dir}")

if __name__ == "__main__":
    main()
