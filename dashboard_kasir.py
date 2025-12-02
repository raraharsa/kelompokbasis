import tkinter as tk
from tkinter import messagebox
import time
from kasir_window import KasirWindow
from koneksi import connect_db


class DashboardKasir:
    def __init__(self, id_user):
        self.id_user = id_user

        # Ambil nama kasir dari database
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT nama FROM user WHERE id_user = %s", (id_user,))
            self.nama_kasir = cur.fetchone()['nama']
            conn.close()
        except:
            self.nama_kasir = "Kasir"

        self.win = tk.Tk()
        self.win.title("Dashboard Kasir - LUMI.CO")
        self.win.geometry("900x550")
        self.win.configure(bg="#f8f6f4")

        # ---------------- SIDEBAR ----------------
        sidebar = tk.Frame(self.win, bg="#2c3e50", width=230)
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar, text="KASIR LUMI.CO",
            font=("Poppins", 15, "bold"),
            bg="#2c3e50", fg="white", pady=18
        ).pack(fill="x")

        self.create_sidebar_button(sidebar, "🏠  Dashboard", self.show_home)
        self.create_sidebar_button(sidebar, "🛒  Mulai Transaksi", self.buka_transaksi)

        # ===== Tombol Logout =====
        logout_btn = tk.Button(
            sidebar,
            text="  Logout",
            bg="#e74c3c",
            fg="white",
            font=("Poppins", 12, "bold"),
            relief="flat",
            command=self.logout
        )
        logout_btn.pack(fill="x", pady=15, padx=15, side="bottom")

        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="#c0392b"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg="#e74c3c"))

        # ---------------- CONTENT ----------------
        self.content = tk.Frame(self.win, bg="#f8f6f4")
        self.content.pack(expand=True, fill="both")

        self.show_home()
        self.win.mainloop()

    def create_sidebar_button(self, parent, text, command):
        btn = tk.Button(
            parent, text=text,
            font=("Poppins", 12),
            bg="#34495e", fg="white",
            activebackground="#3d566e", activeforeground="white",
            relief="flat",
            anchor="w", padx=18,
            command=command
        )
        btn.pack(fill="x", pady=6, padx=15)

        btn.bind("<Enter>", lambda e: btn.config(bg="#3d566e"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#34495e"))
        return btn

    # ---------------- HOME PAGE ----------------
    def show_home(self):
        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(
            self.content,
            text=f"Halo, {self.nama_kasir}! 👋",
            font=("Poppins", 22, "bold"),
            bg="#f8f6f4", fg="#2c3e50"
        ).pack(pady=(30, 10))

        self.clock_label = tk.Label(
            self.content,
            font=("Poppins", 13),
            bg="#f8f6f4", fg="#2c3e50"
        )
        self.clock_label.pack()
        self.update_clock()

        tk.Label(
            self.content,
            text="Mulai transaksi pelanggan di sini 🔽",
            font=("Poppins", 12),
            bg="#f8f6f4", fg="#34495e"
        ).pack(pady=(5, 18))

        tk.Button(
            self.content,
            text="🛒  Mulai Transaksi",
            bg="#34495e",
            fg="white",
            font=("Poppins", 14, "bold"),
            width=18, relief="flat",
            command=self.buka_transaksi
        ).pack()

    # Real-time Clock
    def update_clock(self):
        self.clock_label.config(text=time.strftime("🕒 %d %B %Y   |   %H:%M:%S"))
        self.clock_label.after(1000, self.update_clock)

    def buka_transaksi(self):
        self.win.withdraw()
        KasirWindow(self.win, self.id_user)
        self.win.deiconify()

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Yakin ingin logout?")
        if confirm:
            self.win.destroy()
            import login
            login.main()
