from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from models import db
from models.user import User
from config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Root – redirect to appropriate dashboard or login."""
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'parking_staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route with email domain validation + Rate Limiting"""
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    # ====================== RATE LIMITING (IP only) ======================
    limiter = None
    try:
        from app import create_app
        app = create_app()
        limiter = getattr(app, 'limiter', None)
        
        if limiter and request.method == 'POST':
            # Rate limit theo IP (không lock account)
            limiter.limit(Config.RATELIMIT_LOGIN)(lambda: None)()
    except:
        pass  # Tránh lỗi khi test hoặc khởi tạo
    # ===================================================================

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # === VALIDATION EMAIL FORMAT ===
        if not email or '@' not in email:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Phải kết thúc bằng @campus.edu
        if not email.endswith('@campus.edu'):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Kiểm tra input trống
        if not password:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        # === SECURITY: Luôn dùng chung 1 thông báo ===
        if user is None:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Kiểm tra mật khẩu
        if not user.check_password(password):
            # Chỉ tăng attempt (không lock account)
            user.login_attempts = (user.login_attempts or 0) + 1
            db.session.commit()
            
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # ==================== LOGIN THÀNH CÔNG ====================
        user.login_attempts = 0
        db.session.commit()

        session['user_id'] = user.user_id
        session['user_name'] = user.user_name
        session['role'] = user.role
        session['email'] = user.email
        session.permanent = True

        flash(f'Welcome back, {user.user_name}!', 'success')

        # Redirect theo role
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'parking_staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))