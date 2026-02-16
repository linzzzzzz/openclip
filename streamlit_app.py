#!/usr/bin/env python3
"""
Streamlit UI for OpenClip
Provides a web interface for video processing with AI-powered analysis
"""

import streamlit as st
import asyncio
import os
import json
import re
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any

# Import the video orchestrator
from video_orchestrator import VideoOrchestrator
from core.config import API_KEY_ENV_VARS, DEFAULT_LLM_PROVIDER, DEFAULT_TITLE_STYLE, MAX_DURATION_MINUTES, WHISPER_MODEL, MAX_CLIPS

# Set page config
st.set_page_config(
    page_title="OpenClip",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# File Helpers (Refresh/Server Restart Safe)
# --------------------------
FILE_PATH = "persistent_data.json"

# Define translation dictionaries
TRANSLATIONS = {
    'en': {
        'app_title': 'OpenClip',
        'sidebar_title': '🎬 OpenClip',
        'input_type': 'Input Type',
        'video_url': 'Video URL',
        'local_file_path': 'Local Video File Path',
        'llm_provider': 'LLM Provider',
        'api_key': 'API Key',
        'title_style': 'Title Style',
        'language': 'Output Language',
        'output_dir': 'Output Directory',
        'use_background': 'Use Background Info',
        'use_custom_prompt': 'Use Custom Highlight Analysis Prompt',
        'force_whisper': 'Force Whisper to Generate Subtitles',
        'generate_clips': 'Generate Clips',
        'max_clips': 'Max Clips',
        'add_titles': 'Add Video Top Banner Title',
        'generate_cover': 'Generate Cover',
        'process_video': '🎬 Process Video',
        'background_info': 'Background Information',
        'custom_highlight_prompt': 'Custom Highlight Analysis Prompt',
        'save_background': 'Save Background Information',
        'save_custom_prompt': 'Save Custom Highlight Analysis Prompt',
        'background_info_notice': 'Please ensure your background information is in the `prompts/background/background.md` file.',
        'background_info_warning': 'The system will use the content of `prompts/background/background.md` for analysis.',
        'background_file_path': 'Background information is stored in:',
        'custom_prompt_editor': 'Custom Highlight Analysis Prompt Editor',
        'custom_prompt_info': 'Edit the prompt below to customize how engaging moments are analyzed.',
        'custom_prompt_help': 'Edit the prompt to customize engaging moments analysis. This will be used instead of the default prompt.',
        'current_saved_prompt': 'Current saved prompt file:',
        'results': '📊 Results',
        'saved_results': '📊 Saved Results',
        'clear_results': 'Clear Saved Results',
        'processing_success': '✅ Video processing completed successfully!',
        'processing_time': '⏱️ Processing time:',
        'video_information': '🎥 Video Information',
        'transcript_source': '📝 Transcript source:',
        'error': '❌ Unexpected error:',
        'reset_form': '🔄 Reset Form',
        'confirmation': 'Are you sure you want to reset all settings?',
        'yes_reset': 'Yes, Reset',
        'cancel': 'Cancel',
        'reset_success': '✅ Form has been reset!',
        'background_info_config': 'Background Information Configuration',
        'background_info_edit': 'Edit the background information to provide context about streamers, nicknames, or recurring themes for better analysis.',
        'background_info_help': 'Enter information about streamers, their nicknames, games, and common terms to improve AI analysis.',
        'background_save_success': 'Background information saved successfully!',
        'background_save_error': 'Failed to save background information:',
        'custom_prompt_save_success': 'Custom highlight analysis prompt saved successfully!',
        'custom_prompt_save_error': 'Failed to save custom highlight analysis prompt:',
        'select_input_type': 'Select input type',
        'enter_video_url': 'Enter Bilibili or YouTube URL',
        'video_url_help': 'Supports Bilibili (https://www.bilibili.com/video/BV...) and YouTube (https://www.youtube.com/watch?v=...) URLs',
        'local_file_help': 'Enter the full path to a local video file',
        'local_file_srt_notice': 'To use existing subtitles, place the .srt file in the same directory with the same filename (e.g. video.mp4 → video.srt).',
        'select_llm_provider': 'Select which AI provider to use for analysis',
        'enter_api_key': 'Enter API key or leave blank if set as environment variable',
        'api_key_help': 'You can also set the API_KEY environment variable',
        'select_title_style': 'Select the visual style for titles and covers',
        'select_language': 'Language for analysis and output',
        'enter_output_dir': 'Directory to save processed videos',
        'force_whisper_help': 'Force transcript generation via Whisper (ignore platform subtitles)',
        'generate_clips_help': 'Generate video clips for engaging moments',
        'max_clips_help': 'Maximum number of highlight clips to generate',
        'add_titles_help': 'Add artistic titles to video clips (this step may be slow)',
        'generate_cover_help': 'Generate cover image for the video',
        'use_background_help': 'Use background information from prompts/background/background.md',
        'use_custom_prompt_help': 'Use custom prompt for highlight analysis',
        'advanced_config_notice': 'For advanced options (e.g. video split duration, Whisper model), edit `core/config.py`.',
        'clip_preview_title': 'Preview Generated Clips',
        'clip_preview_desc': 'Review the clips below. Uncheck any clips you don\'t want to include in title/cover generation.',
        'continue_with_clips': 'Continue with {count}/{total} clips',
        'skip_titles_covers': 'Skip Titles & Covers',
        'select_deselect_all': 'Select / Deselect All',
        'no_clips_selected': 'No clips selected. Select at least one clip to continue, or click "Skip" to finish.',
        'phase2_adding_titles_notice': 'Adding titles and generating covers for selected clips... This may take a few minutes.',
    },
    'zh': {
        'app_title': 'OpenClip',
        'sidebar_title': '🎬 OpenClip',
        'input_type': '输入类型',
        'video_url': '视频链接',
        'local_file_path': '本地视频文件路径',
        'llm_provider': 'LLM 提供商',
        'api_key': 'API 密钥',
        'title_style': '标题风格',
        'language': '输出语言',
        'output_dir': '输出目录',
        'use_background': '使用背景信息提示词',
        'use_custom_prompt': '使用自定义高光分析提示词',
        'force_whisper': '强制使用Whisper生成字幕',
        'generate_clips': '生成高光片段',
        'max_clips': '最大片段数',
        'add_titles': '添加视频上方横幅标题',
        'generate_cover': '生成封面',
        'process_video': '🎬 处理视频',
        'background_info': '背景信息',
        'custom_highlight_prompt': '自定义高光分析提示',
        'save_background': '保存背景信息',
        'save_custom_prompt': '保存自定义高光分析提示',
        'background_info_notice': '请确保您的背景信息在 `prompts/background/background.md` 文件中。',
        'background_info_warning': '系统将使用 `prompts/background/background.md` 文件的内容进行分析。',
        'background_file_path': '背景信息存储在：',
        'custom_prompt_editor': '自定义高光分析提示编辑器',
        'custom_prompt_info': '编辑下面的提示以自定义如何分析精彩时刻。',
        'custom_prompt_help': '编辑提示以自定义精彩时刻分析。这将替代默认提示。',
        'current_saved_prompt': '当前保存的提示文件：',
        'results': '📊 结果',
        'saved_results': '📊 保存的结果',
        'clear_results': '清除保存的结果',
        'processing_success': '✅ 视频处理成功完成！',
        'processing_time': '⏱️ 处理时间：',
        'video_information': '🎥 视频信息',
        'transcript_source': '📝 字幕来源：',
        'error': '❌ 意外错误：',
        'reset_form': '🔄 重置表单',
        'confirmation': '确定要重置所有设置吗？',
        'yes_reset': '是的，重置',
        'cancel': '取消',
        'reset_success': '✅ 表单已重置！',
        'background_info_config': '背景信息配置',
        'background_info_edit': '编辑背景信息以提供有关主播、昵称或 recurring themes 的上下文，以获得更好的分析。',
        'background_info_help': '输入有关主播、他们的昵称、游戏和常用术语的信息，以改善 AI 分析。',
        'background_save_success': '背景信息保存成功！',
        'background_save_error': '保存背景信息失败：',
        'custom_prompt_save_success': '自定义高光分析提示保存成功！',
        'custom_prompt_save_error': '保存自定义高光分析提示失败：',
        'select_input_type': '选择输入类型',
        'enter_video_url': '输入 B 站或 YouTube 链接',
        'video_url_help': '支持 B 站 (https://www.bilibili.com/video/BV...) 和 YouTube (https://www.youtube.com/watch?v=...) 链接',
        'local_file_help': '输入本地视频文件的完整路径',
        'local_file_srt_notice': '如需使用已有字幕，请将 .srt 文件放在同目录下，文件名保持一致（如 video.mp4 → video.srt）。',
        'select_llm_provider': '选择用于分析的 AI 提供商',
        'enter_api_key': '输入 API 密钥或留空（如果已设置为环境变量）',
        'api_key_help': '您也可以设置 API_KEY 环境变量',
        'select_title_style': '选择标题和封面的视觉风格',
        'select_language': '分析和输出的语言',
        'enter_output_dir': '保存处理后视频的目录',
        'force_whisper_help': '强制通过 Whisper 生成字幕（忽略平台字幕）',
        'generate_clips_help': '为精彩时刻生成视频片段',
        'max_clips_help': '生成高光片段的最大数量',
        'add_titles_help': '为视频片段添加艺术标题（此步骤可能较慢）',
        'generate_cover_help': '为视频生成封面图像',
        'use_background_help': '使用 prompts/background/background.md 中的背景信息',
        'use_custom_prompt_help': '使用自定义提示进行高光分析',
        'advanced_config_notice': '如需调整高级选项（如视频分割时长、Whisper 模型），请编辑 `core/config.py`。',
        'clip_preview_title': '预览生成的片段',
        'clip_preview_desc': '查看下方片段，取消勾选不需要添加标题和封面的片段。',
        'continue_with_clips': '继续处理 {count}/{total} 个片段',
        'skip_titles_covers': '跳过标题和封面',
        'select_deselect_all': '全选 / 取消全选',
        'no_clips_selected': '未选择任何片段。请至少选择一个片段继续，或点击"跳过"完成。',
        'phase2_adding_titles_notice': '正在为选中的片段添加标题和生成封面……这可能需要几分钟。',
    }
}

# Define default data
DEFAULT_DATA = {
    # Checkboxes
    'use_background': False,
    'use_custom_prompt': False,
    'force_whisper': False,
    'generate_clips': True,
    'max_clips': MAX_CLIPS,
    'add_titles': True,
    'generate_cover': True,
    # Other form elements
    'input_type': "Video URL",
    'video_source': "",
    'llm_provider': DEFAULT_LLM_PROVIDER,
    'api_key': "",
    'title_style': DEFAULT_TITLE_STYLE,
    'language': "zh",
    'output_dir': "processed_videos",
    'custom_prompt_file': None,
    'custom_prompt_text': "",
    # Language setting
    'ui_language': "zh",
    # Processing result
    'processing_result': None
}

# Initialize file if it doesn't exist
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w") as f:
        json.dump(DEFAULT_DATA, f, indent=2)

def load_from_file():
    with open(FILE_PATH, "r") as f:
        saved = json.load(f)
    # Backfill any new default keys missing from older saved files
    for key, value in DEFAULT_DATA.items():
        if key not in saved:
            saved[key] = value
    return saved

def save_to_file(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

# Load persistent data
data = load_from_file()

# Initialize UI language if not present
if 'ui_language' not in data:
    data['ui_language'] = 'zh'
    save_to_file(data)

# Get current language
current_lang = data.get('ui_language', 'zh')
t = TRANSLATIONS[current_lang]

# Initialize reset counter in session state
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# Initialize processing state
if 'processing' not in st.session_state:
    st.session_state.processing = False
    st.session_state.cancel_event = threading.Event()
    st.session_state.processing_thread = None
    st.session_state.processing_outcome = {'result': None, 'error': None}
    st.session_state.progress_state = {'status': '', 'progress': 0}

# Initialize clip preview/selection state (two-phase processing)
if 'clip_preview_mode' not in st.session_state:
    st.session_state.clip_preview_mode = False
    st.session_state.phase1_result = None
    st.session_state.phase1_params = None
    st.session_state.clip_selections = {}
    st.session_state.phase2_processing = False
    st.session_state.phase2_thread = None
    st.session_state.phase2_outcome = {'result': None, 'error': None}
    st.session_state.phase2_progress = {'status': '', 'progress': 0}

# Track if we just processed a video
just_processed = False

# Function to display results
def display_results(result):
    """Display processing results consistently"""
    if result.success:
        st.success(t['processing_success'])
        
        # Display processing time
        st.info(f"{t['processing_time']} {result.processing_time:.2f} seconds")
        
        # Display video info
        if result.video_info:
            with st.expander(t['video_information']):
                for key, value in result.video_info.items():
                    st.write(f"**{key.capitalize()}:** {value}")
        
        # Display transcript info
        if result.transcript_source:
            st.info(f"{t['transcript_source']} {result.transcript_source}")
        
        # Display analysis info
        if result.engaging_moments_analysis:
            analysis = result.engaging_moments_analysis
            with st.expander("🧠 Analysis Results"):
                st.write(f"Total parts analyzed: {analysis.get('total_parts_analyzed', 0)}")
                if analysis.get('top_moments'):
                    moments = analysis['top_moments']
                    if isinstance(moments, dict) and 'top_engaging_moments' in moments:
                        moments = moments['top_engaging_moments']
                    
                    if isinstance(moments, list):
                        st.write(f"Found {len(moments)} engaging moments")
                        for i, moment in enumerate(moments):
                            with st.container():
                                st.subheader(f"Rank {i+1}: {moment.get('title', 'Untitled')}")
                                if 'description' in moment:
                                    st.write(moment['description'])
                                if 'timestamp' in moment:
                                    st.write(f"Timestamp: {moment['timestamp']}")
        
        # Display clip info
        output_dir = None
        if result.clip_generation and result.clip_generation.get('success'):
            clips = result.clip_generation
            with st.expander("🎬 Generated Clips"):
                st.write(f"Generated {clips.get('total_clips', 0)} clips")
                if clips.get('clips_info'):
                    output_dir = Path(clips.get('output_dir', ''))
                    # Create columns for side-by-side display (2 per row) with minimal gap
                    cols = st.columns(2, gap="xxsmall")
                    for i, clip in enumerate(clips['clips_info']):
                        clip_filename = clip.get('filename')
                        if clip_filename:
                            clip_path = output_dir / clip_filename
                            if clip_path.exists():
                                with cols[i % 2]:
                                    st.video(str(clip_path), width=450)
                                    st.caption(f"**{clip.get('title', 'Untitled')}**")
        
        # Display title info
        if result.title_addition and result.title_addition.get('success'):
            titles = result.title_addition
            with st.expander("🎨 Clips with Titles"):
                st.write(f"Added titles to {titles.get('total_clips', 0)} clips")
                if titles.get('processed_clips'):
                    output_dir = Path(titles.get('output_dir', ''))
                    # Create columns for side-by-side display (2 per row) with minimal gap
                    cols = st.columns(2, gap="xxsmall")
                    for i, clip in enumerate(titles['processed_clips']):
                        clip_filename = clip.get('filename')
                        if clip_filename:
                            clip_path = output_dir / clip_filename
                            if clip_path.exists():
                                with cols[i % 2]:
                                    st.video(str(clip_path), width=450)
                                    st.caption(f"**{clip.get('title', 'Untitled')}**")
        
        # Display cover info
        if result.cover_generation and result.cover_generation.get('success'):
            covers = result.cover_generation
            with st.expander("🖼️ Generated Covers"):
                st.write(f"Generated {covers.get('total_covers', 0)} cover images")
                if covers.get('covers'):
                    cols = st.columns(2, gap="xxsmall")
                    for i, cover in enumerate(covers['covers']):
                        cover_path = cover.get('path')
                        if cover_path and Path(cover_path).exists():
                            with cols[i % 2]:
                                st.image(cover_path, caption=cover.get('title', 'Untitled'), width=450)
        
        # Display output directory
        if output_dir:
            st.info(f"📁 All outputs saved to: {output_dir}")
    else:
        st.error(f"{t['error']} {result.error_message}")

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
    }
    .stFileUploader > label {
        color: #333;
        font-weight: bold;
    }
    .stTextInput > label {
        font-weight: bold;
    }
    .stSelectbox > label {
        font-weight: bold;
    }
    .stCheckbox > label {
        font-weight: bold;
    }
    /* Smaller font for clip preview checkboxes in the main area */
    .stMainBlockContainer .stCheckbox label p {
        font-size: 0.8rem !important;
    }
    .video-container {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .result-card {
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        background-color: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    /* Reduce spacing between columns */
    .stColumns > div {
        gap: 0.25rem !important;
    }
    /* Target column containers directly */
    .stColumn {
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Reduce margin around videos */
    .stVideo {
        margin-bottom: 0.5rem !important;
        margin-right: 0 !important;
        margin-left: 0 !important;
    }
    /* Reduce margin around text under videos */
    .stMarkdown {
        margin-bottom: 0.5rem !important;
        margin-right: 0 !important;
        margin-left: 0 !important;
    }
    /* Reduce padding in expander content */
    .streamlit-expanderContent {
        padding: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎬 OpenClip")
st.markdown("""
A lightweight automated video processing pipeline that identifies and extracts the most engaging moments from long-form videos (especially livestream recordings). Uses AI-powered analysis to find highlights, generates clips, and adds artistic titles.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # UI Language Selector
    ui_language = st.selectbox(
        "UI Language",
        options=["English", "中文"],
        index=["English", "中文"].index("中文" if current_lang == "zh" else "English"),
        help="Select language for the user interface",
        key=f"ui_language_{st.session_state.reset_counter}"
    )
    new_lang = "zh" if ui_language == "中文" else "en"
    if new_lang != current_lang:
        data['ui_language'] = new_lang
        save_to_file(data)
        st.rerun()
    
    st.divider()
    
    # Video input options
    input_type = st.radio(
        t['input_type'],
        options=["Video URL", "Local File"],
        index=["Video URL", "Local File"].index(data['input_type']),
        key=f"input_type_{st.session_state.reset_counter}"
    )
    data['input_type'] = input_type
    
    if input_type == "Video URL":
        video_source = st.text_input(
            t['video_url'],
            value=data['video_source'],
            placeholder=t['enter_video_url'],
            help=t['video_url_help'],
            key=f"video_source_{st.session_state.reset_counter}"
        )
        data['video_source'] = video_source
    else:
        video_source = st.text_input(
            t['local_file_path'],
            value="" if data['input_type'] != "Local File" else data.get('video_source', ""),
            help=t['local_file_help'],
            key=f"local_file_path_{st.session_state.reset_counter}"
        )
        st.caption(t['local_file_srt_notice'])
        data['video_source'] = video_source
    
    # LLM provider selection
    llm_provider = st.selectbox(
        t['llm_provider'],
        options=["qwen", "openrouter"],
        index=["qwen", "openrouter"].index(data['llm_provider']),
        help=t['select_llm_provider'],
        key=f"llm_provider_{st.session_state.reset_counter}"
    )
    data['llm_provider'] = llm_provider
    
    # API key input (optional, since it can be set via environment variable)
    api_key_env_var = API_KEY_ENV_VARS.get(llm_provider, "QWEN_API_KEY")
    api_key = st.text_input(
        f"{llm_provider.upper()} {t['api_key']}",
        value=data['api_key'],
        type="password",
        placeholder=t['enter_api_key'],
        help=t['api_key_help'],
        key=f"api_key_{st.session_state.reset_counter}"
    )
    data['api_key'] = api_key
    
    title_style = data['title_style']

    # Additional options
    languages = ["zh", "en"]
    language = st.selectbox(
        t['language'],
        options=languages,
        index=languages.index(data['language']),
        help=t['select_language'],
        key=f"language_{st.session_state.reset_counter}"
    )
    data['language'] = language

    # Clip generation options (always enabled)
    generate_clips = True
    data['generate_clips'] = generate_clips

    max_clips = st.number_input(
        t['max_clips'],
        min_value=1,
        max_value=20,
        value=int(data['max_clips']),
        step=1,
        help=t['max_clips_help'],
        key=f"max_clips_{st.session_state.reset_counter}"
    )
    data['max_clips'] = max_clips

    # Output directory
    output_dir = st.text_input(
        t['output_dir'],
        value=data['output_dir'],
        help=t['enter_output_dir'],
        key=f"output_dir_{st.session_state.reset_counter}"
    )
    data['output_dir'] = output_dir

    # Checkboxes for additional options
    add_titles = st.checkbox(
        t['add_titles'],
        value=data['add_titles'],
        help=t['add_titles_help'],
        key=f"add_titles_{st.session_state.reset_counter}"
    )
    data['add_titles'] = add_titles
    
    generate_cover = st.checkbox(
        t['generate_cover'],
        value=data['generate_cover'],
        help=t['generate_cover_help'],
        key=f"generate_cover_{st.session_state.reset_counter}"
    )
    data['generate_cover'] = generate_cover

    use_background = st.checkbox(
        t['use_background'],
        value=data['use_background'],
        help=t['use_background_help'],
        key=f"use_background_{st.session_state.reset_counter}"
    )
    data['use_background'] = use_background

    # Background info notice (only shown if use_background is checked)
    if use_background:
        # st.subheader("📝 Background Information")
        st.info(t['background_info_notice'])
    
    # Custom prompt file option
    use_custom_prompt = st.checkbox(
        t['use_custom_prompt'],
        value=data.get('use_custom_prompt', False),
        help=t['use_custom_prompt_help'],
        key=f"use_custom_prompt_{st.session_state.reset_counter}"
    )
    data['use_custom_prompt'] = use_custom_prompt
    
    # Initialize custom_prompt_text if not present
    if 'custom_prompt_text' not in data:
        data['custom_prompt_text'] = ""

    force_whisper = st.checkbox(
        t['force_whisper'],
        value=data['force_whisper'],
        help=t['force_whisper_help'],
        key=f"force_whisper_{st.session_state.reset_counter}"
    )
    data['force_whisper'] = force_whisper

    st.caption(t['advanced_config_notice'])

    # Start Over button in sidebar
    st.divider()
    if st.button(t['reset_form']):
        # Reset all data to defaults
        for key, value in DEFAULT_DATA.items():
            data[key] = value
        save_to_file(data)
        # Increment reset counter to force widget recreation
        st.session_state.reset_counter += 1
        # Force a rerun
        st.rerun()

    # Save data to file
    save_to_file(data)

# Main content area
st.header("▶️ Process Video")

# Custom prompt editor (shown only if use_custom_prompt is checked)
custom_prompt_file = data.get('custom_prompt_file')
if use_custom_prompt:
    st.subheader(t['custom_prompt_editor'])
    st.info(t['custom_prompt_info'])
    
    # Load default prompt if custom prompt text is empty
    if not data.get('custom_prompt_text'):
        default_prompt_path = Path("./prompts/engaging_moments_part_requirement.md")
        if default_prompt_path.exists():
            with open(default_prompt_path, 'r', encoding='utf-8') as f:
                data['custom_prompt_text'] = f.read()
    
    # Text area for custom prompt
    custom_prompt_text = st.text_area(
        t['custom_highlight_prompt'],
        value=data['custom_prompt_text'],
        height=500,
        help=t['custom_prompt_help'],
        key=f"custom_prompt_text_{st.session_state.reset_counter}"
    )
    data['custom_prompt_text'] = custom_prompt_text
    
    # Save button for custom prompt
    if st.button("💾 Save Prompt", key=f"save_custom_prompt_{st.session_state.reset_counter}"):
        if custom_prompt_text:
            try:
                # Create temp directory if it doesn't exist
                temp_dir = Path("./temp_prompts")
                temp_dir.mkdir(exist_ok=True)
                
                # Generate unique filename with timestamp
                custom_prompt_file = str(temp_dir / f"custom_highlight_prompt_{int(time.time())}.md")
                
                # Write custom prompt to file
                with open(custom_prompt_file, "w", encoding='utf-8') as f:
                    f.write(custom_prompt_text)
                
                # Save file path to data
                data['custom_prompt_file'] = custom_prompt_file
                
                # Show success message
                st.success(f"✅ {t['custom_prompt_save_success']}")
                st.caption(f"Saved to: {custom_prompt_file}")
            except Exception as e:
                st.error(f"❌ {t['custom_prompt_save_error']} {str(e)}")
        else:
            st.warning("⚠️ Please enter a highlight analysis prompt before saving.")
    
    # Show current saved prompt file if exists
    if custom_prompt_file and Path(custom_prompt_file).exists():
        st.info(f"{t['current_saved_prompt']} {Path(custom_prompt_file).name}")

# Progress bar and status — restore last known state so widgets don't reset on rerun
_ps = st.session_state.progress_state
progress_bar = st.progress(min(int(_ps['progress']), 100))
status_text = st.empty()
if _ps['status']:
    status_text.text(_ps['status'])
    # Show notice when adding titles (this step is slow)
    if "Adding titles" in _ps['status']:
        st.info("⏳ Adding titles to clips... This step may take a few minutes. Please be patient.")

# Process Video / Cancel buttons
btn_col1, btn_col2 = st.columns([3, 1])
is_processing = st.session_state.processing

with btn_col1:
    process_clicked = st.button(
        t['process_video'],
        disabled=not video_source or is_processing
    )

with btn_col2:
    cancel_clicked = st.button(
        t['cancel'],
        disabled=not is_processing
    )

# --- Handle Cancel ---
if cancel_clicked and is_processing:
    st.session_state.cancel_event.set()
    status_text.text("⏹️ Cancelling...")

# --- Handle Start ---
if process_clicked and not is_processing:
    if not video_source:
        st.error("Please provide a video URL or upload a file")
    else:
        # Get API key from input or environment
        resolved_api_key = api_key or os.getenv(api_key_env_var)

        if not resolved_api_key:
            st.error(f"Please provide {llm_provider.upper()} API key or set the {api_key_env_var} environment variable")
        else:
            # Reset cancel event and state
            st.session_state.cancel_event = threading.Event()
            st.session_state.processing_outcome = {'result': None, 'error': None}
            st.session_state.progress_state = {'status': '', 'progress': 0}

            _cancel_event = st.session_state.cancel_event
            # Grab direct references so the background thread can
            # mutate dicts in-place without needing st.session_state.
            _progress = st.session_state.progress_state
            _outcome = st.session_state.processing_outcome

            # Build progress callback with cancellation check.
            # Mutates _progress dict in-place — the main thread reads
            # the same object on each rerun to render the widgets.
            def progress_callback(status: str, progress: float):
                if _cancel_event.is_set():
                    raise Exception("Processing cancelled by user")
                clean_status = re.sub(r'\x1b\[[0-9;]*m', '', status)
                _progress['status'] = f"🔄 {clean_status} ({progress:.1f}%)"
                _progress['progress'] = progress

            # Determine if we need the clip preview step
            # Preview is shown when clips are generated AND titles or covers are requested
            needs_preview = generate_clips and (add_titles or generate_cover)

            if needs_preview:
                # Save original prefs for Phase 2; disable titles/covers in Phase 1
                st.session_state.phase1_params = {
                    'add_titles': add_titles,
                    'generate_cover': generate_cover,
                    'title_style': title_style,
                    'output_dir': output_dir,
                    'api_key': resolved_api_key,
                    'llm_provider': llm_provider,
                    'language': language,
                    'use_background': use_background,
                    'max_clips': max_clips,
                }
            else:
                st.session_state.phase1_params = None

            # Snapshot all parameters for the background thread
            _params = dict(
                output_dir=output_dir,
                max_duration_minutes=MAX_DURATION_MINUTES,
                whisper_model=WHISPER_MODEL,
                api_key=resolved_api_key,
                llm_provider=llm_provider,
                generate_clips=generate_clips,
                add_titles=False if needs_preview else add_titles,
                title_style=title_style,
                use_background=use_background,
                generate_cover=False if needs_preview else generate_cover,
                language=language,
                custom_prompt_file=custom_prompt_file,
                max_clips=max_clips,
                video_source=video_source,
                force_whisper=force_whisper,
            )

            def _run_processing():
                try:
                    p = _params
                    orchestrator = VideoOrchestrator(
                        output_dir=p['output_dir'],
                        max_duration_minutes=p['max_duration_minutes'],
                        whisper_model=p['whisper_model'],
                        browser="firefox",
                        api_key=p['api_key'],
                        llm_provider=p['llm_provider'],
                        skip_analysis=False,
                        generate_clips=p['generate_clips'],
                        add_titles=p['add_titles'],
                        title_style=p['title_style'],
                        use_background=p['use_background'],
                        generate_cover=p['generate_cover'],
                        language=p['language'],
                        debug=False,
                        custom_prompt_file=p['custom_prompt_file'],
                        max_clips=p['max_clips'],
                    )
                    result = asyncio.run(orchestrator.process_video(
                        p['video_source'],
                        force_whisper=p['force_whisper'],
                        skip_download=False,
                        progress_callback=progress_callback,
                    ))
                    _outcome['result'] = result
                except Exception as e:
                    _outcome['error'] = e

            thread = threading.Thread(target=_run_processing, daemon=True)
            st.session_state.processing_thread = thread
            st.session_state.processing = True
            status_text.text("Starting video processing...")
            thread.start()
            st.rerun()

# --- Polling loop while processing ---
if is_processing:
    thread = st.session_state.processing_thread
    if thread is not None and thread.is_alive():
        time.sleep(0.5)
        st.rerun()
    else:
        # Thread finished — update state and rerun so buttons re-render correctly
        st.session_state.processing = False
        st.rerun()

# --- Helper to save and display final results ---
def _finalize_results(result):
    data['processing_result'] = {
        'success': result.success,
        'error_message': getattr(result, 'error_message', None),
        'processing_time': getattr(result, 'processing_time', None),
        'video_info': getattr(result, 'video_info', None),
        'transcript_source': getattr(result, 'transcript_source', None),
        'engaging_moments_analysis': getattr(result, 'engaging_moments_analysis', None),
        'clip_generation': getattr(result, 'clip_generation', None),
        'title_addition': getattr(result, 'title_addition', None),
        'cover_generation': getattr(result, 'cover_generation', None),
    }
    save_to_file(data)

# --- Handle finished processing result (runs on the rerun after thread completes) ---
_outcome = st.session_state.processing_outcome
_finished_result = _outcome['result']
_finished_error = _outcome['error']
if not is_processing and (_finished_result is not None or _finished_error is not None):
    # Clear stored outcome so this block only runs once
    _outcome['result'] = None
    _outcome['error'] = None

    if _finished_error is not None:
        st.error(f"❌ Unexpected error: {str(_finished_error)}")
    elif _finished_result is not None:
        if getattr(_finished_result, 'error_message', None) and 'cancelled' in _finished_result.error_message.lower():
            st.warning("⏹️ Processing was cancelled.")
        elif _finished_result.success:
            # Check if we need the clip preview step
            clip_gen = getattr(_finished_result, 'clip_generation', None)
            has_clips = clip_gen and clip_gen.get('success') and clip_gen.get('clips_info')
            if st.session_state.phase1_params and has_clips:
                # Enter clip preview mode instead of showing final results
                st.session_state.clip_preview_mode = True
                st.session_state.phase1_result = _finished_result
                st.session_state.clip_selections = {
                    i: True for i in range(len(clip_gen['clips_info']))
                }
                st.rerun()
            else:
                # No preview needed — finalize directly
                _finalize_results(_finished_result)
                st.header("📊 Results")
                display_results(_finished_result)
                just_processed = True
        else:
            st.error(f"❌ Processing failed: {getattr(_finished_result, 'error_message', 'Unknown error')}")

# --- Clip Preview UI (between Phase 1 and Phase 2) ---
if st.session_state.clip_preview_mode and not st.session_state.phase2_processing:
    phase1_result = st.session_state.phase1_result
    clip_gen = phase1_result.clip_generation

    if clip_gen and clip_gen.get('clips_info'):
        st.header(t['clip_preview_title'])
        st.write(t['clip_preview_desc'])

        clips_info = clip_gen['clips_info']
        output_dir_path = Path(clip_gen.get('output_dir', ''))

        # Display clips in 2-column grid with checkboxes
        cols = st.columns(2, gap="small")
        for i, clip in enumerate(clips_info):
            clip_filename = clip.get('filename')
            if clip_filename:
                clip_path = output_dir_path / clip_filename
                if clip_path.exists():
                    with cols[i % 2]:
                        title = clip.get('title', 'Untitled')
                        rank = clip.get('rank', i + 1)
                        # Truncate title to keep checkbox labels single-line
                        max_label_len = 25
                        short_title = title if len(title) <= max_label_len else title[:max_label_len] + '...'
                        selected = st.checkbox(
                            f"Rank {rank}: {short_title}",
                            value=st.session_state.clip_selections.get(i, True),
                            key=f"clip_select_{i}"
                        )
                        st.session_state.clip_selections[i] = selected
                        st.video(str(clip_path), width=450)
                        duration = clip.get('duration', 'N/A')
                        engagement = clip.get('engagement_level', 'N/A')
                        st.caption(f"**{title}** | Duration: {duration} | Engagement: {engagement}")

        # Count selected clips
        selected_count = sum(1 for v in st.session_state.clip_selections.values() if v)
        total_count = len(clips_info)

        # Action buttons
        btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 2])

        with btn_col1:
            continue_label = t['continue_with_clips'].format(count=selected_count, total=total_count)
            continue_clicked = st.button(
                continue_label,
                disabled=(selected_count == 0),
                type="primary"
            )

        with btn_col2:
            skip_clicked = st.button(t['skip_titles_covers'])

        with btn_col3:
            toggle_clicked = st.button(t['select_deselect_all'])

        if toggle_clicked:
            all_selected = all(st.session_state.clip_selections.values())
            for k in st.session_state.clip_selections:
                st.session_state.clip_selections[k] = not all_selected
            st.rerun()

        if selected_count == 0:
            st.warning(t['no_clips_selected'])

        if skip_clicked:
            # Finalize with Phase 1 results only (no titles/covers)
            _finalize_results(phase1_result)
            st.session_state.clip_preview_mode = False
            st.session_state.phase1_result = None
            st.session_state.phase1_params = None
            st.session_state.clip_selections = {}
            st.rerun()

        if continue_clicked and selected_count > 0:
            # Collect selected ranks and launch Phase 2
            selected_indices = [
                i for i, sel in st.session_state.clip_selections.items() if sel
            ]
            selected_ranks = [clips_info[i]['rank'] for i in selected_indices]

            p1_params = st.session_state.phase1_params
            engaging_result = phase1_result.engaging_moments_analysis

            st.session_state.phase2_processing = True
            st.session_state.phase2_outcome = {'result': None, 'error': None}
            st.session_state.phase2_progress = {'status': '', 'progress': 0}

            _p2_progress = st.session_state.phase2_progress
            _p2_outcome = st.session_state.phase2_outcome
            _cancel_event = st.session_state.cancel_event

            def _phase2_progress_cb(status, progress):
                if _cancel_event.is_set():
                    raise Exception("Processing cancelled by user")
                clean = re.sub(r'\x1b\[[0-9;]*m', '', status)
                _p2_progress['status'] = f"🔄 {clean} ({progress:.1f}%)"
                _p2_progress['progress'] = progress

            _p2_selected_ranks = selected_ranks
            _p2_phase1_result = phase1_result
            _p2_engaging_result = engaging_result
            _p2_params = p1_params

            def _run_phase2():
                try:
                    orchestrator = VideoOrchestrator(
                        output_dir=_p2_params['output_dir'],
                        add_titles=_p2_params['add_titles'],
                        title_style=_p2_params['title_style'],
                        generate_cover=_p2_params['generate_cover'],
                        api_key=_p2_params['api_key'],
                        llm_provider=_p2_params['llm_provider'],
                        language=_p2_params['language'],
                        use_background=_p2_params['use_background'],
                        max_clips=_p2_params['max_clips'],
                        generate_clips=False,
                        skip_analysis=True,
                    )
                    result = orchestrator.process_titles_and_covers(
                        _p2_phase1_result,
                        _p2_engaging_result,
                        _p2_selected_ranks,
                        progress_callback=_phase2_progress_cb,
                    )
                    _p2_outcome['result'] = result
                except Exception as e:
                    _p2_outcome['error'] = e

            thread = threading.Thread(target=_run_phase2, daemon=True)
            st.session_state.phase2_thread = thread
            thread.start()
            st.rerun()

# --- Phase 2 polling loop ---
if st.session_state.phase2_processing:
    p2_ps = st.session_state.phase2_progress
    progress_bar.progress(min(int(p2_ps['progress']), 100))
    if p2_ps['status']:
        status_text.text(p2_ps['status'])
        if "Adding titles" in p2_ps['status']:
            st.info(t['phase2_adding_titles_notice'])

    thread = st.session_state.phase2_thread
    if thread is not None and thread.is_alive():
        time.sleep(0.5)
        st.rerun()
    else:
        # Phase 2 finished
        st.session_state.phase2_processing = False
        p2_outcome = st.session_state.phase2_outcome

        if p2_outcome.get('error'):
            st.error(f"❌ Error: {p2_outcome['error']}")
        elif p2_outcome.get('result'):
            merged_result = p2_outcome['result']
            _finalize_results(merged_result)
            st.header("📊 Results")
            display_results(merged_result)
            just_processed = True

        # Clean up preview state
        st.session_state.clip_preview_mode = False
        st.session_state.phase1_result = None
        st.session_state.phase1_params = None
        st.session_state.clip_selections = {}
        st.session_state.phase2_outcome = {'result': None, 'error': None}
        st.session_state.phase2_progress = {'status': '', 'progress': 0}

# Display saved results if they exist and we didn't just process a video
if data['processing_result'] and not just_processed:
    st.header("📊 Saved Results")
    # Convert dictionary back to object-like structure
    class ResultObject:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)

    result_obj = ResultObject(data['processing_result'])
    display_results(result_obj)
    
    # Add a button to clear saved results
    if st.button("Clear Saved Results"):
        data['processing_result'] = None
        save_to_file(data)
        st.rerun()

# Footer
st.markdown("""
---
**Made with ❤️ for content creators**
""")

# GitHub buttons row
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    st.markdown("""
    <a href="https://github.com/linzzzzzz/openclip/issues" target="_blank" style="text-decoration: none;">
        <button style="
            background-color: transparent;
            color: #58a6ff;
            border: none;
            outline: none;
            box-shadow: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            <span>🐛</span> Report Bug
        </button>
    </a>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <a href="https://github.com/linzzzzzz/openclip" target="_blank" style="text-decoration: none;">
        <button style="
            background-color: transparent;
            color: #f0883e;
            border: none;
            outline: none;
            box-shadow: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        ">
            <span>⭐</span> Star on GitHub
        </button>
    </a>
    """, unsafe_allow_html=True)
