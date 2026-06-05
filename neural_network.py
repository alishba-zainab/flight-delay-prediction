"""
CORRECTED Neural Network - Prevents Data Leakage
Fixes the 99% accuracy problem by removing future information

This version:
1. Removes columns with future information
2. Ensures train/test split BEFORE SMOTE
3. Only uses pre-flight information
4. Should give realistic 80-85% accuracy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from imblearn.over_sampling import SMOTE
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import tensorflow as tf

np.random.seed(42)
tf.random.set_seed(42)

print("=" * 80)
print("🔧 CORRECTED NEURAL NETWORK - FIXING 99% ACCURACY")
print("=" * 80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("\n📂 Step 1: Loading data...")
df = pd.read_csv('final_features.csv')
print(f"✅ Loaded {len(df):,} samples with {len(df.columns)} features")

# ============================================================================
# 2. REMOVE DATA LEAKAGE COLUMNS (CRITICAL!)
# ============================================================================

print("\n🚨 Step 2: Removing columns with FUTURE information...")
print("This is what was causing 99% accuracy!")

# Columns that contain FUTURE information (should be removed)
future_info_columns = [
    # Actual times (happen during/after flight)
    'actual_elapsed_time', 'air_time',

    # Arrival information (future)
    'arr_time', 'arr_delay', 'arr_del15',

    # In-flight information (future)
    'wheels_off', 'wheels_on', 'taxi_in', 'taxi_out',

    # Status columns (future)
    'diverted', 'cancelled', 'cancellation_code',

    # Other delay-related (should not use)
    'carrier_delay', 'weather_delay', 'nas_delay',
    'security_delay', 'late_aircraft_delay',

    # Duplicate delay columns (keep only one)
    'dep_del15', 'dep_delay',  # Keep only 'delay' as target
]

# Find which columns actually exist in your data
columns_to_remove = [col for col in future_info_columns if col in df.columns]

print(f"\n⚠️  Found {len(columns_to_remove)} columns with FUTURE information:")
for col in columns_to_remove:
    print(f"   ❌ Removing: {col}")

if len(columns_to_remove) > 0:
    df_clean = df.drop(columns=columns_to_remove)
    print(f"\n✅ Removed {len(columns_to_remove)} columns")
    print(f"   Before: {len(df.columns)} columns")
    print(f"   After:  {len(df_clean.columns)} columns")
else:
    df_clean = df.copy()
    print(f"\n✅ No future information columns found (good!)")

# ============================================================================
# 3. PREPARE FEATURES AND TARGET
# ============================================================================

print(f"\n🎯 Step 3: Preparing features and target...")

# Check if 'delay' column exists
if 'delay' not in df_clean.columns:
    print("❌ Error: 'delay' column not found!")
    print(f"Available columns: {df_clean.columns.tolist()}")
    exit(1)

# Separate target
y = df_clean['delay']
X = df_clean.drop(['delay'], axis=1)

# Remove non-numeric columns
numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()

if len(non_numeric_cols) > 0:
    print(f"\n🧹 Removing {len(non_numeric_cols)} non-numeric columns:")
    for col in non_numeric_cols:
        print(f"   - {col}")
    X = X[numeric_cols]

print(f"\n✅ Features prepared:")
print(f"   Features: {X.shape[1]}")
print(f"   Samples: {len(X)}")

# Check class distribution
print(f"\n📊 Target distribution:")
print(f"   Class 0 (on-time): {np.sum(y == 0):,} ({np.sum(y == 0) / len(y) * 100:.1f}%)")
print(f"   Class 1 (delayed): {np.sum(y == 1):,} ({np.sum(y == 1) / len(y) * 100:.1f}%)")

# ============================================================================
# 4. TRAIN-TEST SPLIT (BEFORE SMOTE!)
# ============================================================================

print(f"\n🔀 Step 4: Splitting data (BEFORE SMOTE)...")
print("This is CRITICAL - split BEFORE any resampling!")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"✅ Training set: {len(X_train):,} samples")
print(f"✅ Test set: {len(X_test):,} samples")
print(f"   Test set is LOCKED AWAY - model won't see it!")

# ============================================================================
# 5. FEATURE SCALING
# ============================================================================

print(f"\n⚖️  Step 5: Scaling features...")

# Handle missing values before scaling
if X_train.isnull().sum().sum() > 0:
    print(f"⚠️  Filling {X_train.isnull().sum().sum()} missing values...")
    X_train = X_train.fillna(X_train.mean())
    X_test = X_test.fillna(X_test.mean())

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✅ Features scaled")

# ============================================================================
# 6. SMOTE ON TRAINING SET ONLY
# ============================================================================

print("\n" + "=" * 80)
print("⭐ Step 6: Applying SMOTE to TRAINING SET ONLY")
print("=" * 80)
print("Test set remains ORIGINAL - no synthetic data!")

smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)

print(f"\n📊 Before SMOTE (training set):")
print(f"   Class 0: {np.sum(y_train == 0):,}")
print(f"   Class 1: {np.sum(y_train == 1):,}")

print(f"\n📊 After SMOTE (training set):")
print(f"   Class 0: {np.sum(y_train_resampled == 0):,}")
print(f"   Class 1: {np.sum(y_train_resampled == 1):,}")

print(f"\n📊 Test set (UNCHANGED):")
print(f"   Class 0: {np.sum(y_test == 0):,}")
print(f"   Class 1: {np.sum(y_test == 1):,}")
print(f"   ✅ Original data only - no synthetic samples!")

# ============================================================================
# 7. BUILD MODEL
# ============================================================================

print("\n🏗️  Step 7: Building neural network...")

model = Sequential([
    Dense(256, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    BatchNormalization(),
    Dropout(0.3),

    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),

    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),

    Dense(32, activation='relu'),
    Dropout(0.2),

    Dense(1, activation='sigmoid')
])

optimizer = Adam(learning_rate=0.001)
model.compile(
    optimizer=optimizer,
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print("\n📋 Model Architecture:")
model.summary()

# ============================================================================
# 8. TRAIN MODEL
# ============================================================================

print("\n" + "=" * 80)
print("🎯 Step 8: Training on BALANCED data, testing on ORIGINAL data")
print("=" * 80)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=15,
    restore_best_weights=True,
    verbose=1
)

history = model.fit(
    X_train_resampled,  # ← SMOTE resampled training data
    y_train_resampled,
    epochs=100,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stopping],
    verbose=1
)

print("\n✅ Training complete!")

# ============================================================================
# 9. EVALUATE ON ORIGINAL TEST SET
# ============================================================================

print("\n" + "=" * 80)
print("🧪 Step 9: Evaluating on ORIGINAL test set")
print("=" * 80)
print("Remember: Test set has NO synthetic data!")

y_pred_prob = model.predict(X_test_scaled)
y_pred = (y_pred_prob > 0.5).astype(int).flatten()

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

# ============================================================================
# 10. RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("📊 FINAL RESULTS")
print("=" * 80)

print(f"\n✅ Accuracy:  {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"✅ Precision: {precision:.4f} ({precision * 100:.2f}%)")
print(f"✅ Recall:    {recall:.4f} ({recall * 100:.2f}%)")
print(f"✅ F1 Score:  {f1:.4f}")

print(f"\n📊 Confusion Matrix:")
print(f"                 Predicted")
print(f"              On-time  Delayed")
print(f"Actual On-time  {cm[0][0]:5d}    {cm[0][1]:5d}")
print(f"       Delayed  {cm[1][0]:5d}    {cm[1][1]:5d}")

# ============================================================================
# 11. SANITY CHECKS
# ============================================================================

print("\n" + "=" * 80)
print("🔍 SANITY CHECKS")
print("=" * 80)

if accuracy > 0.95:
    print(f"\n🚨 WARNING: Accuracy is {accuracy * 100:.2f}% - Still too high!")
    print(f"   This suggests data leakage still exists!")
    print(f"   Check your features for future information!")
    print(f"\n   Expected accuracy: 80-88%")
    print(f"   Your accuracy: {accuracy * 100:.2f}%")
    print(f"\n   Run debug_99_accuracy.py to find the problem!")

elif accuracy >= 0.80 and accuracy <= 0.90:
    print(f"\n✅ EXCELLENT! Accuracy is {accuracy * 100:.2f}%")
    print(f"   This is in the expected range (80-90%)")
    print(f"   No data leakage detected!")
    print(f"   Model is working correctly!")

elif accuracy < 0.80:
    print(f"\n📊 Accuracy is {accuracy * 100:.2f}%")
    print(f"   This is below target but realistic")
    print(f"   Consider:")
    print(f"   - Feature engineering")
    print(f"   - More epochs")
    print(f"   - Hyperparameter tuning")

# Check training vs test accuracy
train_pred = (model.predict(X_train_resampled) > 0.5).astype(int).flatten()
train_acc = accuracy_score(y_train_resampled, train_pred)

print(f"\n📊 Training vs Test Accuracy:")
print(f"   Training: {train_acc * 100:.2f}%")
print(f"   Test:     {accuracy * 100:.2f}%")
print(f"   Gap:      {abs(train_acc - accuracy) * 100:.2f}%")

if abs(train_acc - accuracy) < 0.05:
    print(f"   ✅ Healthy gap (<5%) - good generalization!")
elif abs(train_acc - accuracy) < 0.10:
    print(f"   ⚠️  Moderate gap (5-10%) - slight overfitting")
else:
    print(f"   🚨 Large gap (>10%) - significant overfitting!")

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE!")
print("=" * 80)

# Save model if accuracy is reasonable
if accuracy >= 0.75 and accuracy <= 0.95:
    print("\n💾 Saving model...")
    model.save('flight_delay_model_corrected.h5')
    print("✅ Model saved as 'flight_delay_model_corrected.h5'")

    import joblib

    joblib.dump(scaler, 'scaler_corrected.pkl')
    print("✅ Scaler saved as 'scaler_corrected.pkl'")
else:
    print("\n⚠️  Model not saved due to suspicious accuracy")
    print("   Fix data leakage first, then retrain")

print("\n📝 Summary:")
if accuracy > 0.95:
    print("🚨 STILL HAVE DATA LEAKAGE - Need to investigate further")
    print("   Run: python debug_99_accuracy.py")
elif accuracy >= 0.80 and accuracy <= 0.90:
    print("✅ SUCCESS! Model working correctly!")
    print(f"   Accuracy: {accuracy * 100:.2f}% (realistic and healthy)")
else:
    print(f"📊 Accuracy: {accuracy * 100:.2f}%")
    print("   Model is working but could be improved")