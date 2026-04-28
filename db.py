import sqlite3

DB_NAME = "food.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expiration_date TEXT NOT NULL,
        image_path TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_item(name, expiration_date, image_path=None):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (name, expiration_date, image_path) VALUES (?, ?, ?)",
        (name, str(expiration_date), image_path)
    )

    conn.commit()
    conn.close()

def get_items():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, expiration_date, image_path
    FROM items
    ORDER BY expiration_date
""")

    items = cursor.fetchall()
    conn.close()
    return items

def delete_item(item_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()