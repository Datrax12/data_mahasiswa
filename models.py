class User:

    def __init__(self, username, password, email):

        self.username = username
        self.__password = password
        self.email = email

    def get_password(self):
        return self.__password


class Mahasiswa:

    def __init__(self, nim, nama, jurusan):

        self.nim = nim
        self.nama = nama
        self.jurusan = jurusan

    def tampilkan(self):

        return f"{self.nim} - {self.nama}"


class MahasiswaAktif(Mahasiswa):

    def tampilkan(self):

        return f"Mahasiswa Aktif : {self.nama}"


class MahasiswaCuti(Mahasiswa):

    def tampilkan(self):

        return f"Mahasiswa Cuti : {self.nama}"