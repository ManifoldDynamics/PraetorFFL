import sqlite3
import os

DB_FILE = 'ffl_data.db'

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database by running the schema script."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

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
