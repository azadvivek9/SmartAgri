from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from services.weather_service import WeatherService, LOCATION_COORDINATES
from models.database import get_db_connection
from routes.auth import login_required

weather_bp = Blueprint('weather', __name__)
weather_svc = WeatherService()

@weather_bp.route('/weather', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    # Priority: lat/lon query > location query > user's profile location > Patna, Bihar, India
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    user_location = user['location'] if user and user['location'] else 'Patna, Bihar, India'
    selected_location = request.args.get('location', user_location)
    
    weather_data = weather_svc.get_weather_data(selected_location, lat=lat, lon=lon)

    locations_list = [
        'Patna, Bihar, India',
        'Meerut, Uttar Pradesh, India',
        'Delhi, India',
        'Lucknow, Uttar Pradesh, India',
        'Chandigarh, India',
        'Jaipur, Rajasthan, India',
        'Bhopal, Madhya Pradesh, India',
        'Pune, Maharashtra, India',
        'Ahmedabad, Gujarat, India',
        'Kolkata, West Bengal, India',
        'Hyderabad, Telangana, India',
        'Bengaluru, Karnataka, India',
        'Chennai, Tamil Nadu, India',
        'Mumbai, Maharashtra, India'
    ]

    return render_template(
        'weather.html',
        user=user,
        weather=weather_data['current'],
        forecast=weather_data['forecast'],
        visual_summary=weather_data.get('visual_summary', {}),
        advisories=weather_data['advisories'],
        chart_data=weather_data['chart_data'],
        seven_day_charts=weather_data.get('seven_day_charts', weather_data['chart_data']),
        selected_location=weather_data.get('location', selected_location),
        locations_list=locations_list,
        weather_success=weather_data.get('success', False),
        weather_error=weather_data.get('error', None),
        is_live=weather_data.get('is_live', False),
        last_updated=weather_data.get('last_updated', '')
    )

@weather_bp.route('/api/weather', methods=['GET'])
@weather_bp.route('/api/weather/forecast', methods=['GET'])
@weather_bp.route('/weather/api', methods=['GET'])
def api_weather():
    """
    Clean JSON API endpoint returning live weather & genuine 7-day forecast.
    Accepts ?lat=...&lon=... or ?location=...
    Never exposes API key.
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    location = request.args.get('location', 'Patna, Bihar, India')
    data = weather_svc.get_weather_data(location, lat=lat, lon=lon)
    
    return jsonify({
        'success': data.get('success', False),
        'is_live': data.get('is_live', False),
        'location': data.get('location', location),
        'last_updated': data.get('last_updated', ''),
        'local_date': data.get('local_date', ''),
        'local_date_display': data.get('local_date_display', ''),
        'timezone': data.get('timezone', ''),
        'utc_offset_seconds': data.get('utc_offset_seconds', 0),
        'error': data.get('error', None),
        'current': {
            'temperature': data['current']['temp'],
            'feels_like': data['current']['feels_like'],
            'temp_min': data['current']['temp_min'],
            'temp_max': data['current']['temp_max'],
            'humidity': data['current']['humidity'],
            'wind_speed': data['current']['wind_speed'],
            'wind_speed_kmh': data['current'].get('wind_speed_kmh'),
            'pressure': data['current']['pressure'],
            'visibility': data['current'].get('visibility'),
            'condition': data['current']['condition'],
            'description': data['current']['description'],
            'icon_code': data['current']['icon_code'],
            'icon_url': data['current']['icon_url'],
            'fa_icon': data['current']['fa_icon'],
            'rain_probability': data['current'].get('rain_probability'),
            'rain_prob_available': data['current'].get('rain_prob_available', False),
            'local_date': data['current'].get('local_date', ''),
            'local_date_display': data['current'].get('local_date_display', ''),
            'local_datetime': data['current'].get('local_datetime', ''),
            'timezone': data['current'].get('timezone', ''),
            'utc_offset_seconds': data['current'].get('utc_offset_seconds', 0)
        },
        'forecast': data['forecast'], # 7 normalized daily records
        'visual_summary': data.get('visual_summary', {}),
        'advisories': data['advisories'],
        'chart_data': data['chart_data'],
        'seven_day_charts': data.get('seven_day_charts', data['chart_data'])
    })
