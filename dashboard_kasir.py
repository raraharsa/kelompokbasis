import tkinter as tk
from tkinter import messagebox
import time
from kasir_window import KasirWindow
from koneksi import connect_db


class DashboardKasir:
    def __init__(self, id_user):
        self.id_user = id_user

        # Ambil nama kasir
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT nama FROM user WHERE id_user = %s", (id_user,))
            self.nama_kasir = cur.fetchone()['nama']
            conn.close()
        except:
            self.nama_kasir = "Kasir"

        # Window utama
        self.win = tk.Tk()
        self.win.title("Dashboard Kasir - LUMI.CO")
        self.win.geometry("950x580")
        self.win.configure(bg="#F3EDE4")  # krem modern

        # -------------------------------- SIDEBAR --------------------------------
        sidebar = tk.Frame(self.win, bg="#5C4033", width=240)  # coklat gelap elegan
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar, text="LUMI.CO KASIR",
            font=("Poppins", 16, "bold"),
            bg="#5C4033", fg="white", pady=22
        ).pack(fill="x")

        # Tombol Sidebar
        self.create_sidebar_button(sidebar, "🏠   Dashboard", self.show_home)
        self.create_sidebar_button(sidebar, "🛒   Mulai Transaksi", self.buka_transaksi)

        # Tombol Logout
        logout_btn = tk.Button(
            sidebar,
            text="⏻  Logout",
            bg="#AB3E3E",
            fg="white",
            font=("Poppins", 12, "bold"),
            relief="flat",
            padx=10,
            pady=8,
            command=self.logout
        )
        logout_btn.pack(fill="x", pady=25, padx=20, side="bottom")

        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="#8B2F2F"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg="#AB3E3E"))

        # ------------------------------ CONTENT AREA ------------------------------
        self.content = tk.Frame(self.win, bg="#F3EDE4")
        self.content.pack(expand=True, fill="both")

        self.show_home()
        self.win.mainloop()

    # ---------------- BUTTON GENERATOR (SIDEBAR) ----------------
    def create_sidebar_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Poppins", 12),
            bg="#6B4F3A",       # coklat medium
            fg="white",
            activebackground="#7A5A44",
            activeforeground="white",
            relief="flat",
            anchor="w",
            padx=20,
            pady=7,
            command=command
        )
        btn.pack(fill="x", pady=5, padx=20)

        btn.bind("<Enter>", lambda e: btn.config(bg="#7A5A44"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#6B4F3A"))

        return btn

    # ----------------------------- HOME PAGE -----------------------------
    def show_home(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Title Halo
        tk.Label(
            self.content,
            text=f"Halo, {self.nama_kasir}! 👋",
            font=("Poppins", 24, "bold"),
            bg="#F3EDE4",
            fg="#4A3428"
        ).pack(pady=(40, 10))

        self.clock_label = tk.Label(
            self.content,
            font=("Poppins", 13),
            bg="#F3EDE4",
            fg="#4A3428"
        )
        self.clock_label.pack()
        self.update_clock()

        # Subtitle
        tk.Label(
            self.content,
            text="Mulai transaksi pelanggan di sini ⬇️",
            font=("Poppins", 13),
            bg="#F3EDE4",
            fg="#6B4F3A"
        ).pack(pady=(10, 20))

        # Button Mulai Transaksi
        tk.Button(
            self.content,
            text="🛒  Mulai Transaksi",
            bg="#6B4F3A",
            fg="white",
            font=("Poppins", 14, "bold"),
            width=20,
            relief="flat",
            pady=7,
            command=self.buka_transaksi
        ).pack()

    # --------------------- CLOCK ---------------------
    def update_clock(self):
        self.clock_label.config(text=time.strftime("🕒 %d %B %Y | %H:%M:%S"))
        self.clock_label.after(1000, self.update_clock)

    # --------------------- OPEN TRANSACTION ---------------------
    def buka_transaksi(self):
        self.win.withdraw()
        KasirWindow(self.win, self.id_user)
        self.win.deiconify()

    # ------------------------ LOGOUT ------------------------
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Yakin ingin logout?")
        if confirm:
            self.win.destroy()
            import login
            login.main()
