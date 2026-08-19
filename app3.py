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
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>MySQL Connection Error</h2>

        <p>
        Please start MySQL from XAMPP.
        </p>
        """

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        # ---------------------------------------------
        # TOTAL
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """)

        total = cursor.fetchone()["total"]

        # ---------------------------------------------
        # EXCELLENT
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM students
            WHERE performance = 'Excellent'
        """)

        excellent = cursor.fetchone()["count"]

        # ---------------------------------------------
        # GOOD
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM students
            WHERE performance = 'Good'
        """)

        good = cursor.fetchone()["count"]

        # ---------------------------------------------
        # AVERAGE
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM students
            WHERE performance = 'Average'
        """)

        average = cursor.fetchone()["count"]

        # ---------------------------------------------
        # POOR
        # ---------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM students
            WHERE performance = 'Poor'
        """)

        poor = cursor.fetchone()["count"]

        cursor.close()

        connection.close()

        # ---------------------------------------------
        # DASHBOARD HTML
        # ---------------------------------------------

        return render_template(

            "dashboard.html",

            total=total,

            excellent=excellent,

            good=good,

            average=average,

            poor=poor

        )

    except Exception as e:

        print("DASHBOARD ERROR:", e)

        return f"""
        <h2>Dashboard Error</h2>

        <p>{e}</p>
        """


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print("Dashboard server running...")

    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True
    )