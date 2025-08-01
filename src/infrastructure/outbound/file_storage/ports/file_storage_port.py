from abc import ABC, abstractmethod

class FileStoragePort(ABC):
    @abstractmethod
    def save(self, data: str, file_path: str) -> str:
        """
        Save the plain text transcription to a file and return the file path.
        :param data: The data to save.
        :param file_path: The full path of the file.
        """
        pass

