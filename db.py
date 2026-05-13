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
        image_path TEXT,
        is_frozen INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        quantity INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produce (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ripeness TEXT NOT NULL,
        storage_location TEXT DEFAULT 'Fridge',
        notes TEXT DEFAULT '',
        quantity INTEGER DEFAULT 1,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    try:
        cursor.execute("ALTER TABLE items ADD COLUMN quantity INTEGER DEFAULT 1")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE produce ADD COLUMN image_path TEXT")
    except:
        pass

    conn.commit()
    conn.close()

def add_item(name, expiration_date, image_path=None, is_frozen=False, notes="", quantity=1):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (name, expiration_date, image_path, is_frozen, notes, quantity) VALUES (?, ?, ?, ?, ?, ?)",
        (name, str(expiration_date), image_path, int(is_frozen), notes, int(quantity))
    )

    conn.commit()
    conn.close()

def get_items():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, expiration_date, image_path, is_frozen, notes, quantity
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

def update_item(item_id, name, expiration_date, is_frozen, notes, quantity):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE items SET name = ?, expiration_date = ?, is_frozen = ?, notes = ?, quantity = ? WHERE id = ?",
        (name, str(expiration_date), int(is_frozen), notes, int(quantity), item_id)
    )

    conn.commit()
    conn.close()

def add_produce(name, ripeness, storage_location="Fridge", notes="", quantity=1, image_path=None):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO produce (name, ripeness, storage_location, notes, quantity, image_path) VALUES (?, ?, ?, ?, ?, ?)",
        (name, ripeness, storage_location, notes, int(quantity), image_path)
    )

    conn.commit()
    conn.close()

def get_produce():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, ripeness, storage_location, notes, quantity, image_path, created_at
    FROM produce
    ORDER BY created_at DESC
    """)

    produce = cursor.fetchall()
    conn.close()
    return produce

def delete_produce(produce_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produce WHERE id = ?", (produce_id,))

    conn.commit()
    conn.close()

def update_produce(produce_id, name, ripeness, storage_location, notes, quantity):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE produce SET name = ?, ripeness = ?, storage_location = ?, notes = ?, quantity = ? WHERE id = ?",
        (name, ripeness, storage_location, notes, int(quantity), produce_id)
    )

    conn.commit()
    conn.close()