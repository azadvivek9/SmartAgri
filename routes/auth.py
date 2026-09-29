import re
import logging
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db_connection
from extensions import limiter

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('agrismart.security')

COMMON_WEAK_PASSWORDS = {
    '12345678', 'password', '123456789', 'admin123', 'password123',
    'qwertyuiop', 'abcdefgh', 'pass1234', '11111111', '00000000'
}

def is_safe_url(target):
    """Ensure redirect URL is strictly internal to avoid open redirect vulnerabilities."""
    if not target:
        return False
    target = target.strip()
    # Must start with single slash, not double slash, no backslashes, no scheme
    if target.startswith('/') and not target.startswith('//') and not target.startswith('/\\') and ':' not in target:
        return True
    return False

def validate_password_strength(password):
    """
    Validate password requirements:
    - At least 8 characters
    - Not in common weak passwords
    - Contains letters and numbers
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if password.lower() in COMMON_WEAK_PASSWORDS:
        return False, "This password is too simple or common. Please choose a stronger password."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return False, "Password must contain a combination of letters and numbers."
    return True, ""

def is_api_request():
    """Detect whether incoming request expects JSON/API response."""
    return (
        request.path.startswith('/api/') or
        request.is_json or
        request.headers.get('Accept') == 'application/json' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )

def login_required(f):
    """Decorator to require authenticated active user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if is_api_request():
                return jsonify({
                    'status': 'error',
                    'error': 'Unauthorized',
                    'message': 'Authentication required. Please sign in.'
                }), 401
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))

        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, is_active FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            session.clear()
            if is_api_request():
                return jsonify({
                    'status': 'error',
                    'error': 'Unauthorized',
                    'message': 'User session invalid. Please sign in again.'
                }), 401
            flash('Session invalid. Please sign in again.', 'warning')
            return redirect(url_for('auth.login'))

        if row['is_active'] == 0:
            logger.warning(f"Access rejected for deactivated user_id={user_id} on {request.path}")
            session.clear()
            if is_api_request():
                return jsonify({
                    'status': 'error',
                    'error': 'Forbidden',
                    'message': 'Your account has been deactivated by an administrator.'
                }), 403
            flash('Your account has been deactivated by an administrator.', 'danger')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require administrator privileges with server-side DB validation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if is_api_request():
                return jsonify({
                    'status': 'error',
                    'error': 'Unauthorized',
                    'message': 'Authentication required. Please sign in with admin credentials.'
                }), 401
            flash('Please sign in with administrator credentials.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, is_active FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user or user['is_active'] == 0:
            logger.warning(f"Admin access rejected for deactivated user_id={user_id}")
            session.clear()
            if is_api_request():
                return jsonify({
                    'status': 'error',
                    'error': 'Forbidden',
                    'message': 'Account is deactivated.'
                }), 403
            flash('Your account is inactive.', 'danger')
            return redirect(url_for('auth.login'))

        if user['role'] != 'admin':
            logger.warning(f"Unauthorized admin attempt by user_id={user_id} ({session.get('user_email')}) to {request.path} from IP={request.remote_addr}")
            if is_api_request():
                return jsonify({
                    'status': 'error',
                    'error': 'Forbidden',
                    'message': 'Access denied: Administrator privileges required.'
                }), 403
            flash('Access denied: Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
            
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute", methods=["POST"])
def login():
    # If user is already authenticated, redirect appropriately
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.index'))
        return redirect(url_for('dashboard.index'))

    next_url = request.args.get('next', '')
    if not is_safe_url(next_url):
        next_url = ''

    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        posted_next = request.form.get('next', '').strip()
        if is_safe_url(posted_next):
            next_url = posted_next

        if not identifier or not password:
            flash('Please provide your login credentials and password.', 'danger')
            return render_template('login.html', email=identifier, next=next_url)

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Support login by email, phone, or name using parameterized query
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR phone = ? OR LOWER(name) = LOWER(?)",
            (identifier, identifier, identifier)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # Check if user account is active
            is_active = user['is_active'] if ('is_active' in user.keys() and user['is_active'] is not None) else 1
            if not is_active:
                logger.warning(f"Login rejected: Deactivated user attempted login: email='{user['email']}', IP={request.remote_addr}")
                flash('Your account has been deactivated by an administrator. Please contact support.', 'danger')
                return render_template('login.html', email=identifier, next=next_url)

            # Prevent Session Fixation by clearing old session before generating new session state
            session.clear()

            user_role = user['role'] if ('role' in user.keys() and user['role']) else 'user'
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user_role
            session['user_location'] = user['location'] or 'Meerut, Uttar Pradesh'
            session.permanent = True

            logger.info(f"Successful login: user_id={user['id']}, role={user_role}, email={user['email']}, IP={request.remote_addr}")

            # Role-based intelligent routing
            if user_role == 'admin':
                flash(f"Welcome to AgriSmart Admin Control Center, {user['name']}! 🛡️", 'success')
                if next_url and is_safe_url(next_url):
                    return redirect(next_url)
                return redirect(url_for('admin.index'))
            else:
                flash(f"Welcome back, {user['name']}! 👋", 'success')
                if next_url and is_safe_url(next_url) and not next_url.startswith('/admin'):
                    return redirect(next_url)
                return redirect(url_for('dashboard.index'))
        else:
            logger.warning(f"Failed login attempt for identifier='{identifier}' from IP={request.remote_addr}")
            flash('Invalid credentials or password. Please check and try again.', 'danger')
            return render_template('login.html', email=identifier, next=next_url)

    return render_template('login.html', next=next_url)

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("6 per minute", methods=["POST"])
def register():
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.index'))
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        location = request.form.get('location', 'Meerut, Uttar Pradesh').strip()
        village = request.form.get('village', 'Hastinapur').strip()
        land_area = request.form.get('land_area', '4.5 Acres').strip()
        soil_type = request.form.get('soil_type', 'Alluvial Loam').strip()
        main_crop = request.form.get('main_crop', 'Wheat & Sugarcane').strip()

        if not name or not email or not password:
            flash('Name, email, and password are required fields.', 'danger')
            return render_template('register.html')

        # Validate email format
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        # Validate password strength
        is_valid_pwd, pwd_err = validate_password_strength(password)
        if not is_valid_pwd:
            flash(pwd_err, 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if cursor.fetchone():
            conn.close()
            flash('An account with this email address already exists. Please sign in.', 'warning')
            return render_template('register.html')

        pwd_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, role, is_active, location, village, land_area, soil_type, main_crop)
            VALUES (?, ?, ?, ?, 'user', 1, ?, ?, ?, ?, ?)
        ''', (name, email, phone, pwd_hash, location, village, land_area, soil_type, main_crop))
        user_id = cursor.lastrowid

        # Initialize default settings
        cursor.execute('''
            INSERT INTO user_settings (user_id, weather_alerts, irrigation_alerts, crop_alerts, market_alerts, language, temp_unit, theme)
            VALUES (?, 1, 1, 1, 1, 'English', 'Celsius', 'light')
        ''', (user_id,))

        conn.commit()
        conn.close()

        logger.info(f"New user registered: user_id={user_id}, email={email}, IP={request.remote_addr}")

        session.clear()
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_role'] = 'user'
        session['user_location'] = location
        session.permanent = True

        flash('Registration successful! Welcome to AgriSmart Advisory.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        logger.info(f"User logged out: user_id={user_id}")
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))
