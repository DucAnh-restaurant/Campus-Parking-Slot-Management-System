"""
Campus Parking Slot Management System (CPSMS)
Main Flask application entry point.
"""
from flask import Flask, redirect, url_for
from config import Config
from models import db
from models.user import bcrypt

# Import limiter
from extensions import limiter

# Import blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from routes.staff import staff_bp

# === Flask-Limiter ===
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # ====================== RATE LIMITER SETUP ======================
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get("RATELIMIT_DEFAULT", "100 per minute")],
        storage_uri=app.config.get("RATELIMIT_STORAGE_URL", "memory://"),
        headers_enabled=app.config.get("RATELIMIT_HEADERS_ENABLED", True),
        strategy="fixed-window"          # fixed-window hoặc moving-window
    )
    
    limiter.init_app(app)                # Cách chuẩn
    app.limiter = limiter                # Quan trọng: Để dùng trong Blueprint
    # ============================================================

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(staff_bp, url_prefix='/staff')

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))


    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 70)
    print("  CPSMS – Campus Parking Slot Management System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 70)
    print("\n  Default login credentials:")
    print("  Admin    → admin@campus.edu     / admin123")
    print("  Student  → alex@campus.edu      / student123")
    print("  Staff    → guard@campus.edu     / staff123")
    print("=" * 70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)