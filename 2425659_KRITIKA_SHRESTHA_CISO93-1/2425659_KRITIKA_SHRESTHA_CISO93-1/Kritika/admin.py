import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AdminInterface:
    def __init__(self, master, db, login_window):
        self.master = master
        self.db = db
        self.login_window = login_window

        self.master.title("Admin Interface")
        self.master.geometry("1000x600")
        self.master.configure(bg="#E1F5FE")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.master, text="Admin Dashboard", font=("Arial", 18, "bold"), bg="#E1F5FE")
        title_label.pack(pady=20)

        notebook = ttk.Notebook(self.master)
        notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        users_frame = ttk.Frame(notebook)
        trips_frame = ttk.Frame(notebook)

        notebook.add(users_frame, text="Users")
        notebook.add(trips_frame, text="Trips")

        self.create_users_tab(users_frame)
        self.create_trips_tab(trips_frame)

        # Add back button
        back_button = tk.Button(self.master, text="Back to Login", command=self.back_to_login, bg="#f44336", fg="white", font=("Arial", 12))
        back_button.pack(pady=10, padx=20, side=tk.BOTTOM, anchor=tk.SE)

    def create_users_tab(self, parent):
        columns = ("ID", "Username", "Name", "Role", "Email", "Address")
        self.users_tree = ttk.Treeview(parent, columns=columns, show="headings")

        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)

        self.users_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        refresh_button = tk.Button(parent, text="Refresh", command=self.refresh_users, bg="#2196F3", fg="white")
        refresh_button.pack(pady=10)

    def create_trips_tab(self, parent):
        columns = ("ID", "Customer", "Driver", "Pickup", "Drop-off", "Status", "Date/Time")
        self.trips_tree = ttk.Treeview(parent, columns=columns, show="headings")

        for col in columns:
            self.trips_tree.heading(col, text=col)
            self.trips_tree.column(col, width=140)

        self.trips_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(parent, bg="#FFE0B2")
        button_frame.pack(pady=10)

        refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_trips, bg="#2196F3", fg="white")
        refresh_button.pack(side=tk.LEFT, padx=5)

        assign_button = tk.Button(button_frame, text="Assign Driver", command=self.assign_driver, bg="#4CAF50", fg="white")
        assign_button.pack(side=tk.LEFT, padx=5)

        update_status_button = tk.Button(button_frame, text="Update Status", command=self.update_trip_status, bg="#FF9800", fg="white")
        update_status_button.pack(side=tk.LEFT, padx=5)

    def refresh_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        users = self.db.get_all_users()
        for user in users:
            self.users_tree.insert("", "end", values=user[0:6])

    def refresh_trips(self):
        for item in self.trips_tree.get_children():
            self.trips_tree.delete(item)

        trips = self.db.get_all_trips_with_details()
        for trip in trips:
            # Unpack the trip data, using default values if a field is missing
            trip_id, customer_id, driver_id, pickup, dropoff, status, date_time, customer_name, driver_name = (trip + (None,) * 9)[:9]
            
            # Use default values if the data is None
            customer_name = customer_name if customer_name else "N/A"
            driver_name = driver_name if driver_name else "Not Assigned"
            
            self.trips_tree.insert("", "end", values=(trip_id, customer_name, driver_name, pickup, dropoff, status, date_time))

    def assign_driver(self):
        selected_trip = self.trips_tree.selection()
        if not selected_trip:
            messagebox.showerror("Error", "Please select a trip to assign a driver")
            return

        trip_id = self.trips_tree.item(selected_trip)['values'][0]
        trip_details = self.db.get_trip_details(trip_id)

        if trip_details[5] != "Pending":
            messagebox.showerror("Error", "This trip is already assigned or completed")
            return

        available_drivers = self.db.get_available_drivers()
        if not available_drivers:
            messagebox.showerror("Error", "No available drivers")
            return

        assign_window = tk.Toplevel(self.master)
        assign_window.title("Assign Driver")
        assign_window.geometry("300x200")

        tk.Label(assign_window, text="Select Driver:").pack(pady=10)
        driver_var = tk.StringVar(assign_window)
        driver_dropdown = ttk.Combobox(assign_window, textvariable=driver_var, values=[f"{d[0]} - {d[1]}" for d in available_drivers], state="readonly")
        driver_dropdown.pack(pady=10)

        def confirm_assignment():
            if driver_var.get():
                driver_id = int(driver_var.get().split(" - ")[0])
                self.db.assign_trip(trip_id, driver_id)
                messagebox.showinfo("Success", "Driver assigned successfully")
                assign_window.destroy()
                self.refresh_trips()
            else:
                messagebox.showerror("Error", "Please select a driver")

        confirm_button = tk.Button(assign_window, text="Assign", command=confirm_assignment, bg="#4CAF50", fg="white")
        confirm_button.pack(pady=10)

    def update_trip_status(self):
        selected_trip = self.trips_tree.selection()
        if not selected_trip:
            messagebox.showerror("Error", "Please select a trip to update")
            return

        trip_id = self.trips_tree.item(selected_trip)['values'][0]
        trip_details = self.db.get_trip_details(trip_id)

        update_window = tk.Toplevel(self.master)
        update_window.title("Update Trip Status")
        update_window.geometry("300x200")

        tk.Label(update_window, text="Select Status:").pack(pady=10)
        status_var = tk.StringVar(update_window)
        status_dropdown = ttk.Combobox(update_window, textvariable=status_var, values=["Pending", "Assigned", "In Progress", "Completed", "Cancelled"], state="readonly")
        status_dropdown.set(trip_details[5])
        status_dropdown.pack(pady=10)

        def confirm_update():
            if status_var.get():
                self.db.update_trip_status(trip_id, status_var.get())
                messagebox.showinfo("Success", "Trip status updated successfully")
                update_window.destroy()
                self.refresh_trips()
            else:
                messagebox.showerror("Error", "Please select a status")

        confirm_button = tk.Button(update_window, text="Update", command=confirm_update, bg="#FF9800", fg="white")
        confirm_button.pack(pady=10)

    def back_to_login(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to log out?"):
            self.master.destroy()
            self.login_window.deiconify()

class LoginWindow:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.master.title("Taxi Booking System - Login")
        self.master.geometry("300x200")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack(pady=5)

        tk.Label(self.master, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack(pady=5)

        login_button = tk.Button(self.master, text="Login", command=self.login)
        login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.db.authenticate_user(username, password)
        if user:
            self.master.withdraw()
            if user[2] == "admin":
                admin_window = tk.Toplevel(self.master)
                AdminInterface(admin_window, self.db, self.master)
            elif user[2] == "customer":
                customer_window = tk.Toplevel(self.master)
                # Implement CustomerInterface here
            elif user[2] == "driver":
                driver_window = tk.Toplevel(self.master)
                # Implement DriverInterface here
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

if __name__ == "__main__":
    root = tk.Tk()
    db = Database()
    login_window = LoginWindow(root, db)
    root.mainloop()
