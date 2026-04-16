import os
from openai import OpenAI, APITimeoutError, APIConnectionError
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from src.console import console
from src.infrastructure.outbound.agents.ports.summarizer_agent import SummarizerAgent


def calculate_min_summary_lines(
    duration_seconds: int,
    base_lines: int = 50,
    lines_per_minute: float = 15.0,
    max_lines: int = 2000,
    min_lines: int = 20,
) -> int:
    """
    Calculate the minimum number of lines for a summary based on video duration.

    This function can be adjusted to fine-tune summary length requirements.

    :param duration_seconds: Video duration in seconds
    :param base_lines: Minimum lines for very short videos
    :param lines_per_minute: Additional lines per minute of video
    :param max_lines: Maximum lines cap (to prevent extremely long summaries)
    :param min_lines: Minimum lines floor (even for very short videos)
    :return: Recommended minimum number of lines for the summary

    Examples:
        - 5 min video  (300s): 50 + (5 * 15.0) = 125 lines
        - 15 min video (900s): 50 + (15 * 15.0) = 275 lines
        - 17 min video (1020s): 50 + (17 * 15.0) = 305 lines
        - 30 min video (1800s): 50 + (30 * 15.0) = 500 lines
        - 60 min video (3600s): 50 + (60 * 15.0) = 950 lines
        - 120 min video (7200s): 50 + (120 * 15.0) = 1850 lines
    """
    if not duration_seconds or duration_seconds <= 0:
        return base_lines

    duration_minutes = duration_seconds / 60
    calculated_lines = int(base_lines + (duration_minutes * lines_per_minute))

    # Apply bounds
    return max(min_lines, min(calculated_lines, max_lines))


def calculate_summary_timeout(
    duration_seconds: int | None,
    minimum_timeout: float = 1800.0,
    timeout_per_video_minute: float = 120.0,
) -> float:
    """
    Calculate the LLM timeout for a summary request.

    The timeout scales with video duration, while keeping a minimum floor for
    shorter videos and unknown durations.

    :param duration_seconds: Video duration in seconds
    :param minimum_timeout: Minimum timeout floor in seconds
    :param timeout_per_video_minute: Timeout budget added per video minute
    :return: Request timeout in seconds
    """
    if not duration_seconds or duration_seconds <= 0:
        return float(minimum_timeout)

    duration_minutes = duration_seconds / 60
    proportional_timeout = duration_minutes * timeout_per_video_minute
    return max(float(minimum_timeout), float(proportional_timeout))


class SummarizerLMStudioAgent(SummarizerAgent):
    def __init__(self, model: str | None = None):
        """
        Initialize LM Studio agent using OpenAI-compatible API.
        :param model: The LLM model to use (falls back to LM_STUDIO_MODEL env var, then defaults to 'openai/gpt-oss-20b')
        :param api_key: API key (LM Studio doesn't require a real key, defaults to 'not-needed')
        :param base_url: Base URL for LM Studio API (defaults to local LM Studio instance)
        :param timeout: Minimum request timeout in seconds for summary generation
        """
        self.base_url = os.getenv("LM_STUDIO_BASE_URL", "")
        # Use provided model, fall back to env var, then to default
        self.model = model or os.getenv("LM_STUDIO_MODEL", "openai/gpt-oss-20b")
        self.minimum_timeout = float(os.getenv("LM_STUDIO_TIMEOUT", "1800.0"))
        self.timeout_per_video_minute = float(
            os.getenv("LM_STUDIO_TIMEOUT_PER_VIDEO_MINUTE", "120.0")
        )
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=os.getenv("LM_STUDIO_API_KEY", ""),
            timeout=self.minimum_timeout,
        )

        # Perform health check with short timeout
        self._health_check()

    def _health_check(self):
        """Perform a health check to verify LM Studio server is responding."""
        console.print(f"🔍 Checking connection to LM Studio at {self.base_url}...")

        # Create a temporary client with short timeout for health check
        health_client = OpenAI(
            api_key=self.client.api_key,
            base_url=self.base_url,
            timeout=10.0,  # Short timeout for health check
        )

        try:
            # Try to list available models
            models = health_client.models.list()
            model_names = [model.id for model in models.data]

            if model_names:
                console.print(
                    f"✅ LM Studio is responding. Available models: {', '.join(model_names[:3])}"
                )
                if len(model_names) > 3:
                    console.print(f"   ...and {len(model_names) - 3} more")
            else:
                console.print("⚠️  LM Studio is responding but no models are loaded.")
                console.print("   Please load a model in LM Studio before processing.")

        except APITimeoutError:
            error_msg = f"""
❌ Health check failed: Connection to LM Studio timed out!

Troubleshooting steps:
1. Make sure LM Studio is running at: {self.base_url}
2. Verify the local server is started (Click 'Start Server' in LM Studio)
3. Check the base URL is correct in your .env file
4. Test manually: curl {self.base_url.replace("/v1", "")}/v1/models

Current configuration:
- Base URL: {self.base_url}
- Model: {self.model}
"""
            console.print(error_msg)
            raise ConnectionError(error_msg)

        except APIConnectionError as e:
            error_msg = f"""
❌ Health check failed: Cannot connect to LM Studio!

Troubleshooting steps:
1. Verify LM Studio is running
2. Check the base URL is correct: {self.base_url}
3. Ensure the local server is started in LM Studio
4. If using a remote server, check network connectivity and firewall settings

Error: {str(e)}
"""
            console.print(error_msg)
            raise ConnectionError(error_msg)

        except Exception as e:
            console.print(f"⚠️  Unexpected error during health check: {str(e)}")
            console.print("Continuing anyway, but API calls may fail...")

    def organize_transcription(
        self, transcription: str, video_info: dict, lang: str, enrich_text: bool = False
    ) -> str:
        # Calculate minimum lines based on video duration
        raw_video_duration = video_info.get("duration") if video_info else None
        try:
            video_duration = max(0, int(raw_video_duration)) if raw_video_duration is not None else 0
        except (TypeError, ValueError):
            video_duration = 0
        min_lines = calculate_min_summary_lines(video_duration)
        request_timeout = calculate_summary_timeout(
            video_duration,
            minimum_timeout=self.minimum_timeout,
            timeout_per_video_minute=self.timeout_per_video_minute,
        )

        # Format duration for display
        duration_str = ""
        if video_duration:
            minutes = video_duration // 60
            seconds = video_duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            console.print(
                f"📊 Video duration: {duration_str} (~{minutes} min) → Required minimum: {min_lines} lines"
            )

        console.print(
            f"⏱️ Summary request timeout: {int(request_timeout)}s "
            f"(minimum={int(self.minimum_timeout)}s, "
            f"rate={int(self.timeout_per_video_minute)}s/video-minute)"
        )

        video_info_str = ""
        if video_info:
            video_info_str = (
                "Video Information:\n"
                + "\n".join(f"- {k}: {v}" for k, v in video_info.items())
                + "\n\n"
            )

        prompt = (
            f"""
            Main objective: Organise the video information and transcription into a COMPREHENSIVE, DETAILED course document.

            ⚠️ CRITICAL LENGTH REQUIREMENT ⚠️
            * Your response MUST contain AT LEAST {min_lines} lines total (including all content).
            * This is based on video duration ({video_duration // 60} minutes requires {min_lines}+ lines).
            * Every line counts: headers, text, bullets, code blocks, table rows, blank lines between sections.
            * DO NOT summarize or condense - expand each point with full explanations, examples, and details.
            * If your output has fewer than {min_lines} lines, it will be REJECTED and you must regenerate.

            Required level of detail:
            * For EACH major topic: minimum 30-50 lines of detailed explanation
            * Include ALL examples, code snippets, commands, and use cases mentioned
            * Expand on technical concepts with thorough explanations
            * Add subsections for different aspects of each topic
            * Include "Why this matters", "Common pitfalls", "Best practices" for key points
            * Don't skip any information from the transcription - be exhaustive

            Instructions:
            * Do not mention that the summary comes from a video; simply use the transcription as source material.
            * Extract and expand EVERY concept, example, tool, and technique mentioned
            * The output MUST be in {lang} language, even if the transcription is in another language.
            
            Output format:
            * Valid Markdown with proper headings (#, ##, ###), bullet lists, code blocks (```), tables, and formatting.
            
            Required sections (expand each significantly):
            * Title: Based on video title
            * Summary: Comprehensive overview covering all major themes (minimum 10 lines)
                Include at the end: Source: [Youtube Link](<webpage_url>)
            * Detailed Index: Multi-level structure showing all topics and subtopics
            * For EACH topic: Create extensive sections with:
              - Introduction to the concept
              - Detailed explanations with examples
              - Code snippets or commands (in code blocks)
              - Use cases and practical applications
              - Tips, warnings, or best practices
              - Related concepts or tools
            * Conclusion: Thorough wrap-up of key learnings
            * Additional Notes: Any extra information not categorized elsewhere
            """
            + "\nVideo information:\n"
            + video_info_str
            + "\nTranscription:\n"
            + transcription
        )

        system_prompt = """You are a professional teacher and researcher with years of experience creating COMPREHENSIVE, DETAILED courses and guidelines.
Your style is THOROUGH and EXHAUSTIVE - you never skip details or condense information unnecessarily.
You always ensure that NO detail or information is lost from the source material.
You are also an expert in Markdown formatting, so you use headings, bullet points, code snippets, tables, and other formatting features.
You sometimes use emojis to make the document more engaging, but only when appropriate.

IMPORTANT: When given a minimum line count requirement, you MUST meet or exceed it by:
- Providing comprehensive explanations for every concept
- Including all examples, code snippets, and use cases
- Adding subsections to break down complex topics
- Expanding on implications, best practices, and common pitfalls
- Being verbose and detailed rather than concise
"""

        if enrich_text:
            system_prompt += """You are also an expert in finding information on the internet, so you enrich the text with additional information,
using well-known sources and providing references and links to those sources.
"""

        system_prompt += """Do not ask for further information or questions.
Do not use an introduction like "Here is the organized transcription", "Here's the structured document" or similar.
Do not use a conclusion like "I hope this helps" or "Let me know if you have any questions".
Do not include any disclaimer or notes that are not part of the main topic.
"""

        try:
            console.print(f"\n🤖 Connecting to LM Studio at {self.base_url}...")
            console.print(f"📝 Processing transcription with model: {self.model}...")

            response_stream = self.client.with_options(timeout=request_timeout).chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                stream=True,
            )

            # Stream the response with live updates
            full_response = ""
            response_text = Text()

            with Live(
                Panel(response_text, title="🤖 AI Summary", border_style="green"),
                console=console,
                refresh_per_second=4,
            ) as live:
                for chunk in response_stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            full_response += delta.content
                            response_text.append(delta.content)
                            live.update(
                                Panel(response_text, title="🤖 AI Summary", border_style="green")
                            )

            if not full_response:
                raise Exception("No response from LM Studio API")

            console.print("\n✅ Transcription organized successfully!")
            return full_response

        except APITimeoutError as e:
            error_msg = f"""
❌ Connection to LM Studio timed out!

Troubleshooting steps:
1. Make sure LM Studio is running at: {self.base_url}
2. Verify a model is loaded in LM Studio
3. Check that the local server is started (Click 'Start Server' in LM Studio)
4. Test the connection: curl {self.base_url.replace("/v1", "")}/models
5. If on a different machine, ensure the IP address is correct

Current configuration:
- Base URL: {self.base_url}
- Model: {self.model}
"""
            console.print(error_msg)
            raise Exception(error_msg) from e

        except APIConnectionError as e:
            error_msg = f"""
❌ Cannot connect to LM Studio!

Troubleshooting steps:
1. Verify LM Studio is running
2. Check the base URL is correct: {self.base_url}
3. Ensure the local server is started in LM Studio
4. If using a remote server, check network connectivity

Error: {str(e)}
"""
            console.print(error_msg)
            raise Exception(error_msg) from e
