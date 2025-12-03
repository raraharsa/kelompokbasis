import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from koneksi import connect_db
import pandas as pd
from datetime import datetime

class RiwayatWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title("Riwayat Transaksi")
        self.win.geometry("900x550")
        self.win.configure(bg="#eaddcf")  # coklat muda

        # ====================== HEADER ======================
        header = tk.Frame(self.win, bg="#5a4638")
        header.pack(fill="x")

        tk.Label(
            header, text="Riwayat Transaksi",
            font=("Poppins", 18, "bold"),
            bg="#5a4638", fg="white"
        ).pack(side="left", padx=15, pady=12)

        # Tombol header
        btn_style = dict(font=("Poppins", 11), relief="flat", padx=10, pady=5)

        tk.Button(
            header, text="⟳ Refresh",
            bg="#7e6b5a", fg="white",
            command=self.load_transaksi, **btn_style
        ).pack(side="right", padx=6)

        tk.Button(
            header, text="⬇ Export Excel",
            bg="#20bf6b", fg="white",
            command=self.export_excel, **btn_style
        ).pack(side="right", padx=6)

        # ====================== TABLE ======================
        table_frame = tk.Frame(self.win, bg="#eaddcf")
        table_frame.pack(expand=True, fill="both", padx=15, pady=10)

        cols = ("id", "tanggal", "pelanggan", "kasir", "total")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=16)

        style = ttk.Style()
        style.theme_use("clam")

        # header tabel
        style.configure("Treeview.Heading",
                        font=("Poppins", 11, "bold"),
                        background="#5a4638", foreground="white")

        # isi tabel
        style.configure("Treeview",
                        font=("Poppins", 10),
                        rowheight=28,
                        background="#f5efe6",
                        fieldbackground="#f5efe6")

        for c in cols:
            self.tree.heading(c, text=c.capitalize())

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("tanggal", width=170)
        self.tree.column("pelanggan", width=160)
        self.tree.column("kasir", width=150)
        self.tree.column("total", width=110, anchor="e")
        self.tree.pack(expand=True, fill="both", side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ====================== FOOTER ======================
        footer = tk.Frame(self.win, bg="#eaddcf")
        footer.pack(fill="x", pady=8)

        tk.Button(
            footer, text="🔍   Lihat Detail",
            bg="#7e6b5a", fg="white",
            font=("Poppins", 11),
            relief="flat", padx=10, pady=5,
            command=self.lihat_detail
        ).pack(side="left", padx=6)

        # Double click untuk buka detail
        self.tree.bind("<Double-1>", lambda e: self.lihat_detail())

        self.load_transaksi()

    # ===================== LOAD =====================
    def load_transaksi(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT t.id_transaksi, t.tanggal, 
                           p.nama_pelanggan, u.nama AS nama_kasir, t.total
                    FROM transaksi t
                    LEFT JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                    LEFT JOIN user u ON t.id_kasir = u.id_user
                    ORDER BY t.tanggal DESC
                    LIMIT 500
                """)
                rows = cur.fetchall()
            db.close()

            for r in rows:
                tanggal = r["tanggal"].strftime("%d/%m/%Y %H:%M:%S")
                self.tree.insert(
                    "", "end",
                    values=(r["id_transaksi"], tanggal,
                            r["nama_pelanggan"], r["nama_kasir"], r["total"])
                )

        except Exception as e:
            messagebox.showerror("Error", f"Gagal load riwayat:\n{e}")

    # ===================== DETAIL =====================
    def lihat_detail(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih transaksi dulu")
            return

        id_trans = self.tree.item(sel[0])["values"][0]
        self._tampil_detail(id_trans)

    def _tampil_detail(self, id_trans):
        win = tk.Toplevel(self.win)
        win.title(f"Detail Transaksi #{id_trans}")
        win.geometry("600x380")
        win.configure(bg="#eaddcf")

        tk.Label(
            win, text=f"Detail Transaksi #{id_trans}",
            font=("Poppins", 14, "bold"),
            bg="#eaddcf", fg="#5a4638"
        ).pack(pady=8)

        cols = ("barang", "jumlah", "harga", "subtotal")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)

        for c in cols:
            tree.heading(c, text=c.capitalize())

        tree.column("barang", width=250)
        tree.column("jumlah", width=70, anchor="center")
        tree.column("harga", width=100, anchor="e")
        tree.column("subtotal", width=100, anchor="e")
        tree.pack(expand=True, fill="both", padx=10, pady=8)

        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT b.nama_barang, d.jumlah, b.harga, d.subtotal
                    FROM detail_transaksi d
                    JOIN barang b ON d.id_barang = b.id_barang
                    WHERE d.id_transaksi = %s
                """, (id_trans,))
                rows = cur.fetchall()
            db.close()

            for r in rows:
                tree.insert("", "end",
                            values=(r["nama_barang"], r["jumlah"],
                                    r["harga"], r["subtotal"]))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load detail:\n{e}")

    # ===================== EXPORT =====================
    def export_excel(self):
        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT t.id_transaksi, t.tanggal, 
                           COALESCE(p.nama_pelanggan,'-') AS pelanggan,
                           COALESCE(u.nama,'-') AS kasir,
                           t.total
                    FROM transaksi t
                    LEFT JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                    LEFT JOIN user u ON t.id_kasir = u.id_user
                    ORDER BY t.tanggal DESC
                """)
                data = cur.fetchall()
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil data:\n{e}")
            return

        if not data:
            messagebox.showwarning("Kosong", "Tidak ada data untuk diekspor.")
            return

        df = pd.DataFrame(data)
        df["tanggal"] = df["tanggal"].astype(str)

        waktu = datetime.now().strftime("%Y%m%d_%H%M")
        default_name = f"riwayat_{waktu}.xlsx"

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if not path:
            return

        try:
            df.to_excel(path, index=False)
            messagebox.showinfo("Sukses", f"File berhasil diekspor:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export:\n{e}")
