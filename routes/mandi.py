from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from models.database import get_db_connection
from services.mandi_service import MandiService
from routes.auth import login_required

mandi_bp = Blueprint('mandi', __name__, url_prefix='/mandi')
mandi_svc = MandiService()

@mandi_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    # Default state = 'Bihar', default crop = 'Bajra'
    state = request.args.get('state', '').strip() or 'Bihar'
    crop = request.args.get('crop', '').strip() or 'Bajra'
    selected_year = request.args.get('year', '2026').strip()
    try:
        selected_year = int(selected_year)
    except Exception:
        selected_year = 2026

    # Crop filter for the state-wise Live Market Rates table (defaults to selected crop or Bajra)
    table_crop = request.args.get('table_crop', '').strip() or crop or 'Bajra'

    filter_options = mandi_svc.get_filter_options()
    trend_res = mandi_svc.get_trend_data(state=state, crop=crop, selected_year=selected_year)
    stats = trend_res['stats'] if trend_res else None
    chart_data = trend_res['chart_data'] if trend_res else None
    yearly_data = trend_res['yearly_data'] if trend_res else None

    # State-wise Live Mandi Market Rates table: All states (scrollable view)
    live_records = mandi_svc.get_state_rates_for_crop(crop=table_crop, limit=None)

    return render_template(
        'mandi.html',
        user=user,
        records=live_records,
        stats=stats,
        chart_data=chart_data,
        yearly_data=yearly_data,
        filters=filter_options,
        selected_crop=crop,
        selected_state=state,
        selected_year=selected_year,
        table_crop=table_crop,
        has_selection=(trend_res is not None)
    )

@mandi_bp.route('/api/trend', methods=['GET'])
def api_trend():
    state = request.args.get('state', '').strip() or 'Bihar'
    crop = request.args.get('crop', '').strip() or 'Bajra'
    year = request.args.get('year', '2026').strip()
    try:
        year = int(year)
    except Exception:
        year = 2026

    trend_res = mandi_svc.get_trend_data(state=state, crop=crop, selected_year=year)
    if not trend_res:
        return jsonify({
            'success': False,
            'message': f'No market price records found for {crop} in {state}.'
        })

    return jsonify({
        'success': True,
        'state': state,
        'crop': crop,
        'selected_year': year,
        'chart_data': trend_res['chart_data'],
        'yearly_data': trend_res['yearly_data'],
        'stats': trend_res['stats']
    })

@mandi_bp.route('/api/table-rates', methods=['GET'])
@mandi_bp.route('/api/search', methods=['GET'])
def api_table_rates():
    crop = request.args.get('crop', 'Bajra').strip() or 'Bajra'
    records = mandi_svc.get_state_rates_for_crop(crop=crop, limit=None)
    return jsonify({
        'success': True,
        'crop': crop,
        'records': records
    })
