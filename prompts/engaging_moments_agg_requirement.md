# Top Engaging Moments Aggregation

## Task
Review all the highlights from multiple video parts and identify the top 5 most engaging moments. Aggregate and rank them based on engagement potential, content quality, and viewer appeal.

## Requirements

### Selection Criteria
- Select exactly 5 moments (or fewer if less than 5 available)
- Rank them from 1 to 5 based on engagement potential
- Focus on co-hosting segments and highly interactive moments as they are usually most engaging
- Ignore emojis in titles when evaluating
- Consider engagement scores and content quality
- Prioritize moments with high entertainment value

### Content Guidelines
- Maintain original titles and content from the source moments
- Preserve all timing information accurately
- Include source part information for traceability
- Ensure "why_engaging" explanations are compelling and detailed

## Output Format
Return your response as a JSON object following this exact structure:

```json
{
  "analysis_info": {
    "analysis_date": "2024-01-01"
  },
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
    }
  ],
  "total_moments": 5,
  "analysis_timestamp": "2024-01-01T12:00:00Z",
  "aggregation_criteria": "Selected based on engagement score, duration, and content quality",
  "analysis_summary": {
    "highest_engagement_themes": ["co-hosting", "interactive", "humorous"],
    "total_engaging_content_time": "8 minutes 45 seconds",
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
      "why_engaging": "虽然未进入前5，但仍具有一定娱乐价值"
    }
  ]
}
```

## Field Specifications

### Required Fields for Each Top Moment:
- **rank**: Integer from 1 to 5
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
- Include 2-3 additional moments that didn't make top 5 but are still noteworthy
- Use same structure as top moments but without rank

## Analysis Instructions
1. Review all provided engaging moments from different video parts
2. Evaluate each moment based on:
   - Engagement level
   - Content quality and entertainment value
   - Interaction level and co-hosting elements
   - Duration appropriateness and clip potential
3. Select and rank the top 5 moments for maximum viewer appeal
4. Preserve all original timing and content information
5. Convert SRT timestamps (HH:MM:SS,mmm) to simple time format (HH:MM:SS or MM:SS)
6. Create comprehensive analysis summary with themes and recommendations
7. Include honorable mentions for additional content opportunities

## IMPORTANT: JSON Response Format
- Return ONLY valid JSON, no additional text or explanations
- Use the exact structure shown above
- Ensure all strings are properly quoted
- Do not include trailing commas
- Verify JSON syntax before responding