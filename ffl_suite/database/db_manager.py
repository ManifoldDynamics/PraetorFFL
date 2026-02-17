import sqlite3
import os
import sys

# Store DB in data directory for persistence
DB_FILE = os.path.join(os.environ.get('DATA_DIR', '.'), 'ffl_data.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def init_db():
    """Initializes the database by running the schema script."""
    schema_path = get_resource_path('schema.sql')

    conn = get_connection()
    cursor = conn.cursor()

    with open(schema_path, 'r') as f:
        schema_script = f.read()
        cursor.executescript(schema_script)

    conn.commit()
    conn.close()
    print("Database initialized.")

def execute_query(query, params=(), fetch=False):
    """Executes a SQL query with optional parameters."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        conn.commit()
        if query.strip().upper().startswith("INSERT"):
            return cursor.lastrowid
        else:
            return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
