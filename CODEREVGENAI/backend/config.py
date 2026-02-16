import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Code Refine"
    VERSION: str = "2.0.0"
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.urandom(32).hex())
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_ENCRYPTION_KEY: str = os.getenv("APP_ENCRYPTION_KEY")
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    DB_NAME: str = os.getenv("DB_NAME", "coderefine")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "password")
    
    # Email
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: str = os.getenv("SMTP_PORT")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_SENDER_EMAIL: str = os.getenv("SMTP_SENDER_EMAIL")

settings = Settings()

AVAILABLE_MODELS = {
    "llama-3.3-70b": {"name": "Llama 3.3 70B", "provider": "Groq", "speed": "Fast", "quality": "Excellent"},
    "llama-3.1-405b": {"name": "Llama 3.1 405B", "provider": "Groq", "speed": "Slower", "quality": "Best"},
    "mixtral-8x7b-32768": {"name": "Mixtral 8x7B", "provider": "Groq", "speed": "Very Fast", "quality": "Good"},
    "gemini-pro": {"name": "Gemini Pro", "provider": "Google", "speed": "Fast", "quality": "Excellent"},
}