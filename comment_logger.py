import sqlite3
from config import COMMENT_LOG_FILE

class CommentLogger:
    def __init__(self, db_path=COMMENT_LOG_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                persona TEXT,
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def log_comment(self, post_id, persona, comment):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO comments (post_id, persona, comment) VALUES (?, ?, ?)
        ''', (post_id, persona, comment))
        self.conn.commit()

    def get_comments(self, post_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT persona, comment, timestamp FROM comments WHERE post_id = ?
        ''', (post_id,))
        return cursor.fetchall()
