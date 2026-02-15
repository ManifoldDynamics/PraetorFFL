from ffl_suite.database.db_manager import execute_query

def get_setting(key):
    """Retrieves a setting value."""
    sql = "SELECT value FROM settings WHERE key = ?"
    result = execute_query(sql, (key,), fetch=True)
    if result and len(result) > 0:
        return result[0][0]
    return None

def set_setting(key, value):
    """Sets a setting value."""
    # SQLite doesn't have UPSERT in older versions, but 'REPLACE INTO' works.
    sql = "REPLACE INTO settings (key, value) VALUES (?, ?)"
    return execute_query(sql, (key, value))

def get_ffl_info():
    """Returns a dict of FFL information."""
    return {
        'name': get_setting('ffl_name'),
        'license_number': get_setting('ffl_license_number'),
        'premise_address': get_setting('ffl_premise_address')
    }
