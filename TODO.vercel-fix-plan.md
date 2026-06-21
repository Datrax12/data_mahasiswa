# TODO.vercel-fix-plan.md

## Problem
IDE/VSCode menampilkan error import yang tidak bisa di-resolve: 
- werkzeug.utils
- flask
- requests
- mysql.connector

Ini biasanya terjadi karena:
- virtual environment belum dipakai di VSCode
- dependency di `requirements.txt` tidak terpasang
- workspace belum mengarah ke interpreter Python yang benar

## Plan
1) Pastikan `requirements.txt` berisi semua dependency yang dibutuhkan.
2) Buat virtual environment lokal (venv) dan pasang dependency.
3) Set VSCode interpreter ke venv tersebut.
4) (Opsional) Pastikan modul tambahan untuk mypy/pyright (kalau dipakai) mendeteksi interpreter.

## Follow-up
- Jalankan `python -c "import flask, requests, mysql.connector"` untuk validasi.
- Jalankan server lokal: `python app.py`.

