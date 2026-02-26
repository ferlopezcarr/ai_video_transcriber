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

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        :param file_path: The relative path of the file to check.
        :return: True if the file exists, False otherwise.
        """
        pass

    @abstractmethod
    def read(self, file_path: str) -> str:
        """
        Read the content of a file.
        :param file_path: The relative path of the file to read.
        :return: The content of the file.
        """
        pass

