import pandas as pd
import joblib

df = pd.read_csv("final_features.csv")

FORBIDDEN_COLUMNS = [
    "delay",
    "flight_number",
    "dep_delay",
    "arr_delay",
    "taxi_in",
    "taxi_out",
    "air_time",
    "wheels_on",
    "wheels_off",
    "actual_departure",
    "actual_arrival",
    "year"  # include if constant in training
]

X = df.drop(columns=FORBIDDEN_COLUMNS, errors="ignore")

feature_list = list(X.columns)

joblib.dump(feature_list, "feature_list.pkl")

print("✅ feature_list.pkl created successfully")
print("Total features:", len(feature_list))