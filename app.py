from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "any_random_secret_key"  # keep secret in real apps

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("database.db")

# Create users table
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create scores table
conn.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    subject TEXT,
    test_type TEXT,
    score REAL,
    max_score REAL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.close()

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return """
    <h1>Welcome to Study Tracker Web App!</h1>
    <a href='/register'>Register</a> | <a href='/login'>Login</a>
    """

# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists! Try another one."

    return render_template("register.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["username"] = username
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid username or password!"

    return render_template("login.html")

# Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", username=session["username"])

# Add Score Route
@app.route("/add_score", methods=["GET", "POST"])
def add_score():
    if "user_id" not in session:
        return redirect("/login")  # must be logged in

    if request.method == "POST":
        date = request.form["date"]
        subject = request.form["subject"]
        test_type = request.form["test_type"]
        score = float(request.form["score"])
        max_score = float(request.form["max_score"])

        user_id = session["user_id"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO scores (user_id, date, subject, test_type, score, max_score) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, date, subject, test_type, score, max_score))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_score.html")

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
