import jwt
import nh3
from datetime import datetime, timedelta
from config import settings

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

# Encryption Setup
ENCRYPTION_AVAILABLE = False
cipher_suite = None
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
    _key = settings.APP_ENCRYPTION_KEY or Fernet.generate_key()
    cipher_suite = Fernet(_key)
except ImportError:
    pass

def verify_password(plain_password, hashed_password):
    if not BCRYPT_AVAILABLE:
        return plain_password == hashed_password
    try:
        pwd_bytes = plain_password[:72].encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password):
    if not BCRYPT_AVAILABLE:
        return password
    pwd_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def encrypt_secret(secret: str) -> str:
    if not ENCRYPTION_AVAILABLE or not secret or not cipher_suite: return secret
    return cipher_suite.encrypt(secret.encode()).decode()

def decrypt_secret(secret: str) -> str:
    if not ENCRYPTION_AVAILABLE or not secret or not cipher_suite: return secret
    try:
        return cipher_suite.decrypt(secret.encode()).decode()
    except:
        return secret

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def sanitize_html(content: str) -> str:
    allowed_tags = {'h1', 'h2', 'h3', 'h4', 'p', 'pre', 'code', 'ul', 'ol', 'li', 'strong', 'em', 'br', 'b', 'i', 'u', 'span', 'div'}
    return nh3.clean(content, tags=allowed_tags)