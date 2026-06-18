# Vercel entrypoint (serverless)
# Vercel (Python) biasanya jalan dengan "asgi app" callable.

try:
    from app import app as flask_app
except Exception as e:
    # Biar errornya jelas di Vercel logs (mengurangi 404 tanpa penyebab)
    raise RuntimeError(f"Failed to import Flask app from app.py: {e}")

# Flask adalah WSGI app. Untuk Vercel entrypoint, ekspor langsung Flask app.
# Ini menghindari kebutuhan dependensi ASGI (asgiref) yang bisa gagal di resolver.
app = flask_app
handler = flask_app







