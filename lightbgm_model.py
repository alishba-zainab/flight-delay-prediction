import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import lightgbm as lgb

# Load dataset
df = pd.read_csv("final_features.csv")

# ❌ Drop identifier
df = df.drop(columns=['flight_number'], errors='ignore')

# ❌ Drop POST-EVENT / LEAKAGE columns
LEAKAGE_COLS = [
    'dep_delay',
    'arr_delay',
    'actual_arrival_delay',
    'taxi_out_delay',
    'taxi_in_delay'
]
df = df.drop(columns=LEAKAGE_COLS, errors='ignore')

# Encode categorical columns
for col in df.select_dtypes(include=['object']).columns:
    df[col] = pd.factorize(df[col])[0]

# Fill missing values
for col in df.select_dtypes(include=['float64','int64']).columns:
    df[col] = df[col].fillna(df[col].mean())

# Split features & target
X = df.drop(columns=['delay'])
y = df['delay']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train LightGBM
model = lgb.LGBMClassifier(random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
print("📊 LightGBM Classification Results")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1:", f1_score(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
