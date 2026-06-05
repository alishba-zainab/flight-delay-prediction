import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# ===============================
# 1️⃣ Load dataset
# ===============================
df = pd.read_csv("final_features.csv")

# ===============================
# 2️⃣ Remove non-predictive & leakage-prone columns
# ===============================
FORBIDDEN_COLUMNS = [
    "flight_number",      # identifier
    "dep_delay",
    "arr_delay",
    "taxi_in",
    "taxi_out",
    "air_time",
    "wheels_on",
    "wheels_off",
    "actual_departure",
    "actual_arrival"
]

df = df.drop(columns=FORBIDDEN_COLUMNS, errors="ignore")

# ===============================
# 3️⃣ Separate features and target
# ===============================
X = df.drop(columns=["delay"])
y = df["delay"]

# ===============================
# 4️⃣ Handle missing values
# ===============================
# Numeric columns
for col in X.select_dtypes(include=["int64", "float64"]).columns:
    X[col] = X[col].fillna(X[col].mean())

# Categorical columns
for col in X.select_dtypes(include=["object"]).columns:
    X[col] = X[col].fillna(X[col].mode()[0])
    X[col] = pd.factorize(X[col])[0]

# ===============================
# 5️⃣ Train-test split (same for all models)
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"Training rows: {len(X_train)}, Testing rows: {len(X_test)}")

# ===============================
# 6️⃣ Train Random Forest
# ===============================
rf_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

# ===============================
# 7️⃣ Evaluation
# ===============================
y_pred = rf_model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\n📊 Random Forest Classification Results:")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1-score:  {f1:.4f}")
print("Confusion Matrix:")
print(cm)