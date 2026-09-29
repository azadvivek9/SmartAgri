from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models.database import get_db_connection
from routes.auth import login_required

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        village = request.form.get('village', '').strip()
        land_area = request.form.get('land_area', '').strip()
        soil_type = request.form.get('soil_type', '').strip()
        main_crop = request.form.get('main_crop', '').strip()

        if name:
            cursor.execute('''
                UPDATE users
                SET name = ?, phone = ?, location = ?, village = ?, land_area = ?, soil_type = ?, main_crop = ?
                WHERE id = ?
            ''', (name, phone, location, village, land_area, soil_type, main_crop, user_id))
            conn.commit()
            session['user_name'] = name
            session['user_location'] = location
            flash('Farmer profile updated successfully!', 'success')
        else:
            flash('Farmer name cannot be empty.', 'danger')

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    # Statistics
    cursor.execute("SELECT COUNT(*) FROM soil_records WHERE user_id = ?", (user_id,))
    soil_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM crop_recommendations WHERE user_id = ?", (user_id,))
    crop_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM disease_records WHERE user_id = ?", (user_id,))
    disease_count = cursor.fetchone()[0]

    conn.close()

    stats = {
        'soil_tests': soil_count,
        'crop_recommendations': crop_count,
        'disease_scans': disease_count,
        'member_since': user['created_at'][:10] if user['created_at'] else '2026-09-01'
    }

    return render_template('profile.html', user=user, stats=stats)
