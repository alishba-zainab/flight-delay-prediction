
import pandas as pd
from sklearn.preprocessing import StandardScaler

# First, find top 10 carriers, origins, destinations globally
df_temp = pd.read_csv("flight_data_with_weather.csv")
top_carriers = df_temp["op_unique_carrier"].value_counts().nlargest(10).index
top_origins = df_temp["origin"].value_counts().nlargest(10).index
top_dests = df_temp["dest"].value_counts().nlargest(10).index
del df_temp  # free memory

# Columns to scale
num_cols = ["year","month","day_of_month","day_of_week","crs_dep_time",
            "crs_arr_time","crs_elapsed_time","distance","temperature_c",
            "humidity_percent","pressure_hPa"]

# Process in chunks and write directly to CSV
chunksize = 100000
first_chunk = True

for chunk in pd.read_csv("flight_data_with_weather.csv", chunksize=chunksize):
    # Keep only top carriers, origins, destinations
    chunk = chunk[chunk["op_unique_carrier"].isin(top_carriers)]
    chunk = chunk[chunk["origin"].isin(top_origins)]
    chunk = chunk[chunk["dest"].isin(top_dests)]

    if chunk.empty:
        continue  # skip empty chunks

    # Create target
    chunk["delay"] = (chunk["arr_delay"] > 15).astype(int)

    # Drop unnecessary columns
    chunk = chunk.drop(columns=[
        "fl_date","origin_city_name","origin_state_nm","dest_city_name","dest_state_nm",
        "cancellation_code","cancelled","diverted","carrier_delay","weather_delay",
        "nas_delay","security_delay","late_aircraft_delay","arr_delay"
    ])

    # Convert to dummies
    chunk = pd.get_dummies(chunk, columns=["op_unique_carrier","origin","dest"])

    # Scale numeric columns
    chunk[num_cols] = StandardScaler().fit_transform(chunk[num_cols])

    # Write to CSV incrementally
    if first_chunk:
        chunk.to_csv(r"C:\Users\zaina\Documents\AI\final_features.csv", index=False)
        first_chunk = False
    else:
        chunk.to_csv(r"C:\Users\zaina\Documents\AI\final_features.csv", index=False, mode='a', header=False)

print("Feature engineering done")
