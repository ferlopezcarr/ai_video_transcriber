import os
from infrastructure.outbound.agents.ports.summarizer_agent import SummarizerAgent
from infrastructure.outbound.agents.adapters.summarizer_lmstudio_agent import SummarizerLMStudioAgent
from infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage
from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort
from config.env_service import EnvService

def transcription_to_markdown(transcription: str, model: str, video_info: dict, lang: str = 'en', enrich_text: bool = False) -> str:
    """
    Organize the transcription by topics and return a markdown string using the LLM adapter.
    :param transcription: The transcription text to be organized.
    :param model: The LLM model to use for organizing the transcription.
    :param video_info: Metadata about the video, such as title and description.
    :param lang: The language code for the transcription.
    :param enrich_text: Whether to enrich the text with additional information.
    """
    # Get LM Studio API configuration from environment variables
    api_key = EnvService.get_lm_studio_api_key()
    base_url = EnvService.get_lm_studio_base_url()
    
    summarizerAgent: SummarizerAgent = SummarizerLMStudioAgent(model=model, api_key=api_key, base_url=base_url)
    fileStorage: FileStoragePort = LocalFileStorage()

    markdown = summarizerAgent.organize_transcription(transcription, video_info=video_info, lang=lang, enrich_text=enrich_text)
    
    file_path = f"summaries/{video_info.get('title', 'transcription_summary')}.md"
    return fileStorage.save(data=markdown, file_path=file_path) 
