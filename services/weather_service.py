import os
import requests
from datetime import datetime, timezone, timedelta
from config import Config

# Standard coordinate mappings for key agricultural districts in India
LOCATION_COORDINATES = {
    'patna': {'lat': 25.5941, 'lon': 85.1376, 'city': 'Patna', 'state': 'Bihar', 'country': 'India', 'name': 'Patna, Bihar, India'},
    'meerut': {'lat': 28.9845, 'lon': 77.7064, 'city': 'Meerut', 'state': 'Uttar Pradesh', 'country': 'India', 'name': 'Meerut, Uttar Pradesh, India'},
    'delhi': {'lat': 28.6139, 'lon': 77.2090, 'city': 'Delhi', 'state': 'Delhi', 'country': 'India', 'name': 'Delhi, India'},
    'lucknow': {'lat': 26.8467, 'lon': 80.9462, 'city': 'Lucknow', 'state': 'Uttar Pradesh', 'country': 'India', 'name': 'Lucknow, Uttar Pradesh, India'},
    'chandigarh': {'lat': 30.7333, 'lon': 76.7794, 'city': 'Chandigarh', 'state': 'Punjab/Haryana', 'country': 'India', 'name': 'Chandigarh, India'},
    'jaipur': {'lat': 26.9124, 'lon': 75.7873, 'city': 'Jaipur', 'state': 'Rajasthan', 'country': 'India', 'name': 'Jaipur, Rajasthan, India'},
    'bhopal': {'lat': 23.2599, 'lon': 77.4126, 'city': 'Bhopal', 'state': 'Madhya Pradesh', 'country': 'India', 'name': 'Bhopal, Madhya Pradesh, India'},
    'pune': {'lat': 18.5204, 'lon': 73.8567, 'city': 'Pune', 'state': 'Maharashtra', 'country': 'India', 'name': 'Pune, Maharashtra, India'},
    'ahmedabad': {'lat': 23.0225, 'lon': 72.5714, 'city': 'Ahmedabad', 'state': 'Gujarat', 'country': 'India', 'name': 'Ahmedabad, Gujarat, India'},
    'kolkata': {'lat': 22.5726, 'lon': 88.3639, 'city': 'Kolkata', 'state': 'West Bengal', 'country': 'India', 'name': 'Kolkata, West Bengal, India'},
    'hyderabad': {'lat': 17.3850, 'lon': 78.4867, 'city': 'Hyderabad', 'state': 'Telangana', 'country': 'India', 'name': 'Hyderabad, Telangana, India'},
    'bengaluru': {'lat': 12.9716, 'lon': 77.5946, 'city': 'Bengaluru', 'state': 'Karnataka', 'country': 'India', 'name': 'Bengaluru, Karnataka, India'},
    'chennai': {'lat': 13.0827, 'lon': 80.2707, 'city': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India', 'name': 'Chennai, Tamil Nadu, India'},
    'mumbai': {'lat': 19.0760, 'lon': 72.8777, 'city': 'Mumbai', 'state': 'Maharashtra', 'country': 'India', 'name': 'Mumbai, Maharashtra, India'}
}

# WMO Weather Code to Description, Icon code & Font Awesome mapping
WMO_WEATHER_MAP = {
    0: {'condition': 'Clear Sky', 'icon': '01d', 'fa': 'fa-solid fa-sun', 'is_clear': True},
    1: {'condition': 'Mainly Clear', 'icon': '02d', 'fa': 'fa-solid fa-cloud-sun', 'is_clear': True},
    2: {'condition': 'Partly Cloudy', 'icon': '02d', 'fa': 'fa-solid fa-cloud-sun', 'is_clear': True},
    3: {'condition': 'Overcast', 'icon': '04d', 'fa': 'fa-solid fa-cloud', 'is_clear': False},
    45: {'condition': 'Foggy', 'icon': '50d', 'fa': 'fa-solid fa-smog', 'is_clear': False},
    48: {'condition': 'Depositing Rime Fog', 'icon': '50d', 'fa': 'fa-solid fa-smog', 'is_clear': False},
    51: {'condition': 'Light Drizzle', 'icon': '09d', 'fa': 'fa-solid fa-cloud-rain', 'is_clear': False},
    53: {'condition': 'Moderate Drizzle', 'icon': '09d', 'fa': 'fa-solid fa-cloud-rain', 'is_clear': False},
    55: {'condition': 'Dense Drizzle', 'icon': '09d', 'fa': 'fa-solid fa-cloud-rain', 'is_clear': False},
    56: {'condition': 'Light Freezing Drizzle', 'icon': '09d', 'fa': 'fa-solid fa-cloud-rain', 'is_clear': False},
    57: {'condition': 'Dense Freezing Drizzle', 'icon': '09d', 'fa': 'fa-solid fa-cloud-rain', 'is_clear': False},
    61: {'condition': 'Slight Rain', 'icon': '10d', 'fa': 'fa-solid fa-cloud-sun-rain', 'is_clear': False},
    63: {'condition': 'Moderate Rain', 'icon': '10d', 'fa': 'fa-solid fa-cloud-showers-heavy', 'is_clear': False},
    65: {'condition': 'Heavy Rain', 'icon': '10d', 'fa': 'fa-solid fa-cloud-showers-heavy', 'is_clear': False},
    66: {'condition': 'Freezing Rain', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    67: {'condition': 'Heavy Freezing Rain', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    71: {'condition': 'Slight Snow Fall', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    73: {'condition': 'Moderate Snow Fall', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    75: {'condition': 'Heavy Snow Fall', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    77: {'condition': 'Snow Grains', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    80: {'condition': 'Slight Rain Showers', 'icon': '09d', 'fa': 'fa-solid fa-cloud-showers-heavy', 'is_clear': False},
    81: {'condition': 'Moderate Rain Showers', 'icon': '09d', 'fa': 'fa-solid fa-cloud-showers-heavy', 'is_clear': False},
    82: {'condition': 'Violent Rain Showers', 'icon': '09d', 'fa': 'fa-solid fa-cloud-showers-heavy', 'is_clear': False},
    85: {'condition': 'Slight Snow Showers', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    86: {'condition': 'Heavy Snow Showers', 'icon': '13d', 'fa': 'fa-solid fa-snowflake', 'is_clear': False},
    95: {'condition': 'Thunderstorm', 'icon': '11d', 'fa': 'fa-solid fa-cloud-bolt', 'is_clear': False},
    96: {'condition': 'Thunderstorm with Slight Hail', 'icon': '11d', 'fa': 'fa-solid fa-cloud-bolt', 'is_clear': False},
    99: {'condition': 'Thunderstorm with Heavy Hail', 'icon': '11d', 'fa': 'fa-solid fa-cloud-bolt', 'is_clear': False}
}

class WeatherService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY', '').strip() or Config.OPENWEATHER_API_KEY

    def _resolve_coordinates(self, location_str=None, lat=None, lon=None):
        """Resolve latitude and longitude for a given location or coordinates."""
        if lat is not None and lon is not None:
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                # Find matching location name if any
                loc_name = location_str or "Selected Location"
                for key, data in LOCATION_COORDINATES.items():
                    if abs(data['lat'] - lat_f) < 0.2 and abs(data['lon'] - lon_f) < 0.2:
                        loc_name = data['name']
                        break
                return lat_f, lon_f, loc_name
            except Exception:
                pass

        if not location_str:
            return LOCATION_COORDINATES['patna']['lat'], LOCATION_COORDINATES['patna']['lon'], LOCATION_COORDINATES['patna']['name']
        
        loc_lower = location_str.lower()
        for key, data in LOCATION_COORDINATES.items():
            if key in loc_lower or data['city'].lower() in loc_lower:
                return data['lat'], data['lon'], data['name']
        
        # Default fallback to Patna, Bihar, India
        return LOCATION_COORDINATES['patna']['lat'], LOCATION_COORDINATES['patna']['lon'], location_str

    def get_weather_data(self, location="Patna, Bihar, India", lat=None, lon=None):
        """
        Fetch real-time weather & genuine 7-day agro-meteorological forecast.
        Returns:
          - Current weather metrics with selected location's local date
          - Exactly 7 daily calendar records (Today in local timezone + next 6 calendar days)
          - Normalized chart data for green agricultural charts
          - Visual 7-day Summary metrics (Avg Temp, Range, Avg Humidity, Rain Days, Clear Days)
          - Rule-based agriculture advisories
        """
        resolved_lat, resolved_lon, formatted_location_name = self._resolve_coordinates(location, lat, lon)

        # Fetch live precision agricultural data from Open-Meteo with 14-day window to guarantee full 7 days from local today
        om_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={resolved_lat}&longitude={resolved_lon}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m&"
            f"daily=weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant,relative_humidity_2m_mean&"
            f"forecast_days=14&"
            f"timezone=auto"
        )
        
        last_error = None
        for attempt in range(2):
            try:
                om_resp = requests.get(om_url, timeout=10)
                if om_resp.status_code == 200:
                    om_data = om_resp.json()
                    return self._parse_7day_weather_response(om_data, formatted_location_name)
                else:
                    return self._generate_error_response(
                        "Weather forecast service is temporarily unavailable. Please try again.",
                        formatted_location_name,
                        status_code=om_resp.status_code
                    )
            except requests.exceptions.Timeout as e:
                last_error = "Weather service request timed out. Please check your network connection."
            except requests.exceptions.RequestException as e:
                last_error = "Network error connecting to weather forecast provider. Please try again."
            except Exception as e:
                return self._generate_error_response(f"An unexpected error occurred while processing weather data: {str(e)}", formatted_location_name)

        return self._generate_error_response(last_error or "Weather service request failed.", formatted_location_name)

    def _parse_7day_weather_response(self, data, location_name):
        # 1. Determine local datetime and current local date using location's timezone offset
        utc_offset_seconds = data.get('utc_offset_seconds', 19800)
        if utc_offset_seconds is None:
            utc_offset_seconds = 19800 # Default India offset +05:30
        
        timezone_name = data.get('timezone', 'Asia/Kolkata')
        now_utc = datetime.now(timezone.utc)
        local_now = now_utc + timedelta(seconds=utc_offset_seconds)
        today_local = local_now.date() # Current calendar date in selected location
        
        last_updated_time = local_now.strftime('%I:%M %p')
        local_date_str = today_local.strftime('%Y-%m-%d')
        local_date_display = local_now.strftime('%d %B %Y')

        # 2. Current Weather parsing
        curr = data.get('current', {})
        curr_temp = round(curr.get('temperature_2m', 0.0), 1)
        curr_feels = round(curr.get('apparent_temperature', curr_temp), 1)
        curr_humidity = round(curr.get('relative_humidity_2m', 0))
        curr_pressure = round(curr.get('surface_pressure', 1013))
        curr_wind_kmh = round(curr.get('wind_speed_10m', 0.0), 1)
        curr_wind_ms = round(curr_wind_kmh / 3.6, 1)
        curr_wind_dir = curr.get('wind_direction_10m', 0)
        curr_precip = curr.get('precipitation', 0.0)
        curr_wcode = curr.get('weather_code', 0)

        curr_meta = WMO_WEATHER_MAP.get(curr_wcode, {'condition': 'Clear Sky', 'icon': '01d', 'fa': 'fa-solid fa-sun', 'is_clear': True})
        curr_cond = curr_meta['condition']
        curr_icon = curr_meta['icon']
        curr_fa = curr_meta['fa']

        # 3. Daily Forecast Parsing: Align EXACTLY 7 days starting from today_local
        daily = data.get('daily', {})
        daily_times = daily.get('time', [])
        t_max_list = daily.get('temperature_2m_max', [])
        t_min_list = daily.get('temperature_2m_min', [])
        app_max_list = daily.get('apparent_temperature_max', [])
        app_min_list = daily.get('apparent_temperature_min', [])
        pop_list = daily.get('precipitation_probability_max', [])
        precip_sum_list = daily.get('precipitation_sum', [])
        wind_max_list = daily.get('wind_speed_10m_max', []) # km/h
        wind_dir_list = daily.get('wind_direction_10m_dominant', [])
        hum_mean_list = daily.get('relative_humidity_2m_mean', [])
        wcode_list = daily.get('weather_code', [])

        # Construct exact 7 target calendar days: Today + next 6 days
        target_dates = [today_local + timedelta(days=i) for i in range(7)]

        normalized_forecast = []
        chart_labels = []
        chart_temps = []
        chart_feels = []
        chart_pops = []
        chart_winds = []
        chart_humidities = []
        chart_precips = []
        chart_tmax = []
        chart_tmin = []

        rain_days_count = 0
        clear_days_count = 0

        for i, target_dt in enumerate(target_dates):
            date_str = target_dt.strftime('%Y-%m-%d')
            display_date = target_dt.strftime('%d %b') # e.g. "28 Sep", "01 Oct"
            
            if i == 0:
                day_name = 'Today'
            elif i == 1:
                day_name = 'Tomorrow'
            else:
                day_name = target_dt.strftime('%a, %d %b')

            # Find corresponding index in API response daily_times
            if date_str in daily_times:
                idx = daily_times.index(date_str)
                t_max = round(t_max_list[idx], 1) if idx < len(t_max_list) and t_max_list[idx] is not None else curr_temp
                t_min = round(t_min_list[idx], 1) if idx < len(t_min_list) and t_min_list[idx] is not None else curr_temp
                app_max = round(app_max_list[idx], 1) if idx < len(app_max_list) and app_max_list[idx] is not None else t_max
                app_min = round(app_min_list[idx], 1) if idx < len(app_min_list) and app_min_list[idx] is not None else t_min
                hum = round(hum_mean_list[idx]) if idx < len(hum_mean_list) and hum_mean_list[idx] is not None else curr_humidity
                w_kmh = round(wind_max_list[idx], 1) if idx < len(wind_max_list) and wind_max_list[idx] is not None else curr_wind_kmh
                w_dir = round(wind_dir_list[idx]) if idx < len(wind_dir_list) and wind_dir_list[idx] is not None else curr_wind_dir
                pop = round(pop_list[idx]) if idx < len(pop_list) and pop_list[idx] is not None else 0
                precip = round(precip_sum_list[idx], 1) if idx < len(precip_sum_list) and precip_sum_list[idx] is not None else 0.0
                wcode = wcode_list[idx] if idx < len(wcode_list) and wcode_list[idx] is not None else 0
            else:
                # Safe fallback if API returned fewer days
                t_max = curr_temp + 2.0
                t_min = curr_temp - 3.0
                app_max = t_max
                app_min = t_min
                hum = curr_humidity
                w_kmh = curr_wind_kmh
                w_dir = curr_wind_dir
                pop = 10
                precip = 0.0
                wcode = 0

            avg_temp = round((t_max + t_min) / 2.0, 1)
            avg_feels = round((app_max + app_min) / 2.0, 1)
            wmeta = WMO_WEATHER_MAP.get(wcode, {'condition': 'Clear', 'icon': '01d', 'fa': 'fa-solid fa-sun', 'is_clear': True})

            if pop >= 30 or precip >= 0.5:
                rain_days_count += 1
            elif wmeta.get('is_clear', False):
                clear_days_count += 1

            day_record = {
                'date': date_str,
                'local_date': date_str,
                'display_date': display_date,
                'day': day_name,
                'temperature': avg_temp,
                'temp_min': round(t_min),
                'temp_max': round(t_max),
                'feels_like': avg_feels,
                'humidity': hum,
                'wind_speed': w_kmh, # km/h
                'wind_direction': w_dir,
                'rain_probability': pop,
                'precipitation': precip,
                'condition': wmeta['condition'],
                'icon_code': wmeta['icon'],
                'icon_url': f"https://openweathermap.org/img/wn/{wmeta['icon']}@2x.png",
                'fa_icon': wmeta['fa']
            }

            normalized_forecast.append(day_record)

            chart_labels.append(display_date)
            chart_temps.append(avg_temp)
            chart_feels.append(avg_feels)
            chart_pops.append(pop)
            chart_winds.append(w_kmh)
            chart_humidities.append(hum)
            chart_precips.append(precip)
            chart_tmax.append(round(t_max))
            chart_tmin.append(round(t_min))

        # First day rain prob for current card
        curr_rain_prob = chart_pops[0] if chart_pops else 0

        # Dynamic Date Range String (e.g. "28 Sep → 04 Oct 2026")
        date_range_str = f"{target_dates[0].strftime('%d %b')} → {target_dates[-1].strftime('%d %b %Y')}"

        # 7-Day Visual Summary Calculation
        overall_avg_temp = round(sum(chart_temps) / len(chart_temps)) if chart_temps else round(curr_temp)
        overall_max_temp = max(chart_tmax) if chart_tmax else round(curr_temp)
        overall_min_temp = min(chart_tmin) if chart_tmin else round(curr_temp)
        overall_avg_hum = round(sum(chart_humidities) / len(chart_humidities)) if chart_humidities else curr_humidity
        overall_min_hum = min(chart_humidities) if chart_humidities else curr_humidity
        overall_max_hum = max(chart_humidities) if chart_humidities else curr_humidity

        if clear_days_count + rain_days_count < len(normalized_forecast):
            clear_days_count = max(0, len(normalized_forecast) - rain_days_count)

        visual_summary = {
            'date_range': date_range_str,
            'avg_temp': overall_avg_temp,
            'max_temp': overall_max_temp,
            'min_temp': overall_min_temp,
            'avg_humidity': overall_avg_hum,
            'min_humidity': overall_min_hum,
            'max_humidity': overall_max_hum,
            'rain_days': rain_days_count,
            'clear_days': clear_days_count,
            'total_days': len(normalized_forecast)
        }

        current_dict = {
            'location': location_name,
            'temp': curr_temp,
            'feels_like': curr_feels,
            'temp_min': chart_tmin[0] if chart_tmin else curr_temp,
            'temp_max': chart_tmax[0] if chart_tmax else curr_temp,
            'condition': curr_cond,
            'description': curr_cond,
            'icon_code': curr_icon,
            'icon_url': f"https://openweathermap.org/img/wn/{curr_icon}@2x.png",
            'fa_icon': curr_fa,
            'humidity': curr_humidity,
            'wind_speed': curr_wind_ms, # m/s
            'wind_speed_kmh': curr_wind_kmh, # km/h
            'pressure': curr_pressure,
            'visibility': 10.0,
            'rain_probability': curr_rain_prob,
            'rain_prob_available': True,
            'last_updated': last_updated_time,
            'local_date': local_date_str,
            'local_date_display': local_date_display,
            'local_datetime': local_now.isoformat(),
            'timezone': timezone_name,
            'utc_offset_seconds': utc_offset_seconds,
            'is_live': True
        }

        # Rule-based Agriculture Advisories
        advisories = self._generate_agriculture_advisories(current_dict, normalized_forecast)

        # 7-Day Chart Datasets (Normalized for all charts)
        seven_day_charts = {
            'labels': chart_labels,
            'temperatures': chart_temps,
            'feels_like': chart_feels,
            'temp_max': chart_tmax,
            'temp_min': chart_tmin,
            'rain_probabilities': chart_pops,
            'wind_speeds': chart_winds,
            'humidities': chart_humidities,
            'precipitations': chart_precips
        }

        return {
            'success': True,
            'is_live': True,
            'location': location_name,
            'current': current_dict,
            'forecast': normalized_forecast, # Exactly 7 daily records
            'visual_summary': visual_summary, # Horizontal summary stats
            'advisories': advisories,
            'chart_data': seven_day_charts,
            'seven_day_charts': seven_day_charts,
            'last_updated': last_updated_time,
            'local_date': local_date_str,
            'local_date_display': local_date_display,
            'timezone': timezone_name,
            'utc_offset_seconds': utc_offset_seconds
        }

    def _generate_agriculture_advisories(self, current, forecast_cards):
        """Generate simple, rule-based agronomic advisories from real 7-day weather data."""
        temp = current['temp']
        rain_prob = current['rain_probability'] if current.get('rain_probability') is not None else 0
        wind = current['wind_speed'] # m/s
        
        upcoming_max_rain = rain_prob
        if forecast_cards:
            upcoming_max_rain = max([f['rain_probability'] for f in forecast_cards[:2] if f.get('rain_probability') is not None] or [rain_prob])

        # 1. 💧 Irrigation Advisory
        if upcoming_max_rain >= 60:
            irrig_title = "Irrigation Advisory"
            irrig_level = "Hold Irrigation"
            irrig_badge = "badge-info"
            irrig_icon = "fa-solid fa-droplet-slash"
            irrig_headline = f"Rain is expected in the next 24 hours ({upcoming_max_rain}% chance). Irrigation is not required today."
            irrig_points = [
                "Natural rainfall will replenish root zone soil moisture adequately.",
                "Turn off electric and diesel tube-well pumps to conserve groundwater and electricity.",
                "Ensure field boundary bunds and drainage outlets are unobstructed."
            ]
        elif upcoming_max_rain < 25 and temp >= 32.0:
            irrig_title = "Irrigation Advisory"
            irrig_level = "Inspection Advised"
            irrig_badge = "badge-warning"
            irrig_icon = "fa-solid fa-droplet"
            irrig_headline = f"Low rainfall probability ({upcoming_max_rain}%) and high temperature ({temp}°C). Check soil moisture before irrigation."
            irrig_points = [
                "Evapotranspiration rates are elevated under current temperatures.",
                "Inspect top 5 cm soil moisture in root zones.",
                "Prefer evening or early morning drip/furrow irrigation to minimize evaporation."
            ]
        else:
            irrig_title = "Irrigation Advisory"
            irrig_level = "Normal Schedule"
            irrig_badge = "badge-success"
            irrig_icon = "fa-solid fa-droplet"
            irrig_headline = f"Moderate conditions ({temp}°C, {upcoming_max_rain}% rain probability). Maintain standard irrigation cycle."
            irrig_points = [
                "Soil moisture loss is within standard seasonal benchmarks.",
                "Continue standard growth-stage irrigation for standing crops.",
                "Monitor weather forecast before scheduling extensive flood irrigation."
            ]

        # 2. 🌧️ Rain Advisory
        if upcoming_max_rain >= 50:
            rain_title = "Rainfall Advisory"
            rain_level = "Rain Expected"
            rain_badge = "badge-warning"
            rain_icon = "fa-solid fa-cloud-showers-heavy"
            rain_headline = f"High rainfall probability ({upcoming_max_rain}%) expected in your district."
            rain_points = [
                "Rainfall is expected. Avoid unnecessary irrigation and foliar spraying.",
                "Delay chemical pesticide and herbicide broadcasting as rain will wash away active ingredients.",
                "Keep harvested produce under waterproof tarpaulin shelters."
            ]
        else:
            rain_title = "Rainfall Advisory"
            rain_level = "Clear / Low Rain"
            rain_badge = "badge-success"
            rain_icon = "fa-solid fa-cloud-sun"
            rain_headline = f"Low chance of precipitation ({upcoming_max_rain}%). Favorable for farm operations."
            rain_points = [
                "Ideal window for intercultural operations, weeding, and fertilizer top-dressing.",
                "Safe conditions for tractor tilling and pesticide/fungicide spraying.",
                "Good solar radiation available for crop photosynthesis."
            ]

        # 3. 🌡️ Temperature Advisory
        if temp >= 35.0:
            temp_title = "Temperature Advisory"
            temp_level = "High Heat"
            temp_badge = "badge-danger"
            temp_icon = "fa-solid fa-temperature-arrow-up"
            temp_headline = f"High temperature detected ({temp}°C). Monitor crop water requirements."
            temp_points = [
                "High heat increases transpiration stress on young seedlings and fruit flowers.",
                "Apply organic straw mulch around crop beds to retain soil moisture.",
                "Provide light frequent sprinkler irrigation during early mornings."
            ]
        elif temp <= 14.0:
            temp_title = "Temperature Advisory"
            temp_level = "Cool Weather"
            temp_badge = "badge-info"
            temp_icon = "fa-solid fa-temperature-arrow-down"
            temp_headline = f"Cool temperature detected ({temp}°C). Highly favorable for Rabi crops."
            temp_points = [
                "Temperature regime is supportive of tillering in Wheat and Mustard.",
                "Inspect lower leaves for cold-weather fungal spots (Rust / Downy Mildew).",
                "Ensure adequate light penetration through canopy."
            ]
        else:
            temp_title = "Temperature Advisory"
            temp_level = "Optimal Range"
            temp_badge = "badge-success"
            temp_icon = "fa-solid fa-temperature-half"
            temp_headline = f"Current temperature ({temp}°C) is in the optimal vegetative growth zone."
            temp_points = [
                "Daytime temperatures support active enzyme synthesis and chlorophyll activity.",
                "No severe heatwave or frost chilling risk observed in near-term forecast.",
                "Continue standard agronomic management."
            ]

        # 4. 🌬️ Wind Advisory
        if wind >= 6.5:
            wind_title = "Wind Advisory"
            wind_level = "Strong Breeze"
            wind_badge = "badge-warning"
            wind_icon = "fa-solid fa-wind"
            wind_headline = f"Strong winds expected ({wind} m/s). Take precautions for vulnerable crops."
            wind_points = [
                "Postpone tall-canopy chemical spraying to prevent chemical spray drift.",
                "Ensure support staking for horticultural and vegetable crops (Tomato, Banana).",
                "Check polyhouse sheeting and nursery netting anchoring."
            ]
        else:
            wind_title = "Wind Advisory"
            wind_level = "Calm / Light"
            wind_badge = "badge-success"
            wind_icon = "fa-solid fa-wind"
            wind_headline = f"Gentle wind speed ({wind} m/s). Safe for field operations."
            wind_points = [
                "Low wind drift allows accurate foliar spraying of micronutrients.",
                "Safe for mechanical weeding and intercultural farm activities.",
                "Good ambient air exchange across crop canopy."
            ]

        return {
            'irrigation': {
                'title': irrig_title, 'level': irrig_level, 'badge_class': irrig_badge,
                'icon': irrig_icon, 'headline': irrig_headline, 'points': irrig_points
            },
            'rain': {
                'title': rain_title, 'level': rain_level, 'badge_class': rain_badge,
                'icon': rain_icon, 'headline': rain_headline, 'points': rain_points
            },
            'temperature': {
                'title': temp_title, 'level': temp_level, 'badge_class': temp_badge,
                'icon': temp_icon, 'headline': temp_headline, 'points': temp_points
            },
            'wind': {
                'title': wind_title, 'level': wind_level, 'badge_class': wind_badge,
                'icon': wind_icon, 'headline': wind_headline, 'points': wind_points
            }
        }

    def _generate_error_response(self, error_message, location_name, status_code=500):
        now_utc = datetime.now(timezone.utc)
        local_now = now_utc + timedelta(seconds=19800)
        date_range_str = f"{local_now.strftime('%d %b')} → 7 Days"
        last_updated_time = local_now.strftime('%I:%M %p')
        local_date_str = local_now.strftime('%Y-%m-%d')
        local_date_display = local_now.strftime('%d %B %Y')

        return {
            'success': False,
            'is_live': False,
            'error': error_message,
            'status_code': status_code,
            'location': location_name,
            'last_updated': last_updated_time,
            'local_date': local_date_str,
            'local_date_display': local_date_display,
            'timezone': 'Asia/Kolkata',
            'utc_offset_seconds': 19800,
            'current': {
                'location': location_name,
                'temp': '--',
                'feels_like': '--',
                'temp_min': '--',
                'temp_max': '--',
                'condition': 'Data Unavailable',
                'description': error_message,
                'icon_code': '01d',
                'icon_url': 'https://openweathermap.org/img/wn/01d@2x.png',
                'fa_icon': 'fa-solid fa-triangle-exclamation',
                'humidity': '--',
                'wind_speed': '--',
                'wind_speed_kmh': '--',
                'pressure': '--',
                'visibility': '--',
                'rain_probability': None,
                'rain_prob_available': False,
                'last_updated': last_updated_time,
                'local_date': local_date_str,
                'local_date_display': local_date_display,
                'local_datetime': local_now.isoformat(),
                'timezone': 'Asia/Kolkata',
                'utc_offset_seconds': 19800,
                'is_live': False
            },
            'forecast': [],
            'visual_summary': {
                'date_range': date_range_str,
                'avg_temp': '--',
                'max_temp': '--',
                'min_temp': '--',
                'avg_humidity': '--',
                'min_humidity': '--',
                'max_humidity': '--',
                'rain_days': '--',
                'clear_days': '--',
                'total_days': 7
            },
            'advisories': {
                'irrigation': {
                    'title': 'Irrigation Advisory', 'level': 'Pending Weather Data', 'badge_class': 'badge-neutral',
                    'icon': 'fa-solid fa-droplet', 'headline': 'Live weather connection is currently unavailable.',
                    'points': ['Please verify internet connection or refresh weather data.']
                },
                'rain': {
                    'title': 'Rainfall Advisory', 'level': 'Pending Weather Data', 'badge_class': 'badge-neutral',
                    'icon': 'fa-solid fa-cloud-rain', 'headline': 'Precipitation forecast is temporarily unavailable.',
                    'points': ['Check local agro-met station reports.']
                },
                'temperature': {
                    'title': 'Temperature Advisory', 'level': 'Pending Weather Data', 'badge_class': 'badge-neutral',
                    'icon': 'fa-solid fa-temperature-half', 'headline': 'Temperature metrics unavailable.',
                    'points': ['Refresh weather module once network or API key is active.']
                },
                'wind': {
                    'title': 'Wind Advisory', 'level': 'Pending Weather Data', 'badge_class': 'badge-neutral',
                    'icon': 'fa-solid fa-wind', 'headline': 'Wind telemetry unavailable.',
                    'points': ['Inspect wind vanes or farm boundary trees visually.']
                }
            },
            'chart_data': {
                'labels': [],
                'temperatures': [],
                'feels_like': [],
                'temp_max': [],
                'temp_min': [],
                'rain_probabilities': [],
                'wind_speeds': [],
                'humidities': [],
                'precipitations': []
            },
            'seven_day_charts': {
                'labels': [],
                'temperatures': [],
                'feels_like': [],
                'temp_max': [],
                'temp_min': [],
                'rain_probabilities': [],
                'wind_speeds': [],
                'humidities': [],
                'precipitations': []
            }
        }
