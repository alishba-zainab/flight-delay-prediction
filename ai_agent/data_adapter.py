import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance with fallback for invalid coordinates"""
    if any(coord == 0.0 for coord in [lat1, lon1, lat2, lon2]):
        return 500.0  # Default to medium-haul flight

    R = 3959.0  # Earth radius in miles
    try:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        return round(distance, 2)
    except Exception:
        return 500.0

def parse_departure_time(scheduled_departure):
    """Convert scheduled departure to HHMM format"""
    if not scheduled_departure:
        return 1200
    try:
        dt = datetime.fromisoformat(scheduled_departure.replace('Z', '+00:00'))
        return int(dt.strftime('%H%M'))
    except Exception:
        return 1200

def get_airline_code(airline_iata):
    """Map airline IATA codes"""
    airline_map = {
        'AA': 'AA', 'UA': 'UA', 'DL': 'DL', 'WN': 'WN',
        'B6': 'B6', 'AS': 'AS', 'NK': 'NK', 'F9': 'F9',
    }
    return airline_map.get(airline_iata, 'AA')

def adapt_flight_data(flight_api_data, origin_weather, dest_weather):
    """AGENTIC VERSION: Always returns valid data with confidence scores"""
    data_confidence = {
        "flight_data": "high" if flight_api_data else "none",
        "coordinates": "unknown",
        "weather": "unknown",
        "overall": "unknown"
    }

    origin_lat = flight_api_data.get('departure_latitude', 0.0)
    origin_lon = flight_api_data.get('departure_longitude', 0.0)
    dest_lat = flight_api_data.get('arrival_latitude', 0.0)
    dest_lon = flight_api_data.get('arrival_longitude', 0.0)

    if origin_lat != 0.0 and dest_lat != 0.0:
        data_confidence["coordinates"] = "high"
    else:
        data_confidence["coordinates"] = "estimated"

    distance = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)

    scheduled_dt = None
    if flight_api_data.get('scheduled_departure'):
        try:
            scheduled_dt = datetime.fromisoformat(
                flight_api_data['scheduled_departure'].replace('Z', '+00:00')
            )
        except Exception:
            scheduled_dt = datetime.now()
    else:
        scheduled_dt = datetime.now()

    crs_dep_time = int(scheduled_dt.strftime('%H%M'))

    flight_num_str = flight_api_data.get('flight_number', '0')
    op_carrier_fl_num = int(''.join(filter(str.isdigit, flight_num_str)) or '0')
    carrier = get_airline_code(flight_api_data.get('airline_iata', 'AA'))

    avg_speed_mph = 500
    estimated_flight_hours = distance / avg_speed_mph
    crs_elapsed_time = int(estimated_flight_hours * 60)
    crs_arr_time = crs_dep_time + crs_elapsed_time
    if crs_arr_time >= 2400:
        crs_arr_time -= 2400

    origin_conf = origin_weather.get('confidence', 'unknown')
    dest_conf = dest_weather.get('confidence', 'unknown')
    data_confidence["weather"] = "high" if origin_conf == "high" else origin_conf

    confidences = [data_confidence["flight_data"], data_confidence["coordinates"], data_confidence["weather"]]
    if all(c == "high" for c in confidences):
        data_confidence["overall"] = "high"
    elif any(c in ["none", "low"] for c in confidences):
        data_confidence["overall"] = "low"
    else:
        data_confidence["overall"] = "medium"

    complete_data = {
        'month': scheduled_dt.month,
        'day_of_month': scheduled_dt.day,
        'day_of_week': scheduled_dt.weekday(),
        'op_carrier_fl_num': op_carrier_fl_num,
        'crs_dep_time': crs_dep_time,
        'dep_time': crs_dep_time,
        'crs_arr_time': crs_arr_time,
        'arr_time': crs_arr_time,
        'crs_elapsed_time': crs_elapsed_time,
        'actual_elapsed_time': crs_elapsed_time,
        'distance': distance,
        'temperature_c': origin_weather.get('temperature_c', 15.0),
        'humidity_percent': origin_weather.get('humidity_percent', 60.0),
        'pressure_hPa': origin_weather.get('pressure_hPa', 1013.0),
        'op_unique_carrier': carrier,
        'origin': flight_api_data.get('origin', 'ATL'),
        'dest': flight_api_data.get('destination', 'ATL'),
        '_confidence': data_confidence
    }

    print(f"\n📊 Data Quality Assessment:")
    print(f"   Flight Data: {data_confidence['flight_data']}")
    print(f"   Coordinates: {data_confidence['coordinates']}")
    print(f"   Weather: {data_confidence['weather']}")
    print(f"   Overall: {data_confidence['overall'].upper()}")
    if data_confidence["overall"] != "high":
        print(f"   ⚠️  Prediction will use estimated/default values where needed")

    print(f"\n📊 Adapted Data:")
    print(f"   Route: {complete_data['origin']} → {complete_data['dest']}")
    print(f"   Distance: {distance} miles")
    print(f"   Weather: {complete_data['temperature_c']}°C, {complete_data['humidity_percent']}%")

    return complete_data

def load_feature_list(filepath='training_columns.json'):
    """Load feature list from training"""
    try:
        with open(filepath, 'r') as f:
            feature_list = json.load(f)
        print(f"✅ Loaded {len(feature_list)} features from {filepath}")
        return feature_list
    except FileNotFoundError:
        print(f"❌ Feature list not found: {filepath}")
        return None
