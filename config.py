import os

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cpsms-super-secret-key-change-in-production')

    # ── Database Configuration ───────────────────────────────────────
    # Set USE_MYSQL=true to use MySQL. Otherwise SQLite is used for easy local testing.
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() == 'true'

    if USE_MYSQL:
        # MySQL – update these or set environment variables
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'cpsms')

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20,
        }
    else:
        # SQLite – zero-config, works out of the box
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'cpsms.db')
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session config
    SESSION_TYPE = 'filesystem'

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # ── Security & Login Configuration ──────────────────────────────
    # Account lockout (có thể giữ hoặc bỏ sau)
    MAX_LOGIN_ATTEMPTS = 5                    # Tăng lên 5 là hợp lý hơn

    # Thời gian tính login attempts (giây)
    LOGIN_ATTEMPT_WINDOW = 300                # 5 phút

    # ── Rate Limiting (Flask-Limiter) ───────────────────────────────
    RATELIMIT_DEFAULT = "100 per minute"      # Giới hạn mặc định cho toàn app
    RATELIMIT_STORAGE_URL = "memory://"       # Dùng Redis khi production: "redis://localhost:6379"
    
    # Rate limit cụ thể cho login (rất quan trọng)
    RATELIMIT_LOGIN = "10 per minute"         # 10 lần login / phút từ 1 IP
    
    # Rate limit theo IP + Email (chống brute force mạnh hơn)
    RATELIMIT_LOGIN_PER_EMAIL = "5 per minute"

    # Tùy chọn nâng cao
    RATELIMIT_ENABLED = True
    RATELIMIT_HEADERS_ENABLED = True
