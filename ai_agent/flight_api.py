import requests
import sys
from airport_coords import get_airport_coords

AVIATION_API_KEY = "7e51480e869eafa974e5d5aee6681836"


def get_flight_data(flight_number):
    """
    Get flight data from Aviation Stack API and enrich with coordinates

    Args:
        flight_number (str): Flight IATA code (e.g., 'AA100', 'DL123')

    Returns:
        dict: Flight information including coordinates, or None if not found
    """
    if not AVIATION_API_KEY:
        raise RuntimeError("❌ Flight API key not set")

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVIATION_API_KEY,
        "flight_iata": flight_number
    }

    print(f"🔍 Fetching flight data for {flight_number}...")

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"❌ API request failed with status code: {response.status_code}")
            return None

        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            print(f"❌ No data found for flight {flight_number}")
            print("💡 Make sure the flight number is correct (e.g., 'AA100', 'DL123')")
            return None

        flight_data = data["data"][0]

        # Extract basic flight info - FIXED: Use 'or {}' to handle None values
        departure_info = flight_data.get("departure") or {}
        arrival_info = flight_data.get("arrival") or {}
        flight_info = flight_data.get("flight") or {}
        airline_info = flight_data.get("airline") or {}
        aircraft_info = flight_data.get("aircraft") or {}

        # Get IATA codes
        origin_code = departure_info.get("iata", "Unknown")
        destination_code = arrival_info.get("iata", "Unknown")

        # Validate we have required airport codes
        if origin_code == "Unknown" or destination_code == "Unknown":
            print(f"⚠️  Warning: Could not determine origin or destination airports")

        # Get coordinates from our database (since API returns null)
        try:
            origin_coords = get_airport_coords(origin_code)
            dest_coords = get_airport_coords(destination_code)
        except (KeyError, TypeError) as e:
            print(f"⚠️  Warning: Could not get coordinates for airports")
            print(f"    Origin: {origin_code}, Destination: {destination_code}")
            return None

        # Build comprehensive flight data
        result = {
            # Basic Flight Info
            "flight_number": flight_info.get("iata", flight_number),
            "flight_icao": flight_info.get("icao"),
            "flight_status": flight_data.get("flight_status", "unknown"),

            # Airline Info
            "airline": airline_info.get("name", "Unknown"),
            "airline_iata": airline_info.get("iata"),

            # Departure Info
            "origin": origin_code,
            "origin_airport": departure_info.get("airport", "Unknown"),
            "departure_latitude": origin_coords["latitude"],
            "departure_longitude": origin_coords["longitude"],
            "departure_timezone": departure_info.get("timezone"),
            "scheduled_departure": departure_info.get("scheduled"),
            "estimated_departure": departure_info.get("estimated"),
            "actual_departure": departure_info.get("actual"),
            "departure_terminal": departure_info.get("terminal"),
            "departure_gate": departure_info.get("gate"),

            # Arrival Info
            "destination": destination_code,
            "destination_airport": arrival_info.get("airport", "Unknown"),
            "arrival_latitude": dest_coords["latitude"],
            "arrival_longitude": dest_coords["longitude"],
            "arrival_timezone": arrival_info.get("timezone"),
            "scheduled_arrival": arrival_info.get("scheduled"),
            "estimated_arrival": arrival_info.get("estimated"),
            "actual_arrival": arrival_info.get("actual"),
            "arrival_terminal": arrival_info.get("terminal"),
            "arrival_gate": arrival_info.get("gate"),

            # Additional Info - FIXED: Now uses aircraft_info variable
            "aircraft_icao": aircraft_info.get("icao"),
            "flight_date": flight_data.get("flight_date"),
            "live_data": flight_data.get("live"),
        }

        print(f"✅ Retrieved data for {result['airline']} {result['flight_number']}")
        print(f"   Route: {origin_code} → {destination_code}")
        print(
            f"   Coordinates: ({origin_coords['latitude']}, {origin_coords['longitude']}) → ({dest_coords['latitude']}, {dest_coords['longitude']})")

        return result

    except requests.exceptions.Timeout:
        print(f"❌ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def get_flight_info(flight_number, date=None):
    """
    Wrapper function for compatibility with agent code

    Args:
        flight_number (str): Flight IATA code
        date (str, optional): Flight date (not used with free API tier)

    Returns:
        dict: Flight information
    """
    return get_flight_data(flight_number)


def print_flight_summary(result):
    """
    Print a formatted summary of flight data

    Args:
        result (dict): Flight data dictionary
    """
    if not result:
        return

    print("\n" + "=" * 80)
    print("FLIGHT DATA SUMMARY")
    print("=" * 80)
    print(f"Flight: {result['airline']} {result['flight_number']}")
    print(f"Status: {result['flight_status']}")

    print(f"\n📍 Departure:")
    print(f"  Airport: {result['origin_airport']} ({result['origin']})")
    print(f"  Coordinates: {result['departure_latitude']}, {result['departure_longitude']}")
    if result.get('scheduled_departure'):
        print(f"  Scheduled: {result['scheduled_departure']}")
    if result.get('departure_terminal'):
        print(f"  Terminal: {result['departure_terminal']}")
    if result.get('departure_gate'):
        print(f"  Gate: {result['departure_gate']}")

    print(f"\n📍 Arrival:")
    print(f"  Airport: {result['destination_airport']} ({result['destination']})")
    print(f"  Coordinates: {result['arrival_latitude']}, {result['arrival_longitude']}")
    if result.get('scheduled_arrival'):
        print(f"  Scheduled: {result['scheduled_arrival']}")
    if result.get('arrival_terminal'):
        print(f"  Terminal: {result['arrival_terminal']}")
    if result.get('arrival_gate'):
        print(f"  Gate: {result['arrival_gate']}")

    if result.get('aircraft_icao'):
        print(f"\n✈️  Aircraft: {result['aircraft_icao']}")

    print("=" * 80)


# Test/Demo function
if __name__ == "__main__":
    print("=" * 80)
    print("FLIGHT DATA API - GENERAL VERSION")
    print("=" * 80)

    # Check if flight number provided as command line argument
    if len(sys.argv) > 1:
        flight_number = sys.argv[1].upper()
        print(f"\n🔍 Testing with flight: {flight_number}")
    else:
        # Interactive mode - ask user for flight number
        print("\n💡 Usage:")
        print("   - Command line: python flight_api.py AA100")
        print("   - Interactive: Just run python flight_api.py")
        print("\n" + "=" * 80)

        flight_number = input("\n✈️  Enter flight number (e.g., AA100, DL123, UA456): ").strip().upper()

        if not flight_number:
            print("❌ No flight number provided. Exiting.")
            sys.exit(1)

    # Fetch and display flight data
    result = get_flight_data(flight_number)

    if result:
        print_flight_summary(result)
        print("\n✅ Success! Flight data retrieved.")
    else:
        print("\n❌ Could not retrieve flight data.")
        print("\n💡 Tips:")
        print("   - Check if the flight number is correct")
        print("   - Make sure the flight is active/scheduled")
        print("   - Try a different flight (e.g., AA100, DL123, UA456)")
        print("   - Some flights may not be available in the free API tier")