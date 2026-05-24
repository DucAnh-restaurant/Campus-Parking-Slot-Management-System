from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from flask_limiter import Limiter
from models import db
from models.user import User
from config import Config

from flask_limiter.util import get_remote_address

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
@Limiter.limit("10 per minute", methods=["POST"])   # Giới hạn mạnh cho login
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user is None:
            # Vẫn trả về thông báo chung để không leak thông tin user tồn tại
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Không kiểm tra is_locked nữa (hoặc giữ để admin lock manual)

        if not user.check_password(password):
            # Chỉ ghi log failed attempt (không khóa account)
            # Có thể lưu vào bảng login_log nếu muốn audit sau
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        # Successful login – reset attempts
        user.login_attempts = 0
        db.session.commit()

        session['user_id'] = user.user_id
        session['user_name'] = user.user_name
        session['role'] = user.role
        session['email'] = user.email
        session.permanent = True

        flash(f'Welcome back, {user.user_name}!', 'success')

        # Role-based redirect
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
