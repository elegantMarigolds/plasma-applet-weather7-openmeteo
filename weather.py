#!/usr/bin/env python3

import json
import urllib.request
import urllib.parse
import sys
import time
from datetime import datetime

# ===== CONFIGURE HERE =====
LATITUDE = 37.541290
LONGITUDE = -77.434769
USE_FAHRENHEIT = True  # Set to False for Celsius
# ==========================

def fetch_openmeteo(lat, lon, use_fahrenheit=True):
    """Fetches and returns parsed JSON from Open-Meteo API."""
    params = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': 'true',
        'hourly': 'temperature_2m,relativehumidity_2m,weathercode,windspeed_10m,winddirection_10m,precipitation_probability,cloudcover',
        'daily': 'sunrise,sunset,temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset',
        'timezone': 'auto',
        'forecast_days': 3,
        'temperature_unit': 'fahrenheit' if use_fahrenheit else 'celsius',
        'windspeed_unit': 'mph' if use_fahrenheit else 'kmh',
        'precipitation_unit': 'inch' if use_fahrenheit else 'mm'
    }

    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except Exception as e:
        error_output = {
            "status": "failed",
            "error": str(e)
        }
        print(json.dumps(error_output))
        sys.exit(1)

def wmo_to_skycon(wmo_code, is_day=True):
    """Maps Open-Meteo WMO codes to Caiyun skycon values with day/night variants."""
    # Day skycons
    day_map = {
        0: 'CLEAR_DAY', 1: 'CLEAR_DAY', 2: 'PARTLY_CLOUDY_DAY',
        3: 'CLOUDY', 45: 'FOG', 48: 'FOG',
        51: 'LIGHT_RAIN', 53: 'MODERATE_RAIN', 55: 'HEAVY_RAIN',
        61: 'LIGHT_RAIN', 63: 'MODERATE_RAIN', 65: 'HEAVY_RAIN',
        71: 'LIGHT_SNOW', 73: 'MODERATE_SNOW', 75: 'HEAVY_SNOW',
        80: 'LIGHT_RAIN', 81: 'MODERATE_RAIN', 82: 'HEAVY_RAIN',
        95: 'THUNDERSTORM', 96: 'THUNDERSTORM', 99: 'THUNDERSTORM'
    }

    # Night variants for clear and partly cloudy
    night_map = {
        0: 'CLEAR_NIGHT', 1: 'CLEAR_NIGHT', 2: 'PARTLY_CLOUDY_NIGHT'
    }

    if not is_day and wmo_code in night_map:
        return night_map[wmo_code]
    return day_map.get(wmo_code, 'CLOUDY')

def is_daytime(sunrise_iso, sunset_iso, current_iso):
    """Determines if current time is between sunrise and sunset."""
    def parse_time(t):
        return datetime.fromisoformat(t.replace('Z', '+00:00'))

    current = parse_time(current_iso)
    sunrise = parse_time(sunrise_iso)
    sunset = parse_time(sunset_iso)

    return sunrise <= current <= sunset

def transform_to_caiyun(om_data, use_fahrenheit=True):
    """Transforms Open-Meteo JSON to Caiyun v2.6 format."""
    current = om_data.get('current_weather', {})
    hourly = om_data.get('hourly', {})
    daily = om_data.get('daily', {})

    # Determine if it's daytime
    current_time = current.get('time', '')
    sunrise = daily.get('sunrise', [])
    sunset = daily.get('sunset', [])

    is_day = True  # Default
    if sunrise and sunset and current_time:
        # Find today's sunrise/sunset
        today_index = 0
        for i in range(len(sunrise)):
            if sunrise[i].startswith(current_time[:10]):  # Same date
                today_index = i
                break
        if today_index < len(sunrise):
            is_day = is_daytime(sunrise[today_index], sunset[today_index], current_time)

    # Get current weather conditions
    wmo_code = current.get('weathercode', 0)
    skycon = wmo_to_skycon(wmo_code, is_day)

    # Get humidity from hourly data (closest to current time)
    humidity = 50.0
    if 'relativehumidity_2m' in hourly and hourly['relativehumidity_2m']:
        # Find the index matching current time
        current_hour = current_time[:13] + ":00"  # Round to hour
        if current_hour in hourly.get('time', []):
            idx = hourly['time'].index(current_hour)
            humidity = hourly['relativehumidity_2m'][idx]
        else:
            humidity = hourly['relativehumidity_2m'][0]

    # Get current hour's precipitation probability
    precipitation_chance = 0.0
    if 'precipitation_probability' in hourly and hourly['precipitation_probability']:
        # Find the index matching current time
        current_hour = current_time[:13] + ":00"
        if current_hour in hourly.get('time', []):
            idx = hourly['time'].index(current_hour)
            precipitation_chance = hourly['precipitation_probability'][idx]
        else:
            precipitation_chance = hourly['precipitation_probability'][0]

    # Get cloud coverage
    cloudrate = 0.0
    if 'cloudcover' in hourly and hourly['cloudcover']:
        idx = 0
        if current_hour in hourly.get('time', []):
            idx = hourly['time'].index(current_hour)
        cloudrate = hourly['cloudcover'][idx] / 100.0  # Convert percentage to 0-1

    # Build hourly forecast (next 24 hours)
    # Build hourly forecast (next 24 hours) - with proper day/night
    hourly_forecast = []
    if 'time' in hourly and 'temperature_2m' in hourly:
        for i in range(min(24, len(hourly['time']))):
            hour_time = hourly['time'][i]
            hour_temp = hourly['temperature_2m'][i]

            # Find corresponding daily low temp
            low_temp = hour_temp - 2  # Default fallback
            if 'daily' in om_data and 'temperature_2m_min' in om_data['daily']:
                hour_date = hour_time[:10]
                for d in range(len(om_data['daily'].get('time', []))):
                    if hour_date == om_data['daily']['time'][d]:
                        low_temp = om_data['daily']['temperature_2m_min'][d]
                        break

            hourly_forecast.append({
                "datetime": hour_time,
                "value": hour_temp,
                "low": low_temp
            })
    # Build precipitation probability array
    hourly_precip_probability = []
    if 'precipitation_probability' in hourly and hourly['precipitation_probability']:
        for i in range(min(24, len(hourly['time']))):
            hourly_precip_probability.append(hourly['precipitation_probability'][i])
    else:
        hourly_precip_probability = [0] * 24  # Default to 0% if no data
    # Build skycon forecast array with proper day/night for each hour
    hourly_skycon = []
    if 'time' in hourly and 'weathercode' in hourly:
        # Get sunrise/sunset times from daily data
        daily_times = om_data.get('daily', {}).get('time', [])
        daily_sunrises = om_data.get('daily', {}).get('sunrise', [])
        daily_sunsets = om_data.get('daily', {}).get('sunset', [])

        for i in range(min(24, len(hourly['time']))):
            hour_time = hourly['time'][i]
            hour_wmo = hourly['weathercode'][i] if i < len(hourly['weathercode']) else 0

            # Find which day this hour belongs to
            hour_date = hour_time[:10]  # Get just the date part (YYYY-MM-DD)
            day_index = -1
            for d in range(len(daily_times)):
                if daily_times[d].startswith(hour_date):
                    day_index = d
                    break

            # Determine if this specific hour is daytime
            hour_is_day = True  # Default
            if day_index != -1 and daily_sunrises and daily_sunsets:
                sunrise = daily_sunrises[day_index]
                sunset = daily_sunsets[day_index]
                hour_is_day = is_daytime(sunrise, sunset, hour_time)

            hourly_skycon.append({
                "value": wmo_to_skycon(hour_wmo, hour_is_day)
            })

    # Build daily forecast (next 3 days)
    daily_forecast = []
    if 'time' in daily and 'temperature_2m_max' in daily:
        for i in range(min(3, len(daily['time']))):
            day_wmo = daily['weathercode'][i] if i < len(daily.get('weathercode', [])) else 0
            daily_forecast.append({
                "date": daily['time'][i],
                "max": daily['temperature_2m_max'][i],
                "min": daily['temperature_2m_min'][i],
                "skycon": wmo_to_skycon(day_wmo, True)  # Daytime skycon for daily forecast
            })

    # Determine unit strings
    if use_fahrenheit:
        temp_unit = "°F"
        wind_unit = "mph"
        unit_system = "imperial"
    else:
        temp_unit = "°C"
        wind_unit = "km/h"
        unit_system = "metric"

    # Build the complete Caiyun structure
    caiyun_data = {
        "status": "ok",
        "api_version": "v2.6",
        "api_status": "active",
        "lang": "en",
        "unit": unit_system,
        "tzshift": om_data.get('utc_offset_seconds', -18000),
        "timezone": om_data.get('timezone', 'America/New_York'),
        "server_time": int(time.time()),
        "location": [LATITUDE, LONGITUDE],
        "result": {
            "alert": {
                "status": "ok",
                "content": []
            },
            "realtime": {
                "status": "ok",
                "temperature": current.get('temperature', 0),
                "humidity": humidity,
                "cloudrate": cloudrate,
                "skycon": skycon,
                "visibility": 10.0,
                "dswrf": 0.0,
                "wind": {
                    "speed": current.get('windspeed', 0),
                    "direction": current.get('winddirection', 0)
                },
                "pressure": 1013.25,
                "apparent_temperature": current.get('temperature', 0),
                "precipitation": {
                    "local": {
                        "status": "ok",
                        "intensity": 0.0,
                        "probability": precipitation_chance,
                        "datasource": "radar"
                    }
                },
                "life_index": {
                    "comfort": {
                        "index": int(50 - (humidity - 50) / 2),
                        "desc": "Comfortable" if 40 <= humidity <= 60 else "Less comfortable"
                    }
                }
            },
            "hourly": {
                "status": "ok",
                "description": "Hourly forecast",
                "temperature": hourly_forecast,  # Now objects with datetime/value
                "skycon": hourly_skycon,  # Now objects with value
                "probability": hourly_precip_probability
            },
            "daily": {
                "status": "ok",
                "temperature": [
                    {"max": d["max"], "min": d["min"]} for d in daily_forecast
                ],
                "skycon": [d["skycon"] for d in daily_forecast],
                "precipitation": [0] * len(daily_forecast)  # Placeholder
            },
            "minutely": {
                "status": "ok",
                "description": "No precipitation expected",
                "probability": [0] * 120  # 2 hours of minute data
            },
            "primary": 0,
            "forecast_keypoint": f"Currently {current.get('temperature', 0):.1f}{temp_unit}, {skycon.replace('_', ' ').lower()}. Wind: {current.get('windspeed', 0):.1f} {wind_unit}"
        }
    }
    return caiyun_data

def main():
    # 1. Fetch data from Open-Meteo
    om_data = fetch_openmeteo(37.541290, -77.434769, USE_FAHRENHEIT)

    # 2. Transform to Caiyun format
    caiyun_data = transform_to_caiyun(om_data, USE_FAHRENHEIT)

    # 3. Print the JSON for the applet to read
    print(json.dumps(caiyun_data, ensure_ascii=False))

if __name__ == "__main__":
    main()
