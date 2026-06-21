import os
import json
import mysql.connector


def get_mysql_connection():
    """Buat koneksi ke database filess.io (MySQL-compatible) menggunakan env var."""
    hostname = os.environ.get("FILESS_HOSTNAME") or "tldhhr.h.filess.io"
    database = os.environ.get("FILESS_DATABASE") or "database_mahasiswa_vowelbrain"
    port = int(os.environ.get("FILESS_PORT") or "61031")
    username = os.environ.get("FILESS_USERNAME") or "database_mahasiswa_vowelbrain"
    password = os.environ.get("FILESS_PASSWORD") or "74e0fd679e7242039fa9374ab56b46161b6ee32f"

    return mysql.connector.connect(
        host=hostname,
        user=username,
        password=password,
        database=database,
        port=port,
    )


def test_connection():
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute("SELECT 1+1 AS test")
        row = cur.fetchone()
        return row
    finally:
        try:
            con.close()
        except Exception:
            pass


def ensure_tables():
    """Buat tabel minimal bila belum ada."""
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                profile_photo TEXT NULL
            ) ENGINE=InnoDB;
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nim VARCHAR(64) NOT NULL UNIQUE,
                nama VARCHAR(255) NOT NULL,
                jurusan VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB;
            """
        )
        con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def users_find_by_credentials(username: str, password: str):
    con = get_mysql_connection()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT username, password, email, profile_photo FROM users WHERE username=%s AND password=%s LIMIT 1",
            (username, password),
        )
        return cur.fetchone()
    finally:
        try:
            con.close()
        except Exception:
            pass


def users_find_by_username(username: str):
    con = get_mysql_connection()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(
            "SELECT username, password, email, profile_photo FROM users WHERE username=%s LIMIT 1",
            (username,),
        )
        return cur.fetchone()
    finally:
        try:
            con.close()
        except Exception:
            pass


def users_create(username: str, password: str, email: str, profile_photo=None):
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (username, password, email, profile_photo) VALUES (%s,%s,%s,%s)",
            (username, password, email, profile_photo),
        )
        con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def users_update_profile_photo(username: str, profile_photo):
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE users SET profile_photo=%s WHERE username=%s",
            (profile_photo, username),
        )
        con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def mahasiswa_list():
    con = get_mysql_connection()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT nim, nama, jurusan FROM mahasiswa")
        return cur.fetchall()
    finally:
        try:
            con.close()
        except Exception:
            pass


def mahasiswa_create(nim: str, nama: str, jurusan: str):
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO mahasiswa (nim, nama, jurusan) VALUES (%s,%s,%s)",
            (nim, nama, jurusan),
        )
        con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def mahasiswa_delete(nim: str):
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM mahasiswa WHERE nim=%s", (nim,))
        con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def mahasiswa_update(nim: str, nama: str, jurusan: str):
    con = get_mysql_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "UPDATE mahasiswa SET nama=%s, jurusan=%s WHERE nim=%s",
            (nama, jurusan, nim),
        )
        con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass


def mahasiswa_get_by_nim(nim: str):
    con = get_mysql_connection()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT nim, nama, jurusan FROM mahasiswa WHERE nim=%s LIMIT 1", (nim,))
        return cur.fetchone()
    finally:
        try:
            con.close()
        except Exception:
            pass

