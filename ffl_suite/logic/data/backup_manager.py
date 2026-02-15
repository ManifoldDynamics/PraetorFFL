import shutil
import os
import datetime
import csv
from ffl_suite.database.db_manager import DB_FILE, execute_query

BACKUP_DIR = 'backups'

def create_backup():
    """Creates a timestamped copy of the database."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"ffl_data_{timestamp}.db")

    try:
        shutil.copy2(DB_FILE, backup_path)
        return backup_path
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def export_contacts_csv(filepath):
    """Exports contacts to CSV."""
    sql = "SELECT id, name, address_street, address_city, address_state, address_zip, license_number, phone, email, is_ffl FROM contacts"
    rows = execute_query(sql, fetch=True)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'street', 'city', 'state', 'zip', 'license', 'phone', 'email', 'is_ffl'])
        if rows:
            writer.writerows(rows)

def import_contacts_csv(filepath):
    """Imports contacts from CSV."""
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # Basic validation
            if 'name' not in row: continue

            sql = """
                INSERT INTO contacts (name, address_street, address_city, address_state, address_zip, license_number, phone, email, is_ffl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                row.get('name'), row.get('street'), row.get('city'), row.get('state'),
                row.get('zip'), row.get('license'), row.get('phone'), row.get('email'),
                row.get('is_ffl', 0)
            )
            execute_query(sql, params)
            count += 1
        return count
