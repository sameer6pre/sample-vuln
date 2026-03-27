
app = Flask(__name__)

import os  # PRECOGS_FIX: import os to access environment variables
API_KEY = os.getenv("API_KEY")  # PRECOGS_FIX: use environment variable for API key

def get_user_by_name(username):
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    # Fixed SQL injection vulnerability using parameterized query
    query = "SELECT * FROM users WHERE username = ?"  # PRECOGS_FIX: use parameterized query
    cursor.execute(query, (username,))  # PRECOGS_FIX: pass username as a parameter
    result = cursor.fetchall()
    conn.close()
    return result