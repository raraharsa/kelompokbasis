import tkinter as tk
from tkinter import ttk, messagebox
from koneksi import connect_db


class CrudUser:
    def __init__(self, master):
        self.master = master

        self.win = tk.Toplevel(master)
        self.win.title("Kelola User")
        self.win.geometry("750x450")
        self.win.configure(bg="#f8f6f4")

        # ===================== TITLE =====================
        tk.Label(self.win, text="KELOLA USER", font=("Poppins", 16, "bold"),
                 bg="#f8f6f4", fg="#2c3e50").pack(pady=15)

        # ===================== TABLE =====================
        table_frame = tk.Frame(self.win, bg="#f8f6f4")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id", "nama", "username", "level")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#ecf0f1",
                        foreground="#2c3e50",
                        rowheight=25,
                        fieldbackground="#ecf0f1",
                        font=("Poppins", 10))
        style.configure("Treeview.Heading", font=("Poppins", 11, "bold"), foreground="white", background="#34495e")

        for col in columns:
            self.tree.heading(col, text=col.upper())

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nama", width=180)
        self.tree.column("username", width=180)
        self.tree.column("level", width=100, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ===================== BUTTONS =====================
        btn_frame = tk.Frame(self.win, bg="#f8f6f4")
        btn_frame.pack(pady=10)

        self.create_btn(btn_frame, "Tambah User", "#6a89cc", self.tambah_user, 0)
        self.create_btn(btn_frame, "Edit User", "#e58e26", self.edit_user, 1)
        self.create_btn(btn_frame, "Hapus User", "#eb4d4b", self.hapus_user, 2)

        self.tree.bind("<Double-1>", lambda e: self.edit_user())

        # Load data awal
        self.load_user()

    # ================= BUTTON HELPER =================
    def create_btn(self, parent, text, color, command, col):
        tk.Button(parent, text=text, bg=color, fg="white", font=("Poppins", 11, "bold"),
                  relief="flat", activebackground=color, activeforeground="white",
                  command=command).grid(row=0, column=col, padx=8)

    # ================= LOAD USER =================
    def load_user(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute("SELECT id_user, nama, username, level FROM user ORDER BY id_user ASC")
            rows = cur.fetchall()
            db.close()

            for r in rows:
                self.tree.insert("", "end", values=(
                    r["id_user"], r["nama"], r["username"], r["level"]
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Gagal load user:\n{e}")

    # ================= TAMBAH USER =================
    def tambah_user(self):
        self._form_user(mode="add")

    # ================= EDIT USER =================
    def edit_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih user dulu")
            return

        data = self.tree.item(sel[0])["values"]
        self._form_user(mode="edit", data=data)

    # ================= FORM USER =================
    def _form_user(self, mode, data=None):
        win = tk.Toplevel(self.win)
        win.title("Form User")
        win.geometry("350x320")
        win.configure(bg="#f8f6f4")

        tk.Label(win, text="Nama", bg="#f8f6f4", fg="#2c3e50", font=("Poppins", 11)).pack(pady=5)
        nama_e = tk.Entry(win, font=("Poppins", 11))
        nama_e.pack(fill="x", padx=15)

        tk.Label(win, text="Username", bg="#f8f6f4", fg="#2c3e50", font=("Poppins", 11)).pack(pady=5)
        user_e = tk.Entry(win, font=("Poppins", 11))
        user_e.pack(fill="x", padx=15)

        tk.Label(win, text="Password", bg="#f8f6f4", fg="#2c3e50", font=("Poppins", 11)).pack(pady=5)
        pass_e = tk.Entry(win, show="*", font=("Poppins", 11))
        pass_e.pack(fill="x", padx=15)

        tk.Label(win, text="Level", bg="#f8f6f4", fg="#2c3e50", font=("Poppins", 11)).pack(pady=5)
        level_var = tk.StringVar()
        level_box = ttk.Combobox(win, textvariable=level_var, values=["admin", "kasir"], font=("Poppins", 11))
        level_box.pack(fill="x", padx=15)

        # Jika mode edit → isi datanya
        if mode == "edit" and data:
            id_user, nama, username, level = data
            nama_e.insert(0, nama)
            user_e.insert(0, username)
            level_var.set(level)

        def simpan():
            nama = nama_e.get().strip()
            username = user_e.get().strip()
            password = pass_e.get().strip()
            level = level_var.get().strip()

            if nama == "" or username == "" or level == "":
                messagebox.showwarning("Peringatan", "Lengkapi semua data")
                return

            try:
                db = connect_db()
                cur = db.cursor()

                # --------- TAMBAH ---------
                if mode == "add":
                    if password == "":
                        messagebox.showwarning("Peringatan", "Password tidak boleh kosong")
                        return

                    cur.execute("""
                        INSERT INTO user (nama, username, password, level)
                        VALUES (%s, %s, %s, %s)
                    """, (nama, username, password, level))
                    db.commit()
                    messagebox.showinfo("Sukses", "User ditambahkan!")

                # --------- EDIT ---------
                else:
                    if password == "":
                        cur.execute("""
                            UPDATE user SET nama=%s, username=%s, level=%s
                            WHERE id_user=%s
                        """, (nama, username, level, id_user))
                    else:
                        cur.execute("""
                            UPDATE user SET nama=%s, username=%s, password=%s, level=%s
                            WHERE id_user=%s
                        """, (nama, username, password, level, id_user))

                    db.commit()
                    messagebox.showinfo("Sukses", "User diperbarui!")

                db.close()
                win.destroy()
                self.load_user()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal simpan:\n{e}")

        tk.Button(win, text="Simpan", bg="#6a89cc", fg="white", font=("Poppins", 12, "bold"),
                  relief="flat", activebackground="#6a89cc", activeforeground="white",
                  command=simpan).pack(pady=15)

    # ================= HAPUS USER =================
    def hapus_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih user dulu")
            return

        id_user = self.tree.item(sel[0])["values"][0]

        if not messagebox.askyesno("Konfirmasi", "Hapus user ini?"):
            return

        try:
            db = connect_db()
            cur = db.cursor()
            cur.execute("DELETE FROM user WHERE id_user=%s", (id_user,))
            db.commit()
            db.close()

            messagebox.showinfo("Sukses", "User berhasil dihapus")
            self.load_user()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal hapus user:\n{e}")
