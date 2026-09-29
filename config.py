import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'agrismart-production-secret-key-2026-secure')
    DATABASE = os.path.join(BASE_DIR, 'agrismart.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'disease')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '').strip()
    MANDI_API_KEY = os.environ.get('MANDI_API_KEY', '').strip()

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    PERMANENT_SESSION_LIFETIME = 43200  # 12 hours in seconds

    # Rate Limiting & CSRF Configuration
    RATELIMIT_DEFAULT = "120 per minute"
    RATELIMIT_STORAGE_URI = "memory://"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

