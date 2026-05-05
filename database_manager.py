import glob
import os
from typing import List


class DatabaseManager:
    DB_FOLDER = "Database"
    DB_PATTERNS = ("*.sqlite", "*.db")

    @classmethod
    def get_available_databases(cls) -> List[str]:
        os.makedirs(cls.DB_FOLDER, exist_ok=True)
        database_files: List[str] = []

        for pattern in cls.DB_PATTERNS:
            database_files.extend(glob.glob(os.path.join(cls.DB_FOLDER, pattern)))

        return [os.path.basename(file_path) for file_path in database_files]

    @classmethod
    def build_path(cls, database_name: str) -> str:
        return os.path.join(cls.DB_FOLDER, database_name)
