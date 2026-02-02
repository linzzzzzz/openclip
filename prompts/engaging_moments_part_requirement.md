# Engaging Moments Analysis - Video Part

## Task
Analyze the provided video transcript and identify potential interesting and engaging moments from live streaming videos. Focus on segments that would be compelling for viewers and suitable for creating short clips.

## Requirements

### Content Guidelines
- Create **attractive and engaging** titles for each moment (no emojis, punctuation allowed)
- Titles should be in Chinese and avoid sensitive, negative, hate, or offensive words (e.g., no 复仇 in title)
- Co-hosting segments and interactive moments are usually most engaging
- 八卦 moments are usually engaging
- Include relevant transcript excerpts in Chinese
- Provide clear explanations for why each moment is engaging

### Duration Constraints
- Each engaging moment must be AT LEAST 30 seconds long
- Each engaging moment must be LESS THAN 4 minutes long

### Engagement Analysis
- Provide engagement levels: "high", "medium", or "low"
- Add relevant tags from: ["co-hosting", "interactive", "humorous", "live-chemistry", "funny", "highlight", "reaction", "gaming", "chat-interaction"]
- Include "why_engaging" explanations that describe what makes each moment compelling

## Analysis Instructions
1. Carefully review the entire transcript for interactive segments
2. Prioritize co-hosting moments, audience interactions, and humorous exchanges
3. Ensure each moment has clear entertainment value for clip creation
4. Focus on segments that would work well as standalone short videos
5. Provide detailed "why_engaging" explanations to justify selections
6. Use appropriate engagement levels and relevant tags
7. Extract meaningful transcript portions that capture the essence of each moment

## Output Format
Return your response as a JSON object following this exact structure:

```json
{
  "video_part": "part01",
  "engaging_moments": [
    {
      "title": "七人接力鉴定假发造型，现场即兴互动引爆弹幕高潮！",
      "start_time": "00:01:30",
      "end_time": "00:02:45",
      "duration_seconds": 75,
      "transcript": "Relevant transcript content for this moment...",
      "engagement_details": {
        "engagement_level": "high"
      },
      "why_engaging": "多人互动环节，现场气氛热烈，弹幕互动频繁，具有很强的娱乐性和观赏价值",
      "tags": ["co-hosting", "interactive", "humorous", "live-chemistry"]
    }
  ],
  "total_moments": 1,
  "analysis_timestamp": "2024-01-01T12:00:00Z"
}
```

## Field Specifications

### Required Fields for Each Moment:
- **title**: Compelling Chinese title without emojis
- **start_time**: Simple time format (HH:MM:SS or MM:SS) - NOT SRT format with milliseconds
- **end_time**: Simple time format (HH:MM:SS or MM:SS) - NOT SRT format with milliseconds
- **duration_seconds**: Integer duration in seconds
- **transcript**: Relevant transcript excerpt from the moment
- **engagement_details**: Object with "engagement_level" ("high", "medium", "low")
- **why_engaging**: Chinese explanation of what makes this moment compelling. Must be shorter than 100 characters.
- **tags**: Array of relevant tags from the approved list

### Engagement Level Guidelines:
- **"high"**: Exceptional moments with strong viewer appeal, multiple interactions, humor, or memorable content
- **"medium"**: Good moments with decent entertainment value and some interaction
- **"low"**: Mild interest moments that still meet minimum engagement criteria

## IMPORTANT: JSON Response Format
- Return ONLY valid JSON, no additional text or explanations
- Use the exact structure shown above
- Ensure all strings are properly quoted
- Do not include trailing commas
- Verify JSON syntax before responding