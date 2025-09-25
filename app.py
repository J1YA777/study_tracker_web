from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "studytracker2025"  # secret key

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("database.db")
conn.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)""")
conn.execute("""CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    subject TEXT,
    test_type TEXT,
    score REAL,
    max_score REAL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)""")
conn.close()

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return "<h1>Welcome to Study Tracker Web App!</h1>"

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

# (Later you will also add /login, /dashboard, /add_score, /logout here)

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
