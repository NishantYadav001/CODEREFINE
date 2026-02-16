import mysql.connector
from mysql.connector import Error
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

DB_AVAILABLE = False
try:
    import mysql.connector
    DB_AVAILABLE = True
except ImportError:
    pass

def get_db_connection():
    if not DB_AVAILABLE:
        return None
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            connect_timeout=10
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Database Warning: {e} (Using in-memory fallback)")
    return None

def init_db():
    if not DB_AVAILABLE:
        return
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Snippets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    code LONGTEXT NOT NULL,
                    language VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                )
            """)

            # History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    code LONGTEXT NOT NULL,
                    action VARCHAR(50),
                    version INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                )
            """)
            
            # Admin User Setup
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            admin_pwd = settings.ADMIN_PASSWORD
            hashed_pw = get_password_hash(admin_pwd)
            
            if admin:
                cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (hashed_pw,))
                print(f"✅ Admin password synced with environment.")
            else:
                print("⚙️ Creating admin user...")
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    ("admin", "admin@coderefine.ai", hashed_pw, "admin")
                )
                print("✅ Admin user created successfully.")

            conn.commit()
            print(f"✅ Database initialized: 'users' table ready at {settings.DB_HOST}:{settings.DB_PORT}")
        except Error as e:
            print(f"❌ Database Initialization Error: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()