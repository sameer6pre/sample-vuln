
@app.route("/ping")
from flask import request

@app.route("/ping")
def ping():
    ip = request.args.get("ip", "127.0.0.1")
    import ipaddress, subprocess
    try:
        # PRECOGS_FIX: validate the IP address strictly using ipaddress
        ip_obj = ipaddress.ip_address(ip)
    except Exception:
        return {"error": "invalid ip"}, 400

    # PRECOGS_FIX: call ping without invoking a shell, pass arguments as a list
    try:
        subprocess.run(["ping", "-c", "1", str(ip_obj)], check=False)
    except FileNotFoundError:
        return {"error": "ping command not available"}, 500

    return {"status": "ok"}