from ffl_suite.database.db_manager import execute_query
from datetime import datetime, timedelta

def get_sales_analytics():
    # Last 7 days sales
    dates = []
    totals = []
    for i in range(6, -1, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(d)

        # This query is a bit simplified, assumes sale_date is YYYY-MM-DD or ISO
        sql = "SELECT SUM(total) FROM sales_orders WHERE sale_date LIKE ?"
        res = execute_query(sql, (f"{d}%",), fetch=True)
        totals.append(res[0][0] or 0)

    return {'labels': dates, 'data': totals}

def get_inventory_analytics():
    # Breakdown by Type
    sql = "SELECT type, COUNT(*) FROM firearms WHERE disposition_date IS NULL GROUP BY type"
    res = execute_query(sql, fetch=True)
    labels = [r[0] for r in res]
    data = [r[1] for r in res]
    return {'labels': labels, 'data': data}

def get_recent_activity(limit=10):
    # Merge Acq, Disp, Sales
    # For MVP, just Firearms Acq/Disp
    sql = """
        SELECT 'Acquisition' as type, make || ' ' || model as item, acquisition_date as date
        FROM firearms ORDER BY acquisition_date DESC LIMIT ?
    """
    acq = execute_query(sql, (limit,), fetch=True)
    return [{'type': r[0], 'description': r[1], 'date': r[2]} for r in acq]
