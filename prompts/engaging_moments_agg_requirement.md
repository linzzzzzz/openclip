# Top Engaging Moments Aggregation

## Task
Review all the highlights from multiple video parts and identify the top {max_clips} most engaging moments. Aggregate and rank them based on engagement potential, content quality, and viewer appeal.

---

## General Ranking Criteria (Always Apply)

These universal criteria apply to ALL content types:

### Primary Factors:
- **Engagement Level**: Moments rated "high" should be prioritized
- **Content Quality**: Clear, complete segments with strong entertainment value
- **Viewer Appeal**: Moments that would perform well as standalone clips
- **Memorability**: Unique or standout content that's likely to be shared

### Secondary Factors:
- **Duration**: Optimal 45-180 seconds for short-form content
- **Standalone Viability**: Can the clip be understood without context?
- **Emotional Impact**: Does it evoke laughter, surprise, or inspiration?
- **Information Density**: Does it contain valuable or surprising information?

---

## Type-Specific Ranking Criteria (Complement General)

In addition to the general criteria above, apply these type-specific nuances based on dominant content type:

### For ENTERTAINMENT:
- Prioritize complete jokes with setup, punchline, and reaction
- Value game climaxes and unexpected twists
- Consider audience reaction intensity

### For KNOWLEDGE:
- Prioritize "aha moments" and key insights
- Value actionable tips and practical applications
- Consider educational impact

### For SPEECH:
- Prioritize emotional peaks and inspirational moments
- Value memorable quotes and powerful statements
- Consider storytelling impact

### For OPINION:
- Prioritize strong, controversial viewpoints
- Value debates and disagreements
- Consider thought-provoking content

### For EXPERIENCE:
- Prioritize emotional depth and personal stories
- Value relatable moments
- Consider personal revelations

### For BUSINESS:
- Prioritize expert insights and valuable advice
- Value actionable strategies
- Consider professional impact

### For CONTENT_REVIEW:
- Prioritize unique opinions and surprising takes
- Value bold predictions
- Consider entertainment value of critique

---

## Requirements

### Selection Criteria
- Select exactly {max_clips} moments (or fewer if less than {max_clips} available)
- Rank them from 1 to {max_clips} based on engagement potential
- Ignore emojis in titles when evaluating
- Consider engagement scores and content quality
- **Apply BOTH**: Always use the general ranking criteria, AND add type-specific nuances for your detected content type
- Ensure selected moments are diverse and non-redundant

### Content Guidelines
- Maintain original titles and content from the source moments
- Preserve all timing information accurately
- Include source part information for traceability
- Ensure "why_engaging" explanations are compelling and detailed

## Output Format
Return your response as a JSON object following this exact structure:

```json
{
  "top_engaging_moments": [
    {
      "rank": 1,
      "title": "七人接力鉴定假发造型，现场即兴互动引爆弹幕高潮！",
      "timing": {
        "video_part": "part02",
        "start_time": "00:15:30",
        "end_time": "00:17:15",
        "duration": 105
      },
      "transcript": "Relevant transcript content...",
      "engagement_details": {
        "engagement_level": "high"
      },
      "why_engaging": "多人互动环节，现场气氛热烈，弹幕互动频繁，具有很强的娱乐性和观赏价值",
      "tags": ["co-hosting", "interactive", "humorous", "live-chemistry"]
    },
    {
      "rank": 2,
      "title": "主播现场模仿秀惟妙惟肖 网友弹幕笑翻天",
      "timing": {
        "video_part": "part01",
        "start_time": "00:05:20",
        "end_time": "00:06:10",
        "duration": 50
      },
      "transcript": "Another relevant transcript excerpt...",
      "engagement_details": {
        "engagement_level": "medium"
      },
      "why_engaging": "主播模仿惟妙惟肖，现场气氛欢乐，具有一定的娱乐效果",
      "tags": ["humorous", "funny", "highlight"]
    }
  ],
  "total_moments": 2,
  "analysis_timestamp": "2024-01-01T12:00:00Z",
  "aggregation_criteria": "Selected based on engagement score, duration, and content quality",
  "analysis_summary": {
    "highest_engagement_themes": ["co-hosting", "interactive", "humorous"],
    "total_engaging_content_time": "2 minutes 35 seconds",
    "recommendation": "These moments represent the most entertaining and shareable content from the livestream"
  },
  "honorable_mentions": [
    {
      "title": "值得关注的其他精彩时刻",
      "timing": {
        "video_part": "part01",
        "start_time": "00:05:20",
        "end_time": "00:06:30",
        "duration": 70
      },
      "why_engaging": "虽然未进入前{max_clips}，但仍具有一定娱乐价值"
    },
    {
      "title": "另一个值得关注的时刻",
      "timing": {
        "video_part": "part03",
        "start_time": "00:10:00",
        "end_time": "00:10:45",
        "duration": 45
      },
      "why_engaging": "内容有趣但略短，适合作为补充内容"
    }
  ]
}
```

## Field Specifications

### Required Fields:
- **rank**: Integer from 1 to {max_clips}
- **title**: Original compelling title from source moment
- **timing**: Object containing:
  - **video_part**: Source part identifier (e.g., "part01", "part02")
  - **start_time**: Time in MM:SS or HH:MM:SS format (no milliseconds)
  - **end_time**: Time in MM:SS or HH:MM:SS format (no milliseconds)
  - **duration**: Integer duration in seconds
- **transcript**: Original transcript excerpt
- **engagement_details**: Object with "engagement_level" ("high", "medium", "low")
- **why_engaging**: Detailed explanation of appeal
- **tags**: Array of relevant engagement tags

### Analysis Summary Fields:
- **highest_engagement_themes**: Array of most common tags/themes
- **total_engaging_content_time**: Human-readable total duration
- **recommendation**: Brief summary of the content's value

### Optional Honorable Mentions:
- Include 2-3 additional moments that didn't make top {max_clips} but are still noteworthy
- Use same structure as top moments but without rank

## Analysis Instructions
1. Review all provided engaging moments from different video parts
2. Analyze the content type distribution across all moments
3. **Apply ALL criteria**: Always use the general ranking criteria, AND add type-specific nuances for dominant content type
4. Evaluate each moment based on these combined criteria
5. Select and rank the top {max_clips} moments for maximum viewer appeal
6. Ensure selected moments are diverse and non-redundant
7. Preserve all original timing and content information
8. Convert SRT timestamps (HH:MM:SS,mmm) to simple time format (HH:MM:SS or MM:SS)
9. Create comprehensive analysis summary with themes and recommendations
10. Include honorable mentions for additional content opportunities

## IMPORTANT: JSON Response Format
- Return ONLY valid JSON, no additional text or explanations
- Use the exact structure shown above
- Ensure all strings are properly quoted
- Do not include trailing commas
- Verify JSON syntax before responding