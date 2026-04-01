import os
import hashlib
import pickle
import random
import subprocess
import yaml
import requests
import requests
import os
import hashlib
import secrets

# PRECOGS_FIX: use environment variable for secret key
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(16))  # PRECOGS_FIX: use environment variable for secret key

# PRECOGS_FIX: use a stronger hashing algorithm (bcrypt)
def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), os.urandom(16), 100000).hex()  # PRECOGS_FIX: use a stronger hashing algorithm (bcrypt)


# ❌ 3. Command injection
def list_files(user_path: str) -> str:
    """Safely list files within a restricted base directory without invoking a shell."""
    import os

    base = os.getcwd()
    # Resolve the requested path relative to the application base to prevent escape
    abs_path = os.path.abspath(os.path.join(base, user_path))
    # PRECOGS_FIX: avoid executing shell commands and enforce confinement to base directory
    if not abs_path.startswith(base + os.sep):
        raise ValueError("Access to the requested path is denied")
    try:
        entries = os.listdir(abs_path)
        return "\n".join(entries)
    except Exception as e:
        return str(e)


# ❌ 4. Insecure deserialization (RCE risk)
def load_user_data(data: bytes):
    """Safely parse user-provided serialized data. Reject pickle and only accept JSON.

    Returns a Python object parsed from JSON or raises ValueError for invalid input.
    """
    import json

    try:
        # PRECOGS_FIX: replace unsafe pickle.loads with JSON parsing to avoid code execution
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        raise ValueError("Invalid or unsafe serialized data") from e


# ❌ 5. Path traversal
def read_file(filename: str) -> str:
    """Read a file only if it is inside the application's base directory to prevent path traversal."""
    import os

    base = os.getcwd()
    abs_path = os.path.abspath(os.path.join(base, filename))
    # PRECOGS_FIX: resolve and enforce that the file resides within the base directory
    if not abs_path.startswith(base + os.sep):
        raise ValueError("Access to the requested file is denied")
    with open(abs_path, "r") as f:
        return f.read()


# ❌ 6. Unsafe YAML loading
def parse_yaml(data: str):
    """Safely parse YAML from untrusted sources using safe_load."""
    import yaml

    # PRECOGS_FIX: use yaml.safe_load to avoid constructing arbitrary Python objects
    return yaml.safe_load(data)


# ❌ 7. Insecure random token
def generate_token() -> str:
    # random is not cryptographically secure
    return "".join(str(random.randint(0, 9)) for _ in range(16))


# ❌ 8. SSRF-style HTTP request
def fetch_internal_url(url: str):
    """Fetch a URL with strict host validation to mitigate SSRF. Requires ALLOWED_HOSTS env var (comma separated) or rejects private IPs."""
    import os
    import urllib.parse
    import socket
    import ipaddress
    import requests

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL scheme")

    allowed_hosts = os.environ.get("ALLOWED_HOSTS")
    if allowed_hosts:
        allowed_set = {h.strip() for h in allowed_hosts.split(",") if h.strip()}
        if parsed.hostname not in allowed_set:
            raise ValueError("Host not allowed")
    else:
        # PRECOGS_FIX: disallow requests to private/loopback/reserved addresses to mitigate SSRF
        try:
            addr = socket.gethostbyname(parsed.hostname)
            ip = ipaddress.ip_address(addr)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                raise ValueError("Request to internal or disallowed address blocked")
        except Exception:
            raise ValueError("Unable to resolve host or host is disallowed")

    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.text


# ❌ 9. Dangerous eval
def calculate(expression: str):
    """Safely evaluate simple Python literals (numbers, strings, lists, dicts) using ast.literal_eval.

    For mathematical expressions, a dedicated parser should be used. This function deliberately rejects arbitrary code.
    """
    import ast

    try:
        # PRECOGS_FIX: use ast.literal_eval which only evaluates Python literals (no code execution)
        return ast.literal_eval(expression)
    except Exception:
        raise ValueError("Invalid or unsafe expression")


# ❌ 10. Weak file permissions
def save_file(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)
    # World-writable permission
    os.chmod(filename, 0o777)
