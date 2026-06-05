
# airport_coords.py - AGENTIC VERSION
# Now includes fallback to online geocoding API

import requests

AIRPORT_COORDINATES = {
    # China Airports
    "SZX": {"latitude": 22.6393, "longitude": 113.8108, "name": "Shenzhen Bao'an International"},
    "PEK": {"latitude": 40.0799, "longitude": 116.6031, "name": "Beijing Capital International"},
    "PVG": {"latitude": 31.1443, "longitude": 121.8083, "name": "Shanghai Pudong International"},
    "CAN": {"latitude": 23.3924, "longitude": 113.2988, "name": "Guangzhou Baiyun International"},
    "CTU": {"latitude": 30.5785, "longitude": 103.9470, "name": "Chengdu Shuangliu International"},
    "KMG": {"latitude": 25.1019, "longitude": 102.9292, "name": "Kunming Changshui International"},
    "XIY": {"latitude": 34.4471, "longitude": 108.7514, "name": "Xi'an Xianyang International"},
    "HGH": {"latitude": 30.2295, "longitude": 120.4347, "name": "Hangzhou Xiaoshan International"},
    "WUH": {"latitude": 30.7838, "longitude": 114.2081, "name": "Wuhan Tianhe International"},
    "NKG": {"latitude": 31.7420, "longitude": 118.8620, "name": "Nanjing Lukou International"},
    "JJN": {"latitude": 26.8207, "longitude": 100.2460, "name": "Jinjiang Airport"},
    
    # US Airports
    "JFK": {"latitude": 40.6413, "longitude": -73.7781, "name": "John F Kennedy International"},
    "LAX": {"latitude": 33.9416, "longitude": -118.4085, "name": "Los Angeles International"},
    "ORD": {"latitude": 41.9742, "longitude": -87.9073, "name": "O'Hare International"},
    "ATL": {"latitude": 33.6407, "longitude": -84.4277, "name": "Hartsfield-Jackson Atlanta International"},
    "DFW": {"latitude": 32.8998, "longitude": -97.0403, "name": "Dallas/Fort Worth International"},
    "DEN": {"latitude": 39.8561, "longitude": -104.6737, "name": "Denver International"},
    "SFO": {"latitude": 37.6213, "longitude": -122.3790, "name": "San Francisco International"},
    "LAS": {"latitude": 36.0840, "longitude": -115.1537, "name": "Las Vegas McCarran International"},
    "PHX": {"latitude": 33.4352, "longitude": -112.0101, "name": "Phoenix Sky Harbor International"},
    "IAH": {"latitude": 29.9902, "longitude": -95.3368, "name": "George Bush Intercontinental"},
    "MIA": {"latitude": 25.7959, "longitude": -80.2870, "name": "Miami International"},
    "SEA": {"latitude": 47.4502, "longitude": -122.3088, "name": "Seattle-Tacoma International"},
    "EWR": {"latitude": 40.6895, "longitude": -74.1745, "name": "Newark Liberty International"},
    "BOS": {"latitude": 42.3656, "longitude": -71.0096, "name": "Boston Logan International"},
    "MCO": {"latitude": 28.4312, "longitude": -81.3081, "name": "Orlando International"},
    
    # European Airports
    "LHR": {"latitude": 51.4700, "longitude": -0.4543, "name": "London Heathrow"},
    "CDG": {"latitude": 49.0097, "longitude": 2.5479, "name": "Paris Charles de Gaulle"},
    "FRA": {"latitude": 50.0379, "longitude": 8.5622, "name": "Frankfurt Airport"},
    "AMS": {"latitude": 52.3105, "longitude": 4.7683, "name": "Amsterdam Schiphol"},
    "MAD": {"latitude": 40.4983, "longitude": -3.5676, "name": "Madrid Barajas"},
    "BCN": {"latitude": 41.2974, "longitude": 2.0833, "name": "Barcelona El Prat"},
    "FCO": {"latitude": 41.8003, "longitude": 12.2389, "name": "Rome Fiumicino"},
    "MUC": {"latitude": 48.3537, "longitude": 11.7750, "name": "Munich Airport"},
    "LGW": {"latitude": 51.1537, "longitude": -0.1821, "name": "London Gatwick"},
    "IST": {"latitude": 41.2753, "longitude": 28.7519, "name": "Istanbul Airport"},
    
    # Middle East Airports
    "DXB": {"latitude": 25.2532, "longitude": 55.3657, "name": "Dubai International"},
    "DOH": {"latitude": 25.2731, "longitude": 51.6080, "name": "Hamad International Airport"},
    "AUH": {"latitude": 24.4330, "longitude": 54.6511, "name": "Abu Dhabi International"},
    
    # Asia Pacific Airports
    "HKG": {"latitude": 22.3080, "longitude": 113.9185, "name": "Hong Kong International"},
    "SIN": {"latitude": 1.3644, "longitude": 103.9915, "name": "Singapore Changi"},
    "ICN": {"latitude": 37.4602, "longitude": 126.4407, "name": "Seoul Incheon International"},
    "NRT": {"latitude": 35.7720, "longitude": 140.3929, "name": "Tokyo Narita International"},
    "HND": {"latitude": 35.5494, "longitude": 139.7798, "name": "Tokyo Haneda"},
    "BKK": {"latitude": 13.6900, "longitude": 100.7501, "name": "Bangkok Suvarnabhumi"},
    "KUL": {"latitude": 2.7456, "longitude": 101.7072, "name": "Kuala Lumpur International"},
    "SYD": {"latitude": -33.9399, "longitude": 151.1753, "name": "Sydney Kingsford Smith"},
    "MEL": {"latitude": -37.6690, "longitude": 144.8410, "name": "Melbourne Airport"},
    "DEL": {"latitude": 28.5562, "longitude": 77.1000, "name": "Indira Gandhi International"},
    "BOM": {"latitude": 19.0886, "longitude": 72.8678, "name": "Mumbai Chhatrapati Shivaji"},
    
    # Canadian Airports
    "YYZ": {"latitude": 43.6777, "longitude": -79.6248, "name": "Toronto Pearson International"},
    "YVR": {"latitude": 49.1939, "longitude": -123.1844, "name": "Vancouver International"},
    "YUL": {"latitude": 45.4657, "longitude": -73.7450, "name": "Montreal Pierre Elliott Trudeau"},
    
    # South American Airports
    "GRU": {"latitude": -23.4356, "longitude": -46.4731, "name": "Sao Paulo Guarulhos International"},
    "EZE": {"latitude": -34.8222, "longitude": -58.5358, "name": "Buenos Aires Ezeiza International"},
    "BOG": {"latitude": 4.7016, "longitude": -74.1469, "name": "Bogota El Dorado International"},
    
    # African Airports
    "CAI": {"latitude": 30.1219, "longitude": 31.4056, "name": "Cairo International"},
    "JNB": {"latitude": -26.1392, "longitude": 28.2460, "name": "Johannesburg OR Tambo International"},
}

# In-memory cache for dynamically fetched airports
_dynamic_cache = {}

def geocode_airport(iata_code):
    """
    FALLBACK: Use free geocoding API to find airport coordinates
    Uses Nominatim (OpenStreetMap) - free, no API key needed
    """
    try:
        query = f"{iata_code} Airport"
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "FlightDelayPredictor/1.0"}
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            coords = {
                "latitude": float(data["lat"]),
                "longitude": float(data["lon"]),
                "name": f"{iata_code} Airport (geocoded)",
                "source": "geocoded"
            }
            print(f"🌍 Geocoded {iata_code}: {coords['latitude']}, {coords['longitude']}")
            return coords
            
    except Exception as e:
        print(f"⚠️  Geocoding failed for {iata_code}: {e}")
    
    return None

def get_airport_coords(iata_code, use_fallback=True):
    """
    AGENTIC VERSION: Get coordinates with multiple fallback strategies
    
    Strategy:
    1. Try local database
    2. Try dynamic cache
    3. Try geocoding API (if enabled)
    4. Use regional defaults as last resort
    
    Args:
        iata_code (str): 3-letter IATA airport code
        use_fallback (bool): Enable fallback strategies
        
    Returns:
        dict: Coordinates with confidence indicator
    """
    if not iata_code:
        return {
            "latitude": 0.0,
            "longitude": 0.0,
            "name": "Unknown",
            "confidence": "none"
        }
    
    code = iata_code.upper()
    
    # Strategy 1: Local database (HIGH confidence)
    if code in AIRPORT_COORDINATES:
        result = AIRPORT_COORDINATES[code].copy()
        result["confidence"] = "high"
        result["source"] = "database"
        return result
    
    # Strategy 2: Dynamic cache (MEDIUM confidence)
    if code in _dynamic_cache:
        print(f"📦 Using cached coordinates for {code}")
        return _dynamic_cache[code]
    
    # Strategy 3: Geocoding API (MEDIUM confidence)
    if use_fallback:
        print(f"🔍 {code} not in database, trying geocoding...")
        geocoded = geocode_airport(code)
        if geocoded:
            geocoded["confidence"] = "medium"
            _dynamic_cache[code] = geocoded  # Cache it
            return geocoded
    
    # Strategy 4: Regional defaults based on code pattern (LOW confidence)
    regional_defaults = {
        "K": {"latitude": 39.0, "longitude": -95.0, "region": "US Central"},
        "E": {"latitude": 50.0, "longitude": 10.0, "region": "Europe"},
        "Y": {"latitude": 50.0, "longitude": -100.0, "region": "Canada"},
        "Z": {"latitude": 30.0, "longitude": 110.0, "region": "China"},
    }
    
    first_char = code[0] if code else ""
    if first_char in regional_defaults and use_fallback:
        default = regional_defaults[first_char].copy()
        print(f"⚠️  Using regional default for {code} ({default['region']})")
        return {
            "latitude": default["latitude"],
            "longitude": default["longitude"],
            "name": f"{code} Airport (estimated - {default['region']})",
            "confidence": "low",
            "source": "regional_default"
        }
    
    # Last resort: Return zeros but agent can still try to proceed
    print(f"❌ No coordinates found for {code} - using fallback")
    return {
        "latitude": 0.0,
        "longitude": 0.0,
        "name": f"Unknown ({code})",
        "confidence": "none",
        "source": "unknown"
    }

def add_airport(iata_code, latitude, longitude, name):
    """Add airport to permanent database"""
    AIRPORT_COORDINATES[iata_code.upper()] = {
        "latitude": latitude,
        "longitude": longitude,
        "name": name
    }
    print(f"✅ Added {name} ({iata_code}) to database")

def list_all_airports():
    """Print all airports in database"""
    print(f"\n📍 Airport Database ({len(AIRPORT_COORDINATES)} airports):")
    print("="*80)
    for code, info in sorted(AIRPORT_COORDINATES.items()):
        print(f"{code}: {info['name']}")
        print(f"    Coordinates: {info['latitude']}, {info['longitude']}")
    print("="*80)