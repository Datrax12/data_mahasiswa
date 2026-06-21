# Plan: Fix `Vercel Blob upload failed: 403 Token mismatch`

## Information gathered
- Root cause strongly linked to Vercel Blob auth configuration. Code in `app.py` uploads to Vercel Blob using:
  - `upload_url = https://blob.vercel-storage.com/{BLOB_STORE_ID}/{blob_object_name}`
  - `headers = { Authorization: Bearer {BLOB_READ_WRITE_TOKEN} }`
- Error observed: `403 - {"error":{"code":"forbidden","message":"Token mismatch"}}`.
- Templates show profile image is rendered either from:
  - `static/profile/<filename>` route (`/profile/<filename>`) OR
  - a URL if it contains `http://` / `https://`.
- Current `templates/dashboard.html` and `templates/mahasiswa.html` expect the server to provide `profile_photo_filename` which can be either a filename or a full URL.
- `app.py` currently builds `blob_public_url = https://blob.vercel-storage.com/{blob_object_name}` and writes it into MySQL/`data/users.json` as `profile_photo`.
- Local environment does not set `BLOB_STORE_ID` / `BLOB_READ_WRITE_TOKEN` (env vars missing), but the error occurs on Vercel, implying Vercel env vars exist but are inconsistent (token doesn’t belong to the store id being used), or the store id is wrong.

## Plan
1) Add safe debug logging (no token value) in `/profile/upload`:
   - Log whether `BLOB_STORE_ID` and `BLOB_READ_WRITE_TOKEN` are set.
   - Log which upload URL base is used (include store id but not token).
2) Fail fast with a clearer error if store id or token missing/invalid:
   - Return 500 with message: set `BLOB_STORE_ID` and `BLOB_READ_WRITE_TOKEN` correctly for the same Vercel Blob store.
3) Fix URL construction consistency:
   - Use the same scheme/base for the stored photo URL as used for uploads.
   - Store `profile_photo` as a full URL to allow template to render it.
   - Ensure the “public URL” includes the store id when required (we’ll make it configurable: `BLOB_PUBLIC_BASE_URL` env var with a safe default).
4) Update templates (if needed) to use `profile_photo_url` consistently (currently they check `profile_photo_filename`).
5) Redeploy and test:
   - Upload from `/dashboard`.
   - Verify Vercel logs show consistent store id and upload_url.

## Dependent files to edit
- `app.py`
- `templates/dashboard.html` (only if we change the variable name)
- `templates/mahasiswa.html` (only if we change the variable name)

## Followup steps
- `vercel deploy` (or your existing deploy method).
- Perform one upload test and confirm:
  - No 403.
  - `profile_photo` stored and displayed correctly.

<ask_followup_question>
Minta Anda setuju untuk dilakukan perbaikan kode di `app.py` berikut: tambahkan logging aman + validasi store id/token, lalu buat URL publik berbasis env `BLOB_PUBLIC_BASE_URL` (default tetap placeholder lama) agar upload & tampilan konsisten. Setelah ini, redeploy dan upload sekali untuk memverifikasi error hilang.
</ask_followup_question>

