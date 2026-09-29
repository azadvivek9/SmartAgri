import json
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models.database import get_db_connection
from services.crop_recommendation_service import crop_service
from routes.auth import login_required
from extensions import csrf, limiter

logger = logging.getLogger(__name__)

crop_bp = Blueprint('crop', __name__)

@crop_bp.route('/crop', methods=['GET'])
@crop_bp.route('/crop/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    # Get latest soil record to pre-populate form for farmer convenience
    cursor.execute("SELECT * FROM soil_records WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    latest_soil = cursor.fetchone()

    metadata = crop_service.get_metadata()
    feature_configs = metadata.get('feature_configs', {})
    allowed_states = metadata.get('allowed_states', [
        'Uttar Pradesh', 'Punjab', 'Haryana', 'Maharashtra', 'Gujarat', 
        'Madhya Pradesh', 'Rajasthan', 'Bihar', 'West Bengal', 'Karnataka', 
        'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Assam', 'Odisha'
    ])
    allowed_seasons = metadata.get('allowed_seasons', [
        'Kharif', 'Rabi', 'Summer', 'Whole Year', 'Autumn', 'Winter'
    ])

    user_location = user['location'] if user and user['location'] else 'Uttar Pradesh'
    default_state = 'Uttar Pradesh'
    for s in allowed_states:
        if s.lower() in user_location.lower():
            default_state = s
            break

    # Dataset median / configured defaults
    area_cfg = feature_configs.get('area', {})
    rain_cfg = feature_configs.get('rainfall', {})
    fert_cfg = feature_configs.get('fertilizer', {})
    pest_cfg = feature_configs.get('pesticide', {})

    form_data = {
        'state': default_state,
        'season': 'Kharif',
        'area': area_cfg.get('default', 5.0),
        'rainfall': rain_cfg.get('default', 1248.0),
        'fertilizer': fert_cfg.get('default', 1250.0),
        'pesticide': pest_cfg.get('default', 24.0),
        'nitrogen': latest_soil['nitrogen'] if latest_soil else 85,
        'phosphorus': latest_soil['phosphorus'] if latest_soil else 42,
        'potassium': latest_soil['potassium'] if latest_soil else 45,
        'ph': latest_soil['ph'] if latest_soil else 6.8
    }

    # Initial ML Prediction
    prediction_response = crop_service.predict(form_data)
    result = None
    if prediction_response.get('success'):
        result = prediction_response.get('primary_match', {})
        result['alternatives'] = prediction_response.get('alternatives', [])

    # Enforce database 10-record cap for user history
    cursor.execute("""
        DELETE FROM crop_recommendation_history
        WHERE user_id = ? AND id NOT IN (
            SELECT id FROM (
                SELECT id FROM crop_recommendation_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 10
            )
        )
    """, (user_id, user_id))
    conn.commit()

    # Fetch latest 10 user history records for dynamic client-side filtering & display
    cursor.execute("""
        SELECT * FROM crop_recommendation_history 
        WHERE user_id = ? 
        ORDER BY id DESC
        LIMIT 10
    """, (user_id,))
    history_rows = cursor.fetchall()
    history = [dict(r) for r in history_rows]

    # Collect distinct crops, seasons, suitabilities from history or model classes
    distinct_crops = sorted(list(set([h['recommended_crop'] for h in history if h.get('recommended_crop')] + metadata.get('crop_classes', []))))
    distinct_seasons = sorted(list(set([h['season'] for h in history if h.get('season')] + allowed_seasons)))
    distinct_suitabilities = ['HIGH', 'MODERATE', 'LOW']

    # Crop Planning Advisory data
    planning_crops = crop_service.get_planning_crops()
    default_planning_crop = "Rice" if "Rice" in planning_crops else (planning_crops[0] if planning_crops else "Rice")
    initial_crop_plan = crop_service.get_crop_plan(default_planning_crop, location=user_location)

    conn.close()

    return render_template(
        'crop.html',
        user=user,
        form_data=form_data,
        result=result,
        history=history,
        allowed_states=allowed_states,
        allowed_seasons=allowed_seasons,
        metadata=metadata,
        feature_configs=feature_configs,
        distinct_crops=distinct_crops,
        distinct_seasons=distinct_seasons,
        distinct_suitabilities=distinct_suitabilities,
        planning_crops=planning_crops,
        planning_metadata=crop_service.planning_data,
        initial_crop_plan=initial_crop_plan,
        user_location=user_location
    )


@crop_bp.route('/api/crop-recommendation/predict', methods=['POST'])
@crop_bp.route('/crop/predict', methods=['POST'])
@csrf.exempt
@login_required
@limiter.limit("30 per minute")
def predict_api():

    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'error': 'Session expired. Please log in to get crop recommendations.'
        }), 401

    user_id = session['user_id']
    
    # Extract input data from JSON or Form
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    try:
        # Run ML model prediction
        prediction_result = crop_service.predict(data)

        if not prediction_result.get('success'):
            error_msg = prediction_result.get('error', 'Unable to generate crop recommendation. Please check your inputs and try again.')
            logger.warning(f"Prediction failed for user {user_id}: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

        primary_match = prediction_result['primary_match']
        alternatives = prediction_result['alternatives']
        validated_input = prediction_result['input']

        # Extract optional soil metrics for DB display if provided
        n_val = float(data.get('nitrogen', 85))
        p_val = float(data.get('phosphorus', 42))
        k_val = float(data.get('potassium', 45))
        ph_val = float(data.get('ph', 6.8))

        # Save to SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()

        input_json = json.dumps({
            **validated_input,
            'nitrogen': n_val,
            'phosphorus': p_val,
            'potassium': k_val,
            'ph': ph_val
        })

        cursor.execute('''
            INSERT INTO crop_recommendation_history (
                user_id, recommended_crop, confidence, suitability, season, state,
                area, rainfall, fertilizer, pesticide, nitrogen, phosphorus, potassium, ph,
                input_features
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            primary_match['recommended_crop'],
            primary_match['confidence'],
            primary_match['suitability'],
            validated_input.get('Season', ''),
            validated_input.get('State', ''),
            validated_input.get('Area', 0.0),
            validated_input.get('Annual_Rainfall', 0.0),
            validated_input.get('Fertilizer', 0.0),
            validated_input.get('Pesticide', 0.0),
            n_val,
            p_val,
            k_val,
            ph_val,
            input_json
        ))
        record_id = cursor.lastrowid

        # Also insert into legacy crop_recommendations table
        cursor.execute('''
            INSERT INTO crop_recommendations (
                user_id, recommended_crop, suitability, confidence, season,
                nitrogen, phosphorus, potassium, ph, temperature, humidity, rainfall
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            primary_match['recommended_crop'],
            primary_match['suitability'],
            primary_match['confidence'],
            validated_input.get('Season', ''),
            n_val,
            p_val,
            k_val,
            ph_val,
            float(data.get('temperature', 26.5)),
            float(data.get('humidity', 68.0)),
            validated_input.get('Annual_Rainfall', 1100.0)
        ))

        # Enforce strict 10-record limit per user in database
        cursor.execute('''
            DELETE FROM crop_recommendation_history
            WHERE user_id = ? AND id NOT IN (
                SELECT id FROM (
                    SELECT id FROM crop_recommendation_history
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 10
                )
            )
        ''', (user_id, user_id))

        cursor.execute('''
            DELETE FROM crop_recommendations
            WHERE user_id = ? AND id NOT IN (
                SELECT id FROM (
                    SELECT id FROM crop_recommendations
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT 10
                )
            )
        ''', (user_id, user_id))

        conn.commit()

        # Fetch newly inserted record for instant history rendering
        cursor.execute("SELECT * FROM crop_recommendation_history WHERE id = ?", (record_id,))
        new_row = dict(cursor.fetchone())
        conn.close()

        return jsonify({
            'success': True,
            'primary_match': primary_match,
            'alternatives': alternatives,
            'input': validated_input,
            'metadata': prediction_result.get('metadata', {}),
            'history_record': new_row
        })

    except Exception as e:
        logger.exception(f"Unexpected error in predict_api: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to generate crop recommendation. Please check your inputs and try again.'
        }), 500


@crop_bp.route('/api/crop-recommendation/history', methods=['GET'])
@crop_bp.route('/crop/history', methods=['GET'])
def history_api():
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401

    user_id = session['user_id']
    crop_filter = request.args.get('crop', '').strip()
    suitability_filter = request.args.get('suitability', '').strip()
    season_filter = request.args.get('season', '').strip()
    date_filter = request.args.get('date', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM crop_recommendation_history WHERE user_id = ?"
    params = [user_id]

    if crop_filter and crop_filter.lower() != 'all':
        query += " AND LOWER(recommended_crop) LIKE ?"
        params.append(f"%{crop_filter.lower()}%")

    if suitability_filter and suitability_filter.lower() != 'all':
        query += " AND LOWER(suitability) = ?"
        params.append(suitability_filter.lower())

    if season_filter and season_filter.lower() != 'all':
        query += " AND LOWER(season) LIKE ?"
        params.append(f"%{season_filter.lower()}%")

    if date_filter:
        query += " AND created_at LIKE ?"
        params.append(f"{date_filter}%")

    query += " ORDER BY id DESC LIMIT 10"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    history = [dict(r) for r in rows]
    conn.close()

    return jsonify({
        'success': True,
        'history': history,
        'total_count': len(history)
    })


@crop_bp.route('/api/crop-planning/advisory', methods=['GET', 'POST'])
@crop_bp.route('/crop/advisory', methods=['GET', 'POST'])
@csrf.exempt
def crop_advisory_api():
    """
    Returns practical, crop-specific planning information.
    Date-aware and location-aware.
    """
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()
    else:
        data = request.args.to_dict()

    crop_name = data.get('crop') or data.get('crop_name') or 'Rice'
    custom_date = data.get('date')

    # Get user location if logged in
    user_location = data.get('location')
    if not user_location and 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT location FROM users WHERE id = ?", (session['user_id'],))
        user_row = cursor.fetchone()
        conn.close()
        if user_row and user_row['location']:
            user_location = user_row['location']

    plan_result = crop_service.get_crop_plan(crop_name, location=user_location, check_date=custom_date)
    return jsonify(plan_result)


@crop_bp.route('/api/crop-recommendation/explore', methods=['POST'])
@crop_bp.route('/crop/explore', methods=['POST'])
@csrf.exempt
@login_required
def explore_api():
    user_id = session['user_id']


    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    crop_name = data.get('crop', '')
    target_confidence = data.get('target', 80)
    current_inputs = data.get('current_inputs', {})

    if not crop_name:
        return jsonify({
            'success': False,
            'error': 'Crop name is required for exploration.'
        }), 400

    try:
        explore_result = crop_service.explore_target_conditions(crop_name, target_confidence, current_inputs)
        return jsonify(explore_result)
    except Exception as e:
        logger.exception(f"Error in explore_api: {e}")
        return jsonify({
            'success': False,
            'error': f"Failed to explore target conditions: {str(e)}"
        }), 500


