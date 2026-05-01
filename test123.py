# test_vuln.py — deliberately bad code
import sqlite3

def get_user(username):
    conn = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE name = '{username}'"  # SQL injection
    return conn.execute(query).fetchone()

SECRET_KEY = "hardcoded-secret-123"  # hard-coded secret
