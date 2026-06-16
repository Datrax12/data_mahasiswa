# TODO.vercel-fix-plan (manajemen_mahasiswa)

## Information Gathered
- Repo punya Flask app di `app.py`.
- Ada entrypoint Vercel adapter di `api/index.py` yang mengekspos `app = WsgiToAsgi(flask_app)`.
- `vercel.json` melakukan rewrite **semua** path (`/(.*)`) ke `/api/index`.
- `requirements.txt` hanya berisi `flask`, `werkzeug`, `asgiref`.
- Ada indikasi error deployment: `TODO.md` berjudul `Vercel DEPLOYMENT_NOT_FOUND`.

## Plan
1. Perbaiki `vercel.json` agar tidak rewrite semua route ke `/api/index` (hindari benturan routing Flask vs rewrites Vercel).
2. Pastikan `api/index.py` menjadi entrypoint yang dipakai Vercel dan tidak ada entrypoint lain yang saling bertabrakan.
3. Deploy ulang ke Vercel dan tes akses domain di `/` dan `/login`.

## Dependent Files to be edited
- `vercel.json`
- (opsional setelah diuji) `api/index.py`

## Followup steps
- Setelah deploy: cek log Vercel untuk error import route/templating.
- Cek halaman root domain apakah redirect ke `/login` berjalan.

<ask_followup_question>
Kamu deploy project ini menggunakan Vercel (ada link domain Vercel dan framework “Other/Custom”), atau hanya publish ke GitHub dan berharap web tampil langsung? Kalau sudah Vercel: kirim screenshot/teks error yang muncul di browser (404? blank? DEPLOYMENT_NOT_FOUND?).
</ask_followup_question>

