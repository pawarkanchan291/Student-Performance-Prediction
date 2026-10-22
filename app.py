from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import os
import pandas as pd


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "student_performance_secret_key_2026"


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "student_performance_db"
}


# =========================================================
# ADMIN LOGIN
# =========================================================

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"


# =========================================================
# TEACHER LOGIN
# =========================================================

TEACHER_EMAIL = "teacher@gmail.com"
TEACHER_PASSWORD = "teacher123"


# =========================================================
# MODEL PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STUDENT_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "student_performance_model.pkl"
)

TEACHER_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "teacher_academic_model.pkl"
)


# =========================================================
# LOAD STUDENT MODEL
# =========================================================

student_model = None

try:

    if os.path.exists(STUDENT_MODEL_PATH):

        student_model = joblib.load(
            STUDENT_MODEL_PATH
        )

        print("========================================")
        print("STUDENT MODEL LOADED SUCCESSFULLY")
        print("========================================")

    else:

        print("STUDENT MODEL FILE NOT FOUND:")
        print(STUDENT_MODEL_PATH)

except Exception as e:

    print("========================================")
    print("STUDENT MODEL LOADING ERROR")
    print(e)
    print("========================================")


# =========================================================
# LOAD TEACHER MODEL
# =========================================================

teacher_model = None

try:

    if os.path.exists(TEACHER_MODEL_PATH):

        teacher_model = joblib.load(
            TEACHER_MODEL_PATH
        )

        print("========================================")
        print("TEACHER MODEL LOADED SUCCESSFULLY")
        print("========================================")

    else:

        print("TEACHER MODEL FILE NOT FOUND:")
        print(TEACHER_MODEL_PATH)

except Exception as e:

    print("========================================")
    print("TEACHER MODEL LOADING ERROR")
    print(e)
    print("========================================")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    try:

        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        if connection.is_connected():
            return connection

    except Error as e:

        print("Database Connection Error:", e)

    return None


# =========================================================
# STUDENT DATABASE CONNECTION
# =========================================================

def get_student_db_connection():

    try:

        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        if connection.is_connected():
            return connection

    except Error as e:

        print("Student Database Connection Error:", e)

    return None


# =========================================================
# TEACHER DATABASE CONNECTION
# =========================================================

def get_teacher_db_connection():

    try:

        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        if connection.is_connected():
            return connection

    except Error as e:

        print("Teacher Database Connection Error:", e)

    return None


# =========================================================
# DATABASE SCHEMA
# =========================================================

def ensure_database_schema():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        if connection is None:

            print("Database schema check failed.")
            return

        cursor = connection.cursor()


        # =================================================
        # USERS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # TEACHERS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # ADMIN TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # PREDICTIONS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,

                user_id INT NULL,

                prediction_type
                    VARCHAR(20)
                    NOT NULL
                    DEFAULT 'STUDENT',

                student_id VARCHAR(100) NULL,

                student_name VARCHAR(150) NULL,

                study_hours FLOAT NULL,

                attendance FLOAT NULL,

                sleep_hours FLOAT NULL,

                internet_usage FLOAT NULL,

                assignments_completed FLOAT NULL,

                previous_score FLOAT NULL,

                predicted_score FLOAT NULL,

                performance VARCHAR(30) NULL,

                prediction_date
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # DEDICATED STUDENT PREDICTIONS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                student_id VARCHAR(100) NOT NULL,
                student_name VARCHAR(150) NOT NULL,
                study_hours FLOAT NOT NULL,
                attendance FLOAT NOT NULL,
                sleep_hours FLOAT NOT NULL,
                internet_usage FLOAT NOT NULL,
                predicted_score FLOAT NOT NULL,
                performance VARCHAR(30) NOT NULL,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # DEDICATED TEACHER PREDICTIONS TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                student_id VARCHAR(100) NOT NULL,
                student_name VARCHAR(150) NOT NULL,
                assignments_completed FLOAT NOT NULL,
                previous_score FLOAT NOT NULL,
                predicted_score FLOAT NOT NULL,
                performance VARCHAR(30) NOT NULL,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # ADD MISSING PREDICTION COLUMNS
        # =================================================

        required_columns = {

            "user_id":
                "INT NULL",

            "prediction_type":
                "VARCHAR(20) NOT NULL DEFAULT 'STUDENT'",

            "student_id":
                "VARCHAR(100) NULL",

            "student_name":
                "VARCHAR(150) NULL",

            "study_hours":
                "FLOAT NULL",

            "attendance":
                "FLOAT NULL",

            "sleep_hours":
                "FLOAT NULL",

            "internet_usage":
                "FLOAT NULL",

            "assignments_completed":
                "FLOAT NULL",

            "previous_score":
                "FLOAT NULL",

            "predicted_score":
                "FLOAT NULL",

            "performance":
                "VARCHAR(30) NULL",

            "prediction_date":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }


        for column_name, column_definition in required_columns.items():

            cursor.execute(
                "SHOW COLUMNS FROM predictions LIKE %s",
                (column_name,)
            )

            exists = cursor.fetchone()

            if exists is None:

                try:

                    cursor.execute(
                        f"""
                        ALTER TABLE predictions
                        ADD COLUMN `{column_name}`
                        {column_definition}
                        """
                    )

                except Error as e:

                    print(
                        f"Could not add column {column_name}:",
                        e
                    )


        # =================================================
        # FEEDBACK TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,

                user_id INT NULL,

                name VARCHAR(100) NOT NULL,

                email VARCHAR(150) NOT NULL,

                rating INT NOT NULL,

                feedback TEXT NOT NULL,

                suggestion TEXT NULL,

                created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # =================================================
        # CONTACT TABLE
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,

                user_id INT NULL,

                name VARCHAR(100) NOT NULL,

                email VARCHAR(150) NOT NULL,

                subject VARCHAR(200) NOT NULL,

                message TEXT NOT NULL,

                created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)


        connection.commit()

        print("========================================")
        print("DATABASE SCHEMA READY")
        print("========================================")


    except Error as e:

        if connection:
            connection.rollback()

        print(
            "Database Schema Error:",
            e
        )


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# CREATE DEFAULT ADMIN
# =========================================================

def ensure_default_admin():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        if connection is None:
            return

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id
            FROM admin
            WHERE email = %s
            LIMIT 1
            """,
            (ADMIN_EMAIL,)
        )

        admin = cursor.fetchone()

        hashed_password = generate_password_hash(
            ADMIN_PASSWORD
        )


        if admin is None:

            cursor.execute(
                """
                INSERT INTO admin
                (
                    name,
                    email,
                    password
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    "Administrator",
                    ADMIN_EMAIL,
                    hashed_password
                )
            )

            connection.commit()

            print("Default admin account created.")


        else:

            cursor.execute(
                """
                UPDATE admin
                SET
                    name = %s,
                    password = %s
                WHERE email = %s
                """,
                (
                    "Administrator",
                    hashed_password,
                    ADMIN_EMAIL
                )
            )

            connection.commit()

            print("Default admin password updated.")


    except Error as e:

        if connection:
            connection.rollback()

        print(
            "Default Admin Error:",
            e
        )


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# CREATE DEFAULT TEACHER
# =========================================================

def ensure_default_teacher():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        if connection is None:
            return

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id
            FROM teachers
            WHERE email = %s
            LIMIT 1
            """,
            (TEACHER_EMAIL,)
        )

        teacher = cursor.fetchone()

        hashed_password = generate_password_hash(
            TEACHER_PASSWORD
        )


        if teacher is None:

            cursor.execute(
                """
                INSERT INTO teachers
                (
                    email,
                    password
                )
                VALUES
                (
                    %s,
                    %s
                )
                """,
                (
                    TEACHER_EMAIL,
                    hashed_password
                )
            )

            connection.commit()

            print("Default teacher account created.")


        else:

            cursor.execute(
                """
                UPDATE teachers
                SET password = %s
                WHERE email = %s
                """,
                (
                    hashed_password,
                    TEACHER_EMAIL
                )
            )

            connection.commit()

            print("Default teacher password updated.")


    except Error as e:

        if connection:
            connection.rollback()

        print(
            "Default Teacher Error:",
            e
        )


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# MODEL VALIDATION
# =========================================================

def validate_loaded_models():

    if student_model is not None:

        if hasattr(
            student_model,
            "n_features_in_"
        ):

            print(
                "Student model features:",
                student_model.n_features_in_
            )

            if student_model.n_features_in_ != 4:

                print(
                    "WARNING: Student model should have 4 features."
                )

        if hasattr(
            student_model,
            "feature_names_in_"
        ):

            print(
                "Student model feature names:",
                list(
                    student_model.feature_names_in_
                )
            )

            print(
                "Expected:"
            )

            print(
                "study_hours, attendance, sleep_hours, internet_usage"
            )


    if teacher_model is not None:

        if hasattr(
            teacher_model,
            "n_features_in_"
        ):

            print(
                "Teacher model features:",
                teacher_model.n_features_in_
            )

            if teacher_model.n_features_in_ != 2:

                print(
                    "WARNING: Teacher model should have 2 features."
                )

        if hasattr(
            teacher_model,
            "feature_names_in_"
        ):

            print(
                "Teacher model feature names:",
                list(
                    teacher_model.feature_names_in_
                )
            )

            print(
                "Expected:"
            )

            print(
                "assignments_completed, previous_score"
            )


# =========================================================
# PERFORMANCE CATEGORY
# =========================================================

def get_performance(score):

    score = float(score)

    if score >= 80:
        return "Excellent"

    elif score >= 60:
        return "Good"

    elif score >= 40:
        return "Average"

    else:
        return "Poor"


# =========================================================
# MODEL PREDICTION HELPER
# =========================================================

def predict_with_feature_names(
    model,
    values,
    feature_names
):

    if model is None:

        raise ValueError(
            "Model is not loaded."
        )


    if hasattr(
        model,
        "feature_names_in_"
    ):

        model_feature_names = list(
            model.feature_names_in_
        )


        if len(model_feature_names) != len(
            feature_names
        ):

            raise ValueError(
                "Model feature count mismatch. "
                f"Expected {len(feature_names)} features, "
                f"but model has {len(model_feature_names)}."
            )


        input_data = pd.DataFrame(
            [values],
            columns=model_feature_names
        )


        return float(
            model.predict(input_data)[0]
        )


    input_data = [values]

    return float(
        model.predict(input_data)[0]
    )


# =========================================================
# LOGIN CHECKS
# =========================================================

def student_required():

    return "user_id" in session


def teacher_required():

    return "teacher_id" in session


def admin_required():

    return "admin_id" in session


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    if not student_required():

        return redirect("/login")

    return render_template(
        "index.html",
        user_name=session.get(
            "user_name",
            "Student"
        )
    )


# =========================================================
# STUDENT REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    if not name or not email or not password:

        flash(
            "Please fill all required fields.",
            "error"
        )

        return redirect("/register")


    if password != confirm_password:

        flash(
            "Passwords do not match.",
            "error"
        )

        return redirect("/register")


    if len(password) < 6:

        flash(
            "Password must contain at least 6 characters.",
            "error"
        )

        return redirect("/register")


    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect("/register")


    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing = cursor.fetchone()


        if existing:

            flash(
                "Email already registered.",
                "error"
            )

            return redirect("/login")


        hashed_password = generate_password_hash(
            password
        )


        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                hashed_password
            )
        )


        connection.commit()


        flash(
            "Student account created successfully.",
            "success"
        )

        return redirect("/login")


    except Error as e:

        connection.rollback()

        print(
            "Registration Error:",
            e
        )

        flash(
            "Registration failed.",
            "error"
        )

        return redirect("/register")


    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    if not email or not password:

        flash(
            "Please enter email and password.",
            "error"
        )

        return redirect("/login")


    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect("/login")


    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()


        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect("/login")


        try:

            valid = check_password_hash(
                user["password"],
                password
            )

        except Exception:

            valid = (
                password ==
                user["password"]
            )


        if not valid:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect("/login")


        session.clear()

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]


        flash(
            "Student login successful!",
            "success"
        )

        return redirect("/")


    except Error as e:

        print(
            "Student Login Error:",
            e
        )

        flash(
            "Login failed.",
            "error"
        )

        return redirect("/login")


    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# STUDENT LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect("/login")


# =========================================================
# STUDENT PREDICTION
# PERSONAL PERFORMANCE ONLY
# =========================================================

@app.route(
    "/predict",
    methods=["GET", "POST"]
)
def predict():

    if not student_required():

        flash(
            "Please login first.",
            "error"
        )

        return redirect("/login")


    if request.method == "GET":

        return render_template(
            "predict.html"
        )


    if student_model is None:

        flash(
            "Student ML model is not loaded.",
            "error"
        )

        return redirect("/predict")


    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    student_name = request.form.get(
        "student_name",
        ""
    ).strip()


    study_hours_text = request.form.get(
        "study_hours",
        ""
    ).strip()

    attendance_text = request.form.get(
        "attendance",
        ""
    ).strip()

    sleep_hours_text = request.form.get(
        "sleep_hours",
        ""
    ).strip()

    internet_usage_text = request.form.get(
        "internet_usage",
        ""
    ).strip()


    if not student_id or not student_name:

        flash(
            "Student ID and Student Name are required.",
            "error"
        )

        return redirect("/predict")


    if (
        not study_hours_text
        or not attendance_text
        or not sleep_hours_text
        or not internet_usage_text
    ):

        flash(
            "Please fill all personal performance fields.",
            "error"
        )

        return redirect("/predict")


    try:

        study_hours = float(
            study_hours_text
        )

        attendance = float(
            attendance_text
        )

        sleep_hours = float(
            sleep_hours_text
        )

        internet_usage = float(
            internet_usage_text
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            "Please enter valid numeric values.",
            "error"
        )

        return redirect("/predict")


    if not 0 <= study_hours <= 24:

        flash(
            "Study Hours must be between 0 and 24.",
            "error"
        )

        return redirect("/predict")


    if not 0 <= attendance <= 100:

        flash(
            "Attendance must be between 0 and 100.",
            "error"
        )

        return redirect("/predict")


    if not 0 <= sleep_hours <= 24:

        flash(
            "Sleep Hours must be between 0 and 24.",
            "error"
        )

        return redirect("/predict")


    if not 0 <= internet_usage <= 24:

        flash(
            "Internet Usage must be between 0 and 24.",
            "error"
        )

        return redirect("/predict")


    try:

        predicted_score = predict_with_feature_names(
            student_model,
            [
                study_hours,
                attendance,
                sleep_hours,
                internet_usage
            ],
            [
                "study_hours",
                "attendance",
                "sleep_hours",
                "internet_usage"
            ]
        )


        predicted_score = round(
            max(
                0,
                min(
                    100,
                    predicted_score
                )
            ),
            2
        )


        performance = get_performance(
            predicted_score
        )


    except Exception as e:

        print(
            "Student Prediction Error:",
            e
        )

        flash(
            "Student prediction failed. Please check that "
            "student_performance_model.pkl was trained with "
            "exactly 4 features.",
            "error"
        )

        return redirect("/predict")


    # =========================================================
    # SAVE STUDENT PERSONAL PREDICTION
    # =========================================================

    connection = get_student_db_connection()

    if connection is None:

        flash(
            "Student database connection failed.",
            "error"
        )

        return redirect("/predict")


    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO student_predictions
            (
                user_id,
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                predicted_score,
                performance
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                int(session["user_id"]),
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                predicted_score,
                performance
            )
        )

        if cursor.rowcount != 1:

            raise Error(
                "Student prediction INSERT did not create a record."
            )

        connection.commit()

        saved_student_prediction_id = cursor.lastrowid

        # -------------------------------------------------
        # COMPATIBILITY SAVE
        # Keep the existing predictions table populated so
        # the original Student Dashboard, History, Progress
        # and Reports routes continue to work unchanged.
        # The dedicated student_predictions table above remains
        # the separate Student prediction table.
        # -------------------------------------------------
        cursor.execute(
            """
            INSERT INTO predictions
            (
                user_id,
                prediction_type,
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                assignments_completed,
                previous_score,
                predicted_score,
                performance
            )
            VALUES
            (
                %s,
                'STUDENT',
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NULL,
                NULL,
                %s,
                %s
            )
            """,
            (
                int(session["user_id"]),
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                predicted_score,
                performance
            )
        )

        connection.commit()

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                student_id,
                student_name,
                predicted_score,
                performance
            FROM student_predictions
            WHERE id = %s
              AND user_id = %s
            LIMIT 1
            """,
            (
                saved_student_prediction_id,
                int(session["user_id"])
            )
        )

        saved_student_prediction = cursor.fetchone()

        if saved_student_prediction is None:

            raise Error(
                "Student prediction was not found after database commit."
            )


    except Error as e:

        if connection:
            connection.rollback()

        print(
            "Student Prediction DB Error:",
            e
        )

        flash(
            "Prediction was generated, but Student database saving failed.",
            "error"
        )

        return redirect("/predict")


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


    return render_template(
        "result.html",

        student_id=student_id,

        student_name=student_name,

        study_hours=study_hours,

        attendance=attendance,

        sleep_hours=sleep_hours,

        internet_usage=internet_usage,

        predicted_score=predicted_score,

        performance=performance
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not student_required():

        return redirect("/login")


    total = 0
    excellent = 0
    good = 0
    average = 0
    poor = 0


    connection = get_db_connection()


    if connection is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                """,
                (
                    session["user_id"],
                )
            )

            row = cursor.fetchone()

            if row:
                total = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                AND performance = 'Excellent'
                """,
                (
                    session["user_id"],
                )
            )

            row = cursor.fetchone()

            if row:
                excellent = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                AND performance = 'Good'
                """,
                (
                    session["user_id"],
                )
            )

            row = cursor.fetchone()

            if row:
                good = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                AND performance = 'Average'
                """,
                (
                    session["user_id"],
                )
            )

            row = cursor.fetchone()

            if row:
                average = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                AND performance = 'Poor'
                """,
                (
                    session["user_id"],
                )
            )

            row = cursor.fetchone()

            if row:
                poor = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


        except Error as e:

            print(
                "Student Dashboard Error:",
                e
            )


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "dashboard.html",

        total=total,

        excellent=excellent,

        good=good,

        average=average,

        poor=poor,

        user_name=session.get(
            "user_name",
            "Student"
        )
    )


# =========================================================
# PREDICTION HISTORY
# =========================================================

@app.route("/history")
def history():

    if not student_required():

        return redirect("/login")


    connection = get_db_connection()

    if connection is None:

        return "Database connection failed."


    cursor = None

    try:

        cursor = connection.cursor(
            dictionary=True
        )


        query = """
            SELECT
                id,
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                assignments_completed,
                previous_score,
                predicted_score,
                performance,
                prediction_date
            FROM predictions
            WHERE user_id = %s
            AND prediction_type = 'STUDENT'
            ORDER BY id DESC
        """


        cursor.execute(
            query,
            (
                session["user_id"],
            )
        )


        records = cursor.fetchall()


        return render_template(
            "history.html",
            records=records
        )


    except Error as e:

        print(
            "History error:",
            e
        )

        return "Error loading prediction history."


    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# STUDENT WHAT-IF
# =========================================================

@app.route(
    "/what-if",
    methods=["GET", "POST"]
)
def what_if():

    if not student_required():

        return redirect("/login")


    prediction = None
    performance = None


    values = {
        "study_hours": "",
        "attendance": "",
        "sleep_hours": "",
        "internet_usage": ""
    }


    if request.method == "POST":

        try:

            study_hours = float(
                request.form.get(
                    "study_hours",
                    ""
                )
            )

            attendance = float(
                request.form.get(
                    "attendance",
                    ""
                )
            )

            sleep_hours = float(
                request.form.get(
                    "sleep_hours",
                    ""
                )
            )

            internet_usage = float(
                request.form.get(
                    "internet_usage",
                    ""
                )
            )


        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please enter valid numeric values.",
                "error"
            )

            return render_template(
                "what_if.html",
                prediction=None,
                performance=None,
                values=values
            )


        values = {
            "study_hours": study_hours,
            "attendance": attendance,
            "sleep_hours": sleep_hours,
            "internet_usage": internet_usage
        }


        if not 0 <= study_hours <= 24:

            flash(
                "Study Hours must be between 0 and 24.",
                "error"
            )

            return render_template(
                "what_if.html",
                prediction=None,
                performance=None,
                values=values
            )


        if not 0 <= attendance <= 100:

            flash(
                "Attendance must be between 0 and 100.",
                "error"
            )

            return render_template(
                "what_if.html",
                prediction=None,
                performance=None,
                values=values
            )


        if not 0 <= sleep_hours <= 24:

            flash(
                "Sleep Hours must be between 0 and 24.",
                "error"
            )

            return render_template(
                "what_if.html",
                prediction=None,
                performance=None,
                values=values
            )


        if not 0 <= internet_usage <= 24:

            flash(
                "Internet Usage must be between 0 and 24.",
                "error"
            )

            return render_template(
                "what_if.html",
                prediction=None,
                performance=None,
                values=values
            )


        if student_model is None:

            flash(
                "Student ML model is not loaded.",
                "error"
            )

            return render_template(
                "what_if.html",
                prediction=None,
                performance=None,
                values=values
            )


        try:

            prediction = predict_with_feature_names(
                student_model,
                [
                    study_hours,
                    attendance,
                    sleep_hours,
                    internet_usage
                ],
                [
                    "study_hours",
                    "attendance",
                    "sleep_hours",
                    "internet_usage"
                ]
            )


            prediction = round(
                max(
                    0,
                    min(
                        100,
                        prediction
                    )
                ),
                2
            )


            performance = get_performance(
                prediction
            )


        except Exception as e:

            print(
                "What-If Error:",
                e
            )

            flash(
                "Student What-If prediction failed.",
                "error"
            )


    return render_template(
        "what_if.html",

        prediction=prediction,

        performance=performance,

        values=values
    )


# =========================================================
# STUDENT RECOMMENDATIONS
# =========================================================

@app.route("/recommendations")
def recommendations():

    if not student_required():

        return redirect("/login")


    prediction = 0
    performance = "No Prediction"

    recommendation_list = []


    connection = get_db_connection()


    if connection is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT
                    predicted_score,
                    performance
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    session["user_id"],
                )
            )


            result = cursor.fetchone()


            if result:

                prediction = float(
                    result.get(
                        "predicted_score",
                        0
                    ) or 0
                )


                performance = result.get(
                    "performance",
                    "No Prediction"
                )


                if prediction >= 80:

                    recommendation_list = [
                        "Continue your current study routine.",
                        "Focus on advanced topics.",
                        "Practice challenging questions.",
                        "Maintain regular revision."
                    ]


                elif prediction >= 60:

                    recommendation_list = [
                        "Improve weak subjects.",
                        "Complete regular revision.",
                        "Practice previous examination papers.",
                        "Maintain good attendance."
                    ]


                elif prediction >= 40:

                    recommendation_list = [
                        "Create a fixed daily study timetable.",
                        "Give extra attention to difficult subjects.",
                        "Reduce unnecessary internet usage.",
                        "Take weekly self-tests."
                    ]


                else:

                    recommendation_list = [
                        "Start with basic concepts.",
                        "Follow a regular study schedule.",
                        "Increase study hours gradually.",
                        "Take regular practice tests."
                    ]


            else:

                recommendation_list = [
                    "Make your first prediction to get recommendations."
                ]


        except Error as e:

            print(
                "Recommendation Error:",
                e
            )

            recommendation_list = [
                "Unable to load recommendations."
            ]


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "recommendations.html",

        prediction=prediction,

        performance=performance,

        recommendations=recommendation_list
    )


# =========================================================
# STUDENT PROGRESS
# =========================================================

@app.route("/progress")
def progress():

    if not student_required():

        return redirect("/login")


    total_predictions = 0
    latest_score = 0
    average_score = 0
    improvement = 0

    history_data = []


    connection = get_db_connection()


    if connection is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT
                    predicted_score,
                    prediction_date
                FROM predictions
                WHERE user_id = %s
                AND prediction_type = 'STUDENT'
                ORDER BY id ASC
                """,
                (
                    session["user_id"],
                )
            )


            history_data = cursor.fetchall()


            scores = []


            for row in history_data:

                scores.append(
                    float(
                        row.get(
                            "predicted_score",
                            0
                        ) or 0
                    )
                )


            if scores:

                total_predictions = len(
                    scores
                )

                latest_score = round(
                    scores[-1],
                    2
                )

                average_score = round(
                    sum(scores) / len(scores),
                    2
                )


                if len(scores) >= 2:

                    improvement = round(
                        scores[-1] - scores[0],
                        2
                    )


        except Error as e:

            print(
                "Progress Error:",
                e
            )


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "progress.html",

        history=history_data,

        total_predictions=total_predictions,

        latest_score=latest_score,

        average_score=average_score,

        improvement=improvement
    )


# =========================================================
# STUDENT FEEDBACK
# =========================================================

@app.route(
    "/feedback",
    methods=["GET", "POST"]
)
def feedback():

    if not student_required():

        return redirect("/login")


    if request.method == "GET":

        return render_template(
            "feedback.html"
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    rating = request.form.get(
        "rating",
        ""
    ).strip()

    feedback_text = request.form.get(
        "feedback",
        ""
    ).strip()

    suggestion = request.form.get(
        "suggestion",
        ""
    ).strip()


    if not name or not email or not rating or not feedback_text:

        flash(
            "Please fill all required fields.",
            "error"
        )

        return redirect("/feedback")


    try:

        rating = int(rating)

    except:

        flash(
            "Invalid rating.",
            "error"
        )

        return redirect("/feedback")


    if rating < 1 or rating > 5:

        flash(
            "Rating must be between 1 and 5.",
            "error"
        )

        return redirect("/feedback")


    connection = get_db_connection()


    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect("/feedback")


    cursor = None


    try:

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO feedback
            (
                user_id,
                name,
                email,
                rating,
                feedback,
                suggestion
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                session["user_id"],
                name,
                email,
                rating,
                feedback_text,
                suggestion
            )
        )


        connection.commit()


        flash(
            "Feedback submitted successfully.",
            "success"
        )


    except Error as e:

        connection.rollback()

        print(
            "Feedback Error:",
            e
        )

        flash(
            "Feedback could not be submitted.",
            "error"
        )


    finally:

        if cursor:
            cursor.close()

        connection.close()


    return redirect("/feedback")


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    if not student_required():

        return redirect("/login")


    return render_template(
        "about.html",

        user_name=session.get(
            "user_name",
            "Student"
        )
    )


# =========================================================
# CONTACT
# =========================================================

@app.route(
    "/contact",
    methods=["GET", "POST"]
)
def contact():

    if not student_required():

        return redirect("/login")


    if request.method == "GET":

        return render_template(
            "contact.html"
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()


    if not name or not email or not subject or not message:

        flash(
            "Please fill all required fields.",
            "error"
        )

        return redirect("/contact")


    connection = get_db_connection()


    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect("/contact")


    cursor = None


    try:

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO contact_messages
            (
                user_id,
                name,
                email,
                subject,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                session["user_id"],
                name,
                email,
                subject,
                message
            )
        )


        connection.commit()


        flash(
            "Your message has been sent successfully.",
            "success"
        )


    except Error as e:

        connection.rollback()

        print(
            "Contact Error:",
            e
        )

        flash(
            "Message could not be sent.",
            "error"
        )


    finally:

        if cursor:
            cursor.close()

        connection.close()


    return redirect("/contact")


# =========================================================
# TEACHER LOGIN
# =========================================================

@app.route(
    "/teacher-login",
    methods=["GET", "POST"]
)
def teacher_login():

    if request.method == "GET":

        return render_template(
            "teacher_login.html"
        )


    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    # -----------------------------------------------------
    # FIXED TEACHER CREDENTIALS
    # -----------------------------------------------------

    if (
        email == TEACHER_EMAIL
        and
        password == TEACHER_PASSWORD
    ):

        session.clear()

        session["teacher_id"] = 1

        session["teacher_email"] = TEACHER_EMAIL

        session["teacher_name"] = "Teacher"


        flash(
            "Teacher login successful!",
            "success"
        )


        return redirect(
            "/teacher-dashboard"
        )


    # -----------------------------------------------------
    # DATABASE LOGIN
    # -----------------------------------------------------

    connection = get_db_connection()


    if connection is None:

        flash(
            "Invalid teacher email or password.",
            "error"
        )

        return redirect(
            "/teacher-login"
        )


    cursor = None


    try:

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                id,
                email,
                password
            FROM teachers
            WHERE email = %s
            """,
            (email,)
        )


        teacher = cursor.fetchone()


        if teacher:

            try:

                valid = check_password_hash(
                    teacher["password"],
                    password
                )

            except:

                valid = (
                    password ==
                    teacher["password"]
                )


            if valid:

                session.clear()

                session["teacher_id"] = teacher["id"]

                session["teacher_email"] = teacher["email"]

                session["teacher_name"] = "Teacher"


                flash(
                    "Teacher login successful!",
                    "success"
                )


                return redirect(
                    "/teacher-dashboard"
                )


        flash(
            "Invalid teacher email or password.",
            "error"
        )


        return redirect(
            "/teacher-login"
        )


    except Error as e:

        print(
            "Teacher Login Error:",
            e
        )

        flash(
            "Teacher login failed.",
            "error"
        )

        return redirect(
            "/teacher-login"
        )


    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# TEACHER LOGOUT
# =========================================================

@app.route("/teacher-logout")
def teacher_logout():

    session.clear()

    flash(
        "Teacher logged out successfully.",
        "success"
    )

    return redirect(
        "/teacher-login"
    )


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    if not teacher_required():

        return redirect(
            "/teacher-login"
        )


    total_students = 0
    total_predictions = 0


    connection = get_db_connection()


    if connection is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT COUNT(
                    DISTINCT student_id
                ) AS total
                FROM predictions
                WHERE prediction_type = 'TEACHER'
                """
            )


            row = cursor.fetchone()


            if row:

                total_students = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM predictions
                WHERE prediction_type = 'TEACHER'
                """
            )


            row = cursor.fetchone()


            if row:

                total_predictions = int(
                    row.get(
                        "total",
                        0
                    ) or 0
                )


        except Error as e:

            print(
                "Teacher Dashboard Error:",
                e
            )


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "teacher_dashboard.html",

        teacher_name=session.get(
            "teacher_email",
            "Teacher"
        ),

        total_students=total_students,

        total_predictions=total_predictions
    )


# =========================================================
# TEACHER STUDENTS
# =========================================================

@app.route("/teacher-students")
def teacher_students():

    if not teacher_required():

        return redirect(
            "/teacher-login"
        )


    students = []


    connection = get_db_connection()


    if connection is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    created_at
                FROM users
                ORDER BY name ASC
                """
            )


            students = cursor.fetchall()


        except Error as e:

            print(
                "Teacher Students Error:",
                e
            )


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "teacher_students.html",
        students=students
    )


# =========================================================
# TEACHER WHAT-IF / ACADEMIC PREDICTION
#
# REQUIRED FLOW:
# 1. Student must first complete PERSONAL prediction.
# 2. Teacher selects that SAME student.
# 3. Teacher enters ONLY academic fields:
#       - assignments_completed
#       - previous_score
# 4. Teacher prediction is saved against the SAME users.id.
# 5. Student ID + Student Name are copied from the student's
#    latest PERSONAL prediction. Teacher cannot enter a different
#    ID/name for the same combined result.
# 6. After successful teacher prediction, Combined Result opens
#    automatically for that SAME student.
#
# NO PERSONAL FIELDS are used by teacher model.
# =========================================================

@app.route(
    "/teacher-what-if",
    methods=["GET", "POST"]
)
def teacher_what_if():

    if not teacher_required():

        return redirect(
            "/teacher-login"
        )


    prediction = None
    performance = None


    values = {
        "student_id": "",
        "student_name": "",
        "assignments_completed": "",
        "previous_score": ""
    }


    students = []


    connection = get_db_connection()


    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            "/teacher-dashboard"
        )


    cursor = None


    try:

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # LOAD STUDENTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name
            FROM users
            ORDER BY name ASC
            """
        )


        students = cursor.fetchall()


        # -------------------------------------------------
        # GET
        # -------------------------------------------------

        if request.method == "GET":

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        # -------------------------------------------------
        # POST
        # -------------------------------------------------

        # IMPORTANT:
        # This is users.id (internal database ID), NOT the
        # display Student ID entered by the student.
        selected_user_id = request.form.get(
            "student_id",
            ""
        ).strip()


        assignments_raw = request.form.get(
            "assignments_completed",
            ""
        ).strip()


        previous_score_raw = request.form.get(
            "previous_score",
            ""
        ).strip()


        values = {
            "student_id": selected_user_id,
            "student_name": "",
            "assignments_completed": assignments_raw,
            "previous_score": previous_score_raw
        }


        if not selected_user_id:

            flash(
                "Please select a student.",
                "error"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        # -------------------------------------------------
        # RESOLVE SELECTED STUDENT
        # The teacher form may send either:
        # 1. internal users.id, or
        # 2. the Student ID entered during personal prediction.
        # Resolve both without changing the teacher login or other routes.
        # -------------------------------------------------

        selected_user_id_int = None
        selected_student = None

        try:
            selected_value_int = int(selected_user_id)
        except (ValueError, TypeError):
            selected_value_int = None

        # First treat the submitted value as users.id.
        if selected_value_int is not None:
            cursor.execute(
                """
                SELECT
                    id,
                    name
                FROM users
                WHERE id = %s
                LIMIT 1
                """,
                (selected_value_int,)
            )
            selected_student = cursor.fetchone()

            if selected_student is not None:
                selected_user_id_int = int(selected_student["id"])

        # If it was not users.id, treat it as the display Student ID.
        if selected_student is None:
            cursor.execute(
                """
                SELECT
                    sp.user_id,
                    sp.student_id,
                    sp.student_name
                FROM student_predictions sp
                WHERE sp.student_id = %s
                ORDER BY sp.id DESC
                LIMIT 1
                """,
                (selected_user_id,)
            )
            student_identity = cursor.fetchone()

            if student_identity is not None:
                selected_user_id_int = int(student_identity["user_id"])

                cursor.execute(
                    """
                    SELECT
                        id,
                        name
                    FROM users
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (selected_user_id_int,)
                )
                selected_student = cursor.fetchone()

        if selected_student is None or selected_user_id_int is None:
            flash(
                "Selected student does not exist.",
                "error"
            )

            return render_template(
                "teacher_what_if.html",
                teacher_name=session.get("teacher_email", "Teacher"),
                students=students,
                prediction=None,
                performance=None,
                values=values
            )


        # -------------------------------------------------
        # VERY IMPORTANT:
        # STUDENT PERSONAL PREDICTION MUST EXIST FIRST
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                student_name,
                predicted_score,
                performance,
                prediction_date
            FROM student_predictions
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                selected_user_id_int,
            )
        )


        student_prediction = cursor.fetchone()


        # -------------------------------------------------
        # ROBUST FALLBACK FOR STUDENT IDENTITY
        # -------------------------------------------------
        # Some existing teacher templates submit the display
        # Student ID instead of users.id.  If the first lookup
        # does not find a record, try the exact display Student ID.
        # Finally, check the legacy predictions table so an already
        # completed Student prediction is not rejected just because
        # an older record was saved there.
        # -------------------------------------------------
        if student_prediction is None:

            cursor.execute(
                """
                SELECT
                    id,
                    student_id,
                    student_name,
                    predicted_score,
                    performance,
                    prediction_date
                FROM student_predictions
                WHERE student_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (selected_user_id,)
            )

            student_prediction = cursor.fetchone()


        if student_prediction is None:

            cursor.execute(
                """
                SELECT
                    id,
                    student_id,
                    student_name,
                    predicted_score,
                    performance,
                    prediction_date
                FROM predictions
                WHERE prediction_type = 'STUDENT'
                  AND user_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (selected_user_id_int,)
            )

            student_prediction = cursor.fetchone()


        if student_prediction is None:

            flash(
                "First complete the Student personal prediction "
                "for this student. Then Teacher academic prediction "
                "can be generated.",
                "warning"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        # -------------------------------------------------
        # USE EXACT SAME STUDENT ID + NAME FROM STUDENT
        # PREDICTION
        # -------------------------------------------------

        student_display_id = (
            student_prediction.get("student_id")
            or ""
        ).strip()


        student_name = (
            student_prediction.get("student_name")
            or selected_student["name"]
            or ""
        ).strip()


        if not student_display_id or not student_name:

            flash(
                "Student personal prediction has incomplete "
                "Student ID or Student Name. Please make the "
                "Student prediction again.",
                "warning"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        values["student_id"] = student_display_id
        values["student_name"] = student_name


        # -------------------------------------------------
        # NUMERIC VALUES
        # -------------------------------------------------

        try:

            assignments_completed = float(
                assignments_raw
            )

            previous_score = float(
                previous_score_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please enter valid numeric values.",
                "error"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        values["assignments_completed"] = (
            assignments_completed
        )

        values["previous_score"] = (
            previous_score
        )


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if assignments_completed < 0:

            flash(
                "Assignments Completed cannot be negative.",
                "error"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        if previous_score < 0 or previous_score > 100:

            flash(
                "Previous Score must be between 0 and 100.",
                "error"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        # -------------------------------------------------
        # CHECK TEACHER MODEL
        # -------------------------------------------------

        if teacher_model is None:

            flash(
                "Teacher academic model is not loaded.",
                "error"
            )

            return render_template(
                "teacher_what_if.html",

                teacher_name=session.get(
                    "teacher_email",
                    "Teacher"
                ),

                students=students,

                prediction=None,

                performance=None,

                values=values
            )


        # -------------------------------------------------
        # TEACHER MODEL
        # EXACTLY 2 FEATURES
        # -------------------------------------------------

        prediction = predict_with_feature_names(
            teacher_model,

            [
                assignments_completed,
                previous_score
            ],

            [
                "assignments_completed",
                "previous_score"
            ]
        )


        prediction = round(
            max(
                0,
                min(
                    100,
                    prediction
                )
            ),
            2
        )


        performance = get_performance(
            prediction
        )


        # -------------------------------------------------
        # SAVE TEACHER PREDICTION
        #
        # user_id = SAME users.id as Student prediction
        # student_id = SAME display Student ID as Student
        # student_name = SAME Student Name as Student
        # -------------------------------------------------

        # -------------------------------------------------
        # SAVE TEACHER ACADEMIC PREDICTION
        # =================================================
        # Use a separate Teacher DB connection so Teacher
        # prediction records are stored only in teacher_predictions.
        # =================================================

        if cursor:
            cursor.close()
            cursor = None

        if connection and connection.is_connected():
            connection.close()

        connection = get_teacher_db_connection()

        if connection is None:

            flash(
                "Teacher database connection failed.",
                "error"
            )

            return redirect("/teacher-what-if")

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO teacher_predictions
            (
                user_id,
                student_id,
                student_name,
                assignments_completed,
                previous_score,
                predicted_score,
                performance
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                int(selected_user_id_int),
                student_display_id,
                student_name,
                assignments_completed,
                previous_score,
                prediction,
                performance
            )
        )

        if cursor.rowcount != 1:

            raise Error(
                "Teacher prediction INSERT did not create a record."
            )

        connection.commit()

        saved_teacher_prediction_id = cursor.lastrowid

        # -------------------------------------------------
        # REMEMBER THE SAME STUDENT FOR TEACHER PANEL
        # -------------------------------------------------
        # Teacher Recommendations and Teacher Progress must show
        # the exact student for whom the current What-If prediction
        # was generated. Store the internal users.id in session so
        # those existing pages do not accidentally show another
        # student's latest prediction.
        session["teacher_selected_student_id"] = int(selected_user_id_int)
        session["teacher_selected_student_display_id"] = student_display_id
        session["teacher_selected_student_name"] = student_name

        # -------------------------------------------------
        # COMPATIBILITY SAVE
        # Keep the existing predictions table populated so
        # the original Teacher Dashboard, Progress, Reports
        # and other existing routes continue to work unchanged.
        # The dedicated teacher_predictions table above remains
        # the separate Teacher academic prediction table.
        # -------------------------------------------------
        cursor.execute(
            """
            INSERT INTO predictions
            (
                user_id,
                prediction_type,
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                assignments_completed,
                previous_score,
                predicted_score,
                performance
            )
            VALUES
            (
                %s,
                'TEACHER',
                %s,
                %s,
                NULL,
                NULL,
                NULL,
                NULL,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                int(selected_user_id_int),
                student_display_id,
                student_name,
                assignments_completed,
                previous_score,
                prediction,
                performance
            )
        )

        connection.commit()

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                student_id,
                student_name,
                predicted_score,
                performance
            FROM teacher_predictions
            WHERE id = %s
              AND user_id = %s
            LIMIT 1
            """,
            (
                saved_teacher_prediction_id,
                int(selected_user_id_int)
            )
        )

        saved_teacher_prediction = cursor.fetchone()

        if saved_teacher_prediction is None:

            raise Error(
                "Teacher prediction was not found after database commit."
            )


        flash(
            "Teacher academic prediction generated successfully!",
            "success"
        )


        # =====================================================
        # AUTOMATIC COMBINED RESULT
        # =====================================================

        return redirect(
            "/combined-result?student_id="
            + str(selected_user_id_int)
        )


    except Error as e:

        if connection:
            connection.rollback()

        print(
            "Teacher What-If Database Error:",
            e
        )

        flash(
            "Teacher prediction database error: " + str(e),
            "error"
        )

        return redirect("/teacher-what-if")


    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "Teacher What-If Error:",
            e
        )

        flash(
            "Prediction Error: " + str(e),
            "error"
        )

        return redirect("/teacher-what-if")


    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# TEACHER RECOMMENDATIONS
# =========================================================

@app.route("/teacher-recommendations")
def teacher_recommendations():

    if not teacher_required():

        return redirect(
            "/teacher-login"
        )


    prediction = None
    performance = "No Prediction"
    student_name = None
    recommendations = []


    selected_teacher_student_id = session.get("teacher_selected_student_id")

    connection = get_db_connection()


    if connection is not None and selected_teacher_student_id is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT
                    student_name,
                    predicted_score,
                    performance
                FROM teacher_predictions
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (session.get("teacher_selected_student_id"),)
            )


            result = cursor.fetchone()


            if result:

                student_name = result.get(
                    "student_name"
                )


                prediction = float(
                    result.get(
                        "predicted_score",
                        0
                    ) or 0
                )


                performance = result.get(
                    "performance",
                    "No Prediction"
                )


                if prediction >= 80:

                    recommendations = [
                        "Continue current academic performance.",
                        "Focus on advanced topics.",
                        "Practice higher-level questions.",
                        "Maintain assignment completion."
                    ]


                elif prediction >= 60:

                    recommendations = [
                        "Improve weak academic subjects.",
                        "Complete assignments regularly.",
                        "Revise previous topics.",
                        "Practice previous examination papers."
                    ]


                elif prediction >= 40:

                    recommendations = [
                        "Create a regular academic timetable.",
                        "Complete pending assignments.",
                        "Revise important concepts.",
                        "Take regular practice tests."
                    ]


                else:

                    recommendations = [
                        "Start with basic concepts.",
                        "Complete assignments regularly.",
                        "Revise previous lessons.",
                        "Take teacher guidance."
                    ]


            else:

                recommendations = [
                    "Create a teacher academic prediction first."
                ]


        except Error as e:

            print(
                "Teacher Recommendation Error:",
                e
            )


            recommendations = [
                "Unable to load recommendations."
            ]


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "teacher_recommendations.html",

        student_name=student_name,

        prediction=prediction,

        performance=performance,

        recommendations=recommendations
    )


# =========================================================
# TEACHER PROGRESS
# =========================================================

@app.route("/teacher-progress")
def teacher_progress():

    if not teacher_required():

        return redirect(
            "/teacher-login"
        )


    progress_data = []


    selected_teacher_student_id = session.get("teacher_selected_student_id")

    connection = get_db_connection()


    if connection is not None and selected_teacher_student_id is not None:

        cursor = None

        try:

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT
                    student_id,
                    student_name,
                    assignments_completed,
                    previous_score,
                    predicted_score,
                    performance,
                    prediction_date
                FROM teacher_predictions
                WHERE user_id = %s
                ORDER BY id DESC
                """,
                (session.get("teacher_selected_student_id"),)
            )


            progress_data = cursor.fetchall()


        except Error as e:

            print(
                "Teacher Progress Error:",
                e
            )


        finally:

            if cursor:
                cursor.close()

            connection.close()


    return render_template(
        "teacher_progress.html",
        progress=progress_data
    )
    # =========================================================
# COMBINED PERFORMANCE RESULT
# =========================================================
# FLOW:
# STUDENT LOGIN -> STUDENT PERSONAL PREDICTION
# TEACHER LOGIN -> SELECT SAME STUDENT -> ACADEMIC PREDICTION
# TEACHER PANEL -> COMBINED RESULT
#
# IMPORTANT:
# Student personal prediction is identified by users.id/user_id.
# Teacher academic prediction stores the SAME users.id in user_id.
# The display Student ID remains the exact Student ID entered during
# the Student personal prediction.
# =========================================================

@app.route("/combined-result")
def combined_result():

    # -----------------------------------------------------
    # ALLOW STUDENT OR TEACHER SESSION
    # -----------------------------------------------------

    is_student = "user_id" in session
    is_teacher = "teacher_id" in session

    if not is_student and not is_teacher:
        return redirect("/login")

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        if connection is None:
            flash("Database connection failed.", "danger")

            if is_teacher:
                return redirect("/teacher-dashboard")

            return redirect("/")

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # DETERMINE WHICH STUDENT TO SHOW
        # -------------------------------------------------

        requested_student_id = request.args.get("student_id", "").strip()

        if is_teacher:

            # Teacher MUST select a student.
            if not requested_student_id:
                flash(
                    "Please select a student before opening Combined Result.",
                    "warning"
                )
                return redirect("/teacher-what-if")

            # The link may contain either the internal users.id
            # or the display Student ID. Resolve both forms.
            selected_user_id = None
            selected_user = None

            try:
                requested_value_int = int(requested_student_id)
            except (ValueError, TypeError):
                requested_value_int = None

            # First try internal users.id.
            if requested_value_int is not None:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name
                    FROM users
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (requested_value_int,)
                )
                selected_user = cursor.fetchone()

                if selected_user:
                    selected_user_id = int(selected_user["id"])

            # If it is not users.id, try the display Student ID.
            if selected_user is None:
                cursor.execute(
                    """
                    SELECT
                        sp.user_id AS id,
                        sp.student_name AS name
                    FROM student_predictions sp
                    WHERE sp.student_id = %s
                    ORDER BY sp.id DESC
                    LIMIT 1
                    """,
                    (requested_student_id,)
                )
                selected_user = cursor.fetchone()

                if selected_user:
                    selected_user_id = int(selected_user["id"])

            if selected_user is None or selected_user_id is None:
                flash("Selected student does not exist.", "warning")
                return redirect("/teacher-what-if")

            user_id = selected_user_id

        else:

            # Student sees only his/her own combined result.
            user_id = session["user_id"]

        # -------------------------------------------------
        # FETCH LATEST STUDENT PERSONAL PREDICTION
        # FROM DEDICATED STUDENT TABLE
        # -------------------------------------------------

        if cursor:
            cursor.close()
            cursor = None

        if connection and connection.is_connected():
            connection.close()

        connection = get_student_db_connection()

        if connection is None:
            flash("Student database connection failed.", "danger")

            if is_teacher:
                return redirect("/teacher-dashboard")

            return redirect("/")

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                student_name,
                study_hours,
                attendance,
                sleep_hours,
                internet_usage,
                predicted_score,
                performance,
                prediction_date
            FROM student_predictions
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        student_prediction = cursor.fetchone()

        # Fallback: allow Combined Result to resolve by the
        # display Student ID as well as users.id.
        if not student_prediction and is_teacher:
            cursor.execute(
                """
                SELECT
                    id,
                    student_id,
                    student_name,
                    study_hours,
                    attendance,
                    sleep_hours,
                    internet_usage,
                    predicted_score,
                    performance,
                    prediction_date
                FROM student_predictions
                WHERE student_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (requested_student_id,)
            )
            student_prediction = cursor.fetchone()

        # Final compatibility fallback for older Student records
        # stored only in the legacy predictions table.
        if not student_prediction:
            cursor.execute(
                """
                SELECT
                    id,
                    student_id,
                    student_name,
                    study_hours,
                    attendance,
                    sleep_hours,
                    internet_usage,
                    predicted_score,
                    performance,
                    prediction_date
                FROM predictions
                WHERE prediction_type = 'STUDENT'
                  AND user_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,)
            )
            student_prediction = cursor.fetchone()

        if not student_prediction:
            flash(
                "Student personal prediction not found. "
                "Please complete the Student prediction first.",
                "warning"
            )

            if is_teacher:
                return redirect("/teacher-what-if")

            return redirect("/predict")

        student_score = float(
            student_prediction["predicted_score"] or 0
        )

        student_display_id = student_prediction["student_id"]
        student_name = student_prediction["student_name"] or "Student"

        # -------------------------------------------------
        # FETCH LATEST TEACHER ACADEMIC PREDICTION
        # FROM DEDICATED TEACHER TABLE
        # MATCH USING THE SAME users.id
        # -------------------------------------------------

        if cursor:
            cursor.close()
            cursor = None

        if connection and connection.is_connected():
            connection.close()

        connection = get_teacher_db_connection()

        if connection is None:
            flash("Teacher database connection failed.", "danger")

            if is_teacher:
                return redirect("/teacher-dashboard")

            return redirect("/")

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                student_name,
                assignments_completed,
                previous_score,
                predicted_score,
                performance,
                prediction_date
            FROM teacher_predictions
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        teacher_prediction = cursor.fetchone()

        # Fallback: use the exact display Student ID when an older
        # teacher record has a different/missing user_id linkage.
        if not teacher_prediction:
            cursor.execute(
                """
                SELECT
                    id,
                    student_id,
                    student_name,
                    assignments_completed,
                    previous_score,
                    predicted_score,
                    performance,
                    prediction_date
                FROM teacher_predictions
                WHERE student_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (student_prediction["student_id"],)
            )
            teacher_prediction = cursor.fetchone()

        if not teacher_prediction:
            flash(
                "Teacher academic prediction not found for this student. "
                "Please complete the Teacher academic prediction first.",
                "warning"
            )

            if is_teacher:
                return redirect(
                    "/teacher-what-if?student_id=" + str(user_id)
                )

            return redirect("/teacher-what-if")

        teacher_score = float(
            teacher_prediction["predicted_score"] or 0
        )

        # -------------------------------------------------
        # COMBINED SCORE
        # 50% STUDENT PERSONAL + 50% TEACHER ACADEMIC
        # -------------------------------------------------

        combined_score = round(
            (student_score + teacher_score) / 2,
            2
        )

        # -------------------------------------------------
        # DIFFERENCE / IMPROVEMENT
        # -------------------------------------------------

        improvement = round(
            teacher_score - student_score,
            2
        )

        difference = round(
            abs(teacher_score - student_score),
            2
        )

        # -------------------------------------------------
        # COMBINED PERFORMANCE
        # -------------------------------------------------

        if combined_score >= 80:
            combined_performance = "Excellent"

        elif combined_score >= 60:
            combined_performance = "Good"

        elif combined_score >= 40:
            combined_performance = "Average"

        else:
            combined_performance = "Poor"

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = []

        if combined_score >= 80:

            recommendations.append(
                "Excellent overall performance. Maintain your current academic and personal habits."
            )

            recommendations.append(
                "Continue regular study and maintain consistent attendance."
            )

        elif combined_score >= 60:

            recommendations.append(
                "Good overall performance. Focus on improving weaker academic areas."
            )

            recommendations.append(
                "Maintain regular study and assignment completion."
            )

        elif combined_score >= 40:

            recommendations.append(
                "Average performance. Increase study consistency and academic preparation."
            )

            recommendations.append(
                "Work on assignments and previous academic performance."
            )

        else:

            recommendations.append(
                "Performance needs improvement. Follow a structured study schedule."
            )

            recommendations.append(
                "Focus on assignments, attendance and academic preparation."
            )

        # -------------------------------------------------
        # COMPARE STUDENT + TEACHER PREDICTIONS
        # -------------------------------------------------

        if teacher_score > student_score:

            recommendations.append(
                "Teacher academic prediction is higher than the student personal prediction."
            )

        elif teacher_score < student_score:

            recommendations.append(
                "Teacher academic prediction is lower than the student personal prediction."
            )

        else:

            recommendations.append(
                "Student personal and teacher academic predictions are at the same level."
            )

        # -------------------------------------------------
        # RENDER COMBINED RESULT
        # -------------------------------------------------

        return render_template(
            "combined_result.html",
            student_id=student_display_id,
            student_name=student_name,
            student_score=student_score,
            teacher_score=teacher_score,
            combined_score=combined_score,
            combined_performance=combined_performance,
            improvement=improvement,
            difference=difference,
            recommendations=recommendations
        )

    except mysql.connector.Error as e:

        print("Combined Result Database Error:", e)

        flash(
            "Database error while loading combined result.",
            "danger"
        )

        if is_teacher:
            return redirect("/teacher-dashboard")

        return redirect("/")

    except Exception as e:

        print("Combined Result Error:", e)

        flash(
            "Unable to load combined result.",
            "danger"
        )

        if is_teacher:
            return redirect("/teacher-dashboard")

        return redirect("/")

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# TEACHER REPORTS
# =========================================================

@app.route("/teacher-reports")
def teacher_reports():

    # Teacher login check
    if "teacher_id" not in session:
        return redirect("/teacher-login")

    connection = get_db_connection()

    if connection is None:
        flash("Database connection failed. Check XAMPP/MySQL.", "error")
        return redirect("/teacher-dashboard")

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # TOTAL STUDENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) AS total_students
            FROM predictions
            WHERE prediction_type = 'TEACHER'
              AND student_id IS NOT NULL
              AND student_id <> ''
        """)

        result = cursor.fetchone()

        total_students = result["total_students"] or 0


        # -------------------------------------------------
        # TOTAL TEACHER PREDICTIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total_predictions
            FROM predictions
            WHERE prediction_type = 'TEACHER'
        """)

        result = cursor.fetchone()

        total_predictions = result["total_predictions"] or 0


        # -------------------------------------------------
        # AVERAGE SCORE
        # -------------------------------------------------

        cursor.execute("""
            SELECT AVG(predicted_score) AS average_score
            FROM predictions
            WHERE prediction_type = 'TEACHER'
              AND predicted_score IS NOT NULL
        """)

        result = cursor.fetchone()

        average_score = result["average_score"]

        if average_score is None:
            average_score = 0

        average_score = round(float(average_score), 2)


        # -------------------------------------------------
        # EXCELLENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS excellent
            FROM predictions
            WHERE prediction_type = 'TEACHER'
              AND performance = 'Excellent'
        """)

        result = cursor.fetchone()

        excellent = result["excellent"] or 0


        # -------------------------------------------------
        # GOOD
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS good
            FROM predictions
            WHERE prediction_type = 'TEACHER'
              AND performance = 'Good'
        """)

        result = cursor.fetchone()

        good = result["good"] or 0


        # -------------------------------------------------
        # AVERAGE
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS average
            FROM predictions
            WHERE prediction_type = 'TEACHER'
              AND performance = 'Average'
        """)

        result = cursor.fetchone()

        average = result["average"] or 0


        # -------------------------------------------------
        # POOR
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS poor
            FROM predictions
            WHERE prediction_type = 'TEACHER'
              AND performance = 'Poor'
        """)

        result = cursor.fetchone()

        poor = result["poor"] or 0


        # -------------------------------------------------
        # TEACHER NAME
        # -------------------------------------------------

        teacher_name = session.get(
            "teacher_name",
            "Teacher"
        )


        # -------------------------------------------------
        # SEND DATA TO HTML
        # -------------------------------------------------

        return render_template(
            "teacher_reports.html",

            teacher_name=teacher_name,

            total_students=total_students,

            total_predictions=total_predictions,

            average_score=average_score,

            excellent=excellent,

            good=good,

            average=average,

            poor=poor
        )


    except Exception as e:

        print("TEACHER REPORTS ERROR:", e)

        flash(
            "Unable to load teacher reports. Check Flask terminal.",
            "error"
        )

        return redirect("/teacher-dashboard")


    finally:

        if cursor is not None:
            cursor.close()

        connection.close()



# =========================================================
# ADMIN LOGIN
# IMPORTANT:
# ONLY ONE admin_login FUNCTION
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
@app.route(
    "/admin_login",
    methods=["GET", "POST"]
)
@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "GET":

        return render_template(
            "admin_login.html"
        )


    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    if not email or not password:

        flash(
            "Please enter email and password.",
            "error"
        )

        return redirect(
            "/admin_login"
        )


    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------

    connection = get_db_connection()


    if connection is None:

        flash(
            "Database connection failed. Check XAMPP/MySQL.",
            "error"
        )

        return redirect(
            "/admin_login"
        )


    cursor = None


    try:

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # GET ADMIN
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password
            FROM admin
            WHERE email = %s
            LIMIT 1
            """,
            (email,)
        )


        admin = cursor.fetchone()


        if admin is None:

            flash(
                "Invalid admin email or password.",
                "error"
            )

            return redirect(
                "/admin_login"
            )


        # -------------------------------------------------
        # PASSWORD CHECK
        # -------------------------------------------------

        try:

            valid = check_password_hash(
                admin["password"],
                password
            )

        except Exception:

            valid = (
                password ==
                admin["password"]
            )


        if not valid:

            flash(
                "Invalid admin email or password.",
                "error"
            )

            return redirect(
                "/admin_login"
            )


        # -------------------------------------------------
        # ADMIN SESSION
        # -------------------------------------------------

        session.clear()

        session["admin_id"] = admin["id"]

        session["admin_name"] = admin["name"]

        session["admin_email"] = admin["email"]


        flash(
            "Admin login successful.",
            "success"
        )


        return redirect(
            "/admin/dashboard"
        )


    except Exception as e:

        print("========================================")
        print("ADMIN LOGIN ERROR:")
        print(e)
        print("========================================")


        flash(
            "Admin login error. Check Flask terminal.",
            "error"
        )


        return redirect(
            "/admin_login"
        )


    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if not admin_required():

        return redirect(
            "/admin_login"
        )


    connection = get_db_connection()


    if connection is None:

        return """
        <h2>Database Connection Error</h2>

        <p>
            MySQL connection failed.
            Please check XAMPP and MySQL.
        </p>
        """


    cursor = None


    try:

        cursor = connection.cursor(
            dictionary=True
        )


        # =================================================
        # TOTAL STUDENTS
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS total_students
            FROM users
            """
        )


        result = cursor.fetchone()


        total_students = (
            result["total_students"]
            if result
            else 0
        )


        # =================================================
        # TOTAL PREDICTIONS
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS total_predictions
            FROM predictions
            """
        )


        result = cursor.fetchone()


        total_predictions = (
            result["total_predictions"]
            if result
            else 0
        )


        # =================================================
        # AVERAGE SCORE
        # =================================================

        cursor.execute(
            """
            SELECT
                ROUND(
                    AVG(predicted_score),
                    2
                ) AS average_score
            FROM predictions
            """
        )


        result = cursor.fetchone()


        average_score = (
            result["average_score"]
            if result
            and result["average_score"] is not None
            else 0
        )


        # =================================================
        # EXCELLENT
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS excellent
            FROM predictions
            WHERE performance = 'Excellent'
            """
        )


        result = cursor.fetchone()


        excellent = (
            result["excellent"]
            if result
            else 0
        )


        # =================================================
        # GOOD
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS good
            FROM predictions
            WHERE performance = 'Good'
            """
        )


        result = cursor.fetchone()


        good = (
            result["good"]
            if result
            else 0
        )


        # =================================================
        # AVERAGE
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS average
            FROM predictions
            WHERE performance = 'Average'
            """
        )


        result = cursor.fetchone()


        average = (
            result["average"]
            if result
            else 0
        )


        # =================================================
        # POOR
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS poor
            FROM predictions
            WHERE performance = 'Poor'
            """
        )


        result = cursor.fetchone()


        poor = (
            result["poor"]
            if result
            else 0
        )


        # =================================================
        # RECENT PREDICTIONS
        #
        # IMPORTANT:
        # Database column = prediction_date
        # HTML can continue using created_at
        # =================================================

        cursor.execute(
            """
            SELECT
                id,
                student_id,
                student_name,
                predicted_score,
                performance,
                prediction_date AS created_at
            FROM predictions
            ORDER BY id DESC
            LIMIT 10
            """
        )


        recent_predictions = cursor.fetchall()


        # =================================================
        # RENDER DASHBOARD
        # =================================================

        return render_template(

            "admin_dashboard.html",

            admin_email=session.get(
                "admin_email",
                ""
            ),

            total_students=total_students,

            total_predictions=total_predictions,

            average_score=average_score,

            excellent=excellent,

            good=good,

            average=average,

            poor=poor,

            recent_predictions=recent_predictions

        )


    except Exception as e:

        print("")
        print("========================================")
        print("ADMIN DASHBOARD ERROR:")
        print(e)
        print("========================================")
        print("")


        return f"""
        <h2>Admin Dashboard Database Error</h2>

        <p>{e}</p>

        <p>
            Check the Flask terminal for details.
        </p>
        """


    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# ADMIN REPORTS
# =========================================================

@app.route("/admin/reports")
def admin_reports():

    if not admin_required():

        return redirect(
            "/admin_login"
        )


    connection = get_db_connection()


    if connection is None:

        return """
        <h2>Database Connection Error</h2>

        <p>
            MySQL connection failed.
        </p>
        """


    cursor = None


    try:

        cursor = connection.cursor(
            dictionary=True
        )


        # =================================================
        # TOTAL STUDENTS
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS total_students
            FROM users
            """
        )


        result = cursor.fetchone()


        total_students = (
            result["total_students"]
            if result
            else 0
        )


        # =================================================
        # TOTAL PREDICTIONS
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS total_predictions
            FROM predictions
            """
        )


        result = cursor.fetchone()


        total_predictions = (
            result["total_predictions"]
            if result
            else 0
        )


        # =================================================
        # AVERAGE SCORE
        # =================================================

        cursor.execute(
            """
            SELECT
                ROUND(
                    AVG(predicted_score),
                    2
                ) AS average_score
            FROM predictions
            """
        )


        result = cursor.fetchone()


        average_score = (
            result["average_score"]
            if result
            and result["average_score"] is not None
            else 0
        )


        # =================================================
        # HIGHEST SCORE
        # =================================================

        cursor.execute(
            """
            SELECT
                MAX(predicted_score)
                AS highest_score
            FROM predictions
            """
        )


        result = cursor.fetchone()


        highest_score = (
            result["highest_score"]
            if result
            and result["highest_score"] is not None
            else 0
        )


        # =================================================
        # LOWEST SCORE
        # =================================================

        cursor.execute(
            """
            SELECT
                MIN(predicted_score)
                AS lowest_score
            FROM predictions
            """
        )


        result = cursor.fetchone()


        lowest_score = (
            result["lowest_score"]
            if result
            and result["lowest_score"] is not None
            else 0
        )


        # =================================================
        # EXCELLENT
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS excellent
            FROM predictions
            WHERE performance = 'Excellent'
            """
        )


        result = cursor.fetchone()


        excellent = (
            result["excellent"]
            if result
            else 0
        )


        # =================================================
        # GOOD
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS good
            FROM predictions
            WHERE performance = 'Good'
            """
        )


        result = cursor.fetchone()


        good = (
            result["good"]
            if result
            else 0
        )


        # =================================================
        # AVERAGE
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS average
            FROM predictions
            WHERE performance = 'Average'
            """
        )


        result = cursor.fetchone()


        average = (
            result["average"]
            if result
            else 0
        )


        # =================================================
        # POOR
        # =================================================

        cursor.execute(
            """
            SELECT COUNT(*) AS poor
            FROM predictions
            WHERE performance = 'Poor'
            """
        )


        result = cursor.fetchone()


        poor = (
            result["poor"]
            if result
            else 0
        )


        # =================================================
        # STUDENT REPORTS
        #
        # IMPORTANT:
        # prediction_date AS created_at
        # =================================================

        cursor.execute(
            """
            SELECT
                student_id,
                student_name,
                study_hours,
                attendance,
                previous_score,
                predicted_score,
                performance,
                prediction_date AS created_at
            FROM predictions
            ORDER BY id DESC
            """
        )


        student_reports = cursor.fetchall()


        # =================================================
        # RENDER REPORTS
        # =================================================

        return render_template(

            "admin_reports.html",

            admin_email=session.get(
                "admin_email",
                ""
            ),

            total_students=total_students,

            total_predictions=total_predictions,

            average_score=average_score,

            highest_score=highest_score,

            lowest_score=lowest_score,

            excellent=excellent,

            good=good,

            average=average,

            poor=poor,

            student_reports=student_reports

        )


    except Exception as e:

        print("")
        print("========================================")
        print("ADMIN REPORTS ERROR:")
        print(e)
        print("========================================")
        print("")


        return f"""
        <h2>Admin Reports Database Error</h2>

        <p>{e}</p>

        <p>
            Check the Flask terminal for details.
        </p>
        """


    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    print("")
    print("========================================")
    print("STUDENT PERFORMANCE PREDICTION SYSTEM")
    print("========================================")


    validate_loaded_models()


    ensure_database_schema()


    ensure_default_admin()


    ensure_default_teacher()


    print("")
    print("Student Login:")
    print(
        "http://127.0.0.1:5000/login"
    )


    print("")
    print("Teacher Login:")
    print(
        "http://127.0.0.1:5000/teacher-login"
    )


    print("")
    print(
        "Teacher Email:",
        TEACHER_EMAIL
    )

    print(
        "Teacher Password:",
        TEACHER_PASSWORD
    )


    print("")
    print("Admin Login:")
    print(
        "http://127.0.0.1:5000/admin-login"
    )


    print("")
    print(
        "Admin Email:",
        ADMIN_EMAIL
    )

    print(
        "Admin Password:",
        ADMIN_PASSWORD
    )


    print("")
    print("Application running at:")
    print(
        "http://127.0.0.1:5000"
    )

    print("")


    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )