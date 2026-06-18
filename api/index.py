# Vercel entrypoint (serverless)
# Vercel (Python) biasanya jalan dengan "asgi app" callable.

try:
    import app as app_module
    from app import app as flask_app
except Exception as e:
    # Biar errornya jelas di Vercel logs (mengurangi 404 tanpa penyebab)
    raise RuntimeError(f"Failed to import Flask app from app.py: {e}")

# Debug identitas aplikasi yang sedang berjalan (agar terlihat di Vercel logs)
print("[api/index] loaded app module from:", getattr(app_module, "__file__", "<no __file__>"))

# Debug daftar route yang terdaftar
try:
    rules = getattr(flask_app, "url_map", None)
    if rules is not None:
        route_list = [str(r) for r in flask_app.url_map.iter_rules()]
        print("[api/index] routes:", route_list)
        print(
            "[api/index] has /profile/upload?",
            any((r.rule == "/profile/upload") for r in flask_app.url_map.iter_rules()),
        )
except Exception as e:
    print("[api/index] route debug failed:", repr(e))

# Flask adalah WSGI app. Untuk Vercel entrypoint, ekspor langsung Flask app.
# Ini menghindari kebutuhan dependensi ASGI (asgiref) yang bisa gagal di resolver.
app = flask_app
handler = flask_app








