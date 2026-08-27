import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class CustomerInterface:
    def __init__(self, master, db, user, main_window):
        self.master = master
        self.db = db
        self.user = user
        self.main_window = main_window

        self.master.title("Customer Dashboard")
        self.master.geometry("1200x800")
        self.master.configure(bg="#E1F5FE")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.master, text=f"Welcome, {self.user[4]}!", font=("Arial", 24, "bold"), bg="#E1F5FE")
        title_label.pack(pady=10)

        content_frame = tk.Frame(self.master, bg="#FFFFFF")
        content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        details_frame = tk.LabelFrame(content_frame, text="Your Details", font=("Arial", 18, "bold"), bg="#FFFFFF", padx=15, pady=15)
        details_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        details = [
            ("Name", self.user[4]),
            ("Address", self.user[5]),
            ("Email", self.user[6]),
            ("Phone", self.user[7])
        ]

        for i, (label, value) in enumerate(details):
            tk.Label(details_frame, text=f"{label}:", font=("Arial", 14, "bold"), bg="#FFFFFF").grid(row=i, column=0, padx=10, pady=10, sticky="e")
            tk.Label(details_frame, text=value, font=("Arial", 14), bg="#FFFFFF").grid(row=i, column=1, padx=10, pady=10, sticky="w")

        booking_frame = tk.LabelFrame(content_frame, text="Book a Taxi", font=("Arial", 18, "bold"), bg="#FFFFFF", padx=15, pady=15)
        booking_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        tk.Label(booking_frame, text="Pickup Location:", font=("Arial", 14), bg="#FFFFFF").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.pickup_entry = tk.Entry(booking_frame, font=("Arial", 14))
        self.pickup_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        tk.Label(booking_frame, text="Drop-off Location:", font=("Arial", 14), bg="#FFFFFF").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.dropoff_entry = tk.Entry(booking_frame, font=("Arial", 14))
        self.dropoff_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        book_button = tk.Button(booking_frame, text="Book Taxi", command=self.book_taxi, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
        book_button.grid(row=2, column=0, columnspan=2, pady=20)

        history_frame = tk.LabelFrame(content_frame, text="Trip History", font=("Arial", 18, "bold"), bg="#FFFFFF", padx=15, pady=15)
        history_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")

        columns = ("ID", "Pickup", "Drop-off", "Status", "Date")
        self.trip_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.trip_tree.heading(col, text=col)
            self.trip_tree.column(col, width=200)

        self.trip_tree.pack(expand=True, fill=tk.BOTH)

        button_frame = tk.Frame(history_frame, bg="#FFFFFF")
        button_frame.pack(pady=10)

        refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_trip_history, bg="#2196F3", fg="white", font=("Arial", 12))
        refresh_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel Booking", command=self.cancel_booking, bg="#f44336", fg="white", font=("Arial", 12))
        cancel_button.pack(side=tk.LEFT, padx=5)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Add back button
        back_button = tk.Button(self.master, text="Back to Login", command=self.back_to_login, bg="#f44336", fg="white", font=("Arial", 14, "bold"))
        back_button.pack(pady=20, padx=20, side=tk.BOTTOM, anchor=tk.SE)

        self.refresh_trip_history()

    def book_taxi(self):
        pickup = self.pickup_entry.get()
        dropoff = self.dropoff_entry.get()

        if pickup and dropoff:
            self.db.add_trip(self.user[0], pickup, dropoff)
            messagebox.showinfo("Booking Successful", "Your taxi has been booked and is waiting for assignment")
            self.pickup_entry.delete(0, tk.END)
            self.dropoff_entry.delete(0, tk.END)
            self.refresh_trip_history()
        else:
            messagebox.showerror("Booking Failed", "Please enter both pickup and drop-off locations")

    def refresh_trip_history(self):
        for item in self.trip_tree.get_children():
            self.trip_tree.delete(item)

        trips = self.db.get_user_trips(self.user[0])
        for trip in trips:
            self.trip_tree.insert("", "end", values=trip)

    def cancel_booking(self):
        selected_item = self.trip_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a trip to cancel")
            return

        trip_id = self.trip_tree.item(selected_item)['values'][0]
        trip_status = self.trip_tree.item(selected_item)['values'][3]

        if trip_status not in ["Pending", "Assigned"]:
            messagebox.showerror("Error", "You can only cancel pending or assigned trips")
            return

        if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this booking?"):
            self.db.update_trip_status(trip_id, "Cancelled")
            messagebox.showinfo("Success", "Your booking has been cancelled")
            self.refresh_trip_history()

    def back_to_login(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to log out?"):
            self.master.destroy()
            self.main_window.deiconify()
