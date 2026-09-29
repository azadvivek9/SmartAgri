from flask import Blueprint, render_template, session, redirect, url_for
from models.database import get_db_connection
from services.weather_service import WeatherService
from services.mandi_service import MandiService
from services.soil_service import SoilService
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)
weather_svc = WeatherService()
mandi_svc = MandiService()
soil_svc = SoilService()

@dashboard_bp.route('/')
@login_required
def index():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch User
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    user_loc = user['location'] or "Meerut, Uttar Pradesh, India"

    # 1. Real Weather info from OpenWeather Service
    weather_data = weather_svc.get_weather_data(user_loc)
    current_weather = weather_data['current']

    # 2. Latest Soil Record
    cursor.execute("SELECT * FROM soil_records WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    soil_record = cursor.fetchone()
    if not soil_record:
        soil_summary = {
            'health_score': 'Good (84%)',
            'ph': 6.8,
            'npk_summary': 'N: 78 | P: 38 | K: 210',
            'moisture': '55%'
        }
    else:
        soil_summary = {
            'health_score': f"{soil_record['health_score']}",
            'ph': soil_record['ph'],
            'npk_summary': f"N: {soil_record['nitrogen']:.0f} | P: {soil_record['phosphorus']:.0f} | K: {soil_record['potassium']:.0f}",
            'moisture': f"{soil_record['moisture']:.0f}%" if soil_record['moisture'] else '55%'
        }

    # 3. Market Summary for User Main Crop or Wheat
    crop_name = 'Wheat'
    if user['main_crop']:
        crop_name = user['main_crop'].split('&')[0].strip()
    mandi_res = mandi_svc.search_prices(crop=crop_name)
    market_summary = {
        'crop': mandi_res['stats']['primary_crop'],
        'modal_price': f"₹{mandi_res['stats']['modal_price']:,.0f} / Qtl",
        'trend': mandi_res['stats']['price_change'],
        'is_positive': True
    }

    # 4. Crop Card Summary
    crop_summary = {
        'current_crop': user['main_crop'] or 'Wheat & Sugarcane',
        'growth_stage': 'Vegetative / Tillering Stage',
        'crop_health': 'Healthy & Vigorous',
        'health_badge': 'badge-success'
    }

    # 5. Today's 4 Advisories powered by live weather rules
    w_adv = weather_data.get('advisories', {})
    irrig_adv = w_adv.get('irrigation', {})
    rain_adv = w_adv.get('rain', {})
    temp_adv = w_adv.get('temperature', {})
    wind_adv = w_adv.get('wind', {})

    today_advisories = [
        {
            'type': 'irrigation',
            'title': 'Irrigation Advisory',
            'icon': irrig_adv.get('icon', 'fa-solid fa-droplet'),
            'color': '#0284c7',
            'bg': '#e0f2fe',
            'badge': irrig_adv.get('level', 'Normal'),
            'badge_cls': irrig_adv.get('badge_class', 'badge-info'),
            'message': irrig_adv.get('headline', 'Monitor soil moisture before scheduling irrigation.')
        },
        {
            'type': 'fertilizer',
            'title': 'Fertilizer Advisory',
            'icon': 'fa-solid fa-flask-vial',
            'color': '#16a34a',
            'bg': '#dcfce7',
            'badge': 'Suggested',
            'badge_cls': 'badge-success',
            'message': 'Balanced nitrogen top dressing recommended for active vegetative tiller development.'
        },
        {
            'type': 'weather',
            'title': 'Weather Alert',
            'icon': rain_adv.get('icon', 'fa-solid fa-cloud-bolt'),
            'color': '#d97706',
            'bg': '#fef3c7',
            'badge': rain_adv.get('level', 'Notice'),
            'badge_cls': rain_adv.get('badge_class', 'badge-warning'),
            'message': rain_adv.get('headline', 'Check regional precipitation forecast before scheduling pesticide spraying.')
        },
        {
            'type': 'crop_alert',
            'title': 'Crop Protection Alert',
            'icon': wind_adv.get('icon', 'fa-solid fa-wind'),
            'color': '#dc2626',
            'bg': '#fee2e2',
            'badge': wind_adv.get('level', 'Advisory'),
            'badge_cls': wind_adv.get('badge_class', 'badge-danger'),
            'message': wind_adv.get('headline', 'Maintain routine scouting on flag leaves for early pest prevention.')
        }
    ]

    # Fetch recent recommendations / activities
    cursor.execute("SELECT * FROM crop_recommendations WHERE user_id = ? ORDER BY id DESC LIMIT 3", (user_id,))
    recent_recs = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template(
        'dashboard.html',
        user=user,
        weather=current_weather,
        soil=soil_summary,
        market=market_summary,
        crop=crop_summary,
        advisories=today_advisories,
        weather_chart=weather_data['chart_data'],
        hourly_chart=weather_data.get('hourly_chart', {}),
        recent_recs=recent_recs,
        weather_success=weather_data.get('success', False),
        weather_error=weather_data.get('error', None),
        is_live=weather_data.get('is_live', False),
        last_updated=weather_data.get('last_updated', '')
    )
