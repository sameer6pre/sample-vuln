
@app.route("/load")
from flask import request

def load():
    raw = request.args.get("data", None)
    if not raw:
        return {"error": "no data"}, 400

    import json, binascii
    try:
        # PRECOGS_FIX: do NOT use pickle.loads on untrusted data; expect JSON encoded in hex instead
        data_bytes = bytes.fromhex(raw)
    except (ValueError, TypeError):
        return {"error": "invalid hex data"}, 400

    try:
        obj = json.loads(data_bytes.decode("utf-8"))
    except Exception:
        return {"error": "failed to parse JSON payload; sending pickles is not allowed"}, 400

    return {"loaded": str(obj)}