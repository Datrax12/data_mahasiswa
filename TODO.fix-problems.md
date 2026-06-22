# TODO Fix Problems

## 1) Perbaiki pengaturan dependensi & editor warnings
- [ ] Pastikan `requirements.txt` berisi dependency yang dibutuhkan (flask, werkzeug, cloudinary, python-dotenv sudah dipakai).
- [ ] Tambahkan `python-dotenv` ke `requirements.txt` agar import `dotenv` tidak warning.
- [ ] Pastikan environment virtual/interpreter VSCode mengarah ke environment yang benar (opsional, di luar repo).

## 2) Sinkronkan fitur Cari/Sort/Export
- [ ] Ubah route `/cari`, `/sort`, `/merge-sort`, `/export` agar memakai `mahasiswa_list()` (MySQL) jika tersedia, fallback ke `data/mahasiswa.json`.

## 3) Perbaiki OTP Email configuration
- [ ] Ubah `email_service.py` agar membaca `EMAIL`/`PASSWORD` dari environment variables.
- [ ] Tambahkan validasi env vars; jika tidak ada, lempar error yang jelas.

## 4) Jalankan validasi cepat
- [ ] `python -m py_compile app.py api/app.py api/index.py email_service.py db_filessio.py`
- [ ] Jalankan server dan lakukan test manual singkat.

