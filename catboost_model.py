import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from catboost import CatBoostClassifier

# -----------------------------
# 1️⃣ Load dataset
# -----------------------------
df = pd.read_csv("final_features.csv")


# -----------------------------
# 2️⃣ Remove data leakage columns (VERY IMPORTANT)
# -----------------------------
leakage_cols = [
    'arr_delay',
    'dep_delay',
    'taxi_in',
    'taxi_out',
    'wheels_on',
    'wheels_off',
    'air_time'
]

df = df.drop(columns=[c for c in leakage_cols if c in df.columns])

# -----------------------------
# 3️⃣ Separate identifiers, features, and target
# -----------------------------
flight_numbers = df['flight_number']          # keep only for tracking
X = df.drop(columns=['delay', 'flight_number'])
y = df['delay']

# -----------------------------
# 4️⃣ Handle missing values
# -----------------------------
for col in X.select_dtypes(include=['float64', 'int64']).columns:
    X[col] = X[col].fillna(X[col].mean())

for col in X.select_dtypes(include=['object']).columns:
    X[col] = X[col].fillna("Unknown")

# -----------------------------
# 5️⃣ Encode categorical columns
# -----------------------------
for col in X.select_dtypes(include=['object']).columns:
    X[col] = pd.factorize(X[col])[0]

# -----------------------------
# 6️⃣ Train / Test split
# -----------------------------
X_train, X_test, y_train, y_test, train_flights, test_flights = train_test_split(
    X,
    y,
    flight_numbers,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

# -----------------------------
# 7️⃣ Train CatBoost model
# -----------------------------
model = CatBoostClassifier(
    random_state=42,
    iterations=500,
    learning_rate=0.1,
    depth=6,
    loss_function="Logloss",
    verbose=100,
    allow_writing_files=False
)

model.fit(X_train, y_train)

# -----------------------------
# 9️⃣ Evaluate model
# -----------------------------
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\n📊 CatBoost Evaluation Results")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1-score:  {f1:.4f}")
print("Confusion Matrix:")
print(cm)

# -----------------------------
# 🔟 Map predictions to flight numbers (for verification only)
# -----------------------------
results = pd.DataFrame({
    "flight_number": test_flights.values,
    "predicted_delay": y_pred,
    "actual_delay": y_test.values
})

print("\nFirst 5 test predictions:")
print(results.head())
