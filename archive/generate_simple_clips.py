#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def run_ffmpeg_command(cmd):
    """Run ffmpeg command and handle errors"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✓ Command executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error executing command: {e}")
        print(f"stderr: {e.stderr}")
        return False

def create_clip(input_video, start_time, end_time, output_filename):
    """Create a video clip without overlay"""
    
    # Calculate duration
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time) 
    duration = end_seconds - start_seconds
    
    # Account for video start offset (5 seconds) and use proper keyframe handling
    adjusted_start = start_seconds + 5
    adjusted_start_time = f"{adjusted_start//3600:02d}:{(adjusted_start%3600)//60:02d}:{adjusted_start%60:02d}"
    
    # Use re-encoding to avoid black frames and keyframe issues
    cmd = f'ffmpeg -ss {adjusted_start_time} -i "{input_video}" -t {duration} -c:v libx264 -c:a aac -avoid_negative_ts make_zero "{output_filename}" -y'
    
    print(f"Creating clip: {output_filename}")
    print(f"Original time range: {start_time} to {end_time}")
    print(f"Adjusted start time: {adjusted_start_time}")
    print(f"Duration: {duration} seconds")
    
    return run_ffmpeg_command(cmd)

def time_to_seconds(time_str):
    """Convert MM:SS or HH:MM:SS to seconds"""
    parts = time_str.split(':')
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

def main():
    # Input video path
    input_video = "whisper-env/output_parts/video_part01.mp4"
    
    # Create output directory
    output_dir = Path("whisper-env/highlight_clips")
    output_dir.mkdir(exist_ok=True)
    
    # Define all the interesting moments with their titles
    clips_data = [
        {
            "start": "00:00:47", 
            "end": "00:01:07",
            "title": "主播偶遇神秘人，竟然长得和知名游戏选手一模一样！",
            "filename": "01_撞脸游戏大神.mp4"
        },
        {
            "start": "00:01:17", 
            "end": "00:01:27",
            "title": "太像了！现实中遇到龙珠里的雅琴珠贝？胖胖的拿刀那个！",
            "filename": "02_龙珠角色现实版.mp4"
        },
        {
            "start": "00:02:26", 
            "end": "00:03:21",
            "title": "兄弟放话必须拿下！直播间见证追女神大戏！",
            "filename": "03_追女神剧情.mp4"
        },
        {
            "start": "00:05:00", 
            "end": "00:05:32",
            "title": "谁是真兄弟？关键时刻看出人品，这个人没有同流合污！",
            "filename": "04_忠诚度大考验.mp4"
        },
        {
            "start": "00:08:03", 
            "end": "00:08:59",
            "title": "震撼！山东豪哥正式官宣GoGo飞鸟担任新队长，明年阵容曝光！",
            "filename": "05_重磅官宣新队长.mp4"
        },
        {
            "start": "00:09:32", 
            "end": "00:10:39",
            "title": "富二代加入战队？家庭条件全市排名前二的神秘选手！",
            "filename": "06_富二代身份曝光.mp4"
        },
        {
            "start": "00:11:17", 
            "end": "00:12:00",
            "title": "手机里记录一万多个仇人！主播曝光背叛视频真相！",
            "filename": "07_背叛者名单大公开.mp4"
        },
        {
            "start": "00:14:21", 
            "end": "00:15:00",
            "title": "拿出神秘武器！10点准时开启审讯环节，今晚有人要遭殃了",
            "filename": "08_审讯大戏即将开始.mp4"
        },
        {
            "start": "00:17:00", 
            "end": "00:17:40",
            "title": "壕气冲天！主播现场摆放5个手机盒子，最少送出10台手机！",
            "filename": "09_疯狂撒手机福利.mp4"
        },
        {
            "start": "00:18:40", 
            "end": "00:19:59",
            "title": "秦风送的神秘金色礼物开箱！竟然是价值不菲的都彭打火机！",
            "filename": "10_天价礼物开箱.mp4"
        }
    ]
    
    # Check if input video exists
    if not Path(input_video).exists():
        print(f"Error: Input video {input_video} not found!")
        return
    
    print(f"Processing {len(clips_data)} clips from {input_video}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    successful_clips = 0
    
    # Create a markdown file with titles and filenames
    markdown_path = output_dir / "clips_with_titles.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write("# 精彩时刻视频片段\n\n")
        f.write("| 片段 | 时间范围 | 标题 | 文件名 |\n")
        f.write("|------|----------|------|--------|\n")
        
        for i, clip in enumerate(clips_data, 1):
            f.write(f"| {i:02d} | {clip['start']} - {clip['end']} | {clip['title']} | {clip['filename']} |\n")
    
    print(f"📄 Created title reference: {markdown_path}")
    
    for i, clip in enumerate(clips_data, 1):
        print(f"\n[{i}/{len(clips_data)}] Processing clip...")
        
        output_path = output_dir / clip["filename"]
        
        success = create_clip(
            input_video,
            clip["start"],
            clip["end"], 
            str(output_path)
        )
        
        if success:
            successful_clips += 1
            print(f"✓ Saved: {output_path}")
        else:
            print(f"✗ Failed to create: {output_path}")
            
        print("-" * 30)
    
    print(f"\n🎬 Summary: {successful_clips}/{len(clips_data)} clips created successfully!")
    print(f"📁 All clips saved in: {output_dir}")
    
    if successful_clips > 0:
        print(f"\n📝 Title reference saved in: {markdown_path}")
        print("💡 To add titles later, you can use video editing software or other tools")
        print("💡 Each clip corresponds to its title in the markdown file")

if __name__ == "__main__":
    main()
