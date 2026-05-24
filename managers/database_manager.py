import glob
import json
import os
from typing import Dict, List


class DatabaseManager:
    DB_FOLDER = "Database"
    DB_PATTERNS = ("*.sqlite", "*.db")
    ORACLE_CONNECTIONS_FILE = os.path.join(DB_FOLDER, "oracle_connections.json")

    @classmethod
    def get_available_databases(cls) -> List[str]:
        os.makedirs(cls.DB_FOLDER, exist_ok=True)
        database_files: List[str] = []
        for pattern in cls.DB_PATTERNS:
            database_files.extend(glob.glob(os.path.join(cls.DB_FOLDER, pattern)))
        return [os.path.basename(f) for f in database_files]

    @classmethod
    def build_path(cls, database_name: str) -> str:
        return os.path.join(cls.DB_FOLDER, database_name)

    @classmethod
    def build_sqlite_uri(cls, database_name: str) -> str:
        return f"sqlite:///{cls.build_path(database_name)}"

    @staticmethod
    def build_oracle_uri(user: str, password: str, host: str, port: str, service: str) -> str:
        return f"oracle+oracledb://{user}:{password}@{host}:{port}/{service}"

    # --- Oracle connection management ---

    @classmethod
    def load_oracle_connections(cls) -> List[Dict]:
        if not os.path.exists(cls.ORACLE_CONNECTIONS_FILE):
            return []
        with open(cls.ORACLE_CONNECTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def save_oracle_connections(cls, connections: List[Dict]) -> None:
        os.makedirs(cls.DB_FOLDER, exist_ok=True)
        with open(cls.ORACLE_CONNECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(connections, f, ensure_ascii=False, indent=2)

    @classmethod
    def add_oracle_connection(cls, name: str, host: str, port: str, service: str, user: str, password: str) -> None:
        connections = cls.load_oracle_connections()
        connections.append({
            "name": name,
            "host": host,
            "port": port,
            "service": service,
            "user": user,
            "password": password,
        })
        cls.save_oracle_connections(connections)

    @classmethod
    def delete_oracle_connection(cls, name: str) -> None:
        connections = cls.load_oracle_connections()
        cls.save_oracle_connections([c for c in connections if c["name"] != name])
