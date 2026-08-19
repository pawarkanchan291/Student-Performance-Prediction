import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# ==========================================
# PROJECT PATH
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ==========================================
# DATASET PATH
# ==========================================

DATASET_PATH = os.path.join(
    BASE_DIR,
    "student_performance.csv"
)


# ==========================================
# MODEL DIRECTORY
# ==========================================

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


MODEL_PATH = os.path.join(
    MODEL_DIR,
    "student_performance_model.pkl"
)


# ==========================================
# CREATE MODEL FOLDER
# ==========================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ==========================================
# LOAD DATASET
# ==========================================

print("======================================")
print("Student Performance Prediction")
print("======================================")

print("\nLoading Dataset...")


data = pd.read_csv(
    DATASET_PATH
)


print("Dataset Loaded Successfully!")


# ==========================================
# DATASET INFORMATION
# ==========================================

print("\nDataset Shape:")
print(data.shape)


print("\nDataset Columns:")
print(data.columns.tolist())


# ==========================================
# FEATURES
# ==========================================

features = [
    "study_hours",
    "attendance",
    "sleep_hours",
    "internet_usage",
    "assignments_completed",
    "previous_score"
]


# ==========================================
# CHECK FEATURES
# ==========================================

missing_columns = [
    column
    for column in features
    if column not in data.columns
]


if missing_columns:

    print("\n======================================")
    print("ERROR: Missing Columns")
    print("======================================")

    print(
        "Missing columns:",
        missing_columns
    )

    raise SystemExit


# ==========================================
# CONVERT DATA TO NUMERIC
# ==========================================

for column in features:

    data[column] = pd.to_numeric(
        data[column],
        errors="coerce"
    )


# ==========================================
# REMOVE EMPTY ROWS
# ==========================================

data = data.dropna(
    subset=features
)


# ==========================================
# INPUT FEATURES
# ==========================================

X = data[features]


# ==========================================
# CREATE PERFORMANCE SCORE
# ==========================================

data["performance_score"] = (

    (data["study_hours"] / 10) * 20

    + (data["attendance"] / 100) * 20

    + (data["sleep_hours"] / 10) * 10

    + (1 - data["internet_usage"] / 10) * 10

    + (data["assignments_completed"] / 15) * 15

    + (data["previous_score"] / 100) * 25

)


# ==========================================
# LIMIT SCORE 0-100
# ==========================================

data["performance_score"] = data[
    "performance_score"
].clip(0, 100)


# ==========================================
# TARGET CREATED INTERNALLY
# ==========================================

y = data[
    "performance_score"
]


# ==========================================
# DISPLAY INFORMATION
# ==========================================

print("\n======================================")
print("MODEL FEATURES")
print("======================================")


for feature in features:

    print("-", feature)


print("\nPerformance score generated internally.")


# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42
)


print("\n======================================")
print("DATA SPLIT")
print("======================================")


print(
    "Training Records:",
    len(X_train)
)


print(
    "Testing Records:",
    len(X_test)
)


# ==========================================
# RANDOM FOREST
# ==========================================

model = RandomForestRegressor(

    n_estimators=100,

    random_state=42
)


# ==========================================
# TRAIN MODEL
# ==========================================

print("\n======================================")
print("Training Model...")
print("======================================")


model.fit(
    X_train,
    y_train
)


print(
    "Model Training Completed!"
)


# ==========================================
# PREDICTION
# ==========================================

predictions = model.predict(
    X_test
)


# ==========================================
# EVALUATION
# ==========================================

mae = mean_absolute_error(
    y_test,
    predictions
)


r2 = r2_score(
    y_test,
    predictions
)


print("\n======================================")
print("MODEL PERFORMANCE")
print("======================================")


print(
    "Mean Absolute Error:",
    round(mae, 2)
)


print(
    "R2 Score:",
    round(r2, 2)
)


print(
    "R2 Score (%):",
    round(r2 * 100, 2),
    "%"
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    MODEL_PATH
)


print("\n======================================")
print("MODEL SAVED SUCCESSFULLY")
print("======================================")


print(
    "Model Location:",
    MODEL_PATH
)


print("\n======================================")
print("TRAINING COMPLETED")
print("======================================")