from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import TooManyRequests  # Import này quan trọng
from models import db
from models.user import User
from config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
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
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        # ====================== RATE LIMITING THEO IP ======================
        try:
            limiter = getattr(request, 'limiter', None) or getattr(current_app, 'limiter', None)
            if limiter:
                # Áp dụng rate limit trước khi xử lý logic
                limiter.limit(Config.RATELIMIT_LOGIN, key_func=get_remote_address)()
        except TooManyRequests as e:
            # Lấy thời gian còn lại
            retry_after = getattr(e, 'description', None) or str(e)
            flash(f'Too many login attempts from this IP. Please try again later. ({retry_after})', 'danger')
            return render_template('auth/login.html')
        except Exception as e:
            # Fallback nếu có lỗi
            flash('Too many login attempts. Please try again later.', 'danger')
            return render_template('auth/login.html')
        # ===================================================================

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Email validation
        if not email or '@' not in email or not email.endswith('@campus.edu'):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if not password:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
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

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'parking_staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))