from ffl_suite.database.db_manager import execute_query

def save_draft_4473(data):
    """
    Saves a 4473 draft (incomplete).
    Returns transaction ID.
    """
    # Assuming 'data' is a dict matching columns.
    # For MVP, we'll just insert everything. In a real app, we might check if ID exists to UPDATE.

    columns = [
        'firearm_id', 'transferee_name', 'transferee_address', 'transferee_city', 'transferee_state', 'transferee_zip',
        'transferee_dob', 'transferee_pob', 'transferee_height', 'transferee_weight', 'transferee_sex',
        'transferee_ethnicity', 'transferee_race',
        'q_21a', 'q_21b', 'q_21c', 'q_21d', 'q_21e', 'q_21f', 'q_21g', 'q_21h', 'q_21i', 'q_21j', 'q_21k', 'q_21l1', 'q_21l2', 'q_21m',
        'id_type', 'id_number', 'id_expiration_date',
        'nics_ntn', 'nics_status', 'nics_date',
        'transferor_name', 'transferor_title', 'transfer_date',
        'buyer_signature_svg', 'certification_date'
    ]

    placeholders = ', '.join(['?'] * len(columns))
    col_str = ', '.join(columns)

    values = tuple(data.get(c) for c in columns)

    sql = f"INSERT INTO transactions_4473 ({col_str}) VALUES ({placeholders})"

    # We will just append the values tuple
    return execute_query(sql, tuple(data.get(c) for c in columns))

def get_4473_by_id(transaction_id):
    sql = "SELECT * FROM transactions_4473 WHERE id = ?"
    res = execute_query(sql, (transaction_id,), fetch=True)
    return res[0] if res else None

def get_recent_4473s(limit=10):
    sql = """
        SELECT t.id, t.transferee_name, t.transfer_date, f.serial_number, f.make, f.model
        FROM transactions_4473 t
        JOIN firearms f ON t.firearm_id = f.id
        ORDER BY t.id DESC LIMIT ?
    """
    return execute_query(sql, (limit,), fetch=True)
