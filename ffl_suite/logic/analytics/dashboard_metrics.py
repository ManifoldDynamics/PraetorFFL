from ffl_suite.database.db_manager import execute_query

def get_inventory_count():
    """Returns the total number of firearms currently in inventory (not disposed)."""
    sql = "SELECT COUNT(*) FROM firearms WHERE disposition_date IS NULL"
    result = execute_query(sql, fetch=True)
    return result[0][0] if result else 0

def get_total_acquisitions_count():
    """Returns the total number of firearms ever acquired."""
    sql = "SELECT COUNT(*) FROM firearms"
    result = execute_query(sql, fetch=True)
    return result[0][0] if result else 0

def get_total_dispositions_count():
    """Returns the total number of disposed firearms."""
    sql = "SELECT COUNT(*) FROM firearms WHERE disposition_date IS NOT NULL"
    result = execute_query(sql, fetch=True)
    return result[0][0] if result else 0

def get_open_dispositions_warning():
    """
    Returns a count of firearms that have been in inventory for > 365 days.
    (This is just an example metric, ATF doesn't mandate disposal time, but useful for business).
    """
    # SQLite 'date' function can calculate difference
    sql = """
        SELECT COUNT(*) FROM firearms
        WHERE disposition_date IS NULL
        AND date(acquisition_date) < date('now', '-1 year')
    """
    result = execute_query(sql, fetch=True)
    return result[0][0] if result else 0

def get_recent_activity(limit=5):
    """Returns the last 5 acquisitions or dispositions combined."""
    sql = """
        SELECT 'Acquisition' as type, make || ' ' || model as item, acquisition_date as date
        FROM firearms ORDER BY acquisition_date DESC LIMIT ?
    """
    # Merging acq/disp in one query is complex in simple SQLite without extensive UNION.
    # Let's just show recent acquisitions for now.
    return execute_query(sql, (limit,), fetch=True)
