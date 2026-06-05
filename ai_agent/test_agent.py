"""
Complete working test with data adapter
"""

import pandas as pd
import xgboost as xgb
from flight_api import get_flight_data
from weather_api import get_weather_data
from feature_mapper import map_features_for_prediction, validate_features
from data_adapter import adapt_flight_data


def run_complete_prediction(flight_number, model_path='xgboost_flight_delay.json'):
    """
    Run a complete prediction for a flight

    Args:
        flight_number: Flight IATA code (e.g., 'O36847')
        model_path: Path to trained XGBoost model
    """

    # Your exact training columns
    feature_list = ["month", "day_of_month", "day_of_week", "op_carrier_fl_num", "crs_dep_time",
                    "dep_time", "crs_arr_time", "arr_time", "crs_elapsed_time", "actual_elapsed_time",
                    "distance", "temperature_c", "humidity_percent", "pressure_hPa",
                    "op_unique_carrier_AA", "op_unique_carrier_AS", "op_unique_carrier_B6",
                    "op_unique_carrier_DL", "op_unique_carrier_MQ", "op_unique_carrier_NK",
                    "op_unique_carrier_OO", "op_unique_carrier_UA", "op_unique_carrier_WN",
                    "op_unique_carrier_YX", "origin_ATL", "origin_CLT", "origin_DEN", "origin_DFW",
                    "origin_LAS", "origin_LAX", "origin_LGA", "origin_MCO", "origin_ORD", "origin_PHX",
                    "dest_ATL", "dest_CLT", "dest_DEN", "dest_DFW", "dest_LAS", "dest_LAX", "dest_LGA",
                    "dest_MCO", "dest_ORD", "dest_PHX"]

    print("\n" + "🚀" * 40)
    print(f"FLIGHT DELAY PREDICTION FOR: {flight_number}")
    print("🚀" * 40 + "\n")

    # Step 1: Get Flight Data
    print("=" * 80)
    print("STEP 1: Fetching Flight Data")
    print("=" * 80)

    flight_data = get_flight_data(flight_number)
    if not flight_data:
        print("❌ Failed to get flight data")
        return None

    print(f"✅ Flight: {flight_data['airline']} {flight_data['flight_number']}")
    print(f"   Route: {flight_data['origin']} → {flight_data['destination']}")

    # Step 2: Get Weather Data
    print("\n" + "=" * 80)
    print("STEP 2: Fetching Weather Data")
    print("=" * 80)

    origin_weather = get_weather_data(
        flight_data['departure_latitude'],
        flight_data['departure_longitude']
    )

    dest_weather = get_weather_data(
        flight_data['arrival_latitude'],
        flight_data['arrival_longitude']
    )

    if not origin_weather or not dest_weather:
        print("❌ Failed to get weather data")
        return None

    print(f"✅ Origin Weather: {origin_weather['temperature_c']}°C")
    print(f"✅ Destination Weather: {dest_weather['temperature_c']}°C")

    # Step 3: Adapt Data
    print("\n" + "=" * 80)
    print("STEP 3: Adapting Data for Model")
    print("=" * 80)

    complete_data = adapt_flight_data(flight_data, origin_weather, dest_weather)

    # Step 4: Map Features
    print("\n" + "=" * 80)
    print("STEP 4: Mapping Features")
    print("=" * 80)

    try:
        features_df = map_features_for_prediction(complete_data, feature_list)
        validate_features(features_df, feature_list)
        print(f"✅ Feature DataFrame Shape: {features_df.shape}")
    except Exception as e:
        print(f"❌ Feature mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return None

    # Step 5: Load Model and Predict
    print("\n" + "=" * 80)
    print("STEP 5: Making Prediction")
    print("=" * 80)

    try:
        # Load model
        model = xgb.Booster()
        model.load_model(model_path)
        print(f"✅ Model loaded from {model_path}")

        # Convert to DMatrix
        dmatrix = xgb.DMatrix(features_df)

        # Make prediction
        prediction = model.predict(dmatrix)[0]

        # Interpret results
        print("\n" + "🎯" * 40)
        print("PREDICTION RESULTS")
        print("🎯" * 40)
        print(f"\nFlight: {flight_data['airline']} {flight_data['flight_number']}")
        print(f"Route: {flight_data['origin']} → {flight_data['destination']}")
        print(f"Distance: {complete_data['distance']} miles")
        print(f"Departure: {complete_data['crs_dep_time'] // 100:02d}:{complete_data['crs_dep_time'] % 100:02d}")
        print(f"Date: {complete_data['month']}/{complete_data['day_of_month']} (Day {complete_data['day_of_week']})")
        print(f"\n{'=' * 80}")

        if prediction > 0.5:
            print(f"⚠️  PREDICTION: DELAYED")
            print(f"📊 Delay Probability: {prediction:.2%}")
            print(f"🎯 Confidence: HIGH" if prediction > 0.7 else "🎯 Confidence: MODERATE")
        else:
            print(f"✅ PREDICTION: ON TIME")
            print(f"📊 On-Time Probability: {(1 - prediction):.2%}")
            print(f"🎯 Confidence: HIGH" if prediction < 0.3 else "🎯 Confidence: MODERATE")

        print(f"{'=' * 80}\n")

        return {
            'flight_number': flight_number,
            'prediction': 'DELAYED' if prediction > 0.5 else 'ON_TIME',
            'probability': prediction,
            'flight_data': flight_data,
            'weather': origin_weather
        }

    except FileNotFoundError:
        print(f"❌ Model file not found: {model_path}")
        print("   Make sure your model is saved as 'xgboost_model.json'")
        return None
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test with your flight
    result = run_complete_prediction("O36847")

    if result:
        print("\n✅ SYSTEM TEST COMPLETE - ALL COMPONENTS WORKING!")
        print("🚀 Ready to build your agentic AI!")
    else:
        print("\n❌ SYSTEM TEST FAILED")
        print("📝 Please fix the issues above before proceeding")