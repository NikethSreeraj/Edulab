import tkinter as tk
from tkinter import messagebox

from app.services.auth_service import authenticate_user, create_user


class AuthWindow:
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login
        self.root.title("Edulab Login")
        self.root.geometry("420x520")
        self.root.configure(bg="#eef4fb")

        container = tk.Frame(self.root, bg="#eef4fb", padx=28, pady=28)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="Edulab",
            font=("Segoe UI", 28, "bold"),
            fg="#1f4e79",
            bg="#eef4fb",
        ).pack(pady=(0, 10))

        tk.Label(
            container,
            text="Smart learning for every student",
            font=("Segoe UI", 11),
            fg="#4a5d75",
            bg="#eef4fb",
        ).pack(pady=(0, 20))

        self.mode = tk.StringVar(value="login")
        tk.Radiobutton(container, text="Login", variable=self.mode, value="login", bg="#eef4fb", command=self._toggle_mode).pack(anchor="w")
        tk.Radiobutton(container, text="Create account", variable=self.mode, value="signup", bg="#eef4fb", command=self._toggle_mode).pack(anchor="w")

        self.full_name_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar(show="*")

        self.full_name_entry = tk.Entry(container, textvariable=self.full_name_var, width=32, font=("Segoe UI", 11))
        self.full_name_label = tk.Label(container, text="Full name", bg="#eef4fb")

        self.username_entry = tk.Entry(container, textvariable=self.username_var, width=32, font=("Segoe UI", 11))
        tk.Label(container, text="Username", bg="#eef4fb").pack(anchor="w", pady=(18, 4))
        self.username_entry.pack(fill="x")

        self.email_entry = tk.Entry(container, textvariable=self.email_var, width=32, font=("Segoe UI", 11))
        self.email_label = tk.Label(container, text="Email", bg="#eef4fb")

        self.password_entry = tk.Entry(container, textvariable=self.password_var, width=32, font=("Segoe UI", 11), show="*")
        tk.Label(container, text="Password", bg="#eef4fb").pack(anchor="w", pady=(18, 4))
        self.password_entry.pack(fill="x")

        self.submit_button = tk.Button(
            container,
            text="Login",
            command=self._submit,
            width=20,
            bg="#2d7dd2",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            pady=8,
        )
        self.submit_button.pack(pady=(20, 10))

        self._toggle_mode()

    def _toggle_mode(self):
        is_signup = self.mode.get() == "signup"
        if is_signup:
            self.full_name_label.pack(anchor="w", pady=(14, 4))
            self.full_name_entry.pack(fill="x")
            self.email_label.pack(anchor="w", pady=(14, 4))
            self.email_entry.pack(fill="x")
            self.submit_button.config(text="Create account")
        else:
            self.full_name_label.pack_forget()
            self.full_name_entry.pack_forget()
            self.email_label.pack_forget()
            self.email_entry.pack_forget()
            self.submit_button.config(text="Login")

    def _submit(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Missing fields", "Username and password are required.")
            return

        if self.mode.get() == "signup":
            full_name = self.full_name_var.get().strip()
            email = self.email_var.get().strip()
            if not full_name or not email:
                messagebox.showerror("Missing fields", "Full name and email are required for signup.")
                return
            try:
                user = create_user(username, email, password, full_name)
                messagebox.showinfo("Success", f"Welcome {user['full_name']}! Your account has been created.")
                self.on_login(user)
            except ValueError as exc:
                messagebox.showerror("Signup failed", str(exc))
        else:
            user = authenticate_user(username, password)
            if user is None:
                messagebox.showerror("Login failed", "Invalid username or password.")
                return
            self.on_login(user)
