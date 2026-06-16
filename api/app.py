"""Wrapper agar tidak ada Flask/entrypoint duplikat.

Project ini sudah punya entrypoint Vercel di `api/index.py`.
File ini dibuat supaya kalau ada tooling/deploy yang mengarah ke `api/app.py`,
semuanya tetap memakai Flask app yang sama (root `app.py`).
"""

from app import app as flask_app

app = flask_app
handler = flask_app


