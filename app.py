from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

onn = sqlite3.connect("database.db")

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

@app.route("/")
def home():
    return "<h1>Welcome to Study Tracker Web App!</h1>"

if __name__ == "__main__":
    app.run(debug=True) 
