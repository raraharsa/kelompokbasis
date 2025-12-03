import tkinter as tk
from tkinter import ttk, messagebox
from koneksi import connect_db
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os

from riwayat import RiwayatWindow


class KasirWindow:
    def __init__(self, master, id_user):
        self.master = master
        self.id_kasir = id_user

        # ---------- Window ----------
        self.win = tk.Toplevel(master)
        self.win.title("Form Kasir - LUMI.CO")
        # sedikit lebih lebar untuk tampilan kasir profesional
        self.win.geometry("1100x720")
        # warna latar netral krem (tetap feel coklat)
        self.win.configure(bg="#f3ebe6")

        self.win.protocol("WM_DELETE_WINDOW", self.kembali_ke_dashboard)

        # ---------- Warna Tema (coklat) ----------
        self.color_dark = "#5D4037"    # dark brown (header / tombol utama)
        self.color_mid = "#8D6E63"     # medium brown (aksen)
        self.color_light = "#F7F1EE"   # very light cream
        self.color_accent = "#3E2723"  # deep accent
        self.btn_font = ("Segoe UI", 10, "bold")
        self.base_font = ("Segoe UI", 10)

        # ---------- HEADER ----------
        header = tk.Frame(self.win, bg=self.color_dark, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="🧾  FORM TRANSAKSI KASIR - LUMI.CO",
            fg="white",
            bg=self.color_dark,
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=20)

        # small meta on right
        tk.Label(
            header,
            text=f"Kasir ID: {self.id_kasir}",
            fg="#FFDDAA",
            bg=self.color_dark,
            font=("Segoe UI", 10, "italic")
        ).pack(side="right", padx=16)

        # ---------- MAIN CONTAINER ----------
        main = tk.Frame(self.win, bg=self.color_light)
        main.pack(fill="both", expand=True, padx=14, pady=12)

        # top area: pelanggan + search barang + tombol tambah
        top_frame = tk.Frame(main, bg=self.color_light)
        top_frame.pack(fill="x", pady=(4, 8))
        top_frame.columnconfigure(1, weight=1)

        # Pelanggan
        tk.Label(top_frame, text="👤 Pelanggan:", bg=self.color_light, font=self.base_font).grid(row=0, column=0, sticky="w", padx=6)
        self.pelanggan_var = tk.StringVar()
        self.cmb_pelanggan = ttk.Combobox(top_frame, textvariable=self.pelanggan_var)
        self.cmb_pelanggan.grid(row=0, column=1, sticky="ew", padx=6)
        tk.Button(
            top_frame, text="+ Pelanggan Baru",
            bg=self.color_mid, fg="white", relief="flat",
            font=("Segoe UI", 10),
            command=self.tambah_pelanggan
        ).grid(row=0, column=2, padx=6)

        # Barang (dengan label cari agar terasa kasir modern)
        tk.Label(top_frame, text="📦 Pilih Barang / Cari:", bg=self.color_light, font=self.base_font).grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.cmb_var = tk.StringVar()
        # gunakan entry + combobox supaya user bisa ketik cepat
        search_frame = tk.Frame(top_frame, bg=self.color_light)
        search_frame.grid(row=1, column=1, sticky="ew", padx=6)
        search_frame.columnconfigure(0, weight=1)
        self.combo = ttk.Combobox(search_frame, textvariable=self.cmb_var)
        self.combo.grid(row=0, column=0, sticky="ew")
        tk.Button(
            top_frame, text="Tambah ke Keranjang",
            bg=self.color_dark, fg="white", relief="flat",
            font=self.btn_font,
            command=self.tambah_keranjang
        ).grid(row=1, column=2, padx=6)

        # ---------- MAIN BODY: LEFT = TABLE, RIGHT = SUMMARY ----------
        body = tk.Frame(main, bg=self.color_light)
        body.pack(fill="both", expand=True)

        # kiri: table
        left = tk.Frame(body, bg=self.color_light)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        # TABLE (dengan border halus)
        tree_frame = tk.Frame(left, bg=self.color_light, bd=1, relief="solid")
        tree_frame.pack(fill="both", expand=True, padx=4, pady=2)

        cols = ('no', 'id_barang', 'nama_barang', 'harga', 'jumlah', 'subtotal')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=18)

        self.tree.heading('no', text='No')
        self.tree.heading('id_barang', text='ID')
        self.tree.heading('nama_barang', text='Nama Barang')
        self.tree.heading('harga', text='Harga')
        self.tree.heading('jumlah', text='Jumlah')
        self.tree.heading('subtotal', text='Subtotal')

        # kolom lebih lebar untuk nama barang
        self.tree.column('no', width=50, anchor='center')
        self.tree.column('id_barang', width=80, anchor='center')
        self.tree.column('nama_barang', width=360, anchor='w')
        self.tree.column('harga', width=120, anchor='e')
        self.tree.column('jumlah', width=90, anchor='center')
        self.tree.column('subtotal', width=150, anchor='e')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True, side='left')

        # kanan: ringkasan & aksi (highlight total besar)
        right = tk.Frame(body, bg=self.color_light, width=320)
        right.pack(side="right", fill="y")

        # ringkasan box
        summary_box = tk.Frame(right, bg="#fffaf7", bd=1, relief="solid")
        summary_box.pack(fill="both", padx=4, pady=4, ipady=8)

        # Total besar — fokus utama kasir
        tk.Label(summary_box, text="JUMLAH BELANJA", bg="#fffaf7", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(8,2))
        self.total_var = tk.StringVar(value='0')
        # font sangat besar agar mudah dibaca saat transaksi besar
        tk.Label(summary_box, textvariable=self.total_var, bg="#fffaf7",
                 font=("Segoe UI", 28, "bold"), fg=self.color_accent).pack(anchor="w", padx=12)

        # rincian lain
        rincian = tk.Frame(summary_box, bg="#fffaf7")
        rincian.pack(fill="x", padx=12, pady=10)
        tk.Label(rincian, text="Bayar:", bg="#fffaf7", font=self.base_font).grid(row=0, column=0, sticky='w')
        self.bayar_entry = tk.Entry(rincian, font=("Segoe UI", 12))
        self.bayar_entry.grid(row=0, column=1, sticky='e', padx=6)

        tk.Button(rincian, text="Hitung Kembalian", bg=self.color_dark, fg="white",
                  relief="flat", font=self.btn_font, command=self.hitung_kembalian).grid(row=1, column=0, columnspan=2, pady=(8,0), sticky="ew")

        tk.Label(rincian, text="Kembalian:", bg="#fffaf7", font=self.base_font).grid(row=2, column=0, sticky='w', pady=(8,0))
        self.kembali_var = tk.StringVar(value='0')
        tk.Label(rincian, textvariable=self.kembali_var, bg="#fffaf7", font=("Segoe UI", 12, "bold")).grid(row=2, column=1, sticky='e', pady=(8,0))

        # pemisah
        tk.Frame(right, height=6, bg=self.color_light).pack(fill="x")

        # tombol aksi utama di kanan (lebih mudah dijangkau kasir)
        actions = tk.Frame(right, bg=self.color_light)
        actions.pack(fill="x", padx=4, pady=6)

        def btn(txt, cmd, color=None):
            c = color if color else self.color_dark
            return tk.Button(actions, text=txt, bg=c, fg="white",
                             relief="flat", font=self.btn_font, command=cmd)

        btn("Hapus Item", self.hapus_item, "#C62828").pack(fill="x", pady=4)
        btn("Simpan Transaksi", self.simpan_transaksi, "#2E7D32").pack(fill="x", pady=4)
        btn("Cetak Struk (PDF)", self.cetak_pdf, self.color_mid).pack(fill="x", pady=4)
        btn("Kosongkan Keranjang", self.kosongkan_keranjang, "#6D4C41").pack(fill="x", pady=4)
        tk.Button(actions, text="Riwayat Transaksi", bg=self.color_dark, fg="white",
                  relief="flat", font=self.btn_font, command=lambda: RiwayatWindow(self.win)).pack(fill="x", pady=4)

        # tombol kembali di bawah
        tk.Button(right, text="⬅  Kembali ke Dashboard", bg=self.color_dark, fg="white",
                  relief="flat", font=self.btn_font, command=self.kembali_ke_dashboard).pack(fill="x", padx=4, pady=(14,4))

        # FOOTER kecil
        footer = tk.Frame(self.win, bg=self.color_light, height=28)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="LUMI.CO • Kasir", bg=self.color_light, fg="#7D5A50", font=("Segoe UI", 9)).pack(side="left", padx=8)

        # ---------- INIT DATA (TIDAK DIUBAH FUNGSI) ----------
        self.keranjang = []
        self.load_items_to_combo()
        self.load_pelanggan()
        self.refresh_tree()

    # LOAD BARANG + LOAD PELANGGAN + KERANJANG + HITUNG KEMBALIAN + SIMPAN TRANSAKSI + CETAK
    # (SEMUA FUNGSI DI BAWAH TIDAK DIUBAH SAMA SEKALI)

    def load_items_to_combo(self):
        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute('SELECT * FROM barang')
                rows = cur.fetchall()
            db.close()

            # Build items mapping with "(STOK HABIS)" label for items with stok 0
            self.items = {}
            tampil = []
            for r in rows:
                teks = f"{r['id_barang']} - {r['nama_barang']} - Rp{r['harga']}"
                if r.get('stok', 0) == 0:
                    teks += " (STOK HABIS)"
                self.items[teks] = r
                tampil.append(teks)

            self.combo['values'] = tampil

        except Exception as e:
            messagebox.showerror("Error", f"Gagal load barang:\n{e}")
            self.items = {}
            self.combo['values'] = []

    def load_pelanggan(self):
        try:
            db = connect_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM pelanggan")
                rows = cur.fetchall()
            db.close()
            self.data_pelanggan = {f"{r['id_pelanggan']} - {r['nama_pelanggan']}": r['id_pelanggan'] for r in rows}
            self.cmb_pelanggan['values'] = list(self.data_pelanggan.keys())
            if self.cmb_pelanggan['values']:
                self.cmb_pelanggan.set(self.cmb_pelanggan['values'][0])
        except Exception as e:
            messagebox.showerror("Error", f"Gagal load pelanggan:\n{e}")

    def tambah_pelanggan(self):
        win = tk.Toplevel(self.win)
        win.title("Pelanggan Baru")
        win.geometry("320x160")
        tk.Label(win, text="Nama Pelanggan").pack(pady=(8, 0))
        nama_entry = tk.Entry(win)
        nama_entry.pack(padx=10, fill='x')
        tk.Label(win, text="No HP").pack(pady=(8, 0))
        hp_entry = tk.Entry(win)
        hp_entry.pack(padx=10, fill='x')

        def save():
            nama = nama_entry.get().strip()
            hp = hp_entry.get().strip()
            if nama == "":
                messagebox.showwarning("Peringatan", "Nama tidak boleh kosong")
                return
            try:
                db = connect_db()
                with db.cursor() as cur:
                    cur.execute("INSERT INTO pelanggan (nama_pelanggan, no_hp) VALUES (%s, %s)", (nama, hp))
                db.commit()
                db.close()
                win.destroy()
                self.load_pelanggan()
                messagebox.showinfo("Sukses", "Pelanggan berhasil ditambahkan")
            except Exception as e:
                messagebox.showerror("Gagal", f"Error tambah pelanggan:\n{e}")

        tk.Button(win, text="Simpan", bg=self.color_dark, fg="white", command=save).pack(pady=10)

    def tambah_keranjang(self):
        key = self.cmb_var.get()
        if key not in self.items:
            messagebox.showwarning("Peringatan", "Pilih barang dulu")
            return
        item = self.items[key]

        # BLOCK jika stok 0 (langsung beri peringatan)
        if item.get('stok', 0) == 0:
            messagebox.showwarning("Stok Habis", f"{item['nama_barang']} sedang habis.")
            return

        qty_window = tk.Toplevel(self.win)
        qty_window.title("Jumlah")
        qty_window.geometry("300x140")
        tk.Label(qty_window, text=f"Jumlah untuk {item['nama_barang']}").pack(pady=6)
        qty_entry = tk.Entry(qty_window)
        qty_entry.pack(padx=10)

        def add_qty():
            jm = qty_entry.get().strip()
            if not jm.isdigit() or int(jm) <= 0:
                messagebox.showwarning("Peringatan", "Jumlah tidak valid")
                return
            jm = int(jm)

            # Cek jumlah tidak melebihi stok saat ini
            if jm > item.get('stok', 0):
                messagebox.showwarning(
                    "Stok Tidak Cukup",
                    f"Stok {item['nama_barang']} hanya {item.get('stok', 0)}.\nTidak bisa menambahkan {jm}."
                )
                return

            subtotal = jm * item['harga']
            self.keranjang.append({
                'id_barang': item['id_barang'],
                'nama_barang': item['nama_barang'],
                'harga': item['harga'],
                'jumlah': jm,
                'subtotal': subtotal
            })
            qty_window.destroy()
            self.refresh_tree()

        tk.Button(qty_window, text="OK", bg=self.color_dark, fg="white", command=add_qty).pack(pady=10)

    def refresh_tree(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        total = 0
        db = connect_db()
        with db.cursor() as cur:
            for i, item in enumerate(self.keranjang, start=1):
                cur.execute("SELECT stok FROM barang WHERE id_barang=%s", (item['id_barang'],))
                stok_saat_ini = cur.fetchone()['stok']
                values = (i, item['id_barang'], item['nama_barang'], item['harga'], item['jumlah'], item['subtotal'])
                self.tree.insert('', 'end', values=values)
                item_id = self.tree.get_children()[-1]
                if item['jumlah'] > stok_saat_ini:
                    self.tree.item(item_id, tags=('overstok',))
                total += item['subtotal']
        self.tree.tag_configure('overstok', background='#FFCCCC')
        self.total_var.set(str(total))
        db.close()

    def hapus_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih item dulu")
            return
        idx = int(self.tree.item(sel[0])['values'][0]) - 1
        if 0 <= idx < len(self.keranjang):
            del self.keranjang[idx]
            self.refresh_tree()

    def kosongkan_keranjang(self):
        self.keranjang = []
        self.refresh_tree()

    def hitung_kembalian(self):
        try:
            bayar = int(self.bayar_entry.get())
        except:
            messagebox.showwarning("Peringatan", "Nominal bayar salah")
            return
        total = int(self.total_var.get()) if self.total_var.get().isdigit() else 0
        if bayar < total:
            messagebox.showwarning("Peringatan", "Pembayaran kurang")
            return
        self.kembali_var.set(str(bayar - total))

    def simpan_transaksi(self):
        if not self.keranjang:
            messagebox.showwarning("Peringatan", "Keranjang kosong")
            return
        pel = self.pelanggan_var.get()
        if pel not in self.data_pelanggan:
            messagebox.showwarning("Peringatan", "Pilih pelanggan dulu")
            return
        id_pelanggan = self.data_pelanggan[pel]
        id_kasir = self.id_kasir
        try:
            db = connect_db()
            with db.cursor() as cur:
                for item in self.keranjang:
                    cur.execute("SELECT stok FROM barang WHERE id_barang=%s", (item['id_barang'],))
                    stok_saat_ini = cur.fetchone()['stok']
                    if item['jumlah'] > stok_saat_ini:
                        messagebox.showwarning("Stok Habis",
                            f"Stok {item['nama_barang']} tidak cukup.\nTersedia: {stok_saat_ini}")
                        return
                total = int(self.total_var.get())
                cur.execute("""
                    INSERT INTO transaksi (id_pelanggan, id_kasir, total)
                    VALUES (%s, %s, %s)
                """, (id_pelanggan, id_kasir, total))
                id_trans = cur.lastrowid
                for item in self.keranjang:
                    cur.execute("""
                        INSERT INTO detail_transaksi (id_transaksi, id_barang, jumlah, subtotal)
                        VALUES (%s, %s, %s, %s)
                    """, (id_trans, item['id_barang'], item['jumlah'], item['subtotal']))
                    cur.execute("""
                        UPDATE barang SET stok = stok - %s WHERE id_barang = %s
                    """, (item['jumlah'], item['id_barang']))
            db.commit()
            db.close()
            messagebox.showinfo("Sukses", f"Transaksi berhasil disimpan!\nID: {id_trans}")
            self.kosongkan_keranjang()
            self.load_items_to_combo()
        except Exception as e:
            messagebox.showerror("Gagal", f"Error simpan transaksi:\n{e}")

    def cetak_pdf(self):
        if not self.keranjang:
            messagebox.showwarning("Peringatan", "Keranjang kosong")
            return

        STRUK_WIDTH = 226
        STRUK_HEIGHT = 600

        base = os.path.dirname(os.path.abspath(__file__))
        nama_file = f"struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = os.path.join(base, nama_file)

        pdf = canvas.Canvas(path, pagesize=(STRUK_WIDTH, STRUK_HEIGHT))
        y = 570
        try:
            logo_path = "download.png"
            logo = ImageReader(logo_path)
            lw, lh = logo.getSize()
            scale = 60 / lh
            new_w = lw * scale
            new_h = lh * scale
            pdf.drawImage(logo, (STRUK_WIDTH - new_w) / 2, y - new_h, width=new_w, height=new_h)
            y -= new_h + 10
        except:
            pass

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(STRUK_WIDTH / 2, y, "LUMI.CO")
        y -= 15

        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(STRUK_WIDTH / 2, y, "Jl. Raya Jember, Jawa Timur")
        y -= 10
        pdf.line(0, y, STRUK_WIDTH, y)
        y -= 10

        pdf.drawString(5, y, f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y -= 10
        pdf.drawString(5, y, f"Pelanggan: {self.pelanggan_var.get()}")
        y -= 15
        pdf.line(0, y, STRUK_WIDTH, y)
        y -= 10

        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(5, y, "Barang")
        pdf.drawRightString(STRUK_WIDTH - 5, y, "Subtotal")
        y -= 10
        pdf.line(0, y, STRUK_WIDTH, y)
        y -= 6

        pdf.setFont("Helvetica", 8)
        for item in self.keranjang:
            pdf.drawString(5, y, item['nama_barang'])
            y -= 10
            pdf.drawString(10, y, f"{item['jumlah']} x Rp{item['harga']}")
            pdf.drawRightString(STRUK_WIDTH - 5, y, f"Rp{item['subtotal']}")
            y -= 14

        pdf.line(0, y, STRUK_WIDTH, y)
        y -= 10

        total = int(self.total_var.get())
        bayar = int(self.bayar_entry.get() or 0)
        kembali = bayar - total if bayar >= total else 0

        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(5, y, "TOTAL")
        pdf.drawRightString(STRUK_WIDTH - 5, y, f"Rp{total}")
        y -= 14

        pdf.setFont("Helvetica", 8)
        pdf.drawString(5, y, "Bayar")
        pdf.drawRightString(STRUK_WIDTH - 5, y, f"Rp{bayar}")
        y -= 12

        pdf.drawString(5, y, "Kembali")
        pdf.drawRightString(STRUK_WIDTH - 5, y, f"Rp{kembali}")
        y -= 20

        pdf.line(0, y, STRUK_WIDTH, y)
        y -= 15

        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawCentredString(STRUK_WIDTH / 2, y, "Terima kasih telah berbelanja!")
        y -= 10
        pdf.drawCentredString(STRUK_WIDTH / 2, y, "Barang tidak dapat dikembalikan.")

        pdf.save()
        messagebox.showinfo("Sukses", f"Struk disimpan di:\n{path}")

    def kembali_ke_dashboard(self):
        self.win.destroy()
        self.master.deiconify()
