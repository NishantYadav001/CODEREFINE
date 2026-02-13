import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_connection():
    print("------------------------------------------------")
    print("🛠️  MySQL Database Connectivity Check")
    print("------------------------------------------------")

    try:
        import mysql.connector
        from mysql.connector import Error
    except ImportError:
        print("❌ CRITICAL: 'mysql-connector-python' library is missing.")
        print("   Please run: pip install mysql-connector-python")
        return

    config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "coderefine")
    }

    print(f"Target Configuration:")
    print(f"  Host:     {config['host']}")
    print(f"  User:     {config['user']}")
    print(f"  Database: {config['database']}")
    print("------------------------------------------------")

    connection = None
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ CONNECTION SUCCESSFUL")
            print(f"   Server Version: {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"   Current DB:     {record[0]}")
            
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"\n📊 Tables in '{config['database']}':")
            if not tables:
                print("   (No tables found)")
            for table in tables:
                print(f"   - {table[0]}")
                
    except Error as e:
        print(f"❌ CONNECTION FAILED")
        print(f"   Error: {e}")
        print("\nTroubleshooting Tips:")
        print("   1. Is MySQL server running? (Check XAMPP/WAMP/Services)")
        print("   2. Does the database 'coderefine' exist?")
        print("   3. Are the username/password correct?")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Connection closed.")

if __name__ == "__main__":
    check_connection()