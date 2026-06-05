import csv
import requests
import time
import traceback
import datetime

# ================= CONFIG =================

OPENWEATHERMAP_API_KEY = "your-api"
BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"

INPUT_CSV_PATH = r"C:\Users\user\OneDrive\Desktop\AI\flight_data_with_flight_number.csv"
OUTPUT_CSV_PATH = r"C:\Users\user\OneDrive\Desktop\AI\flight_data_with_weather.csv"

API_SLEEP_SECONDS = 1.1
PROGRESS_EVERY = 1000  # Show progress every X rows

# ================= WEATHER CACHE =================

weather_cache = {}

# ================= GEO LOOKUP (fallback) =================

def get_lat_lon_from_city(city_name):
    manual_coords = {
        "Christiansted, VI": (17.7466, -64.7032),
        "Frederiksted, VI": (17.7111, -64.8807),
        "St. Thomas, VI": (18.3419, -64.9307),
        "St. Croix, VI": (17.7246, -64.8348),
        "St. John, VI": (18.3308, -64.7281),
    }

    if city_name in manual_coords:
        print(f"📍 Using manual coordinates for '{city_name}'")
        return manual_coords[city_name]

    try:
        response = requests.get(GEO_URL, params={
            'q': city_name,
            'limit': 1,
            'appid': OPENWEATHERMAP_API_KEY
        }, timeout=10)
        response.raise_for_status()
        results = response.json()
        if results:
            return results[0]['lat'], results[0]['lon']
    except Exception as e:
        print(f"❌ Failed geolocation for '{city_name}': {e}")
    return None, None

# ================= CITY NAME VARIANTS =================

def generate_city_variants(raw_city):
    variants = []
    raw_city = raw_city.strip()

    parts = [p.strip() for p in raw_city.split(",")]
    city_part = parts[0]
    state_part = parts[1] if len(parts) > 1 else ""

    if "/" in city_part:
        slash_parts = [p.strip() for p in city_part.split("/")]
        variants.extend(slash_parts)

    variants.append(city_part.replace("/", " "))
    variants.append(city_part.replace("/", ""))
    variants.append(city_part)

    if state_part:
        for v in list(variants):
            variants.append(f"{v},{state_part}")
            variants.append(f"{v}, {state_part}")

    seen = set()
    final = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            final.append(v)

    return final

# ================= WEATHER FETCH =================

def get_weather_data(raw_city):
    if raw_city in weather_cache:
        return weather_cache[raw_city]

    city_variants = generate_city_variants(raw_city)

    # Try by name first
    for city in city_variants:
        try:
            response = requests.get(BASE_WEATHER_URL, params={
                "q": city,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric"
            }, timeout=15)
            response.raise_for_status()
            data = response.json()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            weather_cache[raw_city] = (temp, humidity, pressure)
            time.sleep(API_SLEEP_SECONDS)
            return weather_cache[raw_city]
        except requests.exceptions.HTTPError:
            continue
        except Exception as e:
            print(f"⚠️ Name lookup error for '{city}': {e}")
            break

    # Fallback: use geolocation
    lat, lon = get_lat_lon_from_city(raw_city)
    if lat and lon:
        try:
            response = requests.get(BASE_WEATHER_URL, params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric"
            }, timeout=15)
            response.raise_for_status()
            data = response.json()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            weather_cache[raw_city] = (temp, humidity, pressure)
            time.sleep(API_SLEEP_SECONDS)
            return weather_cache[raw_city]
        except Exception as e:
            print(f"❌ Fallback API error for lat/lon of '{raw_city}': {e}")

    print(f"⚠️ Weather not found for: {raw_city}")
    weather_cache[raw_city] = ("", "", "")
    return weather_cache[raw_city]

# ================= MAIN PROCESS =================

def process_flight_data_with_weather():
    try:
        total_rows = sum(1 for _ in open(INPUT_CSV_PATH, encoding="utf-8")) - 1
        print(f"📄 Total rows to process: {total_rows:,}")

        start_time = time.time()

        with open(INPUT_CSV_PATH, "r", newline="", encoding="utf-8") as infile, \
             open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader)
            writer.writerow(header + ["temperature_c", "humidity_percent", "pressure_hPa"])

            city_idx = header.index("origin_city_name")

            for row_num, row in enumerate(reader, start=1):
                raw_city = row[city_idx]
                temp, humidity, pressure = get_weather_data(raw_city)
                writer.writerow(row + [temp, humidity, pressure])

                if row_num % PROGRESS_EVERY == 0:
                    elapsed = time.time() - start_time
                    avg_per_row = elapsed / row_num
                    remaining = total_rows - row_num
                    eta = str(datetime.timedelta(seconds=int(remaining * avg_per_row)))
                    percent = (row_num / total_rows) * 100
                    print(
                        f"✅ {row_num:,}/{total_rows:,} ({percent:.2f}%) | "
                        f"Cached: {len(weather_cache)} | ETA: {eta}"
                    )

        print("\n🎉 DONE SUCCESSFULLY")
        print(f"📁 Output saved to:\n{OUTPUT_CSV_PATH}")
        print(f"🌍 Unique cities queried: {len(weather_cache)}")

    except Exception:
        print("❌ Unexpected error:")
        traceback.print_exc()

# ================= RUN =================

if __name__ == "__main__":
    process_flight_data_with_weather()
