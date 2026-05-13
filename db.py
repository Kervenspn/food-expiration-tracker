import sqlite3

DB_NAME = "food.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    cursor = conn.cursor()

    #Create the items table if it doesn't exist yet
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expiration_date TEXT NOT NULL,
        image_path TEXT,
        category TEXT DEFAULT 'Fridge'
    )
    """)

    # If the table already exists, try adding the category column
    # This won't crash if it already exists. I hope
    try:
        cursor.execute("ALTER TABLE items ADD COLUMN category TEXT DEFAULT 'Fridge'")
    except:
        pass

    conn.commit()
    conn.close()

def add_item(name, expiration_date, image_path=None, category="Fridge"):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (name, expiration_date, image_path, category) VALUES (?, ?, ?, ?)",
        (name, str(expiration_date), image_path, category)
    )

    conn.commit()
    conn.close()

def get_items():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, expiration_date, image_path, category
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

def update_item(item_id, name, expiration_date, category):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE items SET name = ?, expiration_date = ?, category = ? WHERE id = ?",
        (name, str(expiration_date), category, item_id)
    )

    conn.commit()
    conn.close()