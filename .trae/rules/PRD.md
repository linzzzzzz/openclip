# OpenClip 产品需求文档 (PRD)

## 1. 项目概述

### 1.1 产品名称
**OpenClip** - 视频高光时刻提取工具

### 1.2 产品定位
一个轻量化自动化视频处理流水线，用于识别和提取长视频（特别是口播和直播回放）中最精彩的片段。使用 AI 驱动的分析来发现亮点，生成剪辑，并添加标题和封面。

### 1.3 核心价值
- **自动化**: 用户只需提供视频 URL 或本地文件，系统自动完成全流程处理
- **智能化**: 利用 LLM 分析内容、互动和娱乐价值，识别最精彩时刻
- **灵活性**: 支持多种输入源、多个 LLM 提供商、多种输出格式

### 1.4 目标用户
- 内容创作者: 快速从长视频/直播中提取精彩片段
- 社交媒体运营: 高效生产短视频内容
- 个人用户: 保存和分享喜欢的视频高光时刻

---

## 2. 功能需求

### 2.1 视频输入

#### 2.1.1 支持的输入源
| 输入类型 | 说明 | 示例 |
|---------|------|------|
| Bilibili URL | 支持BV号和AV号 | `https://www.bilibili.com/video/BV1wT6GBBEPp` |
| YouTube URL | 标准YouTube链接 | `https://www.youtube.com/watch?v=xxx` |
| 本地视频文件 | 本地存储的视频 | `/path/to/video.mp4` |

#### 2.1.2 支持的视频格式
- MP4, WebM, AVI, MOV, MKV

#### 2.1.3 支持的字幕格式
- SRT (优先)
- VTT, ASS (部分支持)

### 2.2 转录处理

#### 2.2.1 转录来源策略
系统支持两种转录来源，由用户决定:

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| **默认模式** | 优先使用平台下载的字幕 (Bilibili/YouTube) | 视频已有准确字幕时 |
| **强制 Whisper** | 使用 `--force-whisper` 强制通过 Whisper 生成转录 | 平台字幕不准确、需要其他语言转录 |

#### 2.2.2 Whisper 模型选择
| 模型 | 说明 | 适用场景 |
|------|------|----------|
| `base` | 默认，快速 | 清晰音频 |
| `small` | 稍慢，更准确 | 有背景噪音、多说话者、有口音 |
| `turbo` | 快速且准确 | 平衡需求 |
| `medium/large` | 最准确，但慢 | 转录质量至关重要 |

### 2.3 视频分割

#### 2.3.1 分割策略
- **触发条件**: 视频时长 > 20 分钟 (默认，可配置)
- **分割单位**: 每个片段最大 20 分钟
- **分割边界**: 在字幕时间戳边界处分割，保证完整性
- **处理方式**: 每个片段单独分析，最后聚合结果

#### 2.3.2 配置参数
```bash
--max-duration <minutes>  # 默认 20 分钟
```

### 2.4 高光时刻分析

#### 2.4.1 分析内容
通过 LLM 分析识别以下类型的精彩时刻:
- 高互动时刻 (弹幕/评论热点)
- 内容亮点 (关键信息点)
- 娱乐价值 (有趣、感人的片段)
- 情感高潮 (情绪转折点)

#### 2.4.2 配置参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--llm-provider` | LLM 提供商 | `qwen` |
| `--language` | 输出语言 | `zh` (中文) |
| `--max-clips` | 最大高光数量 | 5 |
| `--use-background` | 是否使用背景信息 | 否 |

#### 2.4.3 支持的 LLM 提供商
- **Qwen** (阿里云) - 默认
- **OpenRouter** (支持多种模型)

#### 2.4.4 背景信息支持
用户可创建 `prompts/background/background.md` 提供:
- 主播/UP主信息
- 常用术语
- 历史背景

### 2.5 剪辑生成

#### 2.5.1 剪辑输出
- 从每个高光时刻生成独立视频剪辑
- 输出格式: MP4
- 自动命名: `rank_{序号}_{标题}.mp4`
- 自动生成字幕文件: `rank_{序号}_{标题}.srt`
  - 字幕时间调整为从 00:00:00 开始
  - 仅包含剪辑时间范围内的字幕片段
  - 如果源字幕不存在，则跳过字幕生成

### 2.6 艺术标题

#### 2.6.1 支持的风格
| 风格 | 效果描述 |
|------|----------|
| `fire_flame` | 火焰效果 (默认) |
| `gradient_3d` | 渐变3D效果 |
| `neon_glow` | 霓虹发光效果 |
| `metallic_gold` | 金属金色效果 |
| `rainbow_3d` | 彩虹3D效果 |
| `crystal_ice` | 水晶冰效果 |
| `metallic_silver` | 金属银色效果 |
| `glowing_plasma` | 发光等离子效果 |
| `stone_carved` | 石刻效果 |
| `glass_transparent` | 玻璃透明效果 |

#### 2.6.2 字体大小选项
- `small`: 30px
- `medium`: 40px (默认)
- `large`: 50px
- `xlarge`: 60px

### 2.7 封面图片生成

#### 2.7.1 封面特性
- 从高光片段第一帧生成
- 添加标题文字覆盖
- 可配置文字位置和颜色

#### 2.7.2 配置参数
| 参数 | 选项 | 默认值 |
|------|------|--------|
| `--cover-text-location` | top/upper_middle/bottom/center | center |
| `--cover-fill-color` | yellow/red/white/cyan/green/orange/pink/purple/gold/silver | yellow |
| `--cover-outline-color` | yellow/red/white/cyan/green/orange/pink/purple/gold/silver/black | black |

---

## 3. 用户界面

### 3.1 命令行界面 (CLI)

#### 3.1.1 基本用法
```bash
# 处理 Bilibili 视频
uv run python video_orchestrator.py "https://www.bilibili.com/video/BVxxx"

# 处理 YouTube 视频
uv run python video_orchestrator.py "https://www.youtube.com/watch?v=xxx"

# 处理本地视频
uv run python video_orchestrator.py "/path/to/video.mp4"
```

#### 3.1.2 完整参数列表
见 [README.md](../README.md#命令行参数)

### 3.2 Streamlit 网页界面

启动方式:
```bash
uv run streamlit run streamlit_app.py
```

功能:
- 可视化参数配置
- 实时进度显示
- 视频预览和结果展示

### 3.3 Agent Skills

支持 Claude Code 和 TRAE Agent:
```
"帮我从这个视频里提取精彩片段：https://www.bilibili.com/video/BVxxx"
"处理一下 ~/Downloads/livestream.mp4，用英语作为输出语言"
```

---

## 4. 技术架构

### 4.1 核心模块

```
core/
├── downloaders/           # 视频下载模块
│   ├── bilibili_downloader.py
│   ├── youtube_downloader.py
│   └── video_downloader.py
├── video_splitter.py      # 视频分割模块
├── transcript_generation_whisper.py  # Whisper 转录
├── engaging_moments_analyzer.py       # 高光时刻分析
├── clip_generator.py      # 剪辑生成
├── title_adder.py         # 艺术标题添加
├── cover_image_generator.py  # 封面图片生成
├── config.py              # 配置管理
└── video_utils.py         # 工具函数
```

### 4.2 处理流程

```
输入 (URL 或本地文件)
    ↓
1. 下载/验证视频
    ↓
2. 提取/生成转录
    (优先平台字幕 → 回退 Whisper)
    ↓
3. 检查时长 → 如果 >20分钟则分割
    ↓
4. AI 分析 (每个片段)
    ↓
5. 汇总前5个时刻
    ↓
6. 生成剪辑
    ↓
7. 添加艺术标题
    ↓
8. 生成封面图片
    ↓
输出完成！
```

### 4.3 输出目录结构

```
processed_videos/{video_name}/
├── downloads/            # 原始视频、字幕和元数据
├── splits/               # 分割片段和 AI 分析结果
│   ├── *_part01.mp4
│   ├── *_part01.srt
│   ├── highlights_part01.json
│   └── top_engaging_moments.json
├── clips/                # 生成的精彩剪辑
│   ├── rank_01_xxx.mp4
│   ├── rank_01_xxx.srt
│   └── engaging_moments_summary.md
└── clips_with_titles/    # 带艺术标题的最终剪辑和封面图片
    ├── rank_01_xxx.mp4
    └── cover_rank_01_xxx.jpg
```

---

## 5. 跳过步骤功能

系统支持从中间步骤继续处理:

| 跳过选项 | 说明 |
|---------|------|
| `--skip-download` | 跳过下载，使用已下载的视频 |
| `--skip-transcript` | 跳过转录生成，使用已有转录文件 |
| `--skip-analysis` | 跳过分析，使用已有分析结果 |
| `--skip-clips` | 不生成剪辑 |
| `--skip-titles` | 不添加艺术标题 |
| `--skip-cover` | 不生成封面图片 |

---

## 6. 环境要求

### 6.1 必需工具
- **uv** - Python 包管理器
- **FFmpeg** - 视频处理

### 6.2 API 密钥 (至少一个)
- **QWEN_API_KEY** - 阿里云 Qwen API
- **OPENROUTER_API_KEY** - OpenRouter API

### 6.3 可选工具
- **浏览器** (用于 Cookie 提取) - Firefox (默认), Chrome, Edge, Safari

---

## 7. 非功能需求

### 7.1 性能
- 短视频 (< 20分钟) 处理时间: 5-15 分钟
- 长视频分割后并行处理: 提升整体速度

### 7.2 可靠性
- 支持断点续传 (通过 `--skip-*` 参数)
- 错误信息清晰，便于排查

### 7.3 可扩展性
- 模块化设计，便于二次开发
- 支持自定义提示词模板

---

## 8. 验收标准

### 8.1 功能验收
- [ ] 能够正确下载 Bilibili 视频
- [ ] 能够正确下载 YouTube 视频
- [ ] 能够处理本地视频文件
- [ ] 优先使用平台字幕，失败时回退 Whisper
- [ ] 视频 > 20 分钟时自动分割
- [ ] 正确识别并生成高光时刻
- [ ] 生成的剪辑可正常播放
- [ ] 艺术标题正确添加
- [ ] 封面图片正确生成

### 8.2 用户体验验收
- [ ] CLI 参数使用清晰
- [ ] Streamlit 界面可用
- [ ] Agent Skills 可正常工作
- [ ] 错误信息友好
- [ ] 进度显示准确

### 8.3 测试场景
1. **Bilibili URL 处理**: 使用真实 Bilibili 视频链接测试完整流程
2. **YouTube URL 处理**: 使用 YouTube 视频链接测试
3. **本地文件处理**: 使用本地 MP4 文件测试
4. **长视频分割**: 使用超过 20 分钟的视频测试分割
5. **Whisper 回退**: 测试平台字幕失败时的 Whisper 转录
6. **跳过步骤**: 测试 `--skip-download` 等参数
7. **多语言**: 测试 `--language en` 参数
