import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

from crud_barang import CrudWindow
from crud_user import CrudUser
from riwayat_admin import RiwayatAdminWindow
from koneksi import connect_db

# -------------------------------
# COLOR THEME: COFFEE MINIMAL UI
# -------------------------------
BG = "#f5ebe0"              # background soft cream
SIDEBAR = "#7f5539"         # medium brown
SIDEBAR_HOVER = "#9c6644"   # light brown hover
CARD_BG = "#ede0d4"         # soft beige
TEXT_DARK = "#3e2f2f"       # dark coffee text
LINE = "#d6ccc2"            # soft border


class AdminDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dashboard Admin")
        self.root.geometry("980x600")
        self.root.configure(bg=BG)

        # ---------------- SIDEBAR ----------------
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=230)
        sidebar.pack(side="left", fill="y")

        title = tk.Label(
            sidebar,
            text="ADMIN LUMI.CO",
            font=("Poppins", 17, "bold"),
            bg=SIDEBAR, fg="white",
            pady=28
        )
        title.pack(fill="x")

        # BUTTON LIST
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
            bg="#c0392b",
            fg="white",
            relief="flat",
            activebackground="#962d22",
            font=("Poppins", 12, "bold"),
            pady=9,
            command=self.logout
        ).pack(fill="x", pady=25, padx=25, side="bottom")

        # ---------------- CONTENT ----------------
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(expand=True, fill="both")

        self.show_home()
        self.root.mainloop()

    # ---------------- SIDEBAR BUTTON STYLE ONLY ----------------
    def create_sidebar_button(self, parent, text, command):
        btn = tk.Label(
            parent,
            text=text,
            font=("Poppins", 12),
            bg=SIDEBAR,
            fg="white",
            padx=20,
            pady=12,
            anchor="w",
            cursor="hand2"
        )
        btn.pack(fill="x", padx=15, pady=4)

        # PURE UI ONLY (hover)
        btn.bind("<Enter>", lambda e: btn.configure(bg=SIDEBAR_HOVER))
        btn.bind("<Leave>", lambda e: btn.configure(bg=SIDEBAR))
        btn.bind("<Button-1>", lambda e: command())

        return btn

    # ---------------- DASHBOARD HOME (TAMPILAN AJA DIUBAH) ----------------
    def show_home(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        tk.Label(
            self.content, 
            text="Selamat Datang, Admin!",
            font=("Poppins", 24, "bold"),
            bg=BG,
            fg=TEXT_DARK
        ).pack(pady=25)

        card_frame = tk.Frame(self.content, bg=BG)
        card_frame.pack(pady=10)

        # AMBIL DATA (TIDAK DIUBAH)
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

        # CARD (TAMPILAN SAJA)
        self.create_info_card(card_frame, "Total Produk", total_barang, "#9c6644")
        self.create_info_card(card_frame, "Total User", total_user, "#7f5539")
        self.create_info_card(card_frame, "Total Transaksi", total_trans, "#6f4e37")
        self.create_info_card(
            card_frame, "Pendapatan Hari Ini", f"Rp {pendapatan:,}", "#5c4033"
        )

    # ---------------- CARD STYLE ONLY ----------------
    def create_info_card(self, parent, title, value, color):
        frame = tk.Frame(
            parent,
            bg=CARD_BG,
            width=200,
            height=130,
            highlightbackground=LINE,
            highlightthickness=1
        )
        frame.pack(side="left", padx=18)
        frame.pack_propagate(False)

        tk.Label(
            frame,
            text=title,
            bg=CARD_BG,
            fg=color,
            font=("Poppins", 12, "bold")
        ).pack(pady=12)

        tk.Label(
            frame,
            text=value,
            bg=CARD_BG,
            fg=TEXT_DARK,
            font=("Poppins", 20, "bold")
        ).pack()

    # ---------------- CRUD (TIDAK DIUBAH) ----------------
    def open_crud_barang(self):
        CrudWindow(self.root)

    def open_crud_user(self):
        CrudUser(self.root)

    # ---------------- CHART (TIDAK DIUBAH) ----------------
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

    # ---------------- LOGOUT (TIDAK DIUBAH) ----------------
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Yakin ingin logout?")
        if confirm:
            self.root.destroy()
            import login
            login.main()


def start_admin_dashboard():
    AdminDashboard()