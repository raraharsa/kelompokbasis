import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

from crud_barang import CrudWindow
from crud_user import CrudUser
from riwayat_admin import RiwayatAdminWindow
from koneksi import connect_db


class AdminDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dashboard Admin")
        self.root.geometry("980x600")
        self.root.configure(bg="#f2f4f7")

        # ---------------- SIDEBAR ----------------
        sidebar = tk.Frame(self.root, bg="#1f2937", width=230)
        sidebar.pack(side="left", fill="y")

        title = tk.Label(
            sidebar, text="ADMIN LUMI.CO",
            font=("Poppins", 16, "bold"),
            bg="#1f2937", fg="white", pady=20
        )
        title.pack(fill="x")

        # BUTTON SIDEBAR
        self.create_sidebar_button(sidebar, "🏠  Dashboard", self.show_home)
        self.create_sidebar_button(sidebar, "📦  Kelola Produk", self.open_crud_barang)
        self.create_sidebar_button(sidebar, "👤  Kelola User", self.open_crud_user)
        self.create_sidebar_button(
            sidebar, "🧾  Riwayat Penjualan", lambda: RiwayatAdminWindow(self.root)
        )
        self.create_sidebar_button(sidebar, "📊  Grafik Penjualan", self.show_chart)

        # LOGOUT BUTTON
        tk.Button(
    sidebar,
    text="Logout",
    bg="#ef4444",
    fg="white",
    font=("Poppins", 12, "bold"),
    relief="flat",
    activebackground="#dc2626",
    activeforeground="white",
    pady=8,
    command=self.logout
).pack(fill="x", pady=25, padx=20, side="bottom")

        # ---------------- CONTENT AREA ----------------
        self.content = tk.Frame(self.root, bg="#f2f4f7")
        self.content.pack(expand=True, fill="both")

        self.show_home()
        self.root.mainloop()

    # ---------------- SIDEBAR BUTTON ----------------
    def create_sidebar_button(self, parent, text, command):
        btn = tk.Label(
            parent, text=text,
            font=("Poppins", 12),
            bg="#374151", fg="white",
            padx=15, pady=10,
            anchor="w"
        )
        btn.pack(fill="x", pady=5, padx=15)

        # Hover effect
        btn.bind("<Enter>", lambda e: btn.configure(bg="#4b5563"))
        btn.bind("<Leave>", lambda e: btn.configure(bg="#374151"))
        btn.bind("<Button-1>", lambda e: command())

        return btn

    # ---------------- DASHBOARD HOME ----------------
    def show_home(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        tk.Label(
            self.content,
            text="Selamat Datang, Admin!",
            font=("Poppins", 22, "bold"),
            bg="#f2f4f7",
            fg="#111827"
        ).pack(pady=25)

        card_frame = tk.Frame(self.content, bg="#f2f4f7")
        card_frame.pack(pady=10)

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS total FROM barang")
            total_barang = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) AS total FROM user")
            total_user = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) AS total FROM transaksi")
            total_trans = cursor.fetchone()['total']

            cursor.execute(
                "SELECT COALESCE(SUM(total),0) AS total "
                "FROM transaksi WHERE DATE(tanggal) = CURDATE()"
            )
            pendapatan = cursor.fetchone()['total']

            conn.close()

        except:
            total_barang = total_user = total_trans = pendapatan = 0

        # Modern Card Style
        self.create_info_card(card_frame, "Total Produk", total_barang, "#3b82f6")
        self.create_info_card(card_frame, "Total User", total_user, "#f59e0b")
        self.create_info_card(card_frame, "Total Transaksi", total_trans, "#10b981")
        self.create_info_card(
            card_frame, "Pendapatan Hari Ini", f"Rp {pendapatan:,}", "#ef4444"
        )

    # ---------------- CARD ----------------
    def create_info_card(self, parent, title, value, color):
        frame = tk.Frame(
            parent,
            bg="white",
            width=200,
            height=130,
            bd=0,
            highlightthickness=0
        )
        frame.pack(side="left", padx=15)
        frame.pack_propagate(False)

        # shadow
        frame.configure(highlightbackground="#d1d5db", highlightthickness=1)

        tk.Label(
            frame, text=title,
            fg=color, bg="white",
            font=("Poppins", 12, "bold")
        ).pack(pady=10)

        tk.Label(
            frame, text=value,
            fg="#111827", bg="white",
            font=("Poppins", 20, "bold")
        ).pack()

    # ---------------- CRUD ----------------
    def open_crud_barang(self):
        CrudWindow(self.root)

    def open_crud_user(self):
        CrudUser(self.root)

    # ---------------- GRAFIK ----------------
    def show_chart(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT DATE(tanggal) AS tgl, SUM(total) AS total "
                "FROM transaksi GROUP BY DATE(tanggal)"
            )
            data = cursor.fetchall()

            if not data:
                messagebox.showinfo("Info", "Belum ada transaksi untuk ditampilkan.")
                return

            tanggal = [row['tgl'].strftime("%d-%m-%Y") for row in data]
            total = [row['total'] for row in data]

            plt.figure(figsize=(8, 4))
            plt.plot(tanggal, total, marker='o')
            plt.title("Grafik Penjualan Harian")
            plt.xlabel("Tanggal")
            plt.ylabel("Total Penjualan (Rp)")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")

    # ---------------- LOGOUT ----------------
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Yakin ingin logout?")
        if confirm:
            self.root.destroy()
            import login
            login.main()


def start_admin_dashboard():
    AdminDashboard()
