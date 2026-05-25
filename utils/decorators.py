from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Redirect to login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Allow only admin users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        
        # Sửa ở đây: Cho phép cả 2 role
        if role not in ['parking_staff', 'staff']:
            flash('Bạn không có quyền truy cập khu vực Staff!', 'danger')
            return redirect(url_for('user.login'))   # hoặc url_for('user.dashboard')
        
        return f(*args, **kwargs)
    return decorated_function
