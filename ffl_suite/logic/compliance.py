from ffl_suite.database.db_manager import execute_query

def can_acquire(make, model, serial_number):
    """
    Checks if a firearm with the same make, model, and serial number already exists in inventory.
    """
    # Now that we have UPC, we could check that too, but serial uniqueness is the key ATF requirement.
    # Note: Technically, two manufacturers can have the same serial, so Make/Model/Serial combo is standard check.
    sql = "SELECT id FROM firearms WHERE make = ? AND model = ? AND serial_number = ? AND disposition_date IS NULL"
    result = execute_query(sql, (make, model, serial_number), fetch=True)
    return len(result) == 0

def can_dispose(firearm_id):
    """
    Checks if a firearm can be disposed (must not already be disposed).
    """
    sql = "SELECT disposition_date FROM firearms WHERE id = ?"
    result = execute_query(sql, (firearm_id,), fetch=True)
    if not result:
        return False
    return result[0][0] is None
