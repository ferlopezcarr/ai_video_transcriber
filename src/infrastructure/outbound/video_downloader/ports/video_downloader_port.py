from abc import ABC, abstractmethod
from typing import LiteralString

class VideoDownloaderPort(ABC):
    @abstractmethod
    def get_video_info(self, url: str) -> dict:
        pass

    @abstractmethod
    def download_subtitles(self, url: str, lang: str) -> LiteralString | None:
        pass

    @abstractmethod
    def download_audio(self, url: str) -> str:
        pass