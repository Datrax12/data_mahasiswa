# TODO.filessio-db.md

- [x] Buat modul koneksi & CRUD untuk Filess.io (MySQL-compatible)
  - File: `db_filessio.py`
  - Fungsi: konek, ensure_tables, users_find_by_credentials, users_create, users_update_profile_photo, mahasiswa_list/create/delete/update/get_by_nim

- [ ] Integrasikan ke `app.py`
  - Ganti login/register/dashboard/mahasiswa CRUD dari JSON -> DB
  - Pastikan tetap kompatibel jika env belum diset (fallback ke JSON)

- [ ] Update `requirements.txt`
  - Tambah dependency mysql-connector-python

- [ ] Testing lokal
  - Jalankan server dan pastikan flow register -> verify -> login -> dashboard -> tambah/hapus/edit mahasiswa berjalan

