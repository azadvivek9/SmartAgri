import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

from werkzeug.security import generate_password_hash
from models.database import get_db_connection
from routes.auth import admin_required, validate_password_strength
from extensions import limiter
from config import Config, BASE_DIR

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger('agrismart.admin')


@admin_bp.route('/')
@admin_required
def index():
    """Main Admin Control Center Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. User metrics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    total_admins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'admin' OR role IS NULL")
    total_farmers = cursor.fetchone()[0]

    # 2. Activity metrics
    cursor.execute("SELECT COUNT(*) FROM soil_records")
    total_soil_tests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crop_recommendation_history")
    total_crop_recs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM disease_records")
    total_disease_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM mandi_prices")
    total_mandi_records = cursor.fetchone()[0]

    # 3. Recent Users
    cursor.execute("SELECT id, name, email, phone, role, location, created_at FROM users ORDER BY id DESC LIMIT 10")
    recent_users = [dict(row) for row in cursor.fetchall()]

    # 4. Recent Advisory Activity Stream
    cursor.execute('''
        SELECT 'soil' AS type, s.id, s.created_at, u.name AS user_name, u.email,
               ('Soil Health: ' || s.health_score || ' (pH ' || s.ph || ')') AS detail
        FROM soil_records s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.id DESC LIMIT 5
    ''')
    recent_soil = [dict(row) for row in cursor.fetchall()]

    cursor.execute('''
        SELECT 'crop' AS type, c.id, c.created_at, u.name AS user_name, u.email,
               ('Crop Recommendation: ' || c.recommended_crop || ' (' || ROUND(c.confidence, 1) || '%)') AS detail
        FROM crop_recommendation_history c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.id DESC LIMIT 5
    ''')
    recent_crops = [dict(row) for row in cursor.fetchall()]

    cursor.execute('''
        SELECT 'disease' AS type, d.id, d.created_at, u.name AS user_name, u.email,
               ('Disease Scan: ' || d.disease || ' (' || ROUND(d.confidence, 1) || '%)') AS detail
        FROM disease_records d
        JOIN users u ON d.user_id = u.id
        ORDER BY d.id DESC LIMIT 5
    ''')
    recent_disease = [dict(row) for row in cursor.fetchall()]

    # Combine and sort activity items
    recent_activities = sorted(
        recent_soil + recent_crops + recent_disease,
        key=lambda x: str(x.get('created_at', '')),
        reverse=True
    )[:10]

    # 5. System Health Check
    crop_model_path = os.path.join(BASE_DIR, 'models', 'crop_recommendation_model.pkl')
    disease_model_path = os.path.join(BASE_DIR, 'models', 'plant_disease_model.keras')

    system_health = {
        'database': 'Operational (SQLite)',
        'crop_model': 'Active & Loaded' if os.path.exists(crop_model_path) else 'Pending Model Weights',
        'disease_model': 'Active & Ready' if os.path.exists(disease_model_path) else 'Training / Pending Weights',
        'weather_api': 'Connected' if Config.OPENWEATHER_API_KEY else 'Simulation Fallback Mode',
        'mandi_dataset': f'{total_mandi_records:,} Mandi Records Active'
    }

    conn.close()

    return render_template(
        'admin/index.html',
        total_users=total_users,
        total_admins=total_admins,
        total_farmers=total_farmers,
        total_soil_tests=total_soil_tests,
        total_crop_recs=total_crop_recs,
        total_disease_scans=total_disease_scans,
        total_mandi_records=total_mandi_records,
        recent_users=recent_users,
        recent_activities=recent_activities,
        system_health=system_health
    )


@admin_bp.route('/users')
@admin_required
def users_list():
    """User Management Table & Directory."""
    query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()
    status_filter = request.args.get('status', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM users WHERE 1=1"
    params = []

    if query:
        sql += " AND (LOWER(name) LIKE ? OR LOWER(email) LIKE ? OR phone LIKE ? OR LOWER(location) LIKE ?)"
        wildcard = f"%{query.lower()}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    if role_filter:
        sql += " AND role = ?"
        params.append(role_filter)

    if status_filter == 'active':
        sql += " AND (is_active = 1 OR is_active IS NULL)"
    elif status_filter == 'inactive':
        sql += " AND is_active = 0"

    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    users = [dict(row) for row in cursor.fetchall()]

    # Stats for filter tabs
    cursor.execute("SELECT COUNT(*) FROM users")
    count_all = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    count_admins = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE role != 'admin' OR role IS NULL")
    count_farmers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1 OR is_active IS NULL")
    count_active = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 0")
    count_inactive = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin/users.html',
        users=users,
        query=query,
        role_filter=role_filter,
        status_filter=status_filter,
        count_all=count_all,
        count_admins=count_admins,
        count_farmers=count_farmers,
        count_active=count_active,
        count_inactive=count_inactive
    )


@admin_bp.route('/users/create', methods=['POST'])
@admin_required
@limiter.limit("30 per minute")
def create_user():
    """Create new User or Administrator from Admin Panel."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'user').strip()
    is_active = int(request.form.get('is_active', 1))
    location = request.form.get('location', 'Meerut, Uttar Pradesh').strip()
    village = request.form.get('village', 'Hastinapur').strip()
    land_area = request.form.get('land_area', '4.5 Acres').strip()
    soil_type = request.form.get('soil_type', 'Alluvial Loam').strip()
    main_crop = request.form.get('main_crop', 'Wheat & Sugarcane').strip()

    if not name or not email or not password:
        flash('Name, email, and password are required to create a user.', 'danger')
        return redirect(url_for('admin.users_list'))

    # Validate password
    is_valid_pwd, pwd_err = validate_password_strength(password)
    if not is_valid_pwd:
        flash(f"Password error: {pwd_err}", 'danger')
        return redirect(url_for('admin.users_list'))

    if role not in ['user', 'admin']:
        role = 'user'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    if cursor.fetchone():
        conn.close()
        flash(f"A user with email '{email}' already exists.", 'warning')
        return redirect(url_for('admin.users_list'))

    pwd_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO users (name, email, phone, password, role, is_active, location, village, land_area, soil_type, main_crop)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, pwd_hash, role, is_active, location, village, land_area, soil_type, main_crop))
    user_id = cursor.lastrowid

    cursor.execute('''
        INSERT OR IGNORE INTO user_settings (user_id, weather_alerts, irrigation_alerts, crop_alerts, market_alerts, language, temp_unit, theme)
        VALUES (?, 1, 1, 1, 1, 'English', 'Celsius', 'light')
    ''', (user_id,))

    conn.commit()
    conn.close()

    admin_id = session.get('user_id')
    logger.info(f"Admin (user_id={admin_id}) created user (user_id={user_id}, email={email}, role={role})")

    flash(f"User account for '{name}' created successfully with role '{role}'.", 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@admin_required
@limiter.limit("30 per minute")
def edit_user(user_id):
    """Edit user details and role from Admin Panel."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    role = request.form.get('role', 'user').strip()
    is_active_raw = request.form.get('is_active')
    location = request.form.get('location', '').strip()
    new_password = request.form.get('password', '').strip()

    if not name or not email:
        flash('Name and email cannot be empty.', 'danger')
        return redirect(url_for('admin.users_list'))

    if role not in ['user', 'admin']:
        role = 'user'

    # Prevent current logged-in admin from demoting themselves or deactivating themselves
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id and role != 'admin':
        flash('Security Alert: You cannot remove admin role from your own active account.', 'danger')
        return redirect(url_for('admin.users_list'))

    is_active = 1 if (is_active_raw in ['1', 'on', 'true', 'active'] or is_active_raw is None) else 0
    if user_id == current_admin_id:
        is_active = 1

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for duplicate email in other accounts
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?) AND id != ?", (email, user_id))
    if cursor.fetchone():
        conn.close()
        flash(f"Email '{email}' is already in use by another account.", 'warning')
        return redirect(url_for('admin.users_list'))

    if new_password:
        is_valid_pwd, pwd_err = validate_password_strength(new_password)
        if not is_valid_pwd:
            conn.close()
            flash(f"Password update failed: {pwd_err}", 'danger')
            return redirect(url_for('admin.users_list'))
        pwd_hash = generate_password_hash(new_password)
        cursor.execute('''
            UPDATE users SET name = ?, email = ?, phone = ?, role = ?, is_active = ?, location = ?, password = ?
            WHERE id = ?
        ''', (name, email, phone, role, is_active, location, pwd_hash, user_id))
    else:
        cursor.execute('''
            UPDATE users SET name = ?, email = ?, phone = ?, role = ?, is_active = ?, location = ?
            WHERE id = ?
        ''', (name, email, phone, role, is_active, location, user_id))

    conn.commit()
    conn.close()

    logger.info(f"Admin (user_id={current_admin_id}) edited user_id={user_id} (email={email}, role={role}, is_active={is_active})")

    # If editing current session user, update session name/email
    if user_id == current_admin_id:
        session['user_name'] = name
        session['user_email'] = email
        session['user_location'] = location

    flash(f"User account '{name}' updated successfully.", 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
@limiter.limit("30 per minute")
def toggle_status(user_id):
    """Activate or deactivate a user account."""
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id:
        flash('Security Alert: You cannot deactivate your own active administrator account.', 'danger')
        return redirect(url_for('admin.users_list'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_active, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        flash('User account not found.', 'danger')
        return redirect(url_for('admin.users_list'))

    current_status = user['is_active'] if user['is_active'] is not None else 1
    new_status = 0 if current_status == 1 else 1
    cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
    conn.commit()
    conn.close()

    logger.info(f"Admin (user_id={current_admin_id}) changed status of user_id={user_id} ({user['email']}) to is_active={new_status}")

    if new_status == 1:
        flash(f"Account for '{user['name']}' has been ACTIVATED (user can now log in).", 'success')
    else:
        flash(f"Account for '{user['name']}' has been DEACTIVATED (login is now blocked).", 'warning')

    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@admin_required
@limiter.limit("30 per minute")
def toggle_role(user_id):
    """Quickly toggle between admin and user role."""
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id:
        flash('Security Alert: You cannot demote your own active admin account.', 'danger')
        return redirect(url_for('admin.users_list'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        flash('User account not found.', 'danger')
        return redirect(url_for('admin.users_list'))

    new_role = 'admin' if user['role'] != 'admin' else 'user'
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

    logger.info(f"Admin (user_id={current_admin_id}) changed role of user_id={user_id} ({user['email']}) to role={new_role}")

    flash(f"Role for '{user['name']}' changed to '{new_role.upper()}'.", 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
@limiter.limit("30 per minute")
def delete_user(user_id):
    """Delete a user account and associated records."""
    current_admin_id = session.get('user_id')
    if user_id == current_admin_id:
        flash('Security Alert: You cannot delete your own active administrator account.', 'danger')
        return redirect(url_for('admin.users_list'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        flash('User account not found.', 'danger')
        return redirect(url_for('admin.users_list'))

    user_name = user['name']
    user_email = user['email']

    # Delete related records
    cursor.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM soil_records WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM crop_recommendation_history WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM crop_recommendations WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM disease_records WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    logger.info(f"Admin (user_id={current_admin_id}) deleted user_id={user_id} ({user_email}) and all associated records")

    flash(f"User account '{user_name}' and all associated records have been permanently deleted.", 'success')
    return redirect(url_for('admin.users_list'))

