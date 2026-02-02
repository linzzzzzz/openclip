# Qwen API Integration

This directory contains sample code for integrating with the Qwen API for video processing and content generation tasks.

## Files

- `qwen_api_client.py` - Core Qwen API client with basic chat functionality
- `qwen_video_assistant.py` - Video-specific assistant that leverages Qwen for content analysis
- `README_qwen_integration.md` - This guide

## Setup

1. **Install dependencies:**
   ```bash
   cd whisper-env
   pip install requests
   # or if using uv:
   uv add requests
   ```

2. **Get your Qwen API key:**
   - Sign up at [Alibaba Cloud DashScope](https://dashscope.aliyuncs.com/)
   - Create an API key in your dashboard

3. **Set environment variable:**
   ```bash
   export QWEN_API_KEY="your-api-key-here"
   ```

## Usage Examples

### Basic Chat
```python
from qwen_api_client import QwenAPIClient

client = QwenAPIClient()
response = client.simple_chat("Hello, how are you?")
print(response)
```

### Video Content Analysis
```python
from qwen_video_assistant import QwenVideoAssistant

assistant = QwenVideoAssistant()

# Analyze a transcript
transcript = "Your video transcript here..."
analysis = assistant.analyze_transcript(transcript)
print(analysis)

# Generate engaging titles
titles = assistant.generate_engaging_titles(transcript, count=5)
for title in titles:
    print(f"- {title}")
```

### Integration with Existing Workflow

You can integrate this with your existing video processing scripts:

```python
# In your video processing script
from qwen_video_assistant import QwenVideoAssistant

# After generating transcript with Whisper
transcript = generate_transcript(video_file)  # Your existing function

# Use Qwen to enhance the content
assistant = QwenVideoAssistant()
titles = assistant.generate_engaging_titles(transcript)
description = assistant.generate_description(transcript, titles[0])
improved_subtitles = assistant.improve_subtitles(raw_subtitles)
```

## Available Models

The Qwen API supports several models:
- `qwen-turbo` - Fast and cost-effective (default)
- `qwen-plus` - Balanced performance and capability
- `qwen-max` - Most capable model
- `qwen-long` - For long context tasks

## Features

### QwenAPIClient
- Basic chat completion
- Multi-turn conversations
- Configurable parameters (temperature, max_tokens, etc.)
- Error handling and retries

### QwenVideoAssistant
- **Transcript Analysis**: Extract summaries, topics, tone, and metadata
- **Title Generation**: Create engaging, clickable titles
- **Clip Suggestions**: Identify interesting segments for short clips
- **Subtitle Improvement**: Enhance readability and grammar
- **Description Generation**: Create SEO-optimized video descriptions

## Error Handling

Both classes include comprehensive error handling:
- API key validation
- Network error handling
- Response format validation
- Graceful fallbacks for JSON parsing

## Testing

Run the demo scripts to test your setup:

```bash
python qwen_api_client.py
python qwen_video_assistant.py
```

## Integration Tips

1. **Rate Limiting**: Be mindful of API rate limits for batch processing
2. **Cost Management**: Use `qwen-turbo` for most tasks, upgrade to `qwen-plus` or `qwen-max` only when needed
3. **Context Length**: For long transcripts, consider chunking the content
4. **Caching**: Cache results for repeated analysis of the same content

## Next Steps

Consider extending the integration with:
- Batch processing for multiple videos
- Custom prompts for specific content types
- Integration with your existing video metadata storage
- Automated workflow triggers based on video processing events