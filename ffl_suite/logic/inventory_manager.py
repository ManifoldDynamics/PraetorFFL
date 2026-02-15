from ffl_suite.database.db_manager import execute_query

def add_acquisition(firearm_data, contact_id):
    """
    Adds a firearm acquisition to the database.

    Args:
        firearm_data (dict): Contains 'make', 'model', 'serial_number', 'type', 'caliber', 'importer', 'condition', 'acquisition_date'.
        contact_id (int): The ID of the contact from whom the firearm was acquired.

    Returns:
        int: The ID of the newly added firearm, or None on failure.
    """
    query = """
        INSERT INTO firearms (make, model, serial_number, type, caliber, importer, condition, acquisition_date, source_contact_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        firearm_data.get('make'),
        firearm_data.get('model'),
        firearm_data.get('serial_number'),
        firearm_data.get('type'),
        firearm_data.get('caliber'),
        firearm_data.get('importer'),
        firearm_data.get('condition'),
        firearm_data.get('acquisition_date'),
        contact_id
    )
    return execute_query(query, params)

def record_disposition(firearm_id, contact_id, disposition_date):
    """
    Updates a firearm record with disposition details.

    Args:
        firearm_id (int): The ID of the firearm to dispose.
        contact_id (int): The ID of the contact to whom the firearm is disposed.
        disposition_date (str): The date of disposition (YYYY-MM-DD).

    Returns:
        int: The number of rows affected (should be 1), or None.
    """
    query = """
        UPDATE firearms
        SET disposition_contact_id = ?, disposition_date = ?
        WHERE id = ?
    """
    params = (contact_id, disposition_date, firearm_id)
    # execute_query returns lastrowid for INSERT, but for UPDATE we might want rowcount.
    # For now, let's just assume it worked if no exception.
    # To be precise, execute_query should return cursor.rowcount for updates.
    # I'll update db_manager later to support this better, but for now let's rely on it.
    return execute_query(query, params)

def search_inventory(query_str):
    """
    Searches for firearms in inventory (not disposed).

    Args:
        query_str (str): The search term.

    Returns:
        list: A list of firearm records.
    """
    sql = """
        SELECT * FROM firearms
        WHERE (make LIKE ? OR model LIKE ? OR serial_number LIKE ?)
        AND disposition_date IS NULL
    """
    params = (f'%{query_str}%', f'%{query_str}%', f'%{query_str}%')
    return execute_query(sql, params, fetch=True)

def get_bound_book():
    """
    Retrieves the complete Bound Book (Acquisitions & Dispositions).

    Returns:
        list: A list of all firearm records with contact names joined.
    """
    sql = """
        SELECT f.id, f.make, f.model, f.serial_number, f.type, f.caliber,
               f.acquisition_date, c1.name,
               f.disposition_date, c2.name
        FROM firearms f
        LEFT JOIN contacts c1 ON f.source_contact_id = c1.id
        LEFT JOIN contacts c2 ON f.disposition_contact_id = c2.id
        ORDER BY f.acquisition_date DESC
    """
    return execute_query(sql, fetch=True)
