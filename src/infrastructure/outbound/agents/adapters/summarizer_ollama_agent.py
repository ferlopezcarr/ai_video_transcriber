import ollama
from infrastructure.outbound.agents.ports.summarizer_agent import SummarizerAgent
from infrastructure.outbound.agents.adapters.summarizer_lmstudio_agent import calculate_min_summary_lines


class SummarizerOllamaAgent(SummarizerAgent):
    def __init__(self, model: str = 'gemma3'):
        self.model = model

    def organize_transcription(self, transcription: str, video_info: dict, lang: str, enrich_text: bool = False) -> str:
        # Calculate minimum lines based on video duration
        video_duration = video_info.get('duration', 0) if video_info else 0
        min_lines = calculate_min_summary_lines(video_duration)
        
        # Format duration for display
        duration_str = ""
        if video_duration:
            minutes = video_duration // 60
            seconds = video_duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            print(f"📊 Video duration: {duration_str} (~{minutes} min) → Required minimum: {min_lines} lines")
        
        video_info_str = ""
        if video_info:
            video_info_str = "Video Information:\n" + "\n".join(f"- {k}: {v}" for k, v in video_info.items()) + "\n\n"
        
        prompt = (
            f"""
            Main objective: Organise the video information and transcription into a COMPREHENSIVE, DETAILED course document.

            ⚠️ CRITICAL LENGTH REQUIREMENT ⚠️
            * Your response MUST contain AT LEAST {min_lines} lines total (including all content).
            * This is based on video duration ({video_duration//60} minutes requires {min_lines}+ lines).
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
            + "\nVideo information:\n" + video_info_str
            + "\nTranscription:\n" + transcription
        )

        options = {
            "temperature": 0.2,
            #"max_tokens": 2048,
            "system": """
                You are a professional teacher and researcher with years of experience creating COMPREHENSIVE, DETAILED courses and guidelines.
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
                + (enrich_text and """
                You are also an expert in finding information on the internet, so you enrich the text with additional information,
                using well-known sources and providing references and links to those sources.
                """ or "")
                + """
                Do not ask for further information or questions.
                Do not use an introduction like "Here is the organized transcription", "Here's the structured document" or similar.
                Do not use a conclusion like "I hope this helps" or "Let me know if you have any questions".
                Do not include any disclaimer or notes that are not part of the main topic.
            """
        }
        if enrich_text:
            options["provider"] = "internet"

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options=options
        )
        return response['response']
