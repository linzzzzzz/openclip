#!/usr/bin/env python3
"""
Streamlit UI for OpenClip
Provides a web interface for video processing with AI-powered analysis
"""

import streamlit as st
import asyncio
import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Import the video orchestrator
from video_orchestrator import VideoOrchestrator
from core.config import API_KEY_ENV_VARS

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

# Define default data
DEFAULT_DATA = {
    # Checkboxes
    'use_background': False,
    'force_whisper': False,
    'skip_download': False,
    'skip_analysis': False,
    'generate_clips': True,
    'add_titles': True,
    'generate_cover': True,
    # Other form elements
    'input_type': "Video URL",
    'video_source': "",
    'llm_provider': "qwen",
    'api_key': "",
    'artistic_style': "crystal_ice",
    'max_duration': 20.0,
    'whisper_model': "base",
    'language': "zh",
    'browser': "firefox",
    'output_dir': "processed_videos",
    # Processing result
    'processing_result': None
}

# Initialize file if it doesn't exist
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w") as f:
        json.dump(DEFAULT_DATA, f, indent=2)

def load_from_file():
    with open(FILE_PATH, "r") as f:
        return json.load(f)

def save_to_file(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

# Load persistent data
data = load_from_file()

# Initialize reset counter in session state
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# Track if we just processed a video
just_processed = False

# Function to display results
def display_results(result):
    """Display processing results consistently"""
    if result.success:
        st.success("✅ Video processing completed successfully!")
        
        # Display processing time
        st.info(f"⏱️ Processing time: {result.processing_time:.2f} seconds")
        
        # Display video info
        if result.video_info:
            with st.expander("🎥 Video Information"):
                for key, value in result.video_info.items():
                    st.write(f"**{key.capitalize()}:** {value}")
        
        # Display transcript info
        if result.transcript_source:
            st.info(f"📝 Transcript source: {result.transcript_source}")
        
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
                        for i, moment in enumerate(moments[:5]):  # Show top 5
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
        st.error(f"❌ Processing failed: {result.error_message}")

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
    
    # Video input options
    input_type = st.radio(
        "Input Type",
        options=["Video URL", "Local File"],
        index=["Video URL", "Local File"].index(data['input_type']),
        key=f"input_type_{st.session_state.reset_counter}"
    )
    data['input_type'] = input_type
    
    if input_type == "Video URL":
        video_source = st.text_input(
            "Video URL",
            value=data['video_source'],
            placeholder="Enter Bilibili or YouTube URL",
            help="Supports Bilibili (https://www.bilibili.com/video/BV...) and YouTube (https://www.youtube.com/watch?v=...) URLs",
            key=f"video_source_{st.session_state.reset_counter}"
        )
        data['video_source'] = video_source
    else:
        uploaded_file = st.file_uploader(
            "Upload Video File",
            type=["mp4", "webm", "avi", "mov", "mkv"],
            help="Supports common video formats",
            key=f"uploaded_file_{st.session_state.reset_counter}"
        )
        if uploaded_file:
            # Save uploaded file to temporary location
            temp_dir = Path("./temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            video_source = str(temp_dir / uploaded_file.name)
            with open(video_source, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File uploaded: {uploaded_file.name}")
            data['video_source'] = video_source
        else:
            video_source = None
    
    # LLM provider selection
    llm_provider = st.selectbox(
        "LLM Provider",
        options=["qwen", "openrouter"],
        index=["qwen", "openrouter"].index(data['llm_provider']),
        help="Select which AI provider to use for analysis",
        key=f"llm_provider_{st.session_state.reset_counter}"
    )
    data['llm_provider'] = llm_provider
    
    # API key input (optional, since it can be set via environment variable)
    api_key_env_var = API_KEY_ENV_VARS.get(llm_provider, "QWEN_API_KEY")
    api_key = st.text_input(
        f"{llm_provider.upper()} API Key",
        value=data['api_key'],
        type="password",
        placeholder=f"Enter {api_key_env_var} or leave blank if set as environment variable",
        help=f"You can also set the {api_key_env_var} environment variable",
        key=f"api_key_{st.session_state.reset_counter}"
    )
    data['api_key'] = api_key
    
    # Artistic style selection
    artistic_styles = [
        "crystal_ice", "gradient_3d", "neon_glow", "metallic_gold", "rainbow_3d",
        "fire_flame", "metallic_silver", "glowing_plasma", "stone_carved", "glass_transparent"
    ]
    artistic_style = st.selectbox(
        "Artistic Style",
        options=artistic_styles,
        index=artistic_styles.index(data['artistic_style']),
        help="Select the visual style for titles and covers",
        key=f"artistic_style_{st.session_state.reset_counter}"
    )
    data['artistic_style'] = artistic_style
    
    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        max_duration = st.number_input(
            "Max Duration (minutes)",
            min_value=1.0,
            max_value=60.0,
            value=data['max_duration'],
            step=1.0,
            help="Videos longer than this will be split",
            key=f"max_duration_{st.session_state.reset_counter}"
        )
        data['max_duration'] = max_duration
    
        whisper_models = ["tiny", "base", "small", "medium", "large", "turbo"]
        whisper_model = st.selectbox(
            "Whisper Model",
            options=whisper_models,
            index=whisper_models.index(data['whisper_model']),
            help="Select Whisper model for transcript generation",
            key=f"whisper_model_{st.session_state.reset_counter}"
        )
        data['whisper_model'] = whisper_model
    
    with col2:
        languages = ["zh", "en"]
        language = st.selectbox(
            "Language",
            options=languages,
            index=languages.index(data['language']),
            help="Language for analysis and output",
            key=f"language_{st.session_state.reset_counter}"
        )
        data['language'] = language
    
        browsers = ["firefox", "chrome", "edge", "safari"]
        browser = st.selectbox(
            "Browser",
            options=browsers,
            index=browsers.index(data['browser']),
            help="Browser for cookie extraction (for Bilibili downloads)",
            key=f"browser_{st.session_state.reset_counter}"
        )
        data['browser'] = browser
    
    # Checkboxes for additional options
    use_background = st.checkbox(
        "Use Background Info",
        value=data['use_background'],
        help="Include streamer names and context for better analysis",
        key=f"use_background_{st.session_state.reset_counter}"
    )
    data['use_background'] = use_background
    
    force_whisper = st.checkbox(
        "Force Whisper",
        value=data['force_whisper'],
        help="Force transcript generation via Whisper (ignore platform subtitles)",
        key=f"force_whisper_{st.session_state.reset_counter}"
    )
    data['force_whisper'] = force_whisper
    
    skip_download = st.checkbox(
        "Skip Download",
        value=data['skip_download'],
        help="Skip video download (use existing downloaded video)",
        key=f"skip_download_{st.session_state.reset_counter}"
    )
    data['skip_download'] = skip_download
    
    skip_analysis = st.checkbox(
        "Skip Analysis",
        value=data['skip_analysis'],
        help="Skip engaging moments analysis (use existing analysis file)",
        key=f"skip_analysis_{st.session_state.reset_counter}"
    )
    data['skip_analysis'] = skip_analysis
    
    # Clip generation options
    generate_clips = st.checkbox(
        "Generate Clips",
        value=data['generate_clips'],
        help="Generate video clips from engaging moments",
        key=f"generate_clips_{st.session_state.reset_counter}"
    )
    data['generate_clips'] = generate_clips
    
    add_titles = st.checkbox(
        "Add Titles",
        value=data['add_titles'],
        help="Add artistic titles to clips",
        key=f"add_titles_{st.session_state.reset_counter}"
    )
    data['add_titles'] = add_titles
    
    generate_cover = st.checkbox(
        "Generate Covers",
        value=data['generate_cover'],
        help="Generate cover images for clips",
        key=f"generate_cover_{st.session_state.reset_counter}"
    )
    data['generate_cover'] = generate_cover
    
    # Output directory
    output_dir = st.text_input(
        "Output Directory",
        value=data['output_dir'],
        help="Directory for all processed outputs",
        key=f"output_dir_{st.session_state.reset_counter}"
    )
    data['output_dir'] = output_dir

    # Start Over button in sidebar
    st.divider()
    if st.button("🔄 Start Over"):
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

# Progress bar and status
progress_bar = st.progress(0)
status_text = st.empty()

# Process Video button
if st.button("Process Video", disabled=not video_source):
    if not video_source:
        st.error("Please provide a video URL or upload a file")
    else:
        try:
            # Get API key from input or environment
            if not api_key:
                api_key = os.getenv(api_key_env_var)
            
            if not api_key and not skip_analysis:
                st.error(f"Please provide {llm_provider.upper()} API key or set the {api_key_env_var} environment variable")
            else:
                # Initialize orchestrator
                orchestrator = VideoOrchestrator(
                    output_dir=output_dir,
                    max_duration_minutes=max_duration,
                    whisper_model=whisper_model,
                    browser=browser,
                    api_key=api_key,
                    llm_provider=llm_provider,
                    skip_analysis=skip_analysis,
                    generate_clips=generate_clips,
                    add_titles=add_titles,
                    artistic_style=artistic_style,
                    use_background=use_background,
                    generate_cover=generate_cover,
                    language=language,
                    debug=False
                )
                
                # Progress callback function
                def progress_callback(status: str, progress: float):
                    progress_bar.progress(min(int(progress), 100))
                    status_text.text(f"🔄 {status} ({progress:.1f}%)")
                
                # Process video
                status_text.text("Starting video processing...")
                
                # Run async process_video function
                import asyncio
                result = asyncio.run(orchestrator.process_video(
                    video_source,
                    force_whisper=force_whisper,
                    skip_download=skip_download,
                    progress_callback=progress_callback
                ))
                
                # Save result to file
                data['processing_result'] = {
                    'success': result.success,
                    'error_message': getattr(result, 'error_message', None),
                    'processing_time': getattr(result, 'processing_time', None),
                    'video_info': getattr(result, 'video_info', None),
                    'transcript_source': getattr(result, 'transcript_source', None),
                    'engaging_moments_analysis': getattr(result, 'engaging_moments_analysis', None),
                    'clip_generation': getattr(result, 'clip_generation', None),
                    'title_addition': getattr(result, 'title_addition', None),
                    'cover_generation': getattr(result, 'cover_generation', None)
                }
                save_to_file(data)
                
                # Display results
                st.header("📊 Results")
                display_results(result)
                
                # Mark that we just processed a video
                just_processed = True
                    
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())



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
