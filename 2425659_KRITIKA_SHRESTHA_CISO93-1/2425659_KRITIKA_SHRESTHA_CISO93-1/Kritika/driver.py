import tkinter as tk
from tkinter import ttk, messagebox

class DriverInterface:
    def __init__(self, master, db, user, main_window):
        self.master = master
        self.db = db
        self.user = user
        self.main_window = main_window

        self.master.title("Driver Interface")
        self.master.geometry("1200x900")
        self.master.configure(bg="#E1F5FE")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.master, text=f"Welcome, {self.user[4]}!", font=("Arial", 18), bg="#E1F5FE")
        title_label.pack(pady=20)

        main_frame = tk.Frame(self.master, bg="#FFF9C4")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left_frame = tk.Frame(main_frame, bg="#FFFFFF", width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = tk.Frame(main_frame, bg="#FFFFFF")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.create_dashboard(left_frame)
        self.create_trip_info(right_frame)

        back_button = tk.Button(self.master, text="Back to Login", command=self.back_to_login, bg="#f44336", fg="white", font=("Arial", 12))
        back_button.pack(pady=10, padx=20, side=tk.BOTTOM, anchor=tk.SE)

    def create_dashboard(self, parent):
        tk.Label(parent, text="Driver Detail", font=("Arial", 16, "bold"), bg="#FFFFFF").pack(pady=10)

        details_frame = tk.Frame(parent, bg="#FFFFFF")
        details_frame.pack(padx=10, pady=10, fill=tk.X)

        details = [
            ("Name", self.user[4]),
            ("Email", self.user[6]),
            ("Phone", self.user[7])
        ]

        for i, (label, value) in enumerate(details):
            tk.Label(details_frame, text=f"{label}:", bg="#FFFFFF", font=("Arial", 12, "bold")).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            tk.Label(details_frame, text=value, bg="#FFFFFF", font=("Arial", 12)).grid(row=i, column=1, padx=5, pady=5, sticky="w")

        stats_frame = tk.Frame(parent, bg="#FFFFFF")
        stats_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(stats_frame, text="Driver Statistics", font=("Arial", 14, "bold"), bg="#FFFFFF").pack(pady=10)

        # Add more statistics here as needed
        tk.Label(stats_frame, text="Total Trips: 0", bg="#FFFFFF", font=("Arial", 12)).pack(pady=5)
        tk.Label(stats_frame, text="Average Rating: N/A", bg="#FFFFFF", font=("Arial", 12)).pack(pady=5)

    def create_trip_info(self, parent):
        tk.Label(parent, text="Current Trip", font=("Arial", 16, "bold"), bg="#FFFFFF").pack(pady=10)

        self.trip_info = tk.StringVar()
        self.trip_info.set("No assigned trip")
        self.trip_label = tk.Label(parent, textvariable=self.trip_info, bg="#FFFFFF", font=("Arial", 12), wraplength=350)
        self.trip_label.pack(pady=20)

        button_frame = tk.Frame(parent, bg="#FFFFFF")
        button_frame.pack(pady=10)

        refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_trip, bg="#2196F3", fg="white", font=("Arial", 12))
        refresh_button.pack(side=tk.LEFT, padx=5)

        complete_button = tk.Button(button_frame, text="Complete Trip", command=self.complete_trip, bg="#4CAF50", fg="white", font=("Arial", 12))
        complete_button.pack(side=tk.LEFT, padx=5)

        # Add a treeview for completed trips
        tk.Label(parent, text="Completed Trips", font=("Arial", 14, "bold"), bg="#FFFFFF").pack(pady=10)

        columns = ("ID", "Customer", "Pickup", "Drop-off", "Date/Time")
        self.completed_trips_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

        for col in columns:
            self.completed_trips_tree.heading(col, text=col)
            self.completed_trips_tree.column(col, width=100)

        self.completed_trips_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.refresh_completed_trips()

    def refresh_trip(self):
        trip = self.db.get_assigned_trip(self.user[0])
        if trip:
            self.trip_info.set(f"Customer ID: {trip[1]}\nPickup: {trip[3]}\nDrop-off: {trip[4]}\nStatus: {trip[5]}")
        else:
            self.trip_info.set("No assigned trip")

    def complete_trip(self):
        trip = self.db.get_assigned_trip(self.user[0])
        if trip:
            self.db.update_trip_status(trip[0], "Completed")
            messagebox.showinfo("Success", "Trip marked as completed")
            self.refresh_trip()
            self.refresh_completed_trips()
        else:
            messagebox.showerror("Error", "No active trip to complete")

    def refresh_completed_trips(self):
        for item in self.completed_trips_tree.get_children():
            self.completed_trips_tree.delete(item)

        completed_trips = self.db.get_driver_completed_trips(self.user[0])
        for trip in completed_trips:
            self.completed_trips_tree.insert("", "end", values=trip)

    def back_to_login(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to log out?"):
            self.master.destroy()
            self.main_window.deiconify()
