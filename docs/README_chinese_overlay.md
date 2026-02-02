# 中文艺术字视频叠加工具
# Chinese Artistic Text Overlay Tool

一个强大的Python工具，用于在视频上叠加各种样式的中文艺术字。

A powerful Python tool for overlaying various styles of Chinese artistic text on videos.

## 功能特点 | Features

- ✨ **多种艺术字样式**: 基础文字、描边、阴影、渐变背景
- 🎯 **灵活位置控制**: 自由定位文字位置
- 🎬 **动画效果**: 淡入淡出、滑动进入等动画
- 📝 **多行文本支持**: 支持换行和多行显示
- 🔤 **智能字体选择**: 自动选择最佳中文字体
- 💧 **水印功能**: 添加透明度可调的水印
- 📺 **标题条**: 在视频顶部添加黑条标题

## 安装与使用 | Installation & Usage

### 环境要求 | Requirements

- Python 3.11+
- uv (推荐) 或 pip
- macOS (已测试) / Windows / Linux

### 安装依赖 | Install Dependencies

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install moviepy imageio-ffmpeg
```

### 快速开始 | Quick Start

#### 1. 简单用法 | Simple Usage

```python
from simple_chinese_overlay import add_simple_title

# 添加基础白色文字
add_simple_title(
    'input_video.mp4',
    '你好世界',
    'output_basic.mp4',
    style='basic'
)

# 添加描边文字
add_simple_title(
    'input_video.mp4', 
    '描边效果标题',
    'output_stroke.mp4',
    style='stroke'
)
```

#### 2. 高级用法 | Advanced Usage

```python
from chinese_text_overlay import ChineseTextOverlay

# 创建叠加器
overlay = ChineseTextOverlay('input_video.mp4')

# 创建描边文字
text_clip = overlay.create_stroke_text(
    text='精彩内容',
    font_size=60,
    text_color='yellow',
    stroke_color='black',
    stroke_width=4,
    position='center'
)

# 合成视频
from moviepy import CompositeVideoClip
final_video = CompositeVideoClip([overlay.video, text_clip])
final_video.write_videofile('output.mp4', codec='libx264', audio_codec='aac')

# 清理资源
final_video.close()
overlay.close()
```

### 运行示例 | Run Examples

```bash
# 运行简单示例 (使用 video_sample.mp4)
uv run python simple_chinese_overlay.py

# 运行完整演示
uv run python chinese_text_overlay.py
```

## 样式类型 | Style Types

### 1. 基础文字 (basic)
- 纯色文字，简洁清晰
- 适合: 简单标题、字幕

### 2. 描边文字 (stroke)  
- 文字外围有描边效果
- 适合: 突出显示、对比度不够的背景

### 3. 阴影文字 (shadow)
- 文字带有投影效果
- 适合: 立体感展示、深色背景

### 4. 标题条 (title_bar)
- 在视频顶部添加黑条和标题
- 适合: 正式视频、新闻类内容

### 5. 水印 (watermark)
- 半透明文字水印
- 适合: 版权标识、频道名

## API 参考 | API Reference

### ChineseTextOverlay 类

#### 基础方法

```python
# 创建基础文本
create_basic_text(text, font_size=48, color='white', font='PingFang SC', position='center')

# 创建描边文本
create_stroke_text(text, font_size=48, text_color='white', stroke_color='black', stroke_width=3)

# 创建阴影文本  
create_shadow_text(text, font_size=48, text_color='white', shadow_color='black', shadow_offset=(5,5))

# 创建多行文本
create_multiline_text(lines, font_size=48, color='white', line_spacing=10)

# 创建标题叠加
create_title_overlay(title, style='stroke', font_size=60, bg_height=120)

# 添加水印
add_watermark(text, position='bottom_right', font_size=24, opacity=0.7)
```

#### 动画效果

```python
# 创建动画文本
create_animated_text(
    text='动画文字',
    animation_type='fade_in',  # 'fade_in', 'fade_out', 'slide_in_left'
    animation_duration=1.0,
    start_time=0
)
```

### 位置参数 | Position Parameters

```python
# 字符串位置
position='center'        # 居中
position='top'           # 顶部居中  
position='bottom'        # 底部居中

# 具体坐标 (x, y)
position=(100, 50)       # 距离左上角 (100, 50) 像素

# 预设位置 (用于水印)
position='top_left'      # 左上角
position='top_right'     # 右上角  
position='bottom_left'   # 左下角
position='bottom_right'  # 右下角
```

### 字体列表 | Font List

工具会自动尝试以下中文字体：

```python
fonts = [
    'PingFang SC',          # 苹方 (推荐)
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
```

## 常见问题 | FAQ

### Q: 中文字体显示不正确怎么办？
A: 工具会自动检测可用字体。如果所有字体都不可用，会使用系统默认字体。可以手动指定系统中已安装的中文字体。

### Q: 视频处理速度慢怎么办？
A: 
- 使用较小的测试视频先验证效果
- 降低输出视频的fps (如fps=20)
- 减少文字特效复杂度

### Q: 输出视频没有声音？
A: 确保在 `write_videofile()` 中指定了 `audio_codec='aac'` 参数。

### Q: 如何批量处理多个视频？
A: 可以编写循环脚本，逐个处理视频文件：

```python
import os
from simple_chinese_overlay import add_simple_title

video_dir = "input_videos/"
output_dir = "output_videos/"

for filename in os.listdir(video_dir):
    if filename.endswith('.mp4'):
        input_path = os.path.join(video_dir, filename)
        output_path = os.path.join(output_dir, f"titled_{filename}")
        
        add_simple_title(input_path, "标题文字", output_path, "stroke")
```

## 文件结构 | File Structure

```
whisper-env/
├── chinese_text_overlay.py      # 主要类和高级功能
├── simple_chinese_overlay.py    # 简单易用的接口
├── README_chinese_overlay.md    # 本文档
├── adhoc/
│   ├── video_sample.mp4         # 测试视频样本
│   └── titled_rank_02_*.mp4     # 更大的测试视频
├── overlay_output/              # 输出目录 (运行后生成)
│   ├── basic_title.mp4
│   ├── stroke_title.mp4
│   ├── shadow_title.mp4
│   ├── title_bar.mp4
│   └── watermark_only.mp4
└── test_output.mp4              # 单独测试输出
```

## 性能优化 | Performance Tips

1. **使用较小的字体大小** - 减少渲染时间
2. **选择合适的视频分辨率** - 降低处理复杂度  
3. **限制文字特效数量** - 避免过多叠加效果
4. **使用SSD存储** - 提升文件读写速度
5. **关闭详细日志** - 在生产环境中禁用调试输出

## 许可证 | License

MIT License - 可自由使用和修改

## 贡献 | Contributing

欢迎提交 Issues 和 Pull Requests！

---

## 示例输出 | Example Output

运行示例脚本后，你将得到以下效果的视频：

1. **basic_title.mp4** - 简洁的白色文字叠加
2. **stroke_title.mp4** - 黄色文字配黑色描边  
3. **shadow_title.mp4** - 白色文字配红色阴影
4. **title_bar.mp4** - 专业的顶部标题条
5. **watermark_only.mp4** - 右下角半透明水印

每个样式都展现了不同的视觉效果，适合不同的使用场景。
