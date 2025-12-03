import pymysql                  # ini untuk menghubungkan Python ke MySQL
from tkinter import messagebox  # ini untuk menampilkan pesan error ke user

# ini adalah konfigurasi database (data login ke MySQL + nama database)
DB_CONFIG = {
    'host': 'localhost',                     # alamat server MySQL
    'user': 'root',                          # username MySQL
    'password': '',                 # password MySQL
    'database': 'tokosaya',                 # nama database yang dipakai
    'cursorclass': pymysql.cursors.DictCursor  # biar hasil query berupa dictionary
}

def connect_db():  # ini fungsinya untuk membuat koneksi ke database
    try:
        return pymysql.connect(**DB_CONFIG)  
        # **DB_CONFIG = memasukkan semua konfigurasi di atas ke fungsi connect
    except Exception as e:
        # kalau gagal, tampilkan pesan error ke user
        messagebox.showerror('Database Error', f'Gagal terhubung ke database:\n{e}')
        raise  # ini untuk menghentikan program dan menampilkan error asli
