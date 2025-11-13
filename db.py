import sqlite3
import os

DB_PATH = os.path.join("instance", "medi_reach.db")


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_medicine_table():
    """Create medicines table if not exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def init_orders_table():
    """Create orders table if not exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
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
    conn.commit()
    conn.close()


def seed_medicines():
    """Insert sample data (for development)."""
    sample_data = [
        ("Paracetamol", 5.00),
        ("Amoxicillin", 8.50),
        ("Ibuprofen", 6.75),
        ("Vitamin C", 4.25),
    ]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM medicines")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO medicines (name, price) VALUES (?, ?)", sample_data
        )
        conn.commit()
        print("Sample medicines added!")
    else:
        print("Medicines already exist - skipping seeding.")

    conn.close()
