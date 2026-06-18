import csv
import json
import os
import random
import re

from collections import Counter
from io import BytesIO

from flask import Flask, flash, redirect, render_template, request, session, send_file, abort
from werkzeug.utils import secure_filename
from models import Mahasiswa


from email_service import send_otp
from utils import (
    bubble_sort,
    linear_search,
    merge_sort,
    binary_search
)

app = Flask(__name__)
app.secret_key = "mahasiswa123"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Vercel Blob Storage
# BLOB_STORAGE: nama storage (bucket) di Vercel, mis. data-mahasiswa-9q7l-blob
BLOB_STORAGE = os.environ.get("BLOB_STORAGE", "data-mahasiswa-9q7l-blob")

# BLOB_READ_WRITE_TOKEN: token akses read/write untuk upload.
# Pastikan env var di Vercel ada. (Nama env var bisa BLOB_READ_WRITE_TOKEN atau yang lain.)
BLOB_READ_WRITE_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN", "")

# Untuk menghindari crash saat token env tidak diset.
BLOB_UPLOAD_ENABLED = bool(BLOB_READ_WRITE_TOKEN)




# Pastikan folder data dan upload sudah ada saat aplikasi berjalan
os.makedirs("data", exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    return redirect("/login")


# ==========================================
# REGISTER
# ==========================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # Handle profile photo upload (optional)
        profile_photo_filename = None
        if "profile_photo" in request.files:
            file = request.files["profile_photo"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                # keep extension
                _, ext = os.path.splitext(filename)
                if ext:
                    profile_photo_filename = f"{secure_filename(username)}{ext.lower()}"
                else:
                    profile_photo_filename = f"{secure_filename(username)}.jpg"

                os.makedirs("static/profile", exist_ok=True)
                file.save(os.path.join("static/profile", profile_photo_filename))

        otp = str(random.randint(100000, 999999))

        session["otp"] = otp
        session["temp_user"] = {
            "username": username,
            "password": password,
            "email": email,
            "profile_photo": profile_photo_filename,
        }

        send_otp(email, otp)
        return redirect("/verify")

    return render_template("register.html")


# ==========================================
# VERIFIKASI OTP
# ==========================================
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        user_otp = request.form["otp"]

        if user_otp == session.get("otp"):
            try:
                with open("data/users.json", "r") as file:
                    users = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                users = []

            temp_user = session["temp_user"].copy()
            # ensure field exists for older sessions
            if "profile_photo" not in temp_user:
                temp_user["profile_photo"] = None

            users.append(temp_user)

            with open("data/users.json", "w") as file:
                json.dump(users, file, indent=4)

            # login otomatis setelah OTP berhasil
            session["username"] = temp_user["username"]
            return redirect("/dashboard")

        flash("❌ OTP salah. Silakan coba lagi.", "danger")
        return redirect("/verify")


    return render_template("verify_otp.html")


# ==========================================
# RESEND OTP
# ==========================================
@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    temp_user = session.get("temp_user")
    if not temp_user or not temp_user.get("email"):
        flash("❌ Sesi OTP tidak valid. Silakan daftar ulang.", "danger")
        return redirect("/register")

    otp = str(random.randint(100000, 999999))
    session["otp"] = otp

    try:
        send_otp(temp_user["email"], otp)
        flash("✅ OTP berhasil dikirim ulang. Silakan masukkan kode terbaru.", "success")
    except Exception:
        flash("❌ Gagal mengirim ulang OTP. Coba lagi nanti.", "danger")

    return redirect("/verify")



# ==========================================
# LOGIN
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for user in users:
            if user["username"] == username and user["password"] == password:
                session["username"] = username
                return redirect("/dashboard")

        return "Username atau Password Salah"

    return render_template("login.html")


# ==========================================
# DASHBOARD
# ==========================================
@app.route("/profile/<path:filename>")
def profile_file(filename):
    # Serve profile images through Flask route.
    # This avoids reliance on Vercel static persistence.
    profile_dir = "static/profile"
    try:
        return send_file(os.path.join(profile_dir, filename))
    except Exception:
        abort(404)


@app.route("/dashboard")
def dashboard():


    if "username" not in session:
        return redirect("/login")

    try:

        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)

    except:
        data = []

    total_mahasiswa = len(data)

    jurusan_list = []

    for mhs in data:
        jurusan_list.append(mhs["jurusan"])

    if jurusan_list:

        jurusan_terbanyak = Counter(
            jurusan_list
        ).most_common(1)[0][0]

    else:

        jurusan_terbanyak = "-"

    # Resolve profile photo
    profile_photo_filename = "admin.jpeg"
    try:
        with open("data/users.json", "r") as file:
            users = json.load(file)
        current_username = session["username"]
        for u in users:
            if u.get("username") == current_username:
                if u.get("profile_photo"):
                    profile_photo_filename = u.get("profile_photo")
                break
    except:
        pass

    return render_template(
        "dashboard.html",
        username=session["username"],
        profile_photo_filename=profile_photo_filename,
        total_mahasiswa=total_mahasiswa,
        rata_ipk="3.50",
        jurusan_terbanyak=jurusan_terbanyak
    )


# ==========================================
# TAMPIL DATA MAHASISWA
# ==========================================
@app.route("/mahasiswa")
def mahasiswa():

    try:
        with open("data/mahasiswa.json", "r") as file:
            data_mahasiswa = json.load(file)

    except:
        data_mahasiswa = []

    # Resolve profile photo (same logic as dashboard)
    profile_photo_filename = "admin.jpeg"
    try:
        with open("data/users.json", "r") as file:
            users = json.load(file)
        current_username = session.get("username")
        for u in users:
            if u.get("username") == current_username:
                if u.get("profile_photo"):
                    profile_photo_filename = u.get("profile_photo")
                break
    except:
        pass

    return render_template(
        "mahasiswa.html",
        mahasiswa=data_mahasiswa,
        username=session.get("username", "Admin"),
        profile_photo_filename=profile_photo_filename,
    )



# ==========================================
# TAMBAH MAHASISWA
# ==========================================
@app.route("/tambah", methods=["POST"])
def tambah():

    nim = request.form["nim"]
    nama = request.form["nama"]
    jurusan = request.form["jurusan"]

    if not re.match(r"^\d+$", nim):

        flash("❌ NIM hanya boleh berisi angka!")
        return redirect("/mahasiswa")

    try:

        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)

    except:
        data = []

    mhs = Mahasiswa(
        nim,
        nama,
        jurusan
    )

    data.append({
        "nim": mhs.nim,
        "nama": mhs.nama,
        "jurusan": mhs.jurusan
    })

    with open("data/mahasiswa.json", "w") as file:
        json.dump(data, file, indent=4)

    return redirect("/mahasiswa")


# ==========================================
# HAPUS MAHASISWA (Fixed Route parameter)
# ==========================================
@app.route("/hapus/<nim>")
def hapus(nim):
    try:
        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data_baru = [mhs for mhs in data if mhs["nim"] != nim]

    with open("data/mahasiswa.json", "w") as file:
        json.dump(data_baru, file, indent=4)

    return redirect("/mahasiswa")


# ==========================================
# CARI MAHASISWA
# ==========================================
@app.route("/cari", methods=["POST"])
def cari():

    keyword = request.form["keyword"]
    metode = request.form["metode"]

    try:

        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)

    except:
        data = []

    if metode == "binary":

        hasil = binary_search(data, keyword)

    else:

        hasil = linear_search(data, keyword)

    return render_template(
        "mahasiswa.html",
        mahasiswa=hasil,
        metode=metode,
        total_hasil=len(hasil),
        keyword=keyword
    )


# ==========================================
# SORT DATA (BUBBLE SORT)
# ==========================================
@app.route("/sort")
def sort_data():
    try:
        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data = bubble_sort(data)
    return render_template("mahasiswa.html", mahasiswa=data)


# ==========================================
# SORT DATA (MERGE SORT)
# ==========================================
@app.route("/merge-sort")
def merge_sort_data():
    try:
        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data = merge_sort(data)
    return render_template("mahasiswa.html", mahasiswa=data)


# ==========================================
# EXPORT CSV (Download)
# ==========================================
@app.route("/export")
def export_csv():
    try:
        with open("data/mahasiswa.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Generate CSV in-memory so it works reliably on serverless/Vercel.
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(["NIM", "Nama", "Jurusan"])

    for mhs in data:
        # Avoid KeyError if data structure is unexpected
        nim = mhs.get("nim", "")
        nama = mhs.get("nama", "")
        jurusan = mhs.get("jurusan", "")
        writer.writerow([nim, nama, jurusan])

    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="mahasiswa_export.csv",
    )



# ==========================================
# EDIT MAHASISWA (Fixed Route parameter)
# ==========================================
@app.route("/edit/<nim>", methods=["GET", "POST"])
def edit(nim):
    try:
        with open("data/mahasiswa.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    if request.method == "POST":
        nama_baru = request.form["nama"]
        jurusan_baru = request.form["jurusan"]

        for mhs in data:
            if mhs["nim"] == nim:
                mhs["nama"] = nama_baru
                mhs["jurusan"] = jurusan_baru

        with open("data/mahasiswa.json", "w") as file:
            json.dump(data, file, indent=4)

        return redirect("/mahasiswa")

    mahasiswa_dipilih = None
    for mhs in data:
        if mhs["nim"] == nim:
            mahasiswa_dipilih = mhs
            break

    return render_template("edit.html", mahasiswa=mahasiswa_dipilih)


# ==========================================
# IMPORT CSV
# ==========================================
@app.route("/import", methods=["POST"])
def import_csv():
    try:
        file = request.files["file"]

        if file.filename == "":
            return "Tidak ada file yang dipilih"

        if not file.filename.endswith(".csv"):
            return "File harus berformat CSV"

        data_mahasiswa = []
        csv_file = file.stream.read().decode("utf-8").splitlines()
        reader = csv.DictReader(csv_file)

        kolom_wajib = ["NIM", "Nama", "Jurusan"]
        if not all(kolom in reader.fieldnames for kolom in kolom_wajib):
            return "Format CSV salah. Kolom harus: NIM, Nama, Jurusan"

        for row in reader:
            if not row["NIM"].isdigit():
                return f"NIM tidak valid: {row['NIM']}"

            data_mahasiswa.append(
                {"nim": row["NIM"], "nama": row["Nama"], "jurusan": row["Jurusan"]}
            )

        with open("data/mahasiswa.json", "w") as file_json:
            json.dump(data_mahasiswa, file_json, indent=4)

        return redirect("/mahasiswa")

    except UnicodeDecodeError:
        return "File harus disimpan dengan encoding UTF-8"
    except KeyError:
        return "Kolom CSV tidak sesuai"
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"


# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ==========================================
# FITUR
# ==========================================
@app.route("/fitur")
def fitur():
    return render_template("fitur.html")

# ==========================================
# PROFILE PHOTO UPLOAD (After login)
# ==========================================
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@app.route("/profile/upload", methods=["POST"])
def upload_profile_photo():
    try:
        print("[profile/upload] start")
        if "username" not in session:
            return redirect("/login")

        file = request.files.get("profile_photo")
        if not file or not file.filename:
            flash("❌ Pilih file foto terlebih dahulu")
            return redirect(request.referrer or "/dashboard")

        filename = secure_filename(file.filename)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            flash("❌ Format foto tidak didukung (jpg/jpeg/png/webp)")
            return redirect(request.referrer or "/dashboard")

        current_username = session["username"]
        blob_object_name = f"{secure_filename(current_username)}{ext}"

        # Jika token belum ada, fallback ke filesystem agar tidak error total.
        if not BLOB_READ_WRITE_TOKEN:
            print("[profile/upload] BLOB_READ_WRITE_TOKEN is empty -> fallback filesystem")
            profile_dir = "static/profile"
            os.makedirs(profile_dir, exist_ok=True)
            target_path = os.path.join(profile_dir, blob_object_name)
            file.save(target_path)

            with open("data/users.json", "r") as f:
                users = json.load(f)

            updated = False
            for u in users:
                if u.get("username") == current_username:
                    u["profile_photo"] = blob_object_name
                    updated = True
                    break

            if not updated:
                users.append({"username": current_username, "password": "", "email": "", "profile_photo": blob_object_name})

            with open("data/users.json", "w") as f:
                json.dump(users, f, indent=4)

            flash("✅ Foto profile berhasil diperbarui (local)")
            return redirect(request.referrer or "/dashboard")

        # Upload ke Vercel Blob via REST
        import requests

        blob_url = f"https://blob.vercel-storage.com/{blob_object_name}"
        upload_url = f"https://blob.vercel-storage.com/{BLOB_STORAGE}/{blob_object_name}"

        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
        }

        file_bytes = file.read()
        # kembalikan cursor agar tidak error di beberapa server
        try:
            file.stream.seek(0)
        except Exception:
            pass

        print("[profile/upload] uploading to blob", upload_url)
        resp = requests.put(
            upload_url,
            headers=headers,
            data=file_bytes,
            timeout=30,
        )

        if resp.status_code >= 400:
            raise RuntimeError(f"Vercel Blob upload failed: {resp.status_code} - {resp.text}")

        # Simpan URL ke users.json agar tampilan pakai URL (bukan filesystem)
        blob_public_url = blob_url

        with open("data/users.json", "r") as f:
            users = json.load(f)

        updated = False
        for u in users:
            if u.get("username") == current_username:
                u["profile_photo"] = blob_public_url
                updated = True
                break

        if not updated:
            users.append({"username": current_username, "password": "", "email": "", "profile_photo": blob_public_url})

        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=4)

        flash("✅ Foto profile berhasil diperbarui")
        return redirect(request.referrer or "/dashboard")

    except Exception as e:
        import traceback
        print("[profile/upload] ERROR:", repr(e))
        print(traceback.format_exc())
        return ("Internal Server Error (debug): " + str(e), 500)



# ==========================================
# GLOBAL ERROR HANDLER
# ==========================================
# Pastikan traceback/penyebab muncul di log (terutama untuk deploy serverless/Vercel)
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback

    # Log exception + traceback
    print("[global] Unhandled exception:", repr(e))
    print(traceback.format_exc())

    # Pastikan user tidak mendapatkan respon blank saat request dari halaman HTML
    try:
        if request and request.path and "login" in request.path:
            return ("Internal Server Error", 500)

        # Jika user sudah login, arahkan ke dashboard, kalau belum ke login
        if "username" in session:
            flash("❌ Terjadi kesalahan pada server. Coba lagi.", "danger")
            return redirect("/dashboard")
        flash("❌ Terjadi kesalahan pada server. Silakan login ulang.", "danger")
        return redirect("/login")
    except Exception:
        # Fallback sederhana
        return ("Internal Server Error", 500)


@app.errorhandler(500)
def handle_500(e):
    # e bisa berupa string atau exception object
    print("[global] 500 error:", repr(e))
    return ("Internal Server Error", 500)


# ==========================================
# RUN APPLICATION
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)



