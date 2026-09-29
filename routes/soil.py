from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models.database import get_db_connection
from services.soil_service import SoilService
from routes.auth import login_required

soil_bp = Blueprint('soil', __name__, url_prefix='/soil')
soil_svc = SoilService()

@soil_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM soil_records WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    latest = cursor.fetchone()

    form_data = {
        'ph': latest['ph'] if latest else 6.8,
        'nitrogen': latest['nitrogen'] if latest else 78.0,
        'phosphorus': latest['phosphorus'] if latest else 38.0,
        'potassium': latest['potassium'] if latest else 210.0,
        'organic_carbon': latest['organic_carbon'] if latest else 0.65,
        'moisture': latest['moisture'] if latest else 55.0,
        'soil_type': latest['soil_type'] if latest else (user['soil_type'] or 'Alluvial Loam')
    }

    result = None

    if request.method == 'POST':
        try:
            ph = float(request.form.get('ph', form_data['ph']))
            n = float(request.form.get('nitrogen', form_data['nitrogen']))
            p = float(request.form.get('phosphorus', form_data['phosphorus']))
            k = float(request.form.get('potassium', form_data['potassium']))
            oc = float(request.form.get('organic_carbon', form_data['organic_carbon']))
            moisture = float(request.form.get('moisture', form_data['moisture']))
            soil_type = request.form.get('soil_type', form_data['soil_type'])

            form_data = {
                'ph': ph, 'nitrogen': n, 'phosphorus': p, 'potassium': k,
                'organic_carbon': oc, 'moisture': moisture, 'soil_type': soil_type
            }

            result = soil_svc.analyze(ph, n, p, k, oc, moisture, soil_type)

            # Store in DB
            fert_summary = "; ".join([f"{f['name']} ({f['dosage']})" for f in result['fertilizers'][:2]])
            irrig_summary = result['moisture']['timing']
            cursor.execute('''
                INSERT INTO soil_records (user_id, nitrogen, phosphorus, potassium, ph, organic_carbon, moisture, soil_type, health_score, fertilizer_rec, irrigation_rec)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, n, p, k, ph, oc, moisture, soil_type,
                result['health_category'], fert_summary, irrig_summary
            ))
            conn.commit()
            flash('Soil analysis completed and saved to your farm profile!', 'success')

        except Exception as e:
            flash(f"Error processing soil parameters: {str(e)}", 'danger')

    # Get recent records for history
    cursor.execute("SELECT * FROM soil_records WHERE user_id = ? ORDER BY id DESC LIMIT 5", (user_id,))
    history = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # If first load, compute analysis on initial values
    if not result:
        result = soil_svc.analyze(
            form_data['ph'], form_data['nitrogen'], form_data['phosphorus'],
            form_data['potassium'], form_data['organic_carbon'],
            form_data['moisture'], form_data['soil_type']
        )

    soil_types_list = [
        'Alluvial Loam',
        'Clay Loam',
        'Black Cotton Soil',
        'Sandy Loam',
        'Red & Yellow Soil',
        'Laterite Soil',
        'Silty Clay'
    ]

    return render_template(
        'soil.html',
        user=user,
        form_data=form_data,
        result=result,
        history=history,
        soil_types=soil_types_list
    )
