from openai import OpenAI
from infrastructure.outbound.agents.ports.summarizer_agent import SummarizerAgent


class SummarizerLMStudioAgent(SummarizerAgent):
    def __init__(self, model: str = 'local-model', api_key: str = 'not-needed', base_url: str = 'http://localhost:1234/v1'):
        """
        Initialize LM Studio agent using OpenAI-compatible API.
        :param model: The LLM model to use (defaults to LM Studio's loaded model)
        :param api_key: API key (LM Studio doesn't require a real key, defaults to 'not-needed')
        :param base_url: Base URL for LM Studio API (defaults to local LM Studio instance)
        """
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def organize_transcription(self, transcription: str, video_info: dict, lang: str, enrich_text: bool = False) -> str:
        video_info_str = ""
        if video_info:
            video_info_str = "Video Information:\n" + "\n".join(f"- {k}: {v}" for k, v in video_info.items()) + "\n\n"
        
        prompt = (
            """
            Main objective: Organise the video information and transcription into a course document so that it can be understood more easily.

            Instructions:
            * Do not mention that the summary comes from a video; simply use the transcription as a source of information for the course.
            * If the video information is provided, use it to enrich the context of the transcription.
            * If the transcription is very long, ensure that the response covers ALL the points discussed.
            * The output MUST be in """ + lang + """ language, even if the transcription is in another language.
            
            Output:
            * The response must be valid Markdown with proper headings (#, ##, ###), bullet lists, code snippets (```), and formatting.
            
            Output structure:
            * Title: Usually the title is similar or equal to the video title.
            * Summary: A brief summary of the transcription, capturing the main points discussed in the video. 
                Include in a new line at the end of the summary with the video platform and the url ('webpage_url'), for example: Source: [Youtube Link](<webpage_url>)
            * Index: Create an index after the summary to organize and give structure to the content.
            * Then for each topic, create a section with a title and bullet points, use only paragraphs if needed.
            * Conclusion: After the topics, include the conclusions drawn from the transcription.
            * If there are ideas or concepts that could not be categorized into a specific topic, create a section called "Additional Notes" at the end.
            """
            + "\nVideo information:\n" + video_info_str
            + "\nTranscription:\n" + transcription
        )

        system_prompt = """You are a professional teacher and researcher with years of experience creating courses and guidelines used by millions of students.
You always provide clear and concise information, well-structured and organized.
You always ensure that no detail or information is lost.
You are also an expert in Markdown formatting, so you use headings, bullet points, code snippets, and other formatting features to make the document easy to read and understand.
You sometimes use emojis to make the document more engaging, but only when appropriate and relevant to the content.
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            stream=False
        )

        if not response.choices or len(response.choices) == 0:
            raise Exception("No response from LM Studio API")
        if not response.choices[0].message or not response.choices[0].message.content:
            raise Exception("Invalid response format from LM Studio API")
        
        return response.choices[0].message.content
