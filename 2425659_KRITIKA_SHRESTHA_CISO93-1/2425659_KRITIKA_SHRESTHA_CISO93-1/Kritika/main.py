import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from customer import CustomerInterface
from driver import DriverInterface
from admin import AdminInterface
import sqlite3

class TaxiBookingSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Taxi Booking System")
        self.master.geometry("500x500")
        self.master.configure(bg="#F0F0F0")

        self.db = Database()

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.master, text="Taxi Booking System", font=("Arial", 18, "bold"), bg="#F0F0F0")
        title_label.pack(pady=20)


        # User type selection dropdown
        user_frame = tk.Frame(self.master, bg="#F0F0F0")
        user_frame.pack(pady=10)

        tk.Label(user_frame, text="Select User Type:", bg="#F0F0F0").pack(side=tk.LEFT, padx=5)
        self.user_type = tk.StringVar()
        self.user_type.set("Customer")
        user_dropdown = ttk.Combobox(user_frame, textvariable=self.user_type, values=["Customer", "Driver", "Admin"], state="readonly")
        user_dropdown.pack(side=tk.LEFT)

        # Username and password entry
        tk.Label(self.master, text="Username:", bg="#F0F0F0").pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        tk.Label(self.master, text="Password:", bg="#F0F0F0").pack()
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        # Login and Register buttons
        button_frame = tk.Frame(self.master, bg="#F0F0F0")
        button_frame.pack(pady=20)

        login_button = tk.Button(button_frame, text="Login", command=self.login, bg="#4CAF50", fg="white", width=10)
        login_button.pack(side=tk.LEFT, padx=10)

        register_button = tk.Button(button_frame, text="Register", command=self.show_registration, bg="#2196F3", fg="white", width=10)
        register_button.pack(side=tk.LEFT, padx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type = self.user_type.get().lower()

        user = self.db.get_user(username, password)
        if user and user[3] == user_type:
            self.master.withdraw()
            if user_type == 'customer':
                CustomerInterface(tk.Toplevel(), self.db, user, self.master)
            elif user_type == 'driver':
                DriverInterface(tk.Toplevel(), self.db, user, self.master)
            elif user_type == 'admin':
                AdminInterface(tk.Toplevel(), self.db, self.master)
        else:
            messagebox.showerror("Login Failed", "Invalid username, password, or user type")

    def show_registration(self):
        registration_window = tk.Toplevel(self.master)
        registration_window.title("Register")
        registration_window.geometry("400x500")
        registration_window.configure(bg="#F0F0F0")

        tk.Label(registration_window, text="Register", font=("Arial", 16, "bold"), bg="#F0F0F0").pack(pady=10)

        fields = ["Username", "Password", "Name", "Address", "Email", "Phone"]
        entries = {}

        for field in fields:
            tk.Label(registration_window, text=f"{field}:", bg="#F0F0F0").pack()
            entry = tk.Entry(registration_window)
            entry.pack()
            entries[field.lower()] = entry

        tk.Label(registration_window, text="Role:", bg="#F0F0F0").pack()
        role_var = tk.StringVar(registration_window)
        role_var.set("customer")
        role_option = ttk.Combobox(registration_window, textvariable=role_var, values=["customer", "driver", "admin"], state="readonly")
        role_option.pack()

        def register():
            field_values = {field.lower(): entries[field.lower()].get() for field in fields}
            role = role_var.get()

            if all(field_values.values()):
                try:
                    self.db.add_user(field_values['username'], field_values['password'], role, field_values['name'], field_values['address'], field_values['email'], field_values['phone'])
                    messagebox.showinfo("Registration Successful", "You can now login with your credentials")
                    registration_window.destroy()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Registration Failed", "Username already exists")
            else:
                messagebox.showerror("Registration Failed", "Please fill in all fields")

        register_button = tk.Button(registration_window, text="Register", command=register, bg="#2196F3", fg="white")
        register_button.pack(pady=20)

        back_button = tk.Button(registration_window, text="Back", command=registration_window.destroy, bg="#f44336", fg="white")
        back_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaxiBookingSystem(root)
    root.mainloop()