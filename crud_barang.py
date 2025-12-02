import tkinter as tk
from tkinter import ttk, messagebox
from koneksi import connect_db

class CrudWindow:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.title("Kelola Produk")
        self.win.geometry("780x520")
        self.win.configure(bg="#f8f3e6")  # Cream background

        # =================== TITLE ===================
        tk.Label(self.win, text="KELOLA PRODUK", font=("Poppins", 18, "bold"),
                 bg="#f8f3e6", fg="#5b3924").pack(pady=15)

        # =================== FORM INPUT ===================
        frame_form = tk.Frame(self.win, bg="#e8d7c3", bd=2, relief="ridge")
        frame_form.pack(pady=10, padx=15, fill="x")

        labels = ["Nama Barang", "Harga", "Stok"]
        for i, text in enumerate(labels):
            tk.Label(frame_form, text=text, bg="#e8d7c3", fg="#5b3924", font=("Poppins", 11)).grid(row=i, column=0, padx=10, pady=8, sticky="w")

        # Entry style
        self.nama_entry = tk.Entry(frame_form, font=("Poppins", 11), relief="flat", bd=3, bg="#fff5e9")
        self.harga_entry = tk.Entry(frame_form, font=("Poppins", 11), relief="flat", bd=3, bg="#fff5e9")
        self.stok_entry = tk.Entry(frame_form, font=("Poppins", 11), relief="flat", bd=3, bg="#fff5e9")

        self.nama_entry.grid(row=0, column=1, pady=8, padx=10, sticky="ew")
        self.harga_entry.grid(row=1, column=1, pady=8, padx=10, sticky="ew")
        self.stok_entry.grid(row=2, column=1, pady=8, padx=10, sticky="ew")

        frame_form.columnconfigure(1, weight=1)

        # =================== BUTTONS ===================
        btn_frame = tk.Frame(self.win, bg="#f8f3e6")
        btn_frame.pack(pady=12)

        self.create_btn(btn_frame, "Tambah", "#8b5e34", self.add_barang, 0)
        self.create_btn(btn_frame, "Update", "#b17457", self.update_barang, 1)
        self.create_btn(btn_frame, "Hapus", "#a64b2a", self.delete_barang, 2)

        # =================== TABLE ===================
        table_frame = tk.Frame(self.win, bg="#f8f3e6")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id", "nama", "harga", "stok")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background="#f4ede4",
                        foreground="#3e2723",
                        rowheight=26,
                        fieldbackground="#f4ede4",
                        font=("Poppins", 10))

        style.configure("Treeview.Heading",
                        font=("Poppins", 11, "bold"),
                        foreground="white",
                        background="#5b3924")

        for col, width in zip(columns, [60, 260, 130, 130]):
            self.table.heading(col, text=col.upper())
            self.table.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vsb.set)

        self.table.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.table.bind("<ButtonRelease-1>", self.fill_form)

        # =================== TAG WARNA ===================
        self.table.tag_configure('hampir_habis', background='#ffcc80')
        self.table.tag_configure('habis', background='#e57373', foreground='white')

        self.selected_id = None
        self.load_data()

    # =================== BUTTON HELPER ===================
    def create_btn(self, parent, text, color, command, col):
        tk.Button(parent, text=text, bg=color, fg="white", font=("Poppins", 11, "bold"),
                  relief="flat", padx=15, pady=5, activebackground=color,
                  activeforeground="white", command=command, bd=4).grid(row=0, column=col, padx=10)

    # =================== LOAD DATA ===================
    def load_data(self):
        for row in self.table.get_children():
            self.table.delete(row)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM barang")
        rows = cursor.fetchall()
        db.close()

        for row in rows:
            stok = row['stok']
            if stok <= 0:
                display_stok = "Habis"
                tag = "habis"
            elif stok < 10:
                display_stok = f"{stok} (Hampir Habis)"
                tag = "hampir_habis"
            else:
                display_stok = stok
                tag = ""

            self.table.insert("", "end", values=(row['id_barang'], row['nama_barang'], row['harga'], display_stok), tags=(tag,))

    # =================== FILL FORM ===================
    def fill_form(self, event):
        selected = self.table.focus()
        if not selected:
            return

        values = self.table.item(selected, "values")
        self.selected_id = values[0]

        self.nama_entry.delete(0, tk.END)
        self.harga_entry.delete(0, tk.END)
        self.stok_entry.delete(0, tk.END)

        self.nama_entry.insert(0, values[1])
        self.harga_entry.insert(0, values[2])
        stok_text = values[3].split()[0] if " " in values[3] else values[3]
        self.stok_entry.insert(0, stok_text)

    # =================== VALIDASI ===================
    def validate_numeric(self, value, field_name):
        if value == "":
            messagebox.showerror("Error", f"{field_name} tidak boleh kosong!")
            return False
        if not value.isdigit():
            messagebox.showerror("Error", f"{field_name} harus berupa ANGKA!")
            return False
        if int(value) < 0:
            messagebox.showerror("Error", f"{field_name} tidak boleh negatif!")
            return False
        return True

    # =================== TAMBAH ===================
    def add_barang(self):
        nama = self.nama_entry.get()
        harga = self.harga_entry.get()
        stok = self.stok_entry.get()

        if nama.strip() == "":
            messagebox.showerror("Error", "Nama barang tidak boleh kosong!")
            return
        if not self.validate_numeric(harga, "Harga"): return
        if not self.validate_numeric(stok, "Stok"): return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO barang (nama_barang, harga, stok) VALUES (%s, %s, %s)", (nama, harga, stok))
        db.commit()
        db.close()

        messagebox.showinfo("Success", "Barang berhasil ditambahkan")
        self.load_data()

    # =================== UPDATE ===================
    def update_barang(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Pilih data dulu")
            return

        nama = self.nama_entry.get()
        harga = self.harga_entry.get()
        stok = self.stok_entry.get()

        if nama.strip() == "":
            messagebox.showerror("Error", "Nama barang tidak boleh kosong!")
            return
        if not self.validate_numeric(harga, "Harga"): return
        if not self.validate_numeric(stok, "Stok"): return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("UPDATE barang SET nama_barang=%s, harga=%s, stok=%s WHERE id_barang=%s",
                       (nama, harga, stok, self.selected_id))
        db.commit()
        db.close()

        messagebox.showinfo("Success", "Barang berhasil diupdate")
        self.load_data()

    # =================== DELETE ===================
    def delete_barang(self):
        if not self.selected_id:
            messagebox.showerror("Error", "Pilih data dulu")
            return

        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus barang?"):
            return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM barang WHERE id_barang=%s", (self.selected_id,))
        db.commit()
        db.close()

        messagebox.showinfo("Success", "Barang berhasil dihapus")
        self.load_data()
        self.selected_id = None
