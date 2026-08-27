import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('taxi_booking.db')
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                name TEXT,
                address TEXT,
                email TEXT,
                phone TEXT
            )
        ''')
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                driver_id INTEGER,
                pickup_location TEXT,
                dropoff_location TEXT,
                status TEXT,
                datetime TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, username, password, role, name, address, email, phone):
        self.cur.execute('INSERT INTO users (username, password, role, name, address, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (username, password, role, name, address, email, phone))
        self.conn.commit()

    def get_user(self, username, password):
        self.cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        return self.cur.fetchone()

    def get_all_users(self):
        self.cur.execute('SELECT * FROM users')
        return self.cur.fetchall()

    def add_trip(self, customer_id, pickup_location, dropoff_location):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute('INSERT INTO trips (customer_id, pickup_location, dropoff_location, status, datetime) VALUES (?, ?, ?, ?, ?)',
                         (customer_id, pickup_location, dropoff_location, 'Pending', current_time))
        self.conn.commit()

    def get_pending_trips(self):
        self.cur.execute('SELECT * FROM trips WHERE status = "Pending"')
        return self.cur.fetchall()

    def assign_trip(self, trip_id, driver_id):
        self.cur.execute('UPDATE trips SET driver_id = ?, status = "Assigned" WHERE id = ?', (driver_id, trip_id))
        self.conn.commit()

    def get_assigned_trip(self, driver_id):
        self.cur.execute('SELECT * FROM trips WHERE driver_id = ? AND status = "Assigned"', (driver_id,))
        return self.cur.fetchone()

    def get_user_trips(self, user_id):
        self.cur.execute('SELECT id, pickup_location, dropoff_location, status, datetime FROM trips WHERE customer_id = ? ORDER BY datetime DESC', (user_id,))
        return self.cur.fetchall()

    def get_all_trips(self):
        self.cur.execute('SELECT * FROM trips')
        return self.cur.fetchall()

    def get_driver_trips(self, driver_id):
        self.cur.execute('SELECT * FROM trips WHERE driver_id = ? ORDER BY datetime DESC', (driver_id,))
        return self.cur.fetchall()

    def get_driver_completed_trips(self, driver_id):
        self.cur.execute('''
        SELECT t.id, u.name, t.pickup_location, t.dropoff_location, t.datetime
        FROM trips t
        JOIN users u ON t.customer_id = u.id
        WHERE t.driver_id = ? AND t.status = "Completed"
        ORDER BY t.datetime DESC
        ''', (driver_id,))
        return self.cur.fetchall()

    def get_available_drivers(self):
        self.cur.execute('SELECT id, name FROM users WHERE role = "driver" AND id NOT IN (SELECT DISTINCT driver_id FROM trips WHERE status = "Assigned")')
        return self.cur.fetchall()

    def get_trip_details(self, trip_id):
        self.cur.execute('''
        SELECT t.*, c.name as customer_name, d.name as driver_name 
        FROM trips t 
        LEFT JOIN users c ON t.customer_id = c.id 
        LEFT JOIN users d ON t.driver_id = d.id 
        WHERE t.id = ?
        ''', (trip_id,))
        return self.cur.fetchone()

    def update_trip_status(self, trip_id, status):
        self.cur.execute('UPDATE trips SET status = ? WHERE id = ?', (status, trip_id))
        self.conn.commit()

    def get_all_trips_with_details(self):
        self.cur.execute('''
        SELECT t.*, c.name as customer_name, d.name as driver_name 
        FROM trips t 
        LEFT JOIN users c ON t.customer_id = c.id 
        LEFT JOIN users d ON t.driver_id = d.id 
        ORDER BY t.datetime DESC
        ''')
        return self.cur.fetchall()

    def close(self):
        self.conn.close()
