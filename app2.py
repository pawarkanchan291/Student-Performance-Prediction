from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)


# =========================================================
# MYSQL CONFIG
# =========================================================

DB_CONFIG = {

    "host": "localhost",

    "port": 3306,

    "user": "root",

    "password": "",

    "database": "student_performance_db"

}


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

        return connection

    except mysql.connector.Error as e:

        print("MYSQL ERROR:", e)

        return None


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>MySQL Connection Error</h2>

        <p>
        Please start MySQL from XAMPP.
        </p>

        <a href="http://127.0.0.1:5000/">
        Back to Home
        </a>
        """

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
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
                created_at
            FROM students
            ORDER BY id DESC
        """)

        records = cursor.fetchall()

        cursor.close()

        connection.close()

        return render_template(
            "history.html",
            records=records
        )

    except Exception as e:

        print("HISTORY ERROR:", e)

        return f"""
        <h2>History Error</h2>
        <p>{e}</p>
        """


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print("History server running...")

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )