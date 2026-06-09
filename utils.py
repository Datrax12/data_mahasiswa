# Linear Search untuk mencari mahasiswa berdasarkan nama
def linear_search(data, keyword):
    """Cari mahasiswa berdasarkan nama (substring match)."""
    hasil = []
    keyword_l = keyword.lower()

    for item in data:
        if keyword_l in item.get("nama", "").lower():
            hasil.append(item)

    return hasil


# Bubble Sort untuk mencari mahasiswa berdasarkan nama
def bubble_sort(data):
    """Urutkan berdasarkan nama (ascending)."""
    n = len(data)

    for i in range(n):
        for j in range(0, n - i - 1):
            if data[j]["nama"] > data[j + 1]["nama"]:
                data[j], data[j + 1] = data[j + 1], data[j]

    return data


# MergeSort untuk mencari mahasiswa berdasarkan nama
def merge_sort(data):

    if len(data) <= 1:
        return data

    tengah = len(data) // 2

    kiri = merge_sort(data[:tengah])
    kanan = merge_sort(data[tengah:])

    hasil = []

    i = 0
    j = 0

    while i < len(kiri) and j < len(kanan):

        if int(kiri[i]["nim"]) < int(kanan[j]["nim"]):

            hasil.append(kiri[i])
            i += 1

        else:

            hasil.append(kanan[j])
            j += 1

    hasil.extend(kiri[i:])
    hasil.extend(kanan[j:])

    return hasil


# Binary Search untuk mencari mahasiswa berdasarkan nama
def binary_search(data, keyword):
    """Binary search mahasiswa berdasarkan nama. Mengembalikan list (bisa 1 atau lebih)."""
    data_sorted = sorted(data, key=lambda x: x["nama"].lower())
    keyword_l = keyword.lower()

    kiri = 0
    kanan = len(data_sorted) - 1

    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        nama = data_sorted[tengah]["nama"].lower()

        if nama == keyword_l:
            return [data_sorted[tengah]]
        elif nama < keyword_l:
            kiri = tengah + 1
        else:
            kanan = tengah - 1

    return []

