from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "studytracker2025"

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
    # Add link to add_score page
    return """
    <h1>Welcome to Study Tracker Web App!</h1>
    <a href='/add_score'>Add Score</a>
    """

# Step 2: Add Score Route
@app.route("/add_score", methods=["GET", "POST"])
def add_score():
    if request.method == "POST":
        date = request.form["date"]
        subject = request.form["subject"]
        test_type = request.form["test_type"]
        score = float(request.form["score"])
        max_score = float(request.form["max_score"])

        # Save score in database
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        # For now, using user_id = 1 as placeholder
        cur.execute("INSERT INTO scores (user_id, date, subject, test_type, score, max_score) VALUES (?, ?, ?, ?, ?, ?)",
                    (1, date, subject, test_type, score, max_score))
        conn.commit()
        conn.close()

        return redirect("/add_score")  # reload page after adding

    return render_template("add_score.html")

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True) 
