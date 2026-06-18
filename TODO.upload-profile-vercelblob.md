# TODO: Perbaikan upload foto profile di Vercel (pakai Vercel Blob)

## Step 1 — Tambahkan integrasi Vercel Blob
- Update `requirements.txt` jika perlu.
- Update `app.py`:
  - Tambah konfigurasi endpoint/headers untuk Vercel Blob.
  - Ubah `/profile/upload` agar tidak menyimpan ke `static/profile/`.
  - Upload file ke blob dan simpan `profile_photo_url` ke `data/users.json`.

## Step 2 — Update tampilan
- Update `templates/dashboard.html` agar pakai `profile_photo_url` bila ada.
- Update `templates/mahasiswa.html` agar pakai `profile_photo_url` bila ada.

## Step 3 — Fallback agar tidak 404
- Jika `profile_photo_url` tidak ada, fallback ke `admin.jpeg`.

## Step 4 — Validasi
- Deploy ulang.
- Upload foto dari dashboard.
- Cek di Vercel logs untuk memastikan upload sukses.
- Pastikan URL foto di HTML bisa diakses.

