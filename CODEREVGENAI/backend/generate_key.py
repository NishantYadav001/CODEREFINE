import os
import sys

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("❌ Error: 'cryptography' library not found.")
    print("   Please run: pip install cryptography")
    sys.exit(1)

def generate_key():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Generate a secure URL-safe base64-encoded 32-byte key
    key = Fernet.generate_key().decode()
    
    # Check if .env exists
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(f"APP_ENCRYPTION_KEY={key}\n")
        print(f"✅ Created .env and added APP_ENCRYPTION_KEY.")
        return

    # Read existing content to check for duplicates
    with open(env_path, 'r') as f:
        content = f.read()
    
    if "APP_ENCRYPTION_KEY=" in content:
        print("⚠️  APP_ENCRYPTION_KEY already exists in .env. No changes made to prevent data loss.")
        return

    # Append key
    with open(env_path, 'a') as f:
        if content and not content.endswith('\n'):
            f.write('\n')
        f.write(f"APP_ENCRYPTION_KEY={key}\n")
    
    print(f"✅ APP_ENCRYPTION_KEY generated and appended to .env")
    print(f"🔑 Key: {key}")

if __name__ == "__main__":
    generate_key()