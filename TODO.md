# TODO - Vercel DEPLOYMENT_NOT_FOUND

- [ ] (Analisis) Pastikan penyebabnya bukan link deployment lama (deployment sudah dihapus/expired) atau domain mengarah ke deployment yang salah.
- [ ] (Perbaikan repo) Rekreasi `vercel.json` dalam format plain UTF-8 dan pastikan rewrite path benar ke `/api/index`.
- [ ] (Perbaikan entrypoint) Pastikan hanya ada satu entrypoint yang benar (opsional: bersihkan duplikasi file/alias yang bisa membingungkan Vercel).
- [ ] Deploy ulang project `data_mahasiswa` di Vercel.
- [ ] Setelah deploy sukses, tes akses domain untuk memastikan tidak lagi muncul `DEPLOYMENT_NOT_FOUND`.

