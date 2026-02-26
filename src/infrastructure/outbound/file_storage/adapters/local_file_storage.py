import os

from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort

OUTPUT_PATH = "outputs/"

class LocalFileStorage(FileStoragePort):
    def save(self, data: str, file_path: str) -> str:
        output_path = os.path.join(OUTPUT_PATH, f"{file_path}")
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        else:
            raise Exception("Invalid file path provided.")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"File saved: {output_path}")
        return output_path

    def exists(self, file_path: str) -> bool:
        output_path = os.path.join(OUTPUT_PATH, f"{file_path}")
        return os.path.exists(output_path) and os.path.isfile(output_path)

    def read(self, file_path: str) -> str:
        output_path = os.path.join(OUTPUT_PATH, f"{file_path}")
        if not self.exists(file_path):
            raise FileNotFoundError(f"File not found: {output_path}")
        with open(output_path, "r", encoding="utf-8") as f:
            return f.read()

