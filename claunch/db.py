import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".claunch.db"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id        INTEGER PRIMARY KEY,
                path      TEXT UNIQUE NOT NULL,
                last_used TEXT NOT NULL,
                use_count INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()

    def save_location(self, path: str):
        now = datetime.now().isoformat()
        self.conn.execute(
            """
            INSERT INTO locations (path, last_used, use_count)
            VALUES (?, ?, 1)
            ON CONFLICT(path) DO UPDATE SET
                last_used = excluded.last_used,
                use_count = use_count + 1
            """,
            (path, now),
        )
        self.conn.commit()

    def get_locations(self) -> list:
        cursor = self.conn.execute(
            """
            SELECT path, last_used, use_count
            FROM locations
            ORDER BY last_used DESC
            LIMIT 50
            """
        )
        return [
            {"path": row[0], "last_used": row[1], "use_count": row[2]}
            for row in cursor.fetchall()
        ]

    def remove_location(self, path: str):
        self.conn.execute("DELETE FROM locations WHERE path = ?", (path,))
        self.conn.commit()

    def close(self):
        self.conn.close()
