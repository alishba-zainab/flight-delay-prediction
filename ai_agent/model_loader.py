import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

MODEL_PATH = os.path.join(AI_DIR, "xgboost_delay.pkl")
FEATURE_PATH = os.path.join(AI_DIR, "feature_list.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ Model file not found")

    if not os.path.exists(FEATURE_PATH):
        raise FileNotFoundError("❌ Feature list file not found")

    model = joblib.load(MODEL_PATH)
    feature_list = joblib.load(FEATURE_PATH)

    print("✅ Model & feature list loaded successfully")
    return model, feature_list


# 🔹 Test loader
if __name__ == "__main__":
    load_model()
