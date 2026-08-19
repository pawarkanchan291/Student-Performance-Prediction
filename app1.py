from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "student_performance_secret_key_2026"


# =========================================================
# MYSQL CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,         
    "user": "root",
    "password": "",
    "database": "student_performance_db"
}


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

        if connection.is_connected():

            print("===================================")
            print("MYSQL CONNECTED SUCCESSFULLY")
            print("===================================")

            return connection

    except Error as e:

        print("MYSQL CONNECTION ERROR:", e)

        return None


# =========================================================
# FIRST PAGE
# /  --->  /register
# =========================================================

@app.route("/")
def index():

    return redirect("/register")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # -------------------------------
    # OPEN REGISTER PAGE
    # -------------------------------

    if request.method == "GET":

        return render_template("register.html")


    # -------------------------------
    # GET FORM DATA
    # -------------------------------

    name = request.form.get("name", "").strip()

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "")

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    # -------------------------------
    # VALIDATION
    # -------------------------------

    if not name or not email or not password or not confirm_password:

        flash(
            "Please fill all fields.",
            "error"
        )

        return redirect("/register")


    if password != confirm_password:

        flash(
            "Password and Confirm Password do not match.",
            "error"
        )

        return redirect("/register")


    if len(password) < 6:

        flash(
            "Password must contain at least 6 characters.",
            "error"
        )

        return redirect("/register")


    # -------------------------------
    # CONNECT MYSQL
    # -------------------------------

    connection = get_db_connection()

    if connection is None:

        flash(
            "MySQL connection failed. Please check XAMPP.",
            "error"
        )

        return redirect("/register")


    cursor = None


    try:

        cursor = connection.cursor()


        # -------------------------------
        # CHECK EMAIL
        # -------------------------------

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()


        if existing_user:

            flash(
                "Email already registered. Please login.",
                "error"
            )

            return redirect("/login")


        # -------------------------------
        # HASH PASSWORD
        # -------------------------------

        hashed_password = generate_password_hash(
            password
        )


        # -------------------------------
        # INSERT USER
        # -------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                name,
                email,
                hashed_password
            )
        )


        # -------------------------------
        # SAVE
        # -------------------------------

        connection.commit()


        print("===================================")
        print("ACCOUNT CREATED SUCCESSFULLY")
        print("===================================")


        # -------------------------------
        # REGISTER ---> LOGIN
        # -------------------------------

        flash(
            "Account created successfully! Please login.",
            "success"
        )

        return redirect("/login")


    except Error as e:

        print("REGISTRATION ERROR:", e)

        connection.rollback()

        flash(
            "Database Error: " + str(e),
            "error"
        )

        return redirect("/register")


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # -------------------------------
    # OPEN LOGIN PAGE
    # -------------------------------

    if request.method == "GET":

        return render_template("login.html")


    # -------------------------------
    # GET LOGIN DATA
    # -------------------------------

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )


    # -------------------------------
    # VALIDATION
    # -------------------------------

    if not email or not password:

        flash(
            "Email and password are required.",
            "error"
        )

        return redirect("/login")


    # -------------------------------
    # CONNECT MYSQL
    # -------------------------------

    connection = get_db_connection()

    if connection is None:

        flash(
            "MySQL connection failed. Please check XAMPP.",
            "error"
        )

        return redirect("/login")


    cursor = None


    try:

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------
        # FIND USER
        # -------------------------------

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()


        # -------------------------------
        # USER NOT FOUND
        # -------------------------------

        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect("/login")


        # -------------------------------
        # CHECK PASSWORD
        # -------------------------------

        if not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect("/login")


        # -------------------------------
        # CREATE SESSION
        # -------------------------------

        session["user_id"] = user["id"]

        session["user_name"] = user["name"]

        session["user_email"] = user["email"]


        print("===================================")
        print("LOGIN SUCCESSFUL")
        print("===================================")


        # -------------------------------
        # LOGIN ---> HOME
        # -------------------------------

        return redirect("/home")


    except Error as e:

        print("LOGIN ERROR:", e)

        flash(
            "Database Error: " + str(e),
            "error"
        )

        return redirect("/login")


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# HOME
# /home ---> index.html
# =========================================================

@app.route("/home")
def home():

    # User login आहे का?
    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect("/login")


    return render_template(
        "index.html",
        user_name=session.get("user_name"),
        user_email=session.get("user_email")
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    print("===================================")
    print("STUDENT PERFORMANCE PREDICTION")
    print("===================================")
    print("URL: http://127.0.0.1:5000")
    print("MySQL Port:", DB_CONFIG["port"])
    print("===================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )