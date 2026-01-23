import os
import sqlite3
import pickle

def process_user_request(user_input, username, raw_data):
    """
    This function is intentionally vulnerable.
    It contains multiple security issues for testing purposes.
    """

    # 1️⃣ SQL Injection
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user_data = cursor.fetchall()

    # 2️⃣ Command Injection
    command = "echo Processing user && " + user_input
    os.system(command)

    # 3️⃣ Arbitrary Code Execution via eval
    try:
        result = eval(user_input)
    except Exception:
        result = None

    # 4️⃣ Insecure Deserialization
    try:
        data = pickle.loads(raw_data)
    except Exception:
        data = {}

    # 5️⃣ Hardcoded Secret
    api_key = "sk_test_123456789"

    # 6️⃣ Path Traversal
    try:
        with open(f"/tmp/{user_input}.txt", "r") as f:
            file_data = f.read()
    except Exception:
        file_data = ""

    return {
        "user_data": user_data,
        "eval_result": result,
        "deserialized_data": data,
        "file_data": file_data,
        "api_key_used": api_key
    }
