import sqlite3  # SQLite database module
import os  # OS utilities for paths

DB_PATH = os.path.join("instance", "medi_reach.db")  # DB file path under instance/


def get_db_connection():  # Helper to open DB connection
    """Create and return a database connection."""
    os.makedirs('instance', exist_ok=True)  # Ensure DB directory exists
    conn = sqlite3.connect(DB_PATH)  # Open connection to SQLite file
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn  # Return connection


def init_medicine_table():  # Ensure medicines table exists
    """Create medicines table if not exists."""
    conn = get_db_connection()  # Open DB
    cursor = conn.cursor()  # Cursor for SQL
    cursor.execute(  # Create table if missing
        """
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """
    )
    conn.commit()  # Save changes
    conn.close()  # Close DB


def init_orders_table():  # Ensure orders table exists
    """Create orders table if not exists."""
    conn = get_db_connection()  # Open DB
    cursor = conn.cursor()  # Cursor for SQL
    cursor.execute(  # Create table if missing
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_price REAL NOT NULL,
            delivery_address TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """
    )
    conn.commit()  # Save changes
    conn.close()  # Close DB


def seed_medicines():  # Seed demo medicines in dev
    """Insert sample data (for development)."""
    sample_data = [  # Name and price pairs
        ("Paracetamol", 5.00),
        ("Amoxicillin", 8.50),
        ("Ibuprofen", 6.75),
        ("Vitamin C", 4.25),
    ]

    conn = get_db_connection()  # Open DB
    cursor = conn.cursor()  # Cursor
    cursor.execute("SELECT COUNT(*) FROM medicines")  # Check existing rows
    count = cursor.fetchone()[0]  # Get count

    if count == 0:  # Only insert if empty
        cursor.executemany(
            "INSERT INTO medicines (name, price) VALUES (?, ?)", sample_data
        )
        conn.commit()  # Save insertions
        print("Sample medicines added!")  # Log
    else:
        print("Medicines already exist - skipping seeding.")  # Log

    conn.close()  # Close DB
