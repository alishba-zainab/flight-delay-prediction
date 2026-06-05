"""
Updated Feature Mapper to match your exact training columns
"""

import pandas as pd


def map_features_for_prediction(complete_data, feature_list):
    """
    Map complete data to match training feature columns exactly

    Args:
        complete_data: Dictionary with all flight/weather data from adapter
        feature_list: List of feature names from training (training_columns.json)

    Returns:
        pd.DataFrame: Single row with all features in correct order
    """

    # Initialize all features to 0
    row = {feature: 0 for feature in feature_list}

    # Fill in numerical features
    row['month'] = complete_data.get('month', 1)
    row['day_of_month'] = complete_data.get('day_of_month', 1)
    row['day_of_week'] = complete_data.get('day_of_week', 0)
    row['op_carrier_fl_num'] = complete_data.get('op_carrier_fl_num', 0)
    row['crs_dep_time'] = complete_data.get('crs_dep_time', 1200)
    row['dep_time'] = complete_data.get('dep_time', 1200)
    row['crs_arr_time'] = complete_data.get('crs_arr_time', 1400)
    row['arr_time'] = complete_data.get('arr_time', 1400)
    row['crs_elapsed_time'] = complete_data.get('crs_elapsed_time', 120)
    row['actual_elapsed_time'] = complete_data.get('actual_elapsed_time', 120)
    row['distance'] = complete_data.get('distance', 500)
    row['temperature_c'] = complete_data.get('temperature_c', 20)
    row['humidity_percent'] = complete_data.get('humidity_percent', 50)
    row['pressure_hPa'] = complete_data.get('pressure_hPa', 1013)

    # One-hot encode carrier
    carrier = complete_data.get('op_unique_carrier', 'AA')
    carrier_col = f"op_unique_carrier_{carrier}"
    if carrier_col in row:
        row[carrier_col] = 1

    # One-hot encode origin
    origin = complete_data.get('origin', 'ATL')
    origin_col = f"origin_{origin}"
    if origin_col in row:
        row[origin_col] = 1

    # One-hot encode destination
    dest = complete_data.get('dest', 'ATL')
    dest_col = f"dest_{dest}"
    if dest_col in row:
        row[dest_col] = 1

    print(f"✅ Mapped {len(feature_list)} features")
    print(f"   Carrier: {carrier} → {carrier_col in row}")
    print(f"   Origin: {origin} → {origin_col in row}")
    print(f"   Destination: {dest} → {dest_col in row}")

    # Create DataFrame with features in exact order
    df = pd.DataFrame([row])
    df = df[feature_list]  # Ensure correct column order

    return df


def validate_features(df, feature_list):
    """
    Validate that features match training
    """
    if list(df.columns) != feature_list:
        print("⚠️  Warning: Feature order doesn't match training!")
        return False

    if df.shape[1] != len(feature_list):
        print(f"⚠️  Warning: Feature count mismatch! Got {df.shape[1]}, expected {len(feature_list)}")
        return False

    print(f"✅ Features validated: {df.shape[1]} columns match training")
    return True