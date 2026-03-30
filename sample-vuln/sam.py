def process_user_request(user_input, username, raw_data):
    """
    Secure replacement for the original vulnerable function.
    Preserves the same signature and return structure.
    """
    import sqlite3
    import os
    import subprocess
    import ast
    import json
    import re

    user_data = []
    result = None
    data = {}
    file_data = ""
    api_key = None

    # 1. SQL Injection: use parameterized queries
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        # PRECOGS_FIX: Use parameterized query to prevent SQL injection
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchall()
    except Exception:
        user_data = []
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # 2. Command Injection: do not execute user-controlled data via shell
    try:
        # Run a fixed, safe command and do NOT append user_input or use shell=True
        subprocess.run(["echo", "Processing user"], capture_output=True, text=True)
    except Exception:
        pass

    # 3. Arbitrary Code Execution via eval: use safe literal evaluation
    try:
        result = ast.literal_eval(user_input)
    except Exception:
        result = None

    # 4. Insecure Deserialization: do not use pickle.loads on untrusted data; accept JSON only
    try:
        if isinstance(raw_data, (bytes, bytearray)):
            raw_text = raw_data.decode("utf-8", errors="ignore")
        else:
            raw_text = str(raw_data)
        data = json.loads(raw_text)
    except Exception:
        data = {}

    # 5. Hardcoded Secret: read API key from environment (or a secret manager in production)
    api_key = os.environ.get("API_KEY")

    # 6. Path Traversal: sanitize filename and ensure path is inside /tmp
    try:
        safe_name = os.path.basename(user_input)
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,255}", safe_name):
            raise ValueError("unsafe filename")
        file_path = os.path.join("/tmp", safe_name + ".txt")
        # PRECOGS_FIX: Ensure resolved path is within /tmp to prevent path traversal
        if not os.path.realpath(file_path).startswith(os.path.realpath("/tmp") + os.sep):
            raise ValueError("invalid path")
        with open(file_path, "r") as f:
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
