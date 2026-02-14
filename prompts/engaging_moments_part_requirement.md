# Engaging Moments Analysis - Video Part

## Task
Analyze the provided video transcript and identify potential interesting and engaging moments from live streaming videos. Focus on segments that would be compelling for viewers and suitable for creating short clips.

## Content Type Classification

First, identify the content type of this video from these categories:

| Type | Characteristics | Key Engagement Signals |
|------|-----------------|------------------------|
| **entertainment** | Jokes, games, performances, variety shows | Laughter peaks, audience reactions, game climaxes |
| **knowledge** | Tutorials, explanations, educational content | Key insights, "aha moments", actionable tips |
| **speech** | Presentations, talks, storytelling | Emotional peaks, inspirational quotes, audience applause |
| **opinion** | Debates, commentary, reviews | Strong viewpoints, controversial takes, debates |
| **experience** | Life stories, personal anecdotes | Relatable moments, emotional resonance, personal revelations |
| **business** | Professional advice, market analysis | Value propositions, expert insights, ROI signals |
| **content_review** | Movie/game reviews, analyses | Unique opinions, surprising takes, comparisons |

## General Engagement Criteria (Always Apply)

These universal criteria apply to ALL content types:

### High Engagement Indicators:
- **Emotional Impact**: Moments that evoke strong emotions (laughter, surprise, inspiration, excitement)
- **Information Value**: Segments with unique insights, surprising facts, or valuable knowledge
- **Interactivity**: Moments with dialogue, debates, or audience interaction
- **Memorability**: Standout quotes, unique perspectives, or defining moments
- **Relatability**: Content viewers can identify with or learn from

### Quality Indicators:
- **Completeness**: Segments with clear beginning, development, and conclusion
- **Pacing**: Moments with good energy flow and rhythm
- **Authenticity**: Genuine reactions, unscripted moments, or natural interactions
- **Uniqueness**: Rare occurrences, special guests, or unexpected events

---

## Type-Specific Engagement Criteria (Complement General)

In addition to the general criteria above, apply these type-specific nuances based on detected content type:

### For ENTERTAINMENT:
- Preserve complete jokes (setup → punchline → reaction)
- Capture game climaxes and unexpected twists
- Include audience/chat reactions
- Prioritize comedic timing and funny moments

### For KNOWLEDGE:
- Focus on "aha moments" and key insights
- Identify actionable tips or valuable explanations
- Look for concepts that simplify complex topics
- Prioritize educational value and practical applications

### For SPEECH:
- Find emotional peaks and inspirational moments
- Capture memorable quotes and powerful statements
- Identify audience engagement (applause, etc.)
- Look for storytelling climax and narrative resolution

### For OPINION:
- Prioritize strong, controversial, or surprising viewpoints
- Look for debates or disagreements
- Find relatable or thought-provoking statements
- Identify unique perspectives that challenge common beliefs

### For EXPERIENCE:
- Seek personal stories with emotional depth
- Find relatable moments viewers can identify with
- Look for surprising personal revelations
- Capture authentic emotional expressions

### For BUSINESS:
- Focus on expert insights and valuable advice
- Identify actionable strategies and methodologies
- Look for unique market perspectives and predictions
- Prioritize high-value professional content

### For CONTENT_REVIEW:
- Capture unique or surprising opinions
- Find bold predictions or controversial takes
- Look for entertaining critiques and comparisons
- Identify surprising revelations about reviewed content

## Requirements

### Content Guidelines
- Create **attractive and engaging** titles for each moment (no emojis, punctuation allowed)
- Titles should avoid sensitive, negative, hate, or offensive words
- Co-hosting segments and interactive moments are usually most engaging
- Gossip moments are usually engaging
- Include relevant transcript excerpts
- Provide clear explanations for why each moment is engaging

### Duration Constraints
- Each engaging moment must be AT LEAST 30 seconds long
- Each engaging moment must be LESS THAN 4 minutes long
- Target optimal duration: 45-180 seconds for best short-form engagement

### Time Boundary Principles (Critical)

**How to determine `start_time`:**
- Locate the first core statement about the engaging moment
- Ignore unrelated small talk, filler words, or transitions before it
- Prefer starting at semantic boundaries for natural introduction

**How to determine `end_time` (Most Important):**
- MUST be the end timestamp of the LAST relevant sentence covering the core moment
- Ensure semantic completeness - avoid abrupt cut-off points
- Prefer ending at natural pauses, summary statements, or topic transitions
- If there are summary, transitional, or unrelated sentences after the moment ends, DO NOT include them. The `end_time` must end BEFORE these sentences start
- **Wrong approach**: Blindly setting `end_time` to the end of the transcript. This must be avoided.

### Semantic Boundary Recognition

**Natural Start Point Features:**
- Topic introduction phrases ("speaking of...", "about...", "let's talk about...")
- Opinion shifts ("but...", "however...", "on the other hand...")
- New discussion subject or case introduction
- Clear tone or pitch changes

**Natural End Point Features:**
- Summary statements ("overall...", "in summary...", "that's...")
- Topic transition signals ("next...", "also...", "changing topic...")
- Opinion closure ("so...", "therefore...", "that's my view")
- Natural pauses or relaxed tone

**Avoid Cutting At:**
- Middle of sentences
- During key point development
- Critical logic reasoning steps
- Continuous discussions without clear semantic boundaries

### Engagement Analysis
- Provide engagement levels: "high", "medium", or "low"
- Add relevant tags from: ["co-hosting", "interactive", "humorous", "live-chemistry", "funny", "highlight", "reaction", "gaming", "chat-interaction", "insight", "inspiring", "controversial", "relatable", "valuable", "educational"]
- Include "why_engaging" explanations that describe what makes each moment compelling

## Analysis Instructions
1. **Analyze content**: First, analyze the overall content type of the video from the transcript
2. **Apply ALL criteria**: Always use the general engagement criteria, AND add type-specific nuances for your detected content type
3. Carefully review the transcript for segments matching these criteria
4. Ensure each moment has clear engagement value for clip creation
5. Focus on segments that would work well as standalone short videos
6. Provide detailed "why_engaging" explanations to justify selections
7. Use appropriate engagement levels and relevant tags
8. Extract meaningful transcript portions that capture the essence of each moment

## Output Format
Return your response as a JSON object following this exact structure:

```json
{
  "video_part": "part01",
  "detected_content_type": "entertainment",
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
    },
    {
      "title": "主播现场模仿秀惟妙惟肖 网友弹幕笑翻天",
      "start_time": "00:05:20",
      "end_time": "00:06:10",
      "duration_seconds": 50,
      "transcript": "Another relevant transcript excerpt...",
      "engagement_details": {
        "engagement_level": "medium"
      },
      "why_engaging": "主播模仿惟妙惟肖，现场气氛欢乐，具有一定的娱乐效果",
      "tags": ["humorous", "funny", "highlight"]
    }
  ],
  "total_moments": 2,
  "analysis_timestamp": "2024-01-01T12:00:00Z"
}
```

## Field Specifications

### Top-Level Required Fields:
- **video_part**: Identifier for this video segment (e.g., "part01")
- **detected_content_type**: The content type category detected from the video (entertainment/knowledge/speech/opinion/experience/business/content_review)

### Required Fields for Each Moment:
- **title**: Compelling title without emojis
- **start_time**: Simple time format (HH:MM:SS or MM:SS) - NOT SRT format with milliseconds
- **end_time**: Simple time format (HH:MM:SS or MM:SS) - NOT SRT format with milliseconds
- **duration_seconds**: Integer duration in seconds
- **transcript**: Relevant transcript excerpt from the moment
- **engagement_details**: Object with "engagement_level" ("high", "medium", "low")
- **why_engaging**: Explanation of what makes this moment compelling.
- **tags**: Array of relevant tags from the approved list

### Time Boundary Guidelines:
- **start_time**: Should be the first relevant sentence of the moment, not include unrelated filler
- **end_time**: Should be the last relevant sentence - NOT the end of transcript
- **Semantic completeness**: Ensure the moment ends at a natural boundary, not mid-thought
- **Avoid**: Cutting at random points, including transitional/unrelated content after the moment

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