from infrastructure.outbound.agents.ports.summarizer_agent import SummarizerAgent
from infrastructure.outbound.agents.adapters.summarizer_lmstudio_agent import SummarizerLMStudioAgent
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
    fileStorage: FileStoragePort = LocalFileStorage()
    file_path = f"summaries/{video_info.get('title', 'transcription_summary')}.md"
    
    # Check if markdown summary already exists
    if fileStorage.exists(file_path):
        print(f"\n📄 Found existing summary: {file_path}")
        print("✅ Loading cached summary...")
        return file_path
    
    print("\n🤖 No cached summary found. Generating new summary...")
    
    summarizerAgent: SummarizerAgent = SummarizerLMStudioAgent(model=model)

    markdown = summarizerAgent.organize_transcription(transcription, video_info=video_info, lang=lang, enrich_text=enrich_text)
    
    return fileStorage.save(data=markdown, file_path=file_path) 
