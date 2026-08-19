from flask import Flask, render_template, request
import mysql.connector
import joblib
import pandas as pd
import os

app = Flask(__name__)

# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# MYSQL CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "student_performance_db"
}

# =========================================================
# MODEL PATH
# =========================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "student_performance_model.pkl"
)

# =========================================================
# LOAD MODEL
# =========================================================

model = None

try:

    if os.path.exists(MODEL_PATH):

        model = joblib.load(MODEL_PATH)

        print("MODEL LOADED SUCCESSFULLY")

    else:

        print("MODEL FILE NOT FOUND")
        print("Path:", MODEL_PATH)

except Exception as e:

    print("MODEL LOADING ERROR:", e)


# =========================================================
# MYSQL CONNECTION
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

        return connection

    except mysql.connector.Error as e:

        print("MYSQL CONNECTION ERROR:", e)

        return None


# =========================================================
# CREATE TABLE
# =========================================================

def create_table():

    connection = get_db_connection()

    if connection is None:

        print("MySQL connection failed.")
        return

    try:

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (

                id INT AUTO_INCREMENT PRIMARY KEY,

                student_id VARCHAR(50) NOT NULL,

                student_name VARCHAR(100) NOT NULL,

                study_hours FLOAT,

                attendance FLOAT,

                sleep_hours FLOAT,

                internet_usage FLOAT,

                assignments_completed INT,

                previous_score FLOAT,

                predicted_score FLOAT,

                performance VARCHAR(50),

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        connection.commit()

        cursor.close()
        connection.close()

        print("STUDENTS TABLE READY")

    except mysql.connector.Error as e:

        print("TABLE ERROR:", e)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


# =========================================================
# PREDICTION FORM
# =========================================================

@app.route("/predict", methods=["GET"])
def predict_page():

    return render_template("predict.html")


# =========================================================
# PREDICTION PROCESS
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        student_id = request.form.get(
            "student_id"
        )

        student_name = request.form.get(
            "student_name"
        )

        study_hours = float(
            request.form.get("study_hours")
        )

        attendance = float(
            request.form.get("attendance")
        )

        sleep_hours = float(
            request.form.get("sleep_hours")
        )

        internet_usage = float(
            request.form.get("internet_usage")
        )

        assignments_completed = int(
            request.form.get("assignments_completed")
        )

        previous_score = float(
            request.form.get("previous_score")
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not student_id or not student_name:

            return """
            <h2>Student ID and Student Name are required.</h2>
            <br>
            <a href="/predict">Back</a>
            """

        # -------------------------------------------------
        # CHECK MODEL
        # -------------------------------------------------

        if model is None:

            return """
            <h2>Model Loading Error</h2>
            <p>student_performance_model.pkl could not be loaded.</p>
            <br>
            <a href="/predict">Back</a>
            """

        # -------------------------------------------------
        # CREATE MODEL INPUT
        # -------------------------------------------------

        input_data = pd.DataFrame({

            "study_hours": [
                study_hours
            ],

            "attendance": [
                attendance
            ],

            "sleep_hours": [
                sleep_hours
            ],

            "internet_usage": [
                internet_usage
            ],

            "assignments_completed": [
                assignments_completed
            ],

            "previous_score": [
                previous_score
            ]

        })

        print("--------------------------------")
        print("INPUT DATA")
        print(input_data)
        print("--------------------------------")

        # -------------------------------------------------
        # PREDICTION
        # -------------------------------------------------

        predicted_score = model.predict(
            input_data
        )[0]

        predicted_score = round(
            float(predicted_score),
            2
        )

        # -------------------------------------------------
        # PERFORMANCE CATEGORY
        # -------------------------------------------------

        if predicted_score >= 80:

            performance = "Excellent"

        elif predicted_score >= 60:

            performance = "Good"

        elif predicted_score >= 40:

            performance = "Average"

        else:

            performance = "Poor"

        print("Predicted Score:", predicted_score)
        print("Performance:", performance)

        # -------------------------------------------------
        # DATABASE CONNECTION
        # -------------------------------------------------

        connection = get_db_connection()

        if connection is None:

            return """
            <h2>MySQL Connection Error</h2>

            <p>
            Please start MySQL from XAMPP.
            </p>

            <br>

            <a href="/predict">
            Back to Prediction
            </a>
            """

        # -------------------------------------------------
        # INSERT RECORD
        # -------------------------------------------------

        cursor = connection.cursor()

        query = """
        INSERT INTO students
        (
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
        """

        values = (

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

        cursor.execute(
            query,
            values
        )

        connection.commit()

        cursor.close()

        connection.close()

        print("--------------------------------")
        print("RECORD SAVED SUCCESSFULLY")
        print("--------------------------------")

        # -------------------------------------------------
        # SHOW RESULT PAGE
        # -------------------------------------------------

        return render_template(
            "result.html",

            student_id=student_id,

            student_name=student_name,

            study_hours=study_hours,

            attendance=attendance,

            sleep_hours=sleep_hours,

            internet_usage=internet_usage,

            assignments_completed=assignments_completed,

            previous_score=previous_score,

            predicted_score=predicted_score,

            performance=performance
        )

    except ValueError as e:

        return f"""
        <h2>Invalid Input</h2>

        <p>{e}</p>

        <br>

        <a href="/predict">
        Back to Prediction
        </a>
        """

    except Exception as e:

        print("PREDICTION ERROR:", e)

        return f"""
        <h2>Prediction Error</h2>

        <p>{e}</p>

        <br>

        <a href="/predict">
        Back to Prediction
        </a>
        """


# =========================================================
# START APP
# =========================================================

if __name__ == "__main__":

    print("====================================")
    print(" STUDENT PERFORMANCE PREDICTION")
    print("====================================")

    create_table()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )