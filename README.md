# OpenClip

[English](./README_EN.md) | 简体中文

一个轻量化自动化视频处理流水线，用于识别和提取长视频（特别是直播回放）中最精彩的片段。使用 AI 驱动的分析来发现亮点，生成剪辑，并添加艺术字幕。

## 🎯 功能介绍

本项目编排完整的工作流程：

1. **下载** Bilibili 视频或处理本地视频文件
2. **提取** 字幕（从 Bilibili 或使用 Whisper 生成）
3. **分割** 长视频（>20分钟）为可管理的片段
4. **分析** 使用 AI 识别精彩时刻
5. **生成** 前5个最精彩时刻的视频剪辑
6. **添加** 10种不同视觉风格的艺术字幕
7. **创建** 每个剪辑的封面图片

非常适合想要从长直播或视频中提取精彩片段用于社交媒体分享的内容创作者。

> 💡 **与 AutoClip 的区别？** 查看[对比说明](#-与-autoclip-的对比)了解 OpenClip 的轻量级设计理念。

## ✨ 特性

- **灵活输入**：支持 Bilibili URL 或本地视频文件
- **智能转录**：优先使用 Bilibili 字幕，回退到 Whisper
- **自动分割**：通过分割为20分钟片段处理任意长度视频
- **AI 分析**：基于内容、互动和娱乐价值识别精彩时刻
- **剪辑生成**：提取前5个时刻为独立视频剪辑
- **艺术字幕**：10种专业字幕风格（火焰、霓虹、水晶、金属等）
- **封面图片**：自动生成带样式的封面图片
- **背景上下文**：可选的主播/上下文信息以获得更好的分析

## 📋 前置要求

### 必需

- **Python 3.11+**
- **uv**（Python 包管理器）- [安装指南](https://docs.astral.sh/uv/getting-started/installation/)
- **FFmpeg** - 用于视频处理
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: 从 [ffmpeg.org](https://ffmpeg.org) 下载

### 可选

- **Qwen API Key** - AI 分析和剪辑生成所需
  - 从[阿里云](https://dashscope.aliyun.com/)获取密钥
  - 设置为环境变量：`export QWEN_API_KEY=your_key_here`

## 🚀 快速开始

### 1. 克隆和设置

```bash
# 克隆仓库
git clone <repository-url>
cd OpenClip

# 使用 uv 安装依赖
uv sync
```

### 2. 设置 API 密钥（用于 AI 功能）

```bash
export QWEN_API_KEY=your_api_key_here
```

### 3. 运行流水线

**处理 Bilibili 视频：**
```bash
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

**处理 Bilibili 视频：**
```bash
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"
```

**处理本地视频：**
```bash
uv run python video_orchestrator.py "/path/to/video.mp4"
```

## 📖 使用指南

### 基础命令

```bash
# 完整流水线，启用所有功能
uv run python video_orchestrator.py "VIDEO_URL_OR_PATH"

# 使用自定义艺术风格
uv run python video_orchestrator.py --artistic-style neon_glow "VIDEO_URL"

# 处理本地文件
uv run python video_orchestrator.py ~/Videos/livestream.mp4

# 自定义输出目录
uv run python video_orchestrator.py -o my_output "VIDEO_URL"
```

### 字幕选项

```bash
# 使用 Bilibili 字幕（默认）
uv run python video_orchestrator.py "VIDEO_URL"

# 强制使用 Whisper 转录
uv run python video_orchestrator.py --force-whisper "VIDEO_URL"

# 使用不同的 Whisper 模型（tiny, base, small, medium, large, turbo）
uv run python video_orchestrator.py --whisper-model small "VIDEO_URL"
```

### 视频分割

```bash
# 默认：在20分钟处分割
uv run python video_orchestrator.py "VIDEO_URL"

# 自定义分割时长（15分钟）
uv run python video_orchestrator.py --max-duration 15 "VIDEO_URL"

# 20分钟以下的视频不会被分割
```

### 分析选项

```bash
# 包含背景信息（主播名称、上下文）
uv run python video_orchestrator.py --use-background "VIDEO_URL"

# 跳过分析（使用现有分析文件）
uv run python video_orchestrator.py --skip-analysis "VIDEO_URL"

# 仅分析（不生成剪辑或字幕）
uv run python video_orchestrator.py --no-clips --no-titles "VIDEO_URL"
```

### 剪辑生成

```bash
# 生成带字幕的剪辑（默认）
uv run python video_orchestrator.py "VIDEO_URL"

# 生成不带字幕的剪辑
uv run python video_orchestrator.py --no-titles "VIDEO_URL"

# 跳过剪辑生成
uv run python video_orchestrator.py --no-clips "VIDEO_URL"

# 禁用封面图片生成
uv run python video_orchestrator.py --no-cover "VIDEO_URL"
```

### 艺术风格

从10种不同的字幕风格中选择：

```bash
--artistic-style gradient_3d      # 渐变3D效果
--artistic-style neon_glow         # 霓虹发光效果
--artistic-style metallic_gold     # 金属金色效果
--artistic-style rainbow_3d        # 彩虹3D效果
--artistic-style crystal_ice       # 水晶冰效果
--artistic-style fire_flame        # 火焰效果（默认）
--artistic-style metallic_silver   # 金属银色效果
--artistic-style glowing_plasma    # 发光等离子效果
--artistic-style stone_carved      # 石刻效果
--artistic-style glass_transparent # 玻璃透明效果
```

### 下载选项

```bash
# 跳过下载（使用现有下载的视频）
uv run python video_orchestrator.py --skip-download "VIDEO_URL"

# 使用不同浏览器的 cookies（chrome, firefox, edge, safari）
uv run python video_orchestrator.py --browser firefox "VIDEO_URL"
```

## 📁 输出结构

处理后，输出目录将包含：

```
processed_videos/
├── downloads/                          # 下载的视频
│   └── BV1234567890_video_title/
│       ├── video_title.mp4            # 原始视频
│       ├── video_title.srt            # 字幕
│       ├── video_title.info.json      # 视频元数据
│       └── video_title.jpg            # 缩略图
│
├── splits/                             # 分割的视频片段（如果 >20分钟）
│   └── video_title_split/
│       ├── video_title_part01.mp4     # 视频片段1
│       ├── video_title_part01.srt     # 字幕片段1
│       ├── video_title_part02.mp4     # 视频片段2
│       ├── video_title_part02.srt     # 字幕片段2
│       ├── highlights_part01.json     # AI分析片段1
│       ├── highlights_part02.json     # AI分析片段2
│       └── top_engaging_moments.json  # 前5个汇总时刻
│
├── clips/                              # 生成的剪辑
│   └── video_title/
│       ├── rank_01_moment_title.mp4   # 剪辑 #1
│       ├── rank_02_moment_title.mp4   # 剪辑 #2
│       ├── rank_03_moment_title.mp4   # 剪辑 #3
│       ├── rank_04_moment_title.mp4   # 剪辑 #4
│       ├── rank_05_moment_title.mp4   # 剪辑 #5
│       └── engaging_moments_summary.md # 摘要
│
└── clips_with_titles/                  # 带艺术字幕的剪辑
    └── video_title/
        ├── artistic_fire_flame_rank_01_moment_title.mp4
        ├── artistic_fire_flame_rank_02_moment_title.mp4
        ├── artistic_fire_flame_rank_03_moment_title.mp4
        ├── artistic_fire_flame_rank_04_moment_title.mp4
        ├── artistic_fire_flame_rank_05_moment_title.mp4
        ├── cover_rank_01_moment_title.jpg              # 封面图片
        ├── cover_rank_02_moment_title.jpg
        ├── cover_rank_03_moment_title.jpg
        ├── cover_rank_04_moment_title.jpg
        ├── cover_rank_05_moment_title.jpg
        └── README.md
```

## 🔧 架构

项目由几个模块化组件组成：

### 核心组件

1. **video_orchestrator.py** - 主编排脚本
   - 协调所有组件
   - 管理工作流和进度
   - 处理命令行界面

2. **bilibili_downloader.py** - 视频下载
   - 使用自动 cookie 处理从 Bilibili 下载
   - 提取字幕（优先 AI 生成的中文）
   - 支持多个浏览器进行身份验证

3. **video_splitter.py** - 视频分割
   - 将长视频分割为片段
   - 保持字幕同步
   - 可配置分割时长

4. **transcript_generation_whisper.py** - 转录生成
   - 使用 OpenAI Whisper 进行语音转文字
   - Bilibili 字幕不可用时的回退方案
   - 多种模型大小可选

5. **engaging_moments_analyzer.py** - AI 分析
   - 使用 Qwen API 分析转录
   - 识别精彩时刻
   - 跨片段汇总顶级时刻

6. **clip_generator.py** - 剪辑提取
   - 从时间戳生成视频剪辑
   - 保持视频质量
   - 创建摘要文档

7. **title_adder.py** - 字幕叠加
   - 为剪辑添加艺术字幕
   - 10种不同视觉风格
   - 中文文本支持

8. **cover_image_generator.py** - 封面生成
   - 从剪辑中提取帧
   - 添加样式文本叠加
   - 创建缩略图

### 工作流程

```
输入（URL 或文件）
    ↓
下载/验证视频
    ↓
提取/生成转录
    ↓
检查时长 → 如果 >20分钟则分割
    ↓
AI 分析（每个片段）
    ↓
汇总前5个时刻
    ↓
生成剪辑
    ↓
添加艺术字幕
    ↓
生成封面图片
    ↓
输出完成！
```

## 🎨 自定义

### 添加背景信息

创建或编辑 `prompts/background/background.md` 以提供关于主播、昵称或重复主题的上下文：

```markdown
# 背景信息

## 主播信息
- 主播：旭旭宝宝
- 昵称：宝哥
- 游戏：地下城与勇士（DNF）

## 常用术语
- 增幅：装备强化
- 鉴定：物品鉴定
```

然后使用 `--use-background` 标志：
```bash
uv run python video_orchestrator.py --use-background "VIDEO_URL"
```

### 自定义分析提示词

编辑 `prompts/` 中的提示词模板：
- `engaging_moments_part_requirement.md` - 每个片段的分析标准
- `engaging_moments_agg_requirement.md` - 顶级时刻的汇总标准

### 添加新的艺术风格

编辑 `title_adder.py` 以添加新的视觉效果。详见 `docs/ARTISTIC_TITLES_GUIDE.md`。

## 📚 文档

`docs/` 中提供详细文档：

- **QUICK_START_GUIDE.md** - 快速开始和示例
- **ARTISTIC_TITLES_GUIDE.md** - 字幕风格和自定义
- **README_video_orchestrator.md** - 编排器详情
- **README_bilibili_downloader.md** - 下载组件
- **README_qwen_integration.md** - AI 分析集成
- **SKIP_ANALYSIS_FEATURE.md** - 跳过分析工作流
- **DIRECTORY_STRUCTURE.md** - 项目组织

## 🐛 故障排除

### 未生成剪辑

**原因**：缺少 API 密钥或分析失败

**解决方案**：
```bash
# 检查 API 密钥
echo $QWEN_API_KEY

# 验证分析文件是否存在
ls processed_videos/splits/*/top_engaging_moments.json
```

### FFmpeg 错误

**原因**：FFmpeg 未安装或不在 PATH 中

**解决方案**：
```bash
# 检查 FFmpeg
ffmpeg -version

# 如果缺失则安装
brew install ffmpeg  # macOS
```

### 内存问题

**原因**：处理非常长的视频

**解决方案**：
```bash
# 使用更短的分割时长
uv run python video_orchestrator.py --max-duration 10 "VIDEO_URL"

# 或分阶段处理
uv run python video_orchestrator.py --no-titles "VIDEO_URL"
```

### 中文文本不显示

**原因**：缺少中文字体

**解决方案**：
- macOS：自动检测字体（STHeiti、PingFang）
- Windows：安装宋体或微软雅黑
- Linux：安装 `fonts-wqy-zenhei` 或类似字体

### 下载失败

**原因**：Cookie/身份验证问题

**解决方案**：
```bash
# 尝试不同的浏览器
uv run python video_orchestrator.py --browser firefox "VIDEO_URL"

# 或先在浏览器中登录 Bilibili
```

## 🔍 示例

### 示例 1：快速本地视频处理

```bash
# 使用默认设置处理本地视频
uv run python video_orchestrator.py ~/Downloads/livestream.mp4
```

### 示例 2：完整 Bilibili 流水线

```bash
# 设置 API 密钥
export QWEN_API_KEY=sk-xxxxx

# 使用霓虹发光风格处理
uv run python video_orchestrator.py \
  --artistic-style neon_glow \
  --use-background \
  "https://www.bilibili.com/video/BV1wT6GBBEPp"
```

### 示例 3：仅分析

```bash
# 仅分析，不生成剪辑
uv run python video_orchestrator.py \
  --no-clips \
  --no-titles \
  "https://www.bilibili.com/video/BV1234567890"
```

### 示例 4：重用现有下载

```bash
# 跳过下载，使用现有视频
uv run python video_orchestrator.py \
  --skip-download \
  --artistic-style crystal_ice \
  "https://www.bilibili.com/video/BV1234567890"
```

### 示例 5：自定义分割时长

```bash
# 分割为15分钟片段
uv run python video_orchestrator.py \
  --max-duration 15 \
  --whisper-model small \
  "VIDEO_URL"
```

## 🤝 贡献

欢迎贡献！改进方向：

- 额外的艺术字幕风格
- 支持更多视频平台
- 改进的 AI 分析提示词
- 性能优化
- 额外的语言支持

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- **OpenAI Whisper** - 语音识别
- **阿里巴巴 Qwen** - AI 分析
- **yt-dlp** - 视频下载
- **MoviePy** - 视频处理
- **FFmpeg** - 视频编码

## 🔄 与 AutoClip 的对比

OpenClip 受 [AutoClip](https://github.com/zhouxiaoka/autoclip) 启发，但采用不同设计理念：

| 特性 | OpenClip | AutoClip |
|------|----------|----------|
| **代码规模** | ~5K 行 | ~2M 行 (含前端依赖) |
| **架构** | 轻量命令行工具 | Web应用 (FastAPI + React) |
| **依赖** | Python + FFmpeg | Docker + Redis + PostgreSQL + Celery |
| **定制性** | 可编辑提示词模板 | 配置文件 |
| **界面** | 命令行 | Web界面 + 实时监控 |
| **部署** | `uv sync` 即用 | Docker容器化 |

**OpenClip 特点：** 轻量（5K行代码）、快速启动、提示词可定制、10种艺术字幕风格、易于维护和二次开发

感谢 [AutoClip](https://github.com/zhouxiaoka/autoclip) 为视频自动化处理做出的贡献。

## 📞 支持

如有问题或疑问：
1. 查看 `docs/` 中的文档
2. 查看控制台输出中的错误消息
3. 先用短视频测试
4. 在 GitHub 上提出 issue
5. 加入我们的 [Discord 社区](https://discord.gg/KsC4Keaq) 讨论交流

---

**用 ❤️ 为内容创作者打造**
