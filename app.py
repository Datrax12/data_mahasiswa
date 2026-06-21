import csv
import json
import os
import random
import re

# Load local .env (development only)
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # dotenv may not be installed in prod; env vars on Vercel are provided automatically
    pass


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
    binary_search,
)

# MySQL (Filess.io compatible)
from db_filessio import (
    ensure_tables as mysql_ensure_tables,
    users_find_by_credentials,
    users_find_by_username,
    users_create,
    users_update_profile_photo,
    mahasiswa_list,
    mahasiswa_create,
    mahasiswa_delete,
    mahasiswa_update,
    mahasiswa_get_by_nim,
)


app = Flask(__name__)
app.secret_key = "mahasiswa123"


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Vercel Blob Storage
# BLOB_STORE_ID: id storage (bucket) di Vercel
BLOB_STORE_ID = os.environ.get("BLOB_STORE_ID", "store_9banKO2BrHyI3z8f")

# BLOB_READ_WRITE_TOKEN: token akses read/write untuk upload.
# NOTE: ini default untuk development; pastikan di Vercel pakai env var agar aman.
BLOB_READ_WRITE_TOKEN = os.environ.get(
    "BLOB_READ_WRITE_TOKEN",
    "vercel_blob_rw_9banKO2BrHyI3z8f_esppA87QdNwaJwJPKwUrbYa3WTc9Nk",
)

# Untuk kompatibilitas kode yang sudah ada
BLOB_STORAGE = os.environ.get("BLOB_STORAGE", BLOB_STORE_ID)

# Untuk menghindari crash saat token env tidak diset.
BLOB_UPLOAD_ENABLED = bool(BLOB_READ_WRITE_TOKEN)





# Pastikan folder data dan upload sudah ada saat aplikasi berjalan
os.makedirs("data", exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure MySQL tables (with fallback to filesystem if DB not configured)
try:
    mysql_ensure_tables()
except Exception as e:
    # tetap jalankan agar dev tidak crash
    print("[mysql] ensure_tables failed, fallback to JSON mode:", repr(e))



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
            temp_user = session["temp_user"].copy()
            if "profile_photo" not in temp_user:
                temp_user["profile_photo"] = None

            # Write to MySQL first, fallback to JSON if MySQL not configured.
            mysql_ok = False
            try:
                users_create(
                    username=temp_user["username"],
                    password=temp_user["password"],
                    email=temp_user["email"],
                    profile_photo=temp_user.get("profile_photo"),
                )
                mysql_ok = True
            except Exception as e:
                print("[mysql] users_create failed, fallback to JSON:", repr(e))

            if not mysql_ok:
                try:
                    with open("data/users.json", "r") as file:
                        users = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError):
                    users = []

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

        # MySQL first
        mysql_ok = False
        try:
            user = users_find_by_credentials(username=username, password=password)
            if user:
                session["username"] = username
                mysql_ok = True
                return redirect("/dashboard")
        except Exception as e:
            print("[mysql] login query failed, fallback to JSON:", repr(e))

        # fallback JSON
        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for user in users:
            if user["username"] == username and user["password"] == password:
                session["username"] = username
                return redirect("/dashboard")

        if not mysql_ok:
            return "Username atau Password Salah"

        return "Username atau Password Salah"

    return render_template("login.html")



# ==========================================
# DASHBOARD
# ==========================================
@app.route("/profile/<path:filename>")
def profile_file(filename):
    # Untuk kompatibilitas, hanya untuk file lokal.
    # Saat profile_photo adalah URL Vercel Blob, frontend akan bypass route ini.
    profile_dir = "static/profile"
    path = os.path.join(profile_dir, filename)
    if not os.path.exists(path):
        abort(404)
    return send_file(path)




@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    # mahasiswa list (MySQL first, fallback JSON)
    data = []
    try:
        rows = mahasiswa_list()  # [{nim, nama, jurusan}, ...]
        data = [{"nim": r.get("nim"), "nama": r.get("nama"), "jurusan": r.get("jurusan")} for r in rows]
    except Exception as e:
        print("[mysql] mahasiswa_list failed, fallback to JSON:", repr(e))
        try:
            with open("data/mahasiswa.json", "r") as file:
                data = json.load(file)
        except Exception:
            data = []

    total_mahasiswa = len(data)

    jurusan_list = [mhs.get("jurusan") for mhs in data if mhs.get("jurusan")]

    if jurusan_list:
        jurusan_terbanyak = Counter(jurusan_list).most_common(1)[0][0]
    else:
        jurusan_terbanyak = "-"

    # Resolve profile photo (MySQL first, fallback JSON)
    profile_photo_filename = "admin.jpeg"
    current_username = session.get("username")
    try:
        u = users_find_by_username(current_username)
        if u and u.get("profile_photo"):
            profile_photo_filename = u.get("profile_photo")
    except Exception as e:
        print("[mysql] users_find_by_username failed, fallback to JSON:", repr(e))
        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)
            for u in users:
                if u.get("username") == current_username and u.get("profile_photo"):
                    profile_photo_filename = u.get("profile_photo")
                    break
        except Exception:
            pass

    return render_template(
        "dashboard.html",
        username=session["username"],
        profile_photo_filename=profile_photo_filename,
        total_mahasiswa=total_mahasiswa,
        rata_ipk="3.50",
        jurusan_terbanyak=jurusan_terbanyak,
    )



# ==========================================
# TAMPIL DATA MAHASISWA
# ==========================================
@app.route("/mahasiswa")
def mahasiswa():

    data_mahasiswa = []
    # MySQL first, fallback JSON
    try:
        rows = mahasiswa_list()
        data_mahasiswa = [
            {"nim": r.get("nim"), "nama": r.get("nama"), "jurusan": r.get("jurusan")}
            for r in rows
        ]
    except Exception as e:
        print("[mysql] mahasiswa_list failed, fallback to JSON:", repr(e))
        try:
            with open("data/mahasiswa.json", "r") as file:
                data_mahasiswa = json.load(file)
        except Exception:
            data_mahasiswa = []

    # Resolve profile photo (MySQL first)
    profile_photo_filename = "admin.jpeg"
    current_username = session.get("username")
    try:
        u = users_find_by_username(current_username)
        if u and u.get("profile_photo"):
            profile_photo_filename = u.get("profile_photo")
    except Exception as e:
        print("[mysql] users_find_by_username failed, fallback to JSON:", repr(e))
        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)
            for u in users:
                if u.get("username") == current_username and u.get("profile_photo"):
                    profile_photo_filename = u.get("profile_photo")
                    break
        except Exception:
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

    # MySQL first, fallback JSON
    mysql_ok = False
    try:
        mhs = Mahasiswa(nim, nama, jurusan)
        mahasiswa_create(nim=mhs.nim, nama=mhs.nama, jurusan=mhs.jurusan)
        mysql_ok = True
    except Exception as e:
        print("[mysql] mahasiswa_create failed, fallback to JSON:", repr(e))

    if not mysql_ok:
        try:
            with open("data/mahasiswa.json", "r") as file:
                data = json.load(file)
        except Exception:
            data = []

        mhs = Mahasiswa(nim, nama, jurusan)
        data.append({"nim": mhs.nim, "nama": mhs.nama, "jurusan": mhs.jurusan})

        with open("data/mahasiswa.json", "w") as file:
            json.dump(data, file, indent=4)

    return redirect("/mahasiswa")



# ==========================================
# HAPUS MAHASISWA (Fixed Route parameter)
# ==========================================
@app.route("/hapus/<nim>")
def hapus(nim):
    mysql_ok = False
    try:
        mahasiswa_delete(nim)
        mysql_ok = True
    except Exception as e:
        print("[mysql] mahasiswa_delete failed, fallback to JSON:", repr(e))

    if not mysql_ok:
        try:
            with open("data/mahasiswa.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data_baru = [mhs for mhs in data if mhs.get("nim") != nim]

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
    if request.method == "POST":
        nama_baru = request.form["nama"]
        jurusan_baru = request.form["jurusan"]

        mysql_ok = False
        try:
            mahasiswa_update(nim=nim, nama=nama_baru, jurusan=jurusan_baru)
            mysql_ok = True
        except Exception as e:
            print("[mysql] mahasiswa_update failed, fallback to JSON:", repr(e))

        if not mysql_ok:
            try:
                with open("data/mahasiswa.json", "r") as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

            for mhs in data:
                if mhs.get("nim") == nim:
                    mhs["nama"] = nama_baru
                    mhs["jurusan"] = jurusan_baru

            with open("data/mahasiswa.json", "w") as file:
                json.dump(data, file, indent=4)

        return redirect("/mahasiswa")

    # GET
    mahasiswa_dipilih = None
    try:
        mhs = mahasiswa_get_by_nim(nim)
    except Exception as e:
        mhs = None
        print("[mysql] mahasiswa_get_by_nim failed, fallback to JSON:", repr(e))

    if mhs:
        mahasiswa_dipilih = {"nim": mhs.get("nim"), "nama": mhs.get("nama"), "jurusan": mhs.get("jurusan")}
    else:
        try:
            with open("data/mahasiswa.json", "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        for m in data:
            if m.get("nim") == nim:
                mahasiswa_dipilih = m
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
            flash("❌ Format foto tidahttps://9banko2brhyi3z8f.private.blob.vercel-storage.comk didukung (jpg/jpeg/png/webp)")
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

            # update profile_photo ke MySQL dulu (kalau bisa)
            mysql_ok = False
            try:
                users_update_profile_photo(username=current_username, profile_photo=blob_object_name)
                mysql_ok = True
            except Exception as e:
                print("[mysql] users_update_profile_photo failed, fallback to JSON:", repr(e))

            if not mysql_ok:
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

        upload_url = f"https://blob.vercel-storage.com/{BLOB_STORE_ID}/{blob_object_name}"


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

        # Simpan URL Blob
        # Catatan: kalau store private, URL "upload_url" mungkin tidak bisa diakses publik.
        # Tetap simpan supaya UI bisa menampilkan (jika store diubah ke public) atau untuk debug.
        # Simpan URL blob untuk ditampilkan. Jika store private, browser tidak bisa akses URL publik.
        # Saat ini kita simpan upload_url; untuk private store, seharusnya pakai signed URL (di luar scope ini).
        blob_public_url = f"https://blob.vercel-storage.com/{blob_object_name}"




        # update MySQL first, fallback to JSON
        mysql_ok = False
        try:
            users_update_profile_photo(username=current_username, profile_photo=blob_public_url)
            mysql_ok = True
        except Exception as e:
            print("[mysql] users_update_profile_photo failed, fallback to JSON:", repr(e))

        if not mysql_ok:
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



