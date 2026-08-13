import sqlite3
from pathlib import Path
from typing import Optional
from utils.paths import get_db_path
from utils.logger import get_logger

logger = get_logger("DatabaseManager")

class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_db_path()
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates table schemas if they do not exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Command History Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        raw_command TEXT NOT NULL,
                        intent TEXT,
                        action_type TEXT,
                        status TEXT NOT NULL,
                        details TEXT
                    );
                """)

                # Custom Macro Commands Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_commands (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trigger_phrase TEXT UNIQUE NOT NULL,
                        action_sequence TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Persistent Settings Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                """)

                conn.commit()
                logger.info("Database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")

_db_instance: Optional[DatabaseManager] = None

def get_db() -> DatabaseManager:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
