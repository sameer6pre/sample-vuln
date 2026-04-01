import os
import pickle
import sqlite3
import yaml
from flask import Flask, request

def get_user_by_name(username):
    import sqlite3
    try:
        # Use a parameterized query to avoid SQL injection and proper context management
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        # PRECOGS_FIX: use parameterized query to separate SQL from data
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        # Return empty result on DB error to avoid leaking DB internals
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.route("/user")
def user():
    username = request.args.get("username", "test")
    data = get_user_by_name(username)
    return {"data": str(data)}


@app.route("/ping")
def ping():
    import ipaddress
    import subprocess

    ip = request.args.get("ip", "127.0.0.1")
    # PRECOGS_FIX: validate that 'ip' is a literal IP address to prevent shell/command injection
    try:
        # This will raise a ValueError if ip is not a valid IP address
        ipaddress.ip_address(ip)
    except Exception:
        return {"error": "invalid ip"}, 400

    # PRECOGS_FIX: avoid invoking a shell; call ping with a list of args
    try:
        subprocess.run(["ping", "-c", "1", ip], check=False)
    except Exception:
        return {"error": "ping failed"}, 500
    return {"status": "ok"}

@app.route("/load")
def load():
    import io
    import pickle

    raw = request.args.get("data", None)
    if not raw:
        return {"error": "no data"}, 400

    # PRECOGS_FIX: replace unsafe pickle.loads with a restricted unpickler that forbids globals
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # Only allow safe built-in simple types (no execution of arbitrary globals)
            if module == "builtins" and name in ("set", "frozenset", "dict", "list", "tuple", "str", "int", "float", "bool", "NoneType"):
                return getattr(__import__(module), name)
            raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")

    def restricted_loads(s: bytes):
        return RestrictedUnpickler(io.BytesIO(s)).load()

    try:
        raw_bytes = bytes.fromhex(raw)
    except Exception:
        return {"error": "invalid hex"}, 400

    try:
        obj = restricted_loads(raw_bytes)
    except pickle.UnpicklingError:
        return {"error": "unpickling forbidden or failed"}, 400
    except Exception:
        return {"error": "deserialization error"}, 400

    return {"loaded": str(obj)}

@app.route("/yaml")
def yaml_load():
    import yaml

    data = request.args.get("data", "a: 1")
    # PRECOGS_FIX: use yaml.safe_load to avoid constructing arbitrary Python objects
    try:
        loaded = yaml.safe_load(data)
    except Exception:
        return {"error": "invalid yaml"}, 400
    return {"parsed": str(loaded)}