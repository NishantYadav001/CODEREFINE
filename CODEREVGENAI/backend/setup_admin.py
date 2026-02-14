import os
import mysql.connector
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_password_hash(password):
    pwd_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def setup_admin():
    print("🔌 Connecting to database...")
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            database=os.getenv("DB_NAME", "coderefine")
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Check if admin exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            admin_pwd = os.getenv("ADMIN_PASSWORD", "password")
            
            if admin:
                print("⚠️ Admin user already exists. Resetting password...")
                hashed_pw = get_password_hash(admin_pwd)
                cursor.execute("UPDATE users SET password_hash = %s WHERE username = 'admin'", (hashed_pw,))
                connection.commit()
                print(f"✅ Admin password reset to: {admin_pwd}")
            else:
                print("⚙️ Creating admin user...")
                hashed_pw = get_password_hash(admin_pwd) # Default password
                
                # Ensure table exists (basic check)
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
                
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    ("admin", "admin@coderefine.ai", hashed_pw, "admin")
                )
                connection.commit()
                print("✅ Admin user created successfully.")
                print("   Username: admin")
                print(f"   Password: {admin_pwd}")
                
            cursor.close()
            connection.close()
            
    except mysql.connector.Error as e:
        print(f"❌ Database Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_admin()