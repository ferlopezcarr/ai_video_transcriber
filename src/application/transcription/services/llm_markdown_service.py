import os
from infrastructure.outbound.agents.ports.summarizer_agent import SummarizerAgent
from infrastructure.outbound.agents.adapters.summarizer_ollama_agent import SummarizerOllamaAgent
from infrastructure.outbound.file_storage.adapters.local_file_storage import LocalFileStorage
from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort

def transcription_to_markdown(transcription: str, model: str, video_info: dict, lang: str = 'en', enrich_text: bool = False) -> str:
    """
    Organize the transcription by topics and return a markdown string using the LLM adapter.
    :param transcription: The transcription text to be organized.
    :param model: The LLM model to use for organizing the transcription.
    :param video_info: Metadata about the video, such as title and description.
    :param lang: The language code for the transcription.
    :param enrich_text: Whether to enrich the text with additional information.
    """
    summarizerAgent: SummarizerAgent = SummarizerOllamaAgent(model=model)
    fileStorage: FileStoragePort = LocalFileStorage()

    markdown = summarizerAgent.organize_transcription(transcription, video_info=video_info, lang=lang, enrich_text=enrich_text)
    
    file_path = f"summaries/{video_info.get('title', 'transcription_summary')}.md"
    return fileStorage.save(data=markdown, file_path=file_path) 
