from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db_connection
from routes.auth import login_required, validate_password_strength

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'preferences':
            weather_alerts = 1 if request.form.get('weather_alerts') else 0
            irrigation_alerts = 1 if request.form.get('irrigation_alerts') else 0
            crop_alerts = 1 if request.form.get('crop_alerts') else 0
            market_alerts = 1 if request.form.get('market_alerts') else 0
            language = request.form.get('language', 'English')
            temp_unit = request.form.get('temp_unit', 'Celsius')
            theme = request.form.get('theme', 'light')

            cursor.execute('''
                UPDATE user_settings
                SET weather_alerts = ?, irrigation_alerts = ?, crop_alerts = ?, market_alerts = ?,
                    language = ?, temp_unit = ?, theme = ?
                WHERE user_id = ?
            ''', (weather_alerts, irrigation_alerts, crop_alerts, market_alerts, language, temp_unit, theme, user_id))
            conn.commit()
            flash('Settings & notification preferences updated successfully!', 'success')

        elif action == 'password':
            current_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')

            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            user_pwd = row['password'] if row else ''

            if not check_password_hash(user_pwd, current_pwd):
                flash('Current password is incorrect.', 'danger')
            else:
                is_valid, pwd_err = validate_password_strength(new_pwd)
                if not is_valid:
                    flash(f"New password error: {pwd_err}", 'warning')
                elif new_pwd != confirm_pwd:
                    flash('New passwords do not match.', 'danger')
                else:
                    new_hash = generate_password_hash(new_pwd)
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
                    conn.commit()
                    flash('Password updated successfully!', 'success')

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    settings = cursor.fetchone()
    if not settings:
        cursor.execute('''
            INSERT INTO user_settings (user_id, weather_alerts, irrigation_alerts, crop_alerts, market_alerts, language, temp_unit, theme)
            VALUES (?, 1, 1, 1, 1, 'English', 'Celsius', 'light')
        ''', (user_id,))
        conn.commit()
        cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        settings = cursor.fetchone()

    conn.close()

    return render_template('settings.html', user=user, settings=settings)
