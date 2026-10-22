# ============================================================
# STUDENT PERFORMANCE PREDICTION SYSTEM
# TRAIN TWO SEPARATE ML MODELS
# ============================================================

import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# FILE PATHS
# ============================================================

CSV_PATH = os.path.join(
    BASE_DIR,
    "student_performance.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

STUDENT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "student_performance_model.pkl"
)

TEACHER_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "teacher_academic_model.pkl"
)


# ============================================================
# CREATE MODELS DIRECTORY
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# LOAD CSV
# ============================================================

print("\n================================================")
print("LOADING DATASET")
print("================================================")

if not os.path.exists(CSV_PATH):

    raise FileNotFoundError(
        "\nstudent_performance.csv not found.\n"
        "Please keep the CSV file in the same folder "
        "as train_model.py."
    )


df = pd.read_csv(CSV_PATH)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
)


print("\nDataset loaded successfully.")

print("\nAvailable Columns:")

for column in df.columns:

    print(
        " -",
        column
    )


print(
    "\nDataset Shape:",
    df.shape
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [

    "study_hours",
    "attendance",
    "sleep_hours",
    "internet_usage",

    "assignments_completed",
    "previous_score"

]


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

missing_columns = [

    column
    for column in required_columns
    if column not in df.columns

]


if missing_columns:

    raise ValueError(
        "\nThe following required columns "
        "are missing from CSV:\n"
        + str(missing_columns)
    )


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

print("\n================================================")
print("CONVERTING NUMERIC DATA")
print("================================================")


for column in required_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# REMOVE EMPTY / INVALID ROWS
# ============================================================

before_rows = len(df)


df = df.dropna(
    subset=required_columns
)


after_rows = len(df)


print(
    "\nRows before cleaning:",
    before_rows
)

print(
    "Rows after cleaning:",
    after_rows
)


# ============================================================
# CHECK DATA
# ============================================================

if len(df) < 10:

    raise ValueError(
        "\nNot enough valid data rows "
        "for machine learning training."
    )


# ============================================================
# ============================================================
# STUDENT PERSONAL MODEL
# ============================================================
#
# INPUT FEATURES:
#
# 1. study_hours
# 2. attendance
# 3. sleep_hours
# 4. internet_usage
#
# TOTAL FEATURES = 4
#
# TARGET:
# previous_score
#
# ============================================================
# ============================================================


print("\n")
print("================================================")
print("TRAINING STUDENT PERSONAL MODEL")
print("================================================")


student_features = [

    "study_hours",
    "attendance",
    "sleep_hours",
    "internet_usage"

]


student_target = "previous_score"


X_student = df[
    student_features
]

y_student = df[
    student_target
]


print("\nStudent Features:")

for feature in student_features:

    print(
        " -",
        feature
    )


print(
    "\nStudent Feature Count:",
    len(student_features)
)

print(
    "Student Target:",
    student_target
)


# ============================================================
# STUDENT TRAIN / TEST SPLIT
# ============================================================

X_student_train, X_student_test, \
y_student_train, y_student_test = train_test_split(

    X_student,
    y_student,

    test_size=0.20,

    random_state=42

)


# ============================================================
# CREATE STUDENT MODEL
# ============================================================

student_model = RandomForestRegressor(

    n_estimators=200,

    max_depth=10,

    min_samples_split=2,

    min_samples_leaf=1,

    random_state=42

)


# ============================================================
# TRAIN STUDENT MODEL
# ============================================================

print(
    "\nTraining Student Model..."
)


student_model.fit(

    X_student_train,

    y_student_train

)


print(
    "Student Model Training Completed."
)


# ============================================================
# STUDENT PREDICTION
# ============================================================

student_predictions = student_model.predict(

    X_student_test

)


# ============================================================
# STUDENT MODEL EVALUATION
# ============================================================

student_mae = mean_absolute_error(

    y_student_test,

    student_predictions

)


student_r2 = r2_score(

    y_student_test,

    student_predictions

)


print("\nStudent Model Results:")

print(
    "MAE:",
    round(student_mae, 2)
)

print(
    "R2 Score:",
    round(student_r2, 4)
)


# ============================================================
# SAVE STUDENT MODEL
# ============================================================

joblib.dump(

    student_model,

    STUDENT_MODEL_PATH

)


print(
    "\nStudent Model Saved:"
)

print(
    STUDENT_MODEL_PATH
)


# ============================================================
# VERIFY STUDENT MODEL
# ============================================================

student_loaded = joblib.load(

    STUDENT_MODEL_PATH

)


print(
    "\nStudent Model Feature Count:",
    student_loaded.n_features_in_
)


if student_loaded.n_features_in_ != 4:

    raise ValueError(
        "\nERROR:\n"
        "Student model must contain exactly 4 features."
    )


print(
    "Student Model Verification: PASSED"
)


# ============================================================
# ============================================================
# TEACHER ACADEMIC MODEL
# ============================================================
#
# INPUT FEATURES:
#
# 1. assignments_completed
# 2. previous_score
#
# TOTAL FEATURES = 2
#
# TARGET:
# previous_score
#
# ============================================================
# ============================================================


print("\n")
print("================================================")
print("TRAINING TEACHER ACADEMIC MODEL")
print("================================================")


teacher_features = [

    "assignments_completed",
    "previous_score"

]


# ------------------------------------------------------------
# IMPORTANT
# ------------------------------------------------------------
#
# Since your CSV does NOT contain exam_score,
# we need a target for the teacher model.
#
# We cannot use previous_score itself as both
# input AND target because that would cause
# data leakage.
#
# Therefore we create an academic target
# using the available academic information.
#
# ------------------------------------------------------------


print("\nCreating Teacher Academic Target...")


# ============================================================
# CREATE ACADEMIC TARGET
# ============================================================
#
# Academic Target Formula:
#
# Previous Score contributes 70%
# Assignments contributes 30%
#
# Assignments are normalized to 100.
#
# ============================================================


max_assignments = df[
    "assignments_completed"
].max()


if max_assignments <= 0:

    max_assignments = 1


assignment_percentage = (

    df["assignments_completed"]
    / max_assignments

) * 100


df["teacher_target"] = (

    (
        df["previous_score"] * 0.70
    )

    +

    (
        assignment_percentage * 0.30
    )

)


# ============================================================
# LIMIT TARGET BETWEEN 0 AND 100
# ============================================================

df["teacher_target"] = (

    df["teacher_target"]
    .clip(0, 100)

)


teacher_target = "teacher_target"


# ============================================================
# CREATE TEACHER DATA
# ============================================================

X_teacher = df[
    teacher_features
]

y_teacher = df[
    teacher_target
]


print("\nTeacher Features:")

for feature in teacher_features:

    print(
        " -",
        feature
    )


print(
    "\nTeacher Feature Count:",
    len(teacher_features)
)

print(
    "Teacher Target:",
    teacher_target
)


# ============================================================
# TEACHER TRAIN / TEST SPLIT
# ============================================================

X_teacher_train, X_teacher_test, \
y_teacher_train, y_teacher_test = train_test_split(

    X_teacher,
    y_teacher,

    test_size=0.20,

    random_state=42

)


# ============================================================
# CREATE TEACHER MODEL
# ============================================================

teacher_model = RandomForestRegressor(

    n_estimators=200,

    max_depth=10,

    min_samples_split=2,

    min_samples_leaf=1,

    random_state=42

)


# ============================================================
# TRAIN TEACHER MODEL
# ============================================================

print(
    "\nTraining Teacher Model..."
)


teacher_model.fit(

    X_teacher_train,

    y_teacher_train

)


print(
    "Teacher Model Training Completed."
)


# ============================================================
# TEACHER PREDICTION
# ============================================================

teacher_predictions = teacher_model.predict(

    X_teacher_test

)


# ============================================================
# TEACHER MODEL EVALUATION
# ============================================================

teacher_mae = mean_absolute_error(

    y_teacher_test,

    teacher_predictions

)


teacher_r2 = r2_score(

    y_teacher_test,

    teacher_predictions

)


print("\nTeacher Model Results:")

print(
    "MAE:",
    round(teacher_mae, 2)
)

print(
    "R2 Score:",
    round(teacher_r2, 4)
)


# ============================================================
# SAVE TEACHER MODEL
# ============================================================

joblib.dump(

    teacher_model,

    TEACHER_MODEL_PATH

)


print(
    "\nTeacher Model Saved:"
)

print(
    TEACHER_MODEL_PATH
)


# ============================================================
# VERIFY TEACHER MODEL
# ============================================================

teacher_loaded = joblib.load(

    TEACHER_MODEL_PATH

)


print(
    "\nTeacher Model Feature Count:",
    teacher_loaded.n_features_in_
)


if teacher_loaded.n_features_in_ != 2:

    raise ValueError(
        "\nERROR:\n"
        "Teacher model must contain exactly 2 features."
    )


print(
    "Teacher Model Verification: PASSED"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("======================================================")
print("           MODEL TRAINING COMPLETED")
print("======================================================")


print("\nSTUDENT MODEL")

print(
    "Features:",
    student_features
)

print(
    "Feature Count:",
    student_loaded.n_features_in_
)

print(
    "Target:",
    student_target
)

print(
    "File:",
    STUDENT_MODEL_PATH
)


print("\nTEACHER MODEL")

print(
    "Features:",
    teacher_features
)

print(
    "Feature Count:",
    teacher_loaded.n_features_in_
)

print(
    "Target:",
    teacher_target
)

print(
    "File:",
    TEACHER_MODEL_PATH
)


print("\n======================================================")
print("Student Model : 4 Features")
print("Teacher Model : 2 Features")
print("======================================================")

print(
    "\nBoth .pkl files have been created successfully."
)