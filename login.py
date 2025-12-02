import tkinter as tk
from tkinter import messagebox
from koneksi import connect_db

from dashboard_admin import start_admin_dashboard
from dashboard_kasir import DashboardKasir


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Sistem Kasir - LUMI.CO")
        self.root.geometry("470x420")
        self.root.configure(bg="#f4f5f7")   # abu terang seperti admin

        # ------------------ CARD ------------------
        card = tk.Frame(self.root, bg="white", bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=370, height=360)

        tk.Label(
            card, text="LUMI.CO",
            font=("Poppins", 18, "bold"),
            bg="white", fg="#2c3e50"   # warna utama admin
        ).pack(pady=(18, 4))

        tk.Label(
            card, text="Silakan Login",
            font=("Poppins", 11),
            bg="white", fg="#34495e"   # warna admin
        ).pack(pady=(0, 18))

        # ------------------ INPUT FORM ------------------
        form = tk.Frame(card, bg="white")
        form.pack()

        # Username
        tk.Label(form, text="Username", bg="white", fg="#34495e", font=("Poppins", 10)).grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(form, font=("Poppins", 10), bd=0,
                                       highlightthickness=1, highlightbackground="#BDC3C7",
                                       highlightcolor="#34495e")  # warna border input
        self.username_entry.grid(row=1, column=0, sticky="ew", ipady=4)
        tk.Frame(form, bg="#D5D8DC", height=1).grid(row=2, column=0, sticky="ew")
        self.error_username = tk.Label(form, text="", fg="red", bg="white", font=("Poppins", 8))
        self.error_username.grid(row=3, column=0, sticky="w", pady=(0, 8))

        # Password
        tk.Label(form, text="Password", bg="white", fg="#34495e", font=("Poppins", 10)).grid(row=4, column=0, sticky="w")
        self.password_entry = tk.Entry(form, show="*", font=("Poppins", 10), bd=0,
                                       highlightthickness=1, highlightbackground="#BDC3C7",
                                       highlightcolor="#34495e")
        self.password_entry.grid(row=5, column=0, sticky="ew", ipady=4)
        tk.Frame(form, bg="#D5D8DC", height=1).grid(row=6, column=0, sticky="ew")
        self.error_password = tk.Label(form, text="", fg="red", bg="white", font=("Poppins", 8))
        self.error_password.grid(row=7, column=0, sticky="w", pady=(0, 8))

        # ------------------ BUTTON LOGIN ------------------
        self.login_btn = tk.Button(
            card, text="LOGIN",
            bg="#34495e", fg="white",
            font=("Poppins", 11, "bold"),
            relief="flat", width=20,
            command=self.login
        )
        self.login_btn.pack(pady=12)

        # hover effect (warna tema admin)
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.configure(bg="#263544"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.configure(bg="#34495e"))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.error_username.config(text="")
        self.error_password.config(text="")

        if username == "":
            self.error_username.config(text="Username tidak boleh kosong")
            return

        if password == "":
            self.error_password.config(text="Password tidak boleh kosong")
            return

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
            user = cursor.fetchone()

            if not user:
                self.error_username.config(text="Username tidak ditemukan")
                return

            if password != user['password']:
                self.error_password.config(text="Password salah")
                return

            messagebox.showinfo("Login Berhasil", f"Welcome {user['nama']} ({user['level']})")
            self.root.destroy()

            if user['level'] == "admin":
                start_admin_dashboard()
            else:
                DashboardKasir(user['id_user'])

        except Exception as e:
            messagebox.showerror("Error Login", str(e))


def main():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
