# 如何给视频添加标题字幕 (How to Add Title Overlays to Videos)

## 选项 1: 升级 FFmpeg (推荐)

### 安装完整版 FFmpeg
```bash
# 卸载当前版本
brew uninstall ffmpeg

# 安装带所有功能的完整版
brew install ffmpeg --with-freetype --with-libass --with-libvorbis --with-libvpx --with-x264 --with-x265

# 或者使用 static build
brew install ffmpeg-static
```

安装完成后，可以使用以下脚本添加标题：

```python
# 使用带 drawtext 的 ffmpeg 命令
cmd = f'''ffmpeg -i "{input_video}" \\
-vf "drawtext=text='{title}':fontfile=/System/Library/Fonts/PingFang.ttc:fontsize=32:fontcolor=white:x=(w-text_w)/2:y=50:box=1:boxcolor=black@0.8:boxborderw=10" \\
-c:a copy "{output_video}" -y'''
```

## 选项 2: 使用 MoviePy (Python 库) ⭐推荐

### 安装 MoviePy
```bash
pip install moviepy
```

### 使用现成的脚本
我已经为你创建了完整的脚本：`whisper-env/add_titles_moviepy.py`

运行方法：
```bash
cd /Users/flln/Desktop/dev/ytb
python whisper-env/add_titles_moviepy.py
```

这个脚本会：
- 自动处理所有 10 个视频片段
- 添加白色文字 + 黑色描边的标题
- 标题居中显示在视频顶部
- 输出到 `whisper-env/clips_with_titles/` 目录

## 选项 3: 使用视频编辑软件

### 3.1 Final Cut Pro (Mac)
1. 导入视频片段
2. 添加标题 (Title) 元素
3. 选择合适的字体和样式
4. 设置中文字体 (如 PingFang SC)
5. 导出视频

### 3.2 DaVinci Resolve (免费)
1. 创建新项目
2. 导入视频
3. 在 Edit 页面添加 Text+ 
4. 设置中文字体和样式
5. 渲染输出

### 3.3 Adobe Premiere Pro
1. 新建序列
2. 导入视频素材
3. 添加 Essential Graphics 标题
4. 自定义字体和效果
5. 导出媒体

## 选项 4: 在线视频编辑器

### 4.1 剪映 (CapCut) - 推荐中文用户
- 支持中文字幕和模板
- 有网页版和APP版
- 操作简单，效果丰富

### 4.2 Canva
- 在线视频编辑
- 丰富的模板和字体
- 支持中文

## 选项 5: 批量处理方案

### 如果你想批量处理，推荐顺序：
1. **MoviePy** (最简单，已准备好脚本)
2. **升级FFmpeg + 自动化脚本** (最高效)
3. **剪映批量导入** (适合需要更多特效)

## 快速开始

**推荐方案：使用 MoviePy**
```bash
# 1. 安装 MoviePy
pip install moviepy

# 2. 运行脚本
cd /Users/flln/Desktop/dev/ytb
python whisper-env/add_titles_moviepy.py

# 3. 查看结果
ls whisper-env/clips_with_titles/
```

## 标题样式预览

所有标题都已经过优化，包含：
- ✅ 吸引人的中文表达
- ✅ 适当的换行处理
- ✅ 白色文字 + 黑色描边
- ✅ 居中对齐
- ✅ 适合社交媒体的长度

## 故障排除

### MoviePy 问题
```bash
# 如果遇到字体问题
pip install --upgrade moviepy
pip install imageio-ffmpeg

# 如果中文显示异常
# 将脚本中的字体改为：font='STHeiti' 或 font='SimHei'
```

### FFmpeg 升级问题
```bash
# 检查当前版本
ffmpeg -version

# 查看可用 filters
ffmpeg -filters | grep text
```
