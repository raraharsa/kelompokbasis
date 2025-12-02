import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from koneksi import connect_db
import pandas as pd
from datetime import datetime

# ================= RIWAYAT ADMIN (TEMA COKLAT MODERN) ==================
class RiwayatAdminWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title("Riwayat Penjualan (Admin)")
        self.win.geometry("980x600")
        self.win.configure(bg="#f7f3ef")   # krem lembut

        self.current_filters = {
            'date_from': None,
            'date_to': None,
            'id_kasir': None,
            'id_pelanggan': None
        }

        # ================= HEADER =================
        header = tk.Frame(self.win, bg="#f7f3ef")
        header.pack(fill="x", pady=10, padx=14)

        tk.Label(
            header,
            text="📊 Riwayat Penjualan",
            font=("Poppins", 20, "bold"),
            bg="#f7f3ef",
            fg="#5a4634"
        ).pack(side="left")

        # ================= FILTER PANEL =================
        filter_panel = tk.Frame(header, bg="#f7f3ef")
        filter_panel.pack(side="right")

        # Row 1
        tk.Label(filter_panel, text="Dari (YYYY-MM-DD)", bg="#f7f3ef",
                 font=("Poppins", 9)).grid(row=0, column=0, padx=6, sticky="e")
        self.entry_date_from = tk.Entry(filter_panel, width=12)
        self.entry_date_from.grid(row=0, column=1)

        tk.Label(filter_panel, text="Sampai", bg="#f7f3ef",
                 font=("Poppins", 9)).grid(row=0, column=2, padx=6, sticky="e")
        self.entry_date_to = tk.Entry(filter_panel, width=12)
        self.entry_date_to.grid(row=0, column=3)

        # Row 2
        tk.Label(filter_panel, text="Kasir", bg="#f7f3ef",
                 font=("Poppins", 9)).grid(row=1, column=0, padx=6, pady=5, sticky="e")
        self.cmb_kasir = ttk.Combobox(filter_panel, width=18)
        self.cmb_kasir.grid(row=1, column=1)

        tk.Label(filter_panel, text="Pelanggan", bg="#f7f3ef",
                 font=("Poppins", 9)).grid(row=1, column=2, padx=6, pady=5, sticky="e")
        self.cmb_pelanggan = ttk.Combobox(filter_panel, width=18)
        self.cmb_pelanggan.grid(row=1, column=3)

        # Filter Buttons
        tk.Button(
            filter_panel, text="Terapkan",
            bg="#6d4c41", fg="white",
            font=("Poppins", 9),
            relief="flat",
            command=self.apply_filters
        ).grid(row=0, column=4, rowspan=2, padx=(10,4), sticky="ns")

        tk.Button(
            filter_panel, text="Reset",
            bg="#a47551", fg="white",
            font=("Poppins", 9),
            relief="flat",
            command=self.clear_filters
        ).grid(row=0, column=5, rowspan=2, padx=4, sticky="ns")

        # ================= ACTION BUTTONS =================
        actions = tk.Frame(self.win, bg="#f7f3ef")
        actions.pack(fill="x", padx=14)

        tk.Button(
            actions,
            text="⬇ Export Excel",
            bg="#20bf6b",
            fg="white",
            font=("Poppins", 10, "bold"),
            relief="flat",
            command=self.export_excel
        ).pack(side="right", padx=6)

        tk.Button(
            actions,
            text="⟳ Refresh",
            bg="#6d4c41",
            fg="white",
            font=("Poppins", 10, "bold"),
            relief="flat",
            command=self.load_transaksi
        ).pack(side="right", padx=6)

        # ================= TABLE =================
        table_frame = tk.Frame(self.win, bg="#f7f3ef")
        table_frame.pack(expand=True, fill="both", padx=14, pady=10)

        cols = ("id", "tanggal", "pelanggan", "kasir", "total")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading",
                        font=("Poppins", 11, "bold"),
                        background="#6d4c41",
                        foreground="white")
        style.configure("Treeview",
                        font=("Poppins", 10),
                        rowheight=24)

        for c in cols:
            self.tree.heading(c, text=c.capitalize())

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("tanggal", width=170)
        self.tree.column("pelanggan", width=200)
        self.tree.column("kasir", width=170)
        self.tree.column("total", width=120, anchor="e")

        self.tree.pack(expand=True, fill="both", side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ================= FOOTER BUTTONS =================
        footer = tk.Frame(self.win, bg="#f7f3ef")
        footer.pack(fill="x", pady=8, padx=14)

        tk.Button(
            footer,
            text="🔍 Lihat Detail",
            bg="#6d4c41", fg="white",
            font=("Poppins", 11),
            relief="flat",
            command=self.lihat_detail
        ).pack(side="left", padx=6)

        tk.Button(
            footer,
            text="🗑 Hapus Transaksi",
            bg="#c0392b", fg="white",
            font=("Poppins", 11),
            relief="flat",
            command=self.hapus_transaksi
        ).pack(side="left", padx=6)

        self.tree.bind("<Double-1>", lambda e: self.lihat_detail())

        # Load initial data
        self.load_kasir_list()
        self.load_pelanggan_list()
        self.load_transaksi()

    # ===================== QUERY BUILDER =====================
    def _build_query_and_params(self, for_export=False):
        base = """
            SELECT t.id_transaksi, t.tanggal,
                   COALESCE(p.nama_pelanggan,'-') AS nama_pelanggan,
                   COALESCE(u.nama,'-') AS nama_kasir,
                   t.total
            FROM transaksi t
            LEFT JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
            LEFT JOIN user u ON t.id_kasir = u.id_user
        """
        where = []
        params = []

        df = self.current_filters.get('date_from')
        dt = self.current_filters.get('date_to')

        if df and dt:
            where.append("DATE(t.tanggal) BETWEEN %s AND %s")
            params.extend([df, dt])
        elif df:
            where.append("DATE(t.tanggal) >= %s")
            params.append(df)
        elif dt:
            where.append("DATE(t.tanggal) <= %s")
            params.append(dt)

        if self.current_filters.get('id_kasir'):
            where.append("t.id_kasir = %s")
            params.append(self.current_filters['id_kasir'])

        if self.current_filters.get('id_pelanggan'):
            where.append("t.id_pelanggan = %s")
            params.append(self.current_filters['id_pelanggan'])

        if where:
            base += " WHERE " + " AND ".join(where)

        base += " ORDER BY t.tanggal DESC"

        if not for_export:
            base += " LIMIT 1000"

        return base, params

    # ===================== LOAD TRANSAKSI =====================
    def load_transaksi(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            q, params = self._build_query_and_params(for_export=False)
            db = connect_db()
            with db.cursor() as cur:
                cur.execute(q, params)
                rows = cur.fetchall()
            db.close()

            for r in rows:
                tanggal = (r['tanggal'].strftime("%d/%m/%Y %H:%M:%S")
                           if hasattr(r['tanggal'], 'strftime')
                           else str(r['tanggal']))

                self.tree.insert(
                    "", "end",
                    values=(
                        r['id_transaksi'],
                        tanggal,
                        r['nama_pelanggan'],
                        r['nama_kasir'],
                        r['total']
                    )
                )
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load riwayat:\n{e}")

    # ===================== DETAIL =====================
    def lihat_detail(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih transaksi dulu")
            return

        id_trans = self.tree.item(sel[0])['values'][0]
        self._tampil_detail(id_trans)

    def _tampil_detail(self, id_trans):
        win = tk.Toplevel(self.win)
        win.title(f"Detail Transaksi #{id_trans}")
        win.geometry("600x380")
        win.configure(bg="#fdfbf7")

        tk.Label(
            win, text=f"Detail Transaksi #{id_trans}",
            font=("Poppins", 14, "bold"),
            bg="#fdfbf7", fg="#5a4634"
        ).pack(pady=8)

        cols = ("barang", "jumlah", "harga", "subtotal")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c.capitalize())

        tree.column("barang", width=260)
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
                tree.insert(
                    "",
                    "end",
                    values=(r['nama_barang'], r['jumlah'], r['harga'], r['subtotal'])
                )
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load detail:\n{e}")

    # ===================== HAPUS TRANSAKSI =====================
    def hapus_transaksi(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih transaksi dulu")
            return

        id_trans = self.tree.item(sel[0])['values'][0]

        if not messagebox.askyesno(
            "Konfirmasi",
            f"Hapus transaksi ID {id_trans}?\nStok barang akan dikembalikan."
        ):
            return

        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute("SELECT id_barang, jumlah FROM detail_transaksi WHERE id_transaksi = %s",
                            (id_trans,))
                details = cur.fetchall()

                for d in details:
                    cur.execute("""
                        UPDATE barang
                        SET stok = stok + %s
                        WHERE id_barang = %s
                    """, (d['jumlah'], d['id_barang']))

                cur.execute("DELETE FROM detail_transaksi WHERE id_transaksi = %s", (id_trans,))
                cur.execute("DELETE FROM transaksi WHERE id_transaksi = %s", (id_trans,))

            db.commit()
            db.close()

            messagebox.showinfo(
                "Sukses",
                f"Transaksi #{id_trans} berhasil dihapus dan stok dikembalikan."
            )
            self.load_transaksi()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal hapus transaksi:\n{e}")

    # ===================== EXPORT =====================
    def export_excel(self):
        try:
            q, params = self._build_query_and_params(for_export=True)
            db = connect_db()
            with db.cursor() as cur:
                cur.execute(q, params)
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
        default_name = f"riwayat_admin_{waktu}.xlsx"

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

    # ===================== FILTER LIST LOADERS =====================
    def load_kasir_list(self):
        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT id_user, nama FROM user WHERE level IN ('kasir','admin') ORDER BY nama"
                )
                rows = cur.fetchall()
            db.close()

            self.cmb_kasir['values'] = [""] + [
                f"{r['id_user']} - {r['nama']}" for r in rows
            ]
        except:
            self.cmb_kasir['values'] = [""]

    def load_pelanggan_list(self):
        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute("SELECT id_pelanggan, nama_pelanggan FROM pelanggan ORDER BY nama_pelanggan")
                rows = cur.fetchall()
            db.close()

            self.cmb_pelanggan['values'] = [""] + [
                f"{r['id_pelanggan']} - {r['nama_pelanggan']}" for r in rows
            ]
        except:
            self.cmb_pelanggan['values'] = [""]

    # ===================== APPLY + RESET FILTER =====================
    def apply_filters(self):
        df = self.entry_date_from.get().strip()
        dt = self.entry_date_to.get().strip()

        try:
            if df:
                datetime.strptime(df, "%Y-%m-%d")
            if dt:
                datetime.strptime(dt, "%Y-%m-%d")
        except:
            messagebox.showwarning("Format Tanggal", "Format harus YYYY-MM-DD.")
            return

        kasir_raw = self.cmb_kasir.get().strip()
        pelanggan_raw = self.cmb_pelanggan.get().strip()

        id_kasir = int(kasir_raw.split(" - ")[0]) if kasir_raw else None
        id_pelanggan = int(pelanggan_raw.split(" - ")[0]) if pelanggan_raw else None

        self.current_filters = {
            'date_from': df or None,
            'date_to': dt or None,
            'id_kasir': id_kasir,
            'id_pelanggan': id_pelanggan
        }

        self.load_transaksi()

    def clear_filters(self):
        self.entry_date_from.delete(0, 'end')
        self.entry_date_to.delete(0, 'end')
        self.cmb_kasir.set('')
        self.cmb_pelanggan.set('')

        self.current_filters = {
            'date_from': None,
            'date_to': None,
            'id_kasir': None,
            'id_pelanggan': None
        }

        self.load_transaksi()
