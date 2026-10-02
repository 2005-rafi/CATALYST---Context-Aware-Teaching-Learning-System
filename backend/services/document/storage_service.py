import os
from backend.core.config.settings import get_settings

class StorageService:
    def __init__(self):
        self.settings = get_settings()

    def save_file(self, workspace_id: str, document_id: str, file_content: bytes, original_filename: str) -> tuple[str, float]:
        target_dir = os.path.join(self.settings.UPLOADS_PATH, workspace_id)
        os.makedirs(target_dir, exist_ok=True)
        
        target_path = os.path.join(target_dir, f"{document_id}_{original_filename}")
        
        with open(target_path, "wb") as f:
            f.write(file_content)
            
        file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
        return target_path, file_size_mb

    def delete_file(self, file_path: str) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def delete_workspace_directory(self, workspace_id: str) -> bool:
        target_dir = os.path.join(self.settings.UPLOADS_PATH, workspace_id)
        if os.path.exists(target_dir):
            import shutil
            shutil.rmtree(target_dir)
            return True
        return False

    def workspace_directory_exists(self, workspace_id: str) -> bool:
        target_dir = os.path.join(self.settings.UPLOADS_PATH, workspace_id)
        return os.path.isdir(target_dir)
