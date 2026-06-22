# TODO: Fix "BLOB_READ_WRITE_TOKEN is not set" / token mismatch di Vercel

## Information gathered
- Aplikasi Flask punya endpoint `POST /profile/upload` yang upload foto profile ke **Vercel Blob**.
- Error yang muncul: `Internal Server Error (debug): BLOB_READ_WRITE_TOKEN is not set on serverless runtime. Set env vars di Vercel (BLOB_STORE_ID & BLOB_READ_WRITE_TOKEN).`
- Di `app.py` nilai env var diambil dari `os.environ`:
  - `BLOB_STORE_ID`
  - `BLOB_READ_WRITE_TOKEN`
- Jika `BLOB_READ_WRITE_TOKEN` tidak ada, kode akan meng-raise `RuntimeError` sehingga server mengembalikan HTTP 500.
- `vercel.json` hanya berisi rewrites untuk `/api/*`.

## Plan
1. Pastikan di Vercel, Environment Variables sudah di-set:
   - `BLOB_STORE_ID`
   - `BLOB_READ_WRITE_TOKEN`
   dan nilainya sesuai pasangan yang benar (token harus cocok dengan store).
2. Set variabel tersebut pada scope yang benar:
   - biasanya **Production** dan juga **Preview** (kalau pakai preview deploy), atau minimal environment yang sedang diuji.
3. Redeploy setelah setting env vars.
4. Verifikasi di runtime:
   - refresh halaman dan coba upload ulang.
   - pastikan tidak kembali error 500.

## Dependent files to be edited
- Tidak perlu edit kode untuk langkah env vars.

## Followup steps (testing)
- Coba upload foto dari halaman profile upload.
- Jika masih error, cek log Vercel untuk detail:
  - Apakah token kosong (env vars belum masuk), atau token tidak cocok (token mismatch).
- Jika perlu, baru dilakukan perbaikan kode untuk memberikan pesan kesalahan yang lebih spesifik (tanpa mematikan request).

