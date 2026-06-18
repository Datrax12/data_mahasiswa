# TODO: Perbaikan upload foto profile di Vercel (pakai Vercel Blob)

## Step 1 — Tambahkan integrasi Vercel Blob
- [x] Update `requirements.txt` (add `requests`).
- [x] Update `app.py`:
  - [x] Tambah konfigurasi token Vercel Blob.
  - [x] Ubah `/profile/upload` agar upload ke Vercel Blob (fallback ke filesystem jika token tidak ada).
  - [x] Simpan URL foto ke `data/users.json` pada field `profile_photo`.


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

