from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # enables session storage

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("database.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
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
    return "<h1>Welcome to Study Tracker Web App!</h1><a href='/login'>Login</a> | <a href='/register'>Register</a>"

# Register
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
        except:
            conn.close()
            return "Username already exists!"
        conn.close()
        return redirect("/login")

    return render_template("register.html")

# Login
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
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/dashboard")
        else:
            return "Invalid username or password!"

    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT id, date, subject, test_type, score, max_score FROM scores WHERE user_id=?", (session["user_id"],))
    scores = cur.fetchall()

    cur.execute("""
        SELECT subject, AVG(score), AVG(max_score)
        FROM scores
        WHERE user_id=?
        GROUP BY subject
    """, (session["user_id"],))
    subject_avgs = cur.fetchall()

    conn.close()

    return render_template("dashboard.html", username=session["username"], scores=scores, subject_avgs=subject_avgs)

# Add Score
@app.route("/add_score", methods=["GET", "POST"])
def add_score():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        date = request.form["date"]
        subject = request.form["subject"]
        test_type = request.form["test_type"]
        score = float(request.form["score"])
        max_score = float(request.form["max_score"])

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO scores (user_id, date, subject, test_type, score, max_score) VALUES (?, ?, ?, ?, ?, ?)",
                    (session["user_id"], date, subject, test_type, score, max_score))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_score.html")

# Edit Score
@app.route("/edit_score/<int:score_id>", methods=["GET", "POST"])
def edit_score(score_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":
        date = request.form["date"]
        subject = request.form["subject"]
        test_type = request.form["test_type"]
        score = float(request.form["score"])
        max_score = float(request.form["max_score"])

        cur.execute("""
            UPDATE scores
            SET date=?, subject=?, test_type=?, score=?, max_score=?
            WHERE id=? AND user_id=?
        """, (date, subject, test_type, score, max_score, score_id, session["user_id"]))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    # Pre-fill form with existing data
    cur.execute("SELECT date, subject, test_type, score, max_score FROM scores WHERE id=? AND user_id=?",
                (score_id, session["user_id"]))
    score_data = cur.fetchone()
    conn.close()

    return render_template("edit_score.html", score=score_data, score_id=score_id)

# Delete Score
@app.route("/delete_score/<int:score_id>")
def delete_score(score_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM scores WHERE id=? AND user_id=?", (score_id, session["user_id"]))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
