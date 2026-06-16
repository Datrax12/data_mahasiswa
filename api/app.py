"""ASGI entrypoint untuk Flask di Vercel.

Catatan:
- Vercel akan mencari handler/default export tertentu.
- Kita sediakan beberapa nama callable agar kompatibel.
"""

from asgiref.wsgi import WsgiToAsgi

from app import app as flask_app

asgi_app = WsgiToAsgi(flask_app)

# Beberapa alias agar Vercel/APM bisa menemukan callable
app = asgi_app
handler = asgi_app

