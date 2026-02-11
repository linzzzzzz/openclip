# OpenClip

[English](./README_EN.md) | 简体中文

一个轻量化自动化视频处理流水线，用于识别和提取长视频（特别是口播和直播回放）中最精彩的片段。使用 AI 驱动的分析来发现亮点，生成剪辑，并添加标题和封面。

## 🎯 功能介绍

输入一个视频 URL 或本地文件，自动完成 **下载 → 转录 → 分割 → AI 分析 → 剪辑生成 → 添加标题和封面** 的全流程处理，输出最精彩片段。适合从长直播或视频中快速提取高光时刻。

> 💡 **与 AutoClip 的区别？** 查看[对比说明](#-与-autoclip-的对比)了解 OpenClip 的轻量级设计理念。

## 🎬 演示

### 网页页面

![OpenClip 演示](demo/demo.gif)

### Agent Skills

<video src="https://github.com/user-attachments/assets/1ddf8318-f6ad-418c-9c4c-bbac0dedc668" controls width="600" height="450"></video>

## ✨ 特性

- **灵活输入**：支持 Bilibili、YouTube URL 或本地视频文件
- **智能转录**：优先使用平台字幕，回退到 Whisper
- **自动分割**：通过分割为20分钟片段处理任意长度视频
- **AI 分析**：基于内容、互动和娱乐价值识别精彩时刻
- **剪辑生成**：提取最精彩时刻为独立视频剪辑
- **添加标题和封面**：为视频添加自定义标题和封面图片
- **背景上下文**：可选的添加背景信息（如主播姓名等）以获得更好的分析
- **三界面支持**：Streamlit 网页界面，Agent Skills 和命令行界面，满足不同用户需求
- **实时预览**：Streamlit 界面提供生成内容的实时预览
- **Agent Skills**：内置 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 和 [TRAE](https://www.trae.ai/) agent skill，用自然语言即可处理视频

## 📋 前置要求

### 手动安装

- **uv**（Python 包管理器）- [安装指南](https://docs.astral.sh/uv/getting-started/installation/)
- **FFmpeg** - 用于视频处理
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: 从 [ffmpeg.org](https://ffmpeg.org) 下载

- **LLM API Key**（选择其一）
  - **Qwen API Key** - 从[阿里云](https://dashscope.aliyun.com/)获取密钥
  - **OpenRouter API Key** - 从[OpenRouter](https://openrouter.ai/)获取密钥

### 由 uv 自动管理

运行 `uv sync` 时会自动安装以下依赖：

- **Python 3.11+** - 如果系统未安装，uv 会自动下载
- **yt-dlp** - 用于从 Bilibili、YouTube 等平台下载视频
- **Whisper** - 用于语音转文字
- 其他 Python 依赖（moviepy、streamlit 等）

## 🚀 快速开始

### 1. 克隆和设置

```bash
# 克隆仓库
git clone https://github.com/linzzzzzz/openclip.git
cd openclip

# 使用 uv 安装依赖
uv sync
```

### 2. 设置 API 密钥（用于 AI 功能）

**使用 Qwen：**
```bash
export QWEN_API_KEY=your_api_key_here
```

**使用 OpenRouter：**
```bash
export OPENROUTER_API_KEY=your_api_key_here
```

### 3. 运行流水线

#### 选项 A：使用 Streamlit 网页界面

**启动 Streamlit 应用：**
```bash
uv run streamlit run streamlit_app.py
```

应用启动后，打开浏览器访问显示的 URL（通常是 `http://localhost:8501`）。

**使用流程：**
1. 在侧边栏选择输入类型（视频 URL 或本地文件）
2. 配置处理选项（LLM 提供商等）
3. 点击「Process Video」按钮开始处理
4. 查看实时进度和最终结果
5. 在结果区域预览生成的剪辑和封面

**优势：** 无需记住命令行参数，提供可视化操作界面，适合所有用户。

#### 选项 B：使用 AI Agent 技能

如果你使用 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或 [TRAE](https://www.trae.ai/)，可以直接用自然语言处理视频，无需手动输入命令：

```
"帮我从这个视频里提取精彩片段：https://www.bilibili.com/video/BV1234567890"
"处理一下 ~/Downloads/livestream.mp4，用英语作为输出语言"
```

Agent 会自动调用内置技能，完成下载、转录、分析、剪辑和标题添加等全部流程。

技能定义位于 `.claude/skills/` 和 `.trae/skills/` 目录下。

#### 选项 C：使用命令行界面

```bash
# 处理 Bilibili 视频
uv run python video_orchestrator.py "https://www.bilibili.com/video/BV1234567890"

# 处理 YouTube 视频
uv run python video_orchestrator.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 处理本地视频
uv run python video_orchestrator.py "/path/to/video.mp4"
```

> 如需使用已有字幕，请将 `.srt` 文件放在同目录下，文件名保持一致（如 `video.mp4` → `video.srt`）。

## 📖 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `VIDEO_URL_OR_PATH` | 视频 URL 或本地文件路径（位置参数） | 必填 |
| `-o`, `--output-dir` | 自定义输出目录 | `processed_videos` |
| `--llm-provider` | LLM 提供商（`qwen` 或 `openrouter`） | `qwen` |
| `--language` | 输出语言（`zh` 或 `en`） | `zh` |
| `--title-style` | Banner 标题艺术风格（见下方列表） | `fire_flame` |
| `--max-duration` | 视频分割时长，单位分钟 | `20` |
| `--browser` | 用于 cookie 的浏览器（`chrome`/`firefox`/`edge`/`safari`） | `firefox` |
| `--force-whisper` | 强制使用 Whisper 转录（忽略平台字幕） | 关 |
| `--use-background` | 使用背景信息辅助分析 | 关 |
| `--skip-download` | 跳过下载，使用已下载的视频 | 关 |
| `--skip-analysis` | 跳过分析，使用已有分析结果 | 关 |
| `--skip-clips` | 不生成剪辑 | 关 |
| `--skip-titles` | 不添加艺术标题 | 关 |
| `--skip-cover` | 不生成封面图片 | 关 |

<details>
<summary>🎨 Banner 标题艺术风格</summary>

| 风格 | 效果 |
|------|------|
| `fire_flame` | 火焰效果（默认） |
| `gradient_3d` | 渐变3D效果 |
| `neon_glow` | 霓虹发光效果 |
| `metallic_gold` | 金属金色效果 |
| `rainbow_3d` | 彩虹3D效果 |
| `crystal_ice` | 水晶冰效果 |
| `metallic_silver` | 金属银色效果 |
| `glowing_plasma` | 发光等离子效果 |
| `stone_carved` | 石刻效果 |
| `glass_transparent` | 玻璃透明效果 |

</details>

## 🔍 命令行示例

**处理 Bilibili 视频，加载背景信息， 并使用霓虹风格处理Banner标题：**
```bash
uv run python video_orchestrator.py \
  --title-style neon_glow \
  --use-background \
  "https://www.bilibili.com/video/BV1wT6GBBEPp"
```

**仅分析，不生成剪辑：**
```bash
uv run python video_orchestrator.py --skip-clips --no-titles "VIDEO_URL"
```

**跳过下载，重新处理已有视频：**
```bash
uv run python video_orchestrator.py --skip-download --title-style crystal_ice "VIDEO_URL"
```

## 📁 输出结构

处理后，输出目录结构如下：

```
processed_videos/{video_name}/
├── downloads/            # 原始视频、字幕和元数据
├── splits/               # 分割片段和 AI 分析结果
├── clips/                # 生成的精彩剪辑和摘要
└── clips_with_titles/    # 带艺术标题的最终剪辑和封面图片
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

编辑 `title_adder.py` 以添加新的视觉效果。

## 📎 其他

<details>
<summary>🔧 工作流程</summary>

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
添加艺术标题
    ↓
生成封面图片
    ↓
输出完成！
```

</details>

<details>
<summary>🐛 故障排除</summary>

### 下载失败
**原因**：
- yt-dlp版本过旧。尝试更新依赖版本：`uv sync`。
- Cookie/身份验证问题。尝试 `--browser firefox` 切换浏览器，或先在浏览器中登录 Bilibili。

### 未生成剪辑
**原因**：缺少 API 密钥或分析失败。检查 `echo $QWEN_API_KEY` 或 `echo $OPENROUTER_API_KEY`，并确认分析文件存在。

### FFmpeg 错误
**原因**：FFmpeg 未安装或不在 PATH 中。运行 `ffmpeg -version` 检查，缺失则安装（macOS: `brew install ffmpeg`）。

### 内存问题
**原因**：视频过长。尝试 `--max-duration 10` 缩短分割时长，或 `--skip-titles` 分阶段处理。

### 中文文本不显示
**原因**：缺少中文字体。macOS 自动检测（STHeiti、PingFang），Windows 需安装宋体或微软雅黑，Linux 安装 `fonts-wqy-zenhei`。

</details>

## 🔄 与 AutoClip 的对比

OpenClip 受 [AutoClip](https://github.com/zhouxiaoka/autoclip) 启发，但采用不同设计理念：

| 特性 | OpenClip | AutoClip |
|------|----------|----------|
| **代码规模** | ~5K 行 | ~2M 行 (含前端依赖) |
| **依赖** | Python + FFmpeg | Docker + Redis + PostgreSQL + Celery |
| **定制性** | 可编辑提示词模板 | 配置文件 |
| **界面** | Web界面+Agent Skills+命令行 | Web界面 |
| **部署** | `uv sync` 即用 | Docker容器化 |

**OpenClip 特点：** 轻量（5K行代码）、快速启动、提示词可定制、易于维护和二次开发

感谢 [AutoClip](https://github.com/zhouxiaoka/autoclip) 为视频自动化处理做出的贡献。

## 🤝 贡献

欢迎贡献！改进方向：

- 额外的艺术标题风格
- 支持更多视频平台
- 改进的 AI 分析提示词
- 性能优化
- 额外的语言支持

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

如有问题或疑问：
1. 查看控制台输出中的错误消息
2. 先用短视频测试
3. 在 GitHub 上提出 issue
4. 加入我们的 [Discord 社区](https://discord.gg/KsC4Keaq) 讨论交流
