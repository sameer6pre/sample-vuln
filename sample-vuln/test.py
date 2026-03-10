
# ❌ 3. Command injection
def list_files(user_path: str) -> str:
    import os
    # PRECOGS_FIX: avoid shell use and rely on filesystem APIs to prevent command injection
    try:
        entries = []
        with os.scandir(user_path) as it:
            for e in it:
                entries.append(e.name)
        return "\n".join(entries)
    except Exception as exc:
        return f"Error: {exc}"