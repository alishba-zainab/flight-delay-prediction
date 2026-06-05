
# weather_api.py - AGENTIC VERSION
import requests

WEATHER_API_KEY = "our_api_key"

# Historical averages for different regions (fallback data)
REGIONAL_WEATHER_DEFAULTS = {
    "tropical": {"temperature_c": 28, "humidity_percent": 75, "pressure_hPa": 1013},
    "temperate": {"temperature_c": 15, "humidity_percent": 60, "pressure_hPa": 1015},
    "cold": {"temperature_c": 5, "humidity_percent": 50, "pressure_hPa": 1020},
    "desert": {"temperature_c": 25, "humidity_percent": 30, "pressure_hPa": 1010},
}

def estimate_regional_weather(lat, lon):
    """
    Estimate weather based on geographic location
    Used as fallback when API fails
    """
    # Simple heuristic based on latitude
    abs_lat = abs(lat)
    
    if abs_lat < 23.5:  # Tropics
        region = "tropical"
    elif abs_lat < 40:   # Temperate
        region = "temperate"
    elif abs_lat < 66.5: # Cold temperate
        region = "cold"
    else:                # Polar
        region = "cold"
    
    # Adjust for known desert regions (longitude-based)
    if 20 < lon < 60 and 15 < abs_lat < 35:  # Middle East
        region = "desert"
    elif -120 < lon < -100 and 25 < abs_lat < 40:  # US Southwest
        region = "desert"
    
    return REGIONAL_WEATHER_DEFAULTS[region], region

def get_weather_data(lat, lon, use_fallback=True):
    """
    AGENTIC VERSION: Get weather with multiple fallback strategies
    
    Strategy:
    1. Try OpenWeatherMap API
    2. If coordinates are (0,0), skip API and use global average
    3. If API fails, estimate based on location
    4. Last resort: Use global average
    
    Returns:
        dict: Weather data with confidence indicator
    """
    
    # Handle missing coordinates gracefully
    if lat == 0.0 and lon == 0.0:
        print(f"⚠️  Invalid coordinates (0,0), using global average weather")
        return {
            "temperature_c": 15.0,
            "humidity_percent": 60.0,
            "pressure_hPa": 1013.0,
            "confidence": "low",
            "source": "global_average"
        }
    
    if not WEATHER_API_KEY:
        if use_fallback:
            print(f"⚠️  No API key, using estimated weather for ({lat}, {lon})")
            weather, region = estimate_regional_weather(lat, lon)
            weather["confidence"] = "low"
            weather["source"] = f"estimated_{region}"
            return weather
        return None
    
    # Try API first (HIGH confidence)
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "main" in data:
                return {
                    "temperature_c": data["main"]["temp"],
                    "humidity_percent": data["main"]["humidity"],
                    "pressure_hPa": data["main"]["pressure"],
                    "confidence": "high",
                    "source": "api"
                }
    
    except requests.exceptions.Timeout:
        print(f"⏱️  Weather API timeout for ({lat}, {lon})")
    except Exception as e:
        print(f"⚠️  Weather API error: {e}")
    
    # Fallback strategies
    if use_fallback:
        print(f"🔄 Using estimated weather for ({lat}, {lon})")
        weather, region = estimate_regional_weather(lat, lon)
        weather["confidence"] = "medium"
        weather["source"] = f"estimated_{region}"
        return weather
    
    # Last resort
    print(f"⚠️  All weather strategies failed, using global average")
    return {
        "temperature_c": 15.0,
        "humidity_percent": 60.0,
        "pressure_hPa": 1013.0,
        "confidence": "low",
        "source": "default"
    }