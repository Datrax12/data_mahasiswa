# TODO.vercel-fix-plan

## Tujuan
Merapikan CSS agar tombol tidak terlihat membesar di Vercel (mis. halaman `/dashboard` dan `/mahasiswa`).

## Langkah
- [x] Analisis CSS global `.btn:hover` dan `.btn:active` yang memakai `transform`.
- [x] Ubah `.btn:active` agar tidak pakai `scale()` (yang bisa terlihat seperti membesar).
- [x] Batasi efek `.btn:hover` supaya tidak mempengaruhi tombol `.verify-btn`.
- [x] Override `.verify-btn` supaya transform dinonaktifkan dan ukuran tipografi dibuat konsisten.
- [x] Deploy ke Vercel (perlu push commit atau redeploy).
- [ ] Cek ulang halaman `/dashboard` dan `/mahasiswa` di Vercel untuk memastikan tombol tidak membesar lagi.


