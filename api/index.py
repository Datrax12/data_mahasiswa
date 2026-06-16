# Vercel entrypoint (serverless)
# Vercel (Python) biasanya jalan dengan "asgi app" callable.

from asgiref.wsgi import WsgiToAsgi

try:
    from app import app as flask_app
except Exception as e:
    # Biar errornya jelas di Vercel logs (mengurangi 404 tanpa penyebab)
    raise RuntimeError(f"Failed to import Flask app from app.py: {e}")

asgi_app = WsgiToAsgi(flask_app)

# Vercel akan mencari callable/export bernama `app`.
# Jadi kita expose ASGI callable langsung.
app = asgi_app





