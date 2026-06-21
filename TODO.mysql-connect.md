# TODO.mysql-connect

## Plan
- [ ] Integrate `db_filessio.py` into `app.py` to use MySQL as single source of truth (users + mahasiswa)
- [ ] Update routes:
  - [ ] `/register` & `/verify`: write pending user into MySQL after OTP success
  - [ ] `/login`: authenticate against MySQL
  - [ ] `/dashboard`: read mahasiswa list from MySQL + user profile_photo from MySQL
  - [ ] `/mahasiswa`: read mahasiswa list from MySQL
  - [ ] `/tambah`: insert mahasiswa into MySQL
  - [ ] `/hapus/<nim>`: delete mahasiswa by nim
  - [ ] `/edit/<nim>`: update mahasiswa
  - [ ] `/import`: bulk insert mahasiswa from CSV (truncate/replace or upsert decision)
  - [ ] `/export`: export mahasiswa from MySQL
  - [ ] `/profile/upload`: update `profile_photo` in MySQL (still using Vercel Blob when configured)
- [ ] Remove/stop reading/writing `data/users.json` and `data/mahasiswa.json` from core flows (optional fallback kept only if desired)
- [ ] Add startup call to `ensure_tables()` (guarded so it doesn't crash local dev)
- [ ] Ensure NIM uniqueness errors are handled (flash message)

## Testing
- [ ] Set env vars (FILESS_*) locally
- [ ] Run `python app.py` and test register/login/CRUD
- [ ] Run quick DB test: `test_connection()` (optional endpoint/CLI)

