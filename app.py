from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "any_random_secret_key"  # change this to something else if you want

# -----------------------------
# DATABASE SETUP
# -----------------------------
# Ensure database exists and tables are created
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
            flash("Account created — now log in.", "success")
            return redirect("/login")
        except Exception as e:
            conn.close()
            flash("Username already exists! Try another one.", "danger")
            return redirect("/register")

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
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid username or password.", "danger")
            return redirect("/login")

    return render_template("login.html")

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
        flash("Please log in first.", "warning")
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
        flash("Score added successfully.", "success")
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
        flash("Score updated.", "info")
        return redirect("/dashboard")

    cur.execute("SELECT date, subject, test_type, score, max_score FROM scores WHERE id=? AND user_id=?",
                (score_id, session["user_id"]))
    score_data = cur.fetchone()
    conn.close()

    if not score_data:
        flash("Score not found.", "danger")
        return redirect("/dashboard")

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
    flash("Score deleted.", "warning")
    return redirect("/dashboard")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect("/login")

# -----------------------------
# RUN APP (works locally or on a host that sets PORT)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # bind to 0.0.0.0 so platform can reach it
    app.run(host="0.0.0.0", port=port, debug=False)
