#!/usr/bin/env python3
"""
Engaging Moments Analyzer
Identifies engaging moments from video transcripts using Qwen API
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from core.llm.qwen_api_client import QwenAPIClient, QwenMessage
from core.config import MAX_CLIPS

logger = logging.getLogger(__name__)


class EngagingMomentsAnalyzer:
    """Analyzes video transcripts to identify engaging moments using LLM APIs"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "qwen", use_background: bool = False, language: str = "zh", debug: bool = False, custom_prompt_file: Optional[str] = None, max_clips: int = MAX_CLIPS):
        """
        Initialize the analyzer
        
        Args:
            api_key: API key for the selected provider (optional, can use env var)
            provider: LLM provider to use ("qwen" or "openrouter")
            use_background: Whether to include background information in prompts
            language: Language for output ("zh" for Chinese, "en" for English)
            debug: Enable debug mode to export full prompts sent to LLM
            custom_prompt_file: Path to custom prompt file (optional)
        """
        self.custom_prompt_file = custom_prompt_file
        self.max_clips = max_clips
        self.provider = provider.lower()
        self.prompts_dir = Path("prompts")
        self.use_background = use_background
        self.background_content = None
        self.language = language
        self.debug = debug
        
        # Initialize the appropriate LLM client
        if self.provider == "qwen":
            from core.llm.qwen_api_client import QwenAPIClient
            self.llm_client = QwenAPIClient(api_key)
        elif self.provider == "openrouter":
            from core.llm.openrouter_api_client import OpenRouterAPIClient
            self.llm_client = OpenRouterAPIClient(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers are 'qwen' and 'openrouter'.")
        
        # Load background information if enabled
        if self.use_background:
            self._load_background_info()
    
    def _load_background_info(self):
        """Load background information from prompts/background/background.md"""
        try:
            background_path = self.prompts_dir / "background" / "background.md"
            if background_path.exists():
                with open(background_path, 'r', encoding='utf-8') as f:
                    self.background_content = f.read().strip()
                logger.info("📚 Background information loaded")
            else:
                logger.warning(f"Background file not found: {background_path}")
                self.use_background = False
        except Exception as e:
            logger.error(f"Error loading background information: {e}")
            self.use_background = False
    
    def _export_debug_prompt(self, prompt_content: str, prompt_type: str, part_name: Optional[str] = None):
        """
        Export full prompt content for debugging
        
        Args:
            prompt_content: The full prompt content to export
            prompt_type: Type of prompt ("part_analysis" or "aggregation")
            part_name: Name of the video part (for part analysis prompts)
        """
        if not self.debug:
            return
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create debug directory
            debug_dir = Path("debug_prompts")
            debug_dir.mkdir(exist_ok=True)
            
            # Generate filename
            if part_name:
                filename = f"{prompt_type}_{part_name}_{timestamp}.txt"
            else:
                filename = f"{prompt_type}_{timestamp}.txt"
            
            # Export prompt
            export_path = debug_dir / filename
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"=== DEBUG PROMPT - {prompt_type.upper()} ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Language: {self.language}\n")
                if part_name:
                    f.write(f"Video Part: {part_name}\n")
                f.write(f"Prompt Length: {len(prompt_content)} characters\n")
                f.write("=" * 60 + "\n\n")
                f.write(prompt_content)
            
            logger.info(f"🐛 Debug prompt exported: {export_path}")
            
        except Exception as e:
            logger.error(f"Error exporting debug prompt: {e}")
    
    def load_prompt_template(self, prompt_name: str) -> str:
        """
        Load prompt template from prompts directory
        
        Args:
            prompt_name: Name of the prompt file (without .md extension)
            
        Returns:
            Content of the prompt file
        """
        # Use custom prompt file if specified and this is the part requirement prompt
        if prompt_name == "engaging_moments_part_requirement" and self.custom_prompt_file:
            custom_prompt_path = Path(self.custom_prompt_file)
            if custom_prompt_path.exists():
                logger.info(f"📝 Using custom prompt file: {custom_prompt_path}")
                with open(custom_prompt_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read().strip()
            else:
                logger.warning(f"Custom prompt file not found: {custom_prompt_path}")
                logger.info(f"Falling back to default prompt: engaging_moments_part_requirement.md")
                # Fall back to default prompt
                base_prompt_path = self.prompts_dir / f"{prompt_name}.md"
                if not base_prompt_path.exists():
                    raise FileNotFoundError(f"Base prompt file not found: {base_prompt_path}")
                with open(base_prompt_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read().strip()
        else:
            # Load base prompt template (without language suffix)
            base_prompt_path = self.prompts_dir / f"{prompt_name}.md"
            
            if not base_prompt_path.exists():
                raise FileNotFoundError(f"Base prompt file not found: {base_prompt_path}")
            
            with open(base_prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
        
        # Load and append language-specific patch
        language_patch_path = self.prompts_dir / "language_patches" / f"{self.language}.md"
        
        if language_patch_path.exists():
            with open(language_patch_path, 'r', encoding='utf-8') as f:
                language_patch = f.read().strip()
            
            # Append language patch to the base prompt
            prompt_content += "\n\n" + language_patch
            logger.info(f"🌐 Language patch loaded for: {self.language}")
        else:
            logger.warning(f"Language patch not found: {language_patch_path}")
        
        return prompt_content
    
    def parse_srt_file(self, srt_path: str) -> List[Dict[str, Any]]:
        """
        Parse SRT file and extract subtitle entries
        
        Args:
            srt_path: Path to SRT file
            
        Returns:
            List of subtitle entries with timing and text
        """
        entries = []
        
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Split by double newlines to separate entries
            blocks = content.split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Parse timing line (format: 00:00:00,000 --> 00:00:02,000)
                    timing_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                    if timing_match:
                        start_time = timing_match.group(1)
                        end_time = timing_match.group(2)
                        text = ' '.join(lines[2:])  # Join all text lines
                        
                        entries.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': text
                        })
        
        except Exception as e:
            logger.error(f"Error parsing SRT file {srt_path}: {e}")
            
        return entries
    
    def time_to_seconds(self, time_str: str) -> float:
        """Convert SRT time format to seconds"""
        # Format: 00:01:30,500 or 00:01:30 (without milliseconds)
        if ',' in time_str:
            time_part, ms_part = time_str.split(',')
            ms = int(ms_part)
        else:
            time_part = time_str
            ms = 0
        
        h, m, s = map(int, time_part.split(':'))
        return h * 3600 + m * 60 + s + ms / 1000
    
    def seconds_to_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    def create_transcript_context(self, entries: List[Dict[str, Any]]) -> str:
        """Create a formatted transcript context for Qwen analysis"""
        transcript_lines = []
        
        for entry in entries:
            transcript_lines.append(f"[{entry['start_time']} --> {entry['end_time']}] {entry['text']}")
        
        return '\n'.join(transcript_lines)
    
    def build_part_analysis_prompt(self, srt_path: str, part_name: str) -> str:
        """
        Build the analysis prompt for a video part without calling the LLM.

        Args:
            srt_path: Path to SRT file
            part_name: Name of the video part (e.g., "part01")

        Returns:
            The complete prompt string, or empty string if no entries found
        """
        entries = self.parse_srt_file(srt_path)
        if not entries:
            return ""

        transcript_context = self.create_transcript_context(entries)
        prompt_template = self.load_prompt_template("engaging_moments_part_requirement")

        prompt_parts = []
        if self.use_background and self.background_content:
            prompt_parts.append("## Additional Background Information\n\n")
            prompt_parts.append(self.background_content)
            prompt_parts.append("\n\n")

        prompt_parts.append(prompt_template)
        prompt_parts.append(f"\n\n## Transcript Data for {part_name}\n\n")
        prompt_parts.append(transcript_context)
        prompt_parts.append("\n\nPlease analyze this transcript and identify engaging moments following the requirements above.")

        return "".join(prompt_parts)

    def build_aggregation_prompt(self, highlights_files: List[str]) -> str:
        """
        Build the aggregation prompt from highlights files without calling the LLM.

        Args:
            highlights_files: List of paths to highlights JSON files

        Returns:
            The complete aggregation prompt string
        """
        all_moments = []
        for file_path in highlights_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for moment in data.get('engaging_moments', []):
                    moment['source_part'] = data.get('video_part', 'unknown')
                    all_moments.append(moment)
            except Exception as e:
                logger.error(f"Error loading highlights file {file_path}: {e}")

        moments_context = self._create_moments_context(all_moments)
        prompt_template = self.load_prompt_template("engaging_moments_agg_requirement")

        prompt_parts = []
        if self.use_background and self.background_content:
            prompt_parts.append("## Background Information\n\n")
            prompt_parts.append(self.background_content)
            prompt_parts.append("\n\n")

        prompt_parts.append(prompt_template.replace("{max_clips}", str(self.max_clips)))
        prompt_parts.append(f"\n\n## All Engaging Moments Data\n\n")
        prompt_parts.append(moments_context)
        prompt_parts.append(f"\n\nPlease select and rank the top {self.max_clips} most engaging moments following the requirements above.")

        return "".join(prompt_parts)

    async def analyze_part_for_engaging_moments(self, srt_path: str, part_name: str) -> Dict[str, Any]:
        """
        Analyze a single video part for engaging moments

        Args:
            srt_path: Path to SRT file
            part_name: Name of the video part (e.g., "part01")

        Returns:
            Dictionary with engaging moments analysis
        """
        logger.info(f"🔍 Analyzing {part_name} for engaging moments...")

        # Parse SRT file
        entries = self.parse_srt_file(srt_path)
        if not entries:
            logger.warning(f"No entries found in {srt_path}")
            return self._create_empty_result(part_name)

        # Build the analysis prompt
        analysis_prompt = self.build_part_analysis_prompt(srt_path, part_name)

        # Export debug prompt if enabled
        self._export_debug_prompt(analysis_prompt, "part_analysis", part_name)
        
        try:
            # Call LLM API
            response = self.llm_client.simple_chat(analysis_prompt)
            
            # Try to parse JSON response with improved extraction
            try:
                result = self._extract_and_parse_json(response, part_name, entries)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response length: {len(response)} characters")
                logger.error(f"Response preview: {response[:500]}...")
                if len(response) > 500:
                    logger.error(f"Response ending: ...{response[-200:]}")
                result = self._create_empty_result(part_name)
                
        except Exception as e:
            logger.error(f"Error calling Qwen API: {e}")
            result = self._create_empty_result(part_name)
        
        return result
    
    def _extract_and_parse_json(self, response: str, part_name: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract and parse JSON from AI response with AI-powered error handling
        
        Args:
            response: Raw AI response
            part_name: Video part name
            entries: SRT entries for validation
            
        Returns:
            Parsed and validated JSON result
        """
        # First try standard JSON parsing
        try:
            # Try direct parsing first
            result = json.loads(response.strip())
            logger.debug("Successfully parsed response as direct JSON")
            return self._validate_and_clean_result(result, part_name, entries)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                logger.debug("Successfully parsed JSON from code block")
                return self._validate_and_clean_result(result, part_name, entries)
            except json.JSONDecodeError:
                pass
        
        # If standard parsing fails, use AI to fix the JSON
        logger.info("Standard JSON parsing failed, using AI to fix JSON...")
        try:
            fixed_json = self._ai_fix_json(response, part_name)
            result = json.loads(fixed_json)
            logger.debug("Successfully parsed AI-fixed JSON")
            return self._validate_and_clean_result(result, part_name, entries)
        except Exception as e:
            logger.error(f"AI JSON fixing failed: {e}")
            # Export raw and fixed responses for debugging
            self._export_failed_responses(response, part_name, fixed_json if 'fixed_json' in locals() else None, e)
            return self._create_empty_result(part_name)
    
    def _ai_fix_json(self, malformed_response: str, part_name: str) -> str:
        """
        Use AI to fix malformed JSON response
        
        Args:
            malformed_response: The malformed JSON response
            part_name: Video part name for context
            
        Returns:
            Fixed JSON string
        """
        fix_prompt = f"""
You are a JSON repair expert. I have a malformed JSON response that needs to be fixed. 

The response should follow this structure:
{{
  "video_part": "{part_name}",
  "engaging_moments": [
    {{
      "title": "七人接力鉴定假发造型，现场即兴互动引爆弹幕高潮！",
      "start_time": "00:01:30",
      "end_time": "00:02:45",
      "duration_seconds": 75,
      "transcript": "Relevant transcript content for this moment...",
      "engagement_details": {{
        "engagement_level": "high"
      }},
      "why_engaging": "多人互动环节，现场气氛热烈，弹幕互动频繁，具有很强的娱乐性和观赏价值",
      "tags": ["co-hosting", "interactive", "humorous", "live-chemistry"]
    }}
  ],
  "total_moments": 1,
  "analysis_timestamp": "2024-01-01T12:00:00Z"
}}

IMPORTANT:
- start_time and end_time should be in simple format (HH:MM:SS or MM:SS), NOT SRT format with milliseconds
- Remove any "engagement_score" field if present
- Ensure "why_engaging" is shorter than 100 characters
- Use only approved tags: ["co-hosting", "interactive", "humorous", "live-chemistry", "funny", "highlight", "reaction", "gaming", "chat-interaction", "insight", "inspiring", "controversial", "relatable", "valuable", "educational"]

Here is the malformed response:
{malformed_response}

Please fix the JSON and return ONLY the valid JSON, no explanations:
"""
        
        try:
            # Use a simpler model for JSON fixing to avoid recursion
            fixed_response = self.llm_client.simple_chat(fix_prompt)
            
            # Extract JSON from the fixed response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', fixed_response, re.DOTALL)
            if json_match:
                return json_match.group(1)
            
            # Try to find JSON object in response
            json_match = re.search(r'\{.*\}', fixed_response, re.DOTALL)
            if json_match:
                return json_match.group()
            
            # If no JSON found, return the entire response
            return fixed_response.strip()
            
        except Exception as e:
            logger.error(f"Error in AI JSON fixing: {e}")
            raise
    
    def _clean_json_text(self, json_text: str) -> str:
        """
        Clean common JSON formatting issues
        
        Args:
            json_text: Raw JSON text
            
        Returns:
            Cleaned JSON text
        """
        # Remove leading/trailing whitespace
        json_text = json_text.strip()
        
        # Remove markdown code block markers if present
        json_text = re.sub(r'^```json\s*', '', json_text)
        json_text = re.sub(r'\s*```$', '', json_text)
        
        # Fix common trailing comma issues
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix missing commas between objects/arrays (basic fix)
        json_text = re.sub(r'}\s*{', '},{', json_text)
        json_text = re.sub(r']\s*\[', '],[', json_text)
        
        # Convert SRT timestamp format to simple format if present
        # Convert HH:MM:SS,mmm to HH:MM:SS
        json_text = re.sub(r'(\d{2}:\d{2}:\d{2}),\d{3}', r'\1', json_text)
        
        return json_text
    
    def _validate_and_clean_result(self, result: Dict[str, Any], part_name: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and clean up the analysis result"""
        
        # Ensure required fields
        if 'engaging_moments' not in result:
            result['engaging_moments'] = []
        
        result['video_part'] = part_name
        result['total_moments'] = len(result['engaging_moments'])
        result['analysis_timestamp'] = datetime.now().isoformat() + 'Z'
        
        # Handle detected_content_type field
        if 'detected_content_type' not in result:
            result['detected_content_type'] = 'unknown'
        
        # Validate each moment
        valid_moments = []
        for moment in result['engaging_moments']:
            if self._validate_moment(moment, entries):
                valid_moments.append(moment)
        
        result['engaging_moments'] = valid_moments
        result['total_moments'] = len(valid_moments)
        
        return result
    
    def _validate_moment(self, moment: Dict[str, Any], entries: List[Dict[str, Any]]) -> bool:
        """Validate a single engaging moment"""
        
        required_fields = ['title', 'start_time', 'end_time']
        for field in required_fields:
            if field not in moment:
                logger.warning(f"Missing required field: {field}")
                return False
        
        try:
            # Validate timing
            start_seconds = self.time_to_seconds(moment['start_time'])
            end_seconds = self.time_to_seconds(moment['end_time'])
            duration = end_seconds - start_seconds
            
            # Check duration constraints (30 seconds to 4 minutes)
            if duration < 30 or duration > 240:
                logger.warning(f"Invalid duration: {duration} seconds")
                return False
            
            moment['duration_seconds'] = int(duration)
            
            # Ensure other fields exist
            if 'transcript' not in moment:
                moment['transcript'] = ""
            if 'engagement_details' not in moment:
                moment['engagement_details'] = {"engagement_level": "medium"}
            elif 'engagement_level' not in moment['engagement_details']:
                moment['engagement_details']['engagement_level'] = "medium"
            if 'tags' not in moment:
                moment['tags'] = []
                
        except Exception as e:
            logger.warning(f"Error validating moment: {e}")
            return False
        
        return True
    
    def _create_empty_result(self, part_name: str) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            "video_part": part_name,
            "engaging_moments": [],
            "total_moments": 0,
            "analysis_timestamp": datetime.now().isoformat() + 'Z'
        }
    
    async def aggregate_top_moments(self, highlights_files: List[str], output_dir: str) -> Dict[str, Any]:
        """
        Aggregate engaging moments from multiple parts and select top moments

        Args:
            highlights_files: List of paths to highlights JSON files
            output_dir: Directory to save the aggregated result

        Returns:
            Dictionary with top engaging moments
        """
        logger.info("🔄 Aggregating top engaging moments...")

        # Check if any moments exist
        all_moments = []
        for file_path in highlights_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for moment in data.get('engaging_moments', []):
                    all_moments.append(moment)
            except Exception as e:
                logger.error(f"Error loading highlights file {file_path}: {e}")

        if not all_moments:
            logger.warning("No engaging moments found to aggregate")
            return self._create_empty_aggregation_result()

        # Build aggregation prompt using shared method
        aggregation_prompt = self.build_aggregation_prompt(highlights_files)

        # Export debug prompt if enabled
        self._export_debug_prompt(aggregation_prompt, "aggregation")
        
        try:
            # Call LLM API for aggregation
            response = self.llm_client.simple_chat(aggregation_prompt)
            
            # Parse JSON response with improved extraction
            try:
                result = self._extract_and_parse_aggregation_json(response)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse aggregation JSON: {e}")
                logger.debug(f"Raw response: {response}")
                result = self._create_fallback_aggregation(all_moments)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse aggregation JSON: {e}")
                logger.debug(f"Raw response: {response}")
                result = self._create_fallback_aggregation(all_moments)
                
        except Exception as e:
            logger.error(f"Error in aggregation API call: {e}")
            result = self._create_fallback_aggregation(all_moments)
        
        return result
    
    def _extract_and_parse_aggregation_json(self, response: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from aggregation AI response with AI-powered fixing
        
        Args:
            response: Raw AI response
            
        Returns:
            Parsed and validated JSON result
        """
        # First try standard JSON parsing
        try:
            # Try direct parsing first
            result = json.loads(response.strip())
            logger.debug("Successfully parsed aggregation response as direct JSON")
            return self._validate_aggregation_result(result)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                logger.debug("Successfully parsed aggregation JSON from code block")
                return self._validate_aggregation_result(result)
            except json.JSONDecodeError:
                pass
        
        # If standard parsing fails, use AI to fix the JSON
        logger.info("Standard aggregation JSON parsing failed, using AI to fix JSON...")
        try:
            fixed_json = self._ai_fix_aggregation_json(response)
            result = json.loads(fixed_json)
            logger.debug("Successfully parsed AI-fixed aggregation JSON")
            return self._validate_aggregation_result(result)
        except Exception as e:
            logger.error(f"AI aggregation JSON fixing failed: {e}")
            # Export raw and fixed responses for debugging
            self._export_failed_aggregation_responses(response, fixed_json if 'fixed_json' in locals() else None, e)
            raise json.JSONDecodeError("Could not extract valid JSON from aggregation response", response, 0)
    
    def _ai_fix_aggregation_json(self, malformed_response: str) -> str:
        """
        Use AI to fix malformed aggregation JSON response
        
        Args:
            malformed_response: The malformed JSON response
            
        Returns:
            Fixed JSON string
        """
        fix_prompt = f"""
You are a JSON repair expert. I have a malformed JSON response for video moment aggregation that needs to be fixed.

The response should follow this structure:
{{
  "top_engaging_moments": [
    {{
      "rank": 1,
      "title": "七人接力鉴定假发造型，现场即兴互动引爆弹幕高潮！",
      "timing": {{
        "video_part": "part02",
        "start_time": "00:15:30",
        "end_time": "00:17:15",
        "duration": 105
      }},
      "transcript": "Relevant transcript content...",
      "engagement_details": {{
        "engagement_level": "high"
      }},
      "why_engaging": "多人互动环节，现场气氛热烈，弹幕互动频繁，具有很强的娱乐性和观赏价值",
      "tags": ["co-hosting", "interactive", "humorous", "live-chemistry"]
    }}
  ],
  "total_moments": 5,
  "analysis_timestamp": "2024-01-01T12:00:00Z",
  "aggregation_criteria": "Selected based on engagement score, duration, and content quality",
  "analysis_summary": {{
    "highest_engagement_themes": ["co-hosting", "interactive", "humorous"],
    "total_engaging_content_time": "8 minutes 45 seconds",
    "recommendation": "These moments represent the most entertaining and shareable content from the livestream"
  }},
  "honorable_mentions": []
}}

IMPORTANT:
- start_time and end_time should be in simple format (HH:MM:SS or MM:SS), NOT SRT format with milliseconds
- Ensure all timing information is preserved accurately
- Use only approved tags: ["co-hosting", "interactive", "humorous", "live-chemistry", "funny", "highlight", "reaction", "gaming", "chat-interaction", "insight", "inspiring", "controversial", "relatable", "valuable", "educational"]

Here is the malformed response:
{malformed_response}

Please fix the JSON and return ONLY the valid JSON, no explanations:
"""
        
        try:
            # Use a simpler model for JSON fixing
            fixed_response = self.llm_client.simple_chat(fix_prompt)
            
            # Extract JSON from the fixed response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', fixed_response, re.DOTALL)
            if json_match:
                return json_match.group(1)
            
            # Try to find JSON object in response
            json_match = re.search(r'\{.*\}', fixed_response, re.DOTALL)
            if json_match:
                return json_match.group()
            
            # If no JSON found, return the entire response
            return fixed_response.strip()
            
        except Exception as e:
            logger.error(f"Error in AI aggregation JSON fixing: {e}")
            raise
    
    def _export_failed_responses(self, raw_response: str, part_name: str, fixed_response: Optional[str], error: Exception):
        """
        Export raw and AI-fixed responses when JSON parsing fails for debugging
        
        Args:
            raw_response: Original AI response
            part_name: Video part name
            fixed_response: AI-fixed response (if available)
            error: The parsing error that occurred
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create debug directory
            debug_dir = Path("debug_responses")
            debug_dir.mkdir(exist_ok=True)
            
            # Export raw response
            raw_file = debug_dir / f"{part_name}_raw_response_{timestamp}.txt"
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(f"=== RAW AI RESPONSE FOR {part_name.upper()} ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Error: {str(error)}\n")
                f.write(f"Response Length: {len(raw_response)} characters\n")
                f.write("=" * 50 + "\n\n")
                f.write(raw_response)
            
            # Export AI-fixed response if available
            if fixed_response:
                fixed_file = debug_dir / f"{part_name}_ai_fixed_response_{timestamp}.txt"
                with open(fixed_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== AI-FIXED RESPONSE FOR {part_name.upper()} ===\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Original Error: {str(error)}\n")
                    f.write(f"Fixed Response Length: {len(fixed_response)} characters\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(fixed_response)
            
            logger.info(f"📁 Exported failed responses to debug_responses/ directory")
            logger.info(f"   Raw response: {raw_file.name}")
            if fixed_response:
                logger.info(f"   AI-fixed response: {fixed_file.name}")
                
        except Exception as export_error:
            logger.error(f"Failed to export debug responses: {export_error}")
    
    def _export_failed_aggregation_responses(self, raw_response: str, fixed_response: Optional[str], error: Exception):
        """
        Export raw and AI-fixed aggregation responses when JSON parsing fails
        
        Args:
            raw_response: Original AI response
            fixed_response: AI-fixed response (if available)
            error: The parsing error that occurred
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create debug directory
            debug_dir = Path("debug_responses")
            debug_dir.mkdir(exist_ok=True)
            
            # Export raw response
            raw_file = debug_dir / f"aggregation_raw_response_{timestamp}.txt"
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write("=== RAW AI AGGREGATION RESPONSE ===\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Error: {str(error)}\n")
                f.write(f"Response Length: {len(raw_response)} characters\n")
                f.write("=" * 50 + "\n\n")
                f.write(raw_response)
            
            # Export AI-fixed response if available
            if fixed_response:
                fixed_file = debug_dir / f"aggregation_ai_fixed_response_{timestamp}.txt"
                with open(fixed_file, 'w', encoding='utf-8') as f:
                    f.write("=== AI-FIXED AGGREGATION RESPONSE ===\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Original Error: {str(error)}\n")
                    f.write(f"Fixed Response Length: {len(fixed_response)} characters\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(fixed_response)
            
            logger.info(f"📁 Exported failed aggregation responses to debug_responses/ directory")
            logger.info(f"   Raw response: {raw_file.name}")
            if fixed_response:
                logger.info(f"   AI-fixed response: {fixed_file.name}")
                
        except Exception as export_error:
            logger.error(f"Failed to export debug aggregation responses: {export_error}")
    
    def _create_moments_context(self, moments: List[Dict[str, Any]]) -> str:
        """Create formatted context of all moments for aggregation"""
        context_lines = []
        
        for i, moment in enumerate(moments, 1):
            engagement_level = moment.get('engagement_details', {}).get('engagement_level', 'unknown')
            context_lines.append(f"""
Moment {i}:
- Part: {moment.get('source_part', 'unknown')}
- Title: {moment.get('title', 'No title')}
- Time: {moment.get('start_time', '')} --> {moment.get('end_time', '')}
- Duration: {moment.get('duration_seconds', 0)} seconds
- Engagement Level: {engagement_level}
- Tags: {', '.join(moment.get('tags', []))}
- Transcript: {moment.get('transcript', '')[:200]}...
""")
        
        return '\n'.join(context_lines)
    
    def _validate_aggregation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean up aggregation result"""
        
        if 'top_engaging_moments' not in result:
            result['top_engaging_moments'] = []
        
        # Ensure proper ranking
        for i, moment in enumerate(result['top_engaging_moments']):
            moment['rank'] = i + 1
        
        result['total_moments'] = len(result['top_engaging_moments'])
        result['analysis_timestamp'] = datetime.now().isoformat() + 'Z'
        
        if 'aggregation_criteria' not in result:
            result['aggregation_criteria'] = "Selected based on engagement score, duration, and content quality"
        
        return result
    
    def _create_empty_aggregation_result(self) -> Dict[str, Any]:
        """Create empty aggregation result"""
        return {
            "top_engaging_moments": [],
            "total_moments": 0,
            "analysis_timestamp": datetime.now().isoformat() + 'Z',
            "aggregation_criteria": "No engaging moments found"
        }
    
    def _create_fallback_aggregation(self, all_moments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create fallback aggregation without sorting - just take first N moments"""

        # Take first N moments (no sorting - LLM should have already ranked them)
        top_moments = all_moments[:self.max_clips]
        
        # Add ranking if not present
        for i, moment in enumerate(top_moments):
            if 'rank' not in moment:
                moment['rank'] = i + 1
        
        return {
            "top_engaging_moments": top_moments,
            "total_moments": len(top_moments),
            "analysis_timestamp": datetime.now().isoformat() + 'Z',
            "aggregation_criteria": f"Fallback selection - first {self.max_clips} moments",
            "analysis_summary": {
                "highest_engagement_themes": [],
                "total_engaging_content_time": "N/A",
                "recommendation": "Fallback aggregation used due to parsing error"
            },
            "honorable_mentions": []
        }
    
    async def save_highlights_to_file(self, highlights: Dict[str, Any], output_path: str):
        """Save highlights analysis to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(highlights, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Highlights saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving highlights to {output_path}: {e}")
            raise