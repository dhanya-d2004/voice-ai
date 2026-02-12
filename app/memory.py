import os
import psycopg2
from contextlib import contextmanager

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 15234)
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dbadmin")


class ShaktiMemory:
    def __init__(self, user_id: str, conversation_id: str):
        self.user_id = user_id
        self.conversation_id = conversation_id

        self.conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        self.conn.autocommit = True

        self._ensure_user()
        self._ensure_conversation()

    @contextmanager
    def _cursor(self):
        cur = self.conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def _ensure_user(self):
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (self.user_id,)
            )

    def _ensure_conversation(self):
        with self._cursor() as cur:
            # Ensure conversation belongs to correct user
            cur.execute(
                """
                INSERT INTO conversations (conversation_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (conversation_id)
                DO UPDATE SET user_id = EXCLUDED.user_id
                """,
                (self.conversation_id, self.user_id)
            )

    def add(self, role: str, content: str):
        with self._cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (%s, %s, %s)
                """,
                (self.conversation_id, role, content)
            )

    def get_recent(self, limit=15):
        with self._cursor() as cur:
            cur.execute(
                """
                SELECT role, content
                FROM messages
                WHERE conversation_id = %s
                ORDER BY id DESC
                LIMIT %s
                """,
                (self.conversation_id, limit)
            )
            rows = cur.fetchall()

        return list(reversed(rows))

    def close(self):
        if self.conn:
            self.conn.close()
