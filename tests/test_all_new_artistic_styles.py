#!/usr/bin/env python3
"""
测试所有新增艺术字样式 - 更大字体
Test all new artistic text styles with larger font
"""
import os
import sys
from pathlib import Path
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip

# Import the ArtisticTextRenderer class
sys.path.append('.')
from add_titles_engaging_clips_artistic import ArtisticTextRenderer

def test_all_artistic_styles():
    """测试所有艺术字样式 - 包含新增的6种"""
    
    video_path = "adhoc/video_sample.mp4"
    output_dir = Path("all_artistic_styles_showcase")
    output_dir.mkdir(exist_ok=True)
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return False
    
    # 所有艺术字样式 (原有4种 + 新增6种 = 10种)
    styles_info = {
        'gradient_3d': '渐变3D立体效果',
        'neon_glow': '霓虹发光效果', 
        'metallic_gold': '黄金金属质感',
        'rainbow_3d': '彩虹3D渐变',
        'crystal_ice': '水晶冰霜效果',      # 新增
        'fire_flame': '火焰燃烧效果',       # 新增
        'metallic_silver': '银色金属质感',   # 新增
        'glowing_plasma': '发光等离子体',    # 新增
        'stone_carved': '石刻雕刻效果',     # 新增
        'glass_transparent': '玻璃透明效果'  # 新增
    }
    
    print("🎨 测试所有艺术字样式 - 更大字体 (font_size=50)")
    print("=" * 60)
    print(f"📹 测试视频: {video_path}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🎭 样式总数: {len(styles_info)} 种")
    print("-" * 60)
    
    success_count = 0
    
    try:
        # 加载视频
        video = VideoFileClip(video_path)
        print(f"📐 视频信息: {video.w}x{video.h}, {video.duration:.1f}秒")
        
        # 只处理前5秒
        test_duration = min(5, video.duration)
        
        for i, (style, description) in enumerate(styles_info.items(), 1):
            print(f"\n[{i}/{len(styles_info)}] 🎭 测试样式: {style}")
            print(f"📝 效果说明: {description}")
            
            try:
                # 计算新的视频尺寸 (添加上下黑边)
                original_width = video.w
                original_height = video.h
                top_bar_height = 120  # 上方黑条高度
                bottom_bar_height = 60  # 下方黑条高度
                new_height = original_height + top_bar_height + bottom_bar_height
                
                # 创建黑色背景
                black_bg = ColorClip(size=(original_width, new_height), color=(0, 0, 0), duration=test_duration)
                
                # 将原视频放置在中间位置
                video_segment = video.subclipped(0, test_duration) if hasattr(video, 'subclipped') else video.with_duration(test_duration)
                video_positioned = video_segment.with_position(('center', top_bar_height))
                
                # 创建艺术字渲染器
                renderer = ArtisticTextRenderer()
                
                # 生成艺术字 - 使用更大字体和测试文字
                title_text = f"{description}测试"
                print(f"🎨 创建艺术字: {title_text}")
                artistic_img = renderer.create_gradient_text(title_text, font_size=50, style=style)
                print(f"🖼️ 艺术字尺寸: {artistic_img.shape[1]}x{artistic_img.shape[0]}")
                
                # 计算艺术字在顶部黑条的居中位置
                title_y_position = (top_bar_height - artistic_img.shape[0]) // 2
                
                # 创建艺术字片段
                artistic_clip = ImageClip(artistic_img, duration=test_duration).with_position(('center', title_y_position))
                
                # 合成所有元素
                final_video = CompositeVideoClip([black_bg, video_positioned, artistic_clip])
                
                # 输出文件
                output_path = output_dir / f"style_{i:02d}_{style}.mp4"
                print(f"💾 渲染到: {output_path.name}")
                
                final_video.write_videofile(
                    str(output_path),
                    codec='libx264',
                    audio_codec='aac', 
                    fps=24
                )
                
                # 清理
                video_segment.close()
                final_video.close()
                artistic_clip.close()
                black_bg.close()
                
                print(f"✅ 成功: {style}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 失败: {style} - {e}")
            
            print("-" * 40)
        
        # 清理主视频
        video.close()
        
    except Exception as e:
        print(f"❌ 主处理失败: {e}")
        return False
    
    # 创建说明文档
    readme_path = output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# 🎨 所有艺术字样式展示 - 更大字体\n\n")
        f.write(f"**测试视频**: {video_path}\n")
        f.write(f"**字体大小**: 50px (比之前增大了25%)\n")
        f.write(f"**测试时长**: 5秒\n")
        f.write(f"**成功样式**: {success_count}/{len(styles_info)}\n\n")
        
        f.write("## 🎭 样式完整列表\n\n")
        f.write("| 编号 | 样式代码 | 效果描述 | 文件名 |\n")
        f.write("|------|----------|----------|--------|\n")
        
        for i, (style, description) in enumerate(styles_info.items(), 1):
            filename = f"style_{i:02d}_{style}.mp4"
            if (output_dir / filename).exists():
                status = "✅"
            else:
                status = "❌"
            f.write(f"| {i} | `{style}` | {description} | {status} `{filename}` |\n")
        
        f.write("\n## 💡 新增样式特点\n\n")
        f.write("### 🆕 新增的6种艺术字样式:\n")
        f.write("- **`crystal_ice`** - 水晶冰霜: 冰蓝色渐变 + 白色高光 + 深蓝阴影\n")
        f.write("- **`fire_flame`** - 火焰燃烧: 红橙黄渐变 + 发光效果\n")
        f.write("- **`metallic_silver`** - 银色金属: 银色波纹质感 + 高光阴影\n")
        f.write("- **`glowing_plasma`** - 发光等离子: 紫粉色波动 + 外发光\n")
        f.write("- **`stone_carved`** - 石刻雕刻: 石质纹理 + 凹陷阴影效果\n")
        f.write("- **`glass_transparent`** - 玻璃透明: 半透明蓝色 + 高光边框\n\n")
        
        f.write("### ⚡ 优化改进:\n")
        f.write("- **字体大小**: 从40px增加到50px，视觉效果更突出\n")
        f.write("- **样式丰富**: 总共10种不同风格的艺术字效果\n")
        f.write("- **布局保持**: 所有样式都保持黑色横条布局，与原版一致\n")
        f.write("- **中文支持**: 完美支持中文字符渲染\n\n")
        
        f.write("## 🚀 使用方法\n\n")
        f.write("```bash\n")
        f.write("# 使用新样式\n")
        f.write("uv run python add_titles_engaging_clips_artistic.py --mode artistic --style crystal_ice\n")
        f.write("uv run python add_titles_engaging_clips_artistic.py --mode artistic --style fire_flame\n")
        f.write("uv run python add_titles_engaging_clips_artistic.py --mode artistic --style metallic_silver\n")
        f.write("uv run python add_titles_engaging_clips_artistic.py --mode artistic --style glowing_plasma\n")
        f.write("uv run python add_titles_engaging_clips_artistic.py --mode artistic --style stone_carved\n")
        f.write("uv run python add_titles_engaging_clips_artistic.py --mode artistic --style glass_transparent\n")
        f.write("```\n")
    
    print(f"\n🎯 最终结果:")
    print(f"✓ 成功测试: {success_count}/{len(styles_info)} 种艺术字样式")
    print(f"📁 输出目录: {output_dir}")
    print(f"📄 说明文档: {readme_path}")
    
    if success_count == len(styles_info):
        print(f"\n🎉 完美! 所有 {len(styles_info)} 种艺术字样式测试成功!")
        print("💡 现在你有10种不同的中文艺术字效果可以选择")
        print("🔥 字体大小已增加到50px，视觉效果更加突出")
    else:
        print(f"\n⚠️ 部分样式测试失败，请检查错误信息")
    
    return success_count == len(styles_info)

def main():
    print("🎨🚀 测试所有艺术字样式 - 包含新增的6种效果!")
    print("=" * 50)
    success = test_all_artistic_styles()
    
    if success:
        print("\n🌟 所有艺术字样式测试完成!")
        print("📂 请查看输出目录中的视频文件")
    else:
        print("\n❌ 测试过程中出现错误")

if __name__ == "__main__":
    main()
