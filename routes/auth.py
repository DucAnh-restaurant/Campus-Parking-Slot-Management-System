from flask import (
    Blueprint,
    request,
    session,
    redirect,
    url_for,
    flash,
    render_template
)

from models import db
from models.user import User
from config import Config
from extensions import limiter

# ================= BLUEPRINT =================
auth_bp = Blueprint('auth', __name__)


# ================= INDEX =================
@auth_bp.route('/')
def index():

    if 'user_id' in session:

        role = session.get('role')

        if role == 'admin':
            return redirect(url_for('admin.dashboard'))

        elif role in ['parking_staff', 'staff']:
            return redirect(url_for('staff.dashboard'))

        else:
            return redirect(url_for('user.dashboard'))

    return redirect(url_for('auth.login'))


# ================= LOGIN =================
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit(Config.RATELIMIT_LOGIN)
def login():

    # Nếu đã login
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    # POST request
    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # ================= VALIDATION =================

        if not email:
            flash('Email is required.', 'danger')
            return render_template('auth/login.html')

        if '@' not in email or not email.endswith('@campus.edu'):
            flash('Invalid campus email.', 'danger')
            return render_template('auth/login.html')

        if not password:
            flash('Password is required.', 'danger')
            return render_template('auth/login.html')

        # ================= FIND USER =================

        user = User.query.filter_by(email=email).first()

        # Sai tài khoản
        if user is None or not user.check_password(password):

            flash('Invalid email or password.', 'danger')

            return render_template('auth/login.html')

        # ================= LOGIN SUCCESS =================

        user.login_attempts = 0
        db.session.commit()

        session['user_id'] = user.user_id
        session['user_name'] = user.user_name
        session['role'] = user.role
        session['email'] = user.email

        session.permanent = True

        flash(f'Welcome back, {user.user_name}!', 'success')

        # ================= ROLE REDIRECT =================

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))

        elif user.role == 'parking_staff':
            return redirect(url_for('staff.dashboard'))

        else:
            return redirect(url_for('user.dashboard'))

    # GET request
    return render_template('auth/login.html')


# ================= LOGOUT =================
@auth_bp.route('/logout')
def logout():

    session.clear()

    flash('You have been logged out.', 'info')

    return redirect(url_for('auth.login'))