from abc import ABC, abstractmethod

class SummarizerAgent(ABC):
    @abstractmethod
    def organize_transcription(self, transcription: str, video_info: dict, lang: str, enrich_text: bool) -> str:
        """
        Organize the transcription by topics and return a markdown string.
        :param transcription: The transcription text to be organized.
        :param video_info: Metadata about the video, such as title and description.
        :param lang: The language code for the transcription.
        :param enrich_text: Whether to enrich the transcription with additional information.
        """
        pass

