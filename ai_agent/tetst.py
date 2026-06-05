# test_api.py
from flight_api import get_flight_data
import json

result = get_flight_data("CZ8484")
print(json.dumps(result, indent=2))