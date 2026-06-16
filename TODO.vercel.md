# Vercel Fix Checklist (manajemen_mahasiswa)

- [x] Tambahkan `vercel.json` untuk rewrite semua path ke `/api/*`.
- [x] Tambahkan entrypoint Vercel serverless: `api/index.py` (adapter WSGI->ASGI).
- [x] Tambahkan `requirements.txt` (flask, werkzeug, wsgi-to-asgi).
- [ ] Verifikasi tidak ada route 404 di Vercel setelah deploy ulang.
- [ ] Pastikan Vercel mengaktifkan install requirements (atau sesuaikan `package.json` jika dibutuhkan).
- [ ] Pastikan static file & template berjalan (pastikan `static/` dan `templates/` terbundle).

