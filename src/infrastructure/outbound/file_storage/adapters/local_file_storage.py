import os

from infrastructure.outbound.file_storage.ports.file_storage_port import FileStoragePort

OUTPUT_PATH = "outputs/"

class LocalFileStorage(FileStoragePort):
    def save(self, data: str, file_path: str) -> str:
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        output_path = os.path.join(OUTPUT_PATH, f"{file_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"File saved: {output_path}")
        return output_path

