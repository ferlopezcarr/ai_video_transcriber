from abc import ABC, abstractmethod

class AudioTranscriberPort(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, lang: str | None) -> str:
        """
        Transcribe the audio file at the given path into text.
        :param audio_path: The path to the audio file to transcribe.
        :param lang: The language code for the transcription (default is 'en').
        :return: The transcribed text.
        """
        pass
