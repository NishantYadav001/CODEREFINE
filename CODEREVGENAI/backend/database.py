import sqlite3
from pathlib import Path
from config import settings
from security import get_password_hash

# Global In-Memory Stores
CODE_DATABASE = []
STUDENT_STATS = {}
ACTIVE_SESSIONS = {}
COMPANY_POLICIES = ""
CODE_SNIPPETS = {}
CODE_HISTORY = {}
USER_ANALYTICS = {}
USER_SETTINGS = {}
PERFORMANCE_METRICS = {}
WEBHOOKS = {}
API_RATE_LIMITS = {}
NEWSLETTER_SUBS = []
MAINTENANCE_MODE = False
GUEST_USAGE = {}

# In-memory User Database
USER_DB = {
    "admin": {"password": settings.ADMIN_PASSWORD, "email": "admin@coderefine.ai"}
}

SQLITE_PATH = Path(__file__).parent / "coderefine.db"

class SQLiteConnection:
    def __init__(self, path: Path):
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row

    def cursor(self, dictionary: bool = False):
        return self._conn.cursor()

    def commit(self):
        return self._conn.commit()

    def close(self):
        return self._conn.close()

    def is_connected(self):
        return True


def get_db_connection():
    try:
        return SQLiteConnection(SQLITE_PATH)
    except sqlite3.Error as exc:
        print(f"Database Warning: {exc} (Using in-memory fallback)")
        return None


def init_db():
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                title TEXT NOT NULL,
                code TEXT NOT NULL,
                language TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                code TEXT NOT NULL,
                action TEXT,
                version INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        admin = cursor.fetchone()

        admin_pwd = settings.ADMIN_PASSWORD
        hashed_pw = get_password_hash(admin_pwd)

        if admin:
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (hashed_pw, "admin")
            )
            print("✅ Admin password synced with environment.")
        else:
            print("⚙️ Creating admin user...")
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("admin", "admin@coderefine.ai", hashed_pw, "admin")
            )
            print("✅ Admin user created successfully.")

        conn.commit()
        print(f"✅ Database initialized: SQLite at {SQLITE_PATH}")
    except sqlite3.Error as exc:
        print(f"❌ Database Initialization Error: {exc}")
    finally:
        cursor.close()
        conn.close()
