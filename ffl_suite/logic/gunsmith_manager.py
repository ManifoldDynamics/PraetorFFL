from ffl_suite.database.db_manager import execute_query

def create_job(customer_id, firearm_id, description):
    sql = "INSERT INTO gunsmith_jobs (customer_id, firearm_id, description, status, intake_date) VALUES (?, ?, ?, 'Intake', date('now'))"
    return execute_query(sql, (customer_id, firearm_id, description))

def get_active_jobs():
    sql = """
        SELECT j.id, c.name, f.make || ' ' || f.model, j.description, j.status, j.intake_date
        FROM gunsmith_jobs j
        LEFT JOIN contacts c ON j.customer_id = c.id
        LEFT JOIN firearms f ON j.firearm_id = f.id
        WHERE j.status != 'Delivered'
        ORDER BY j.id DESC
    """
    return execute_query(sql, fetch=True)

def update_job_status(job_id, status):
    execute_query("UPDATE gunsmith_jobs SET status = ? WHERE id = ?", (status, job_id))

def add_job_item(job_id, item_type, description, qty, cost, price):
    sql = "INSERT INTO job_items (job_id, item_type, description, quantity, cost_per_unit, price_per_unit) VALUES (?, ?, ?, ?, ?, ?)"
    execute_query(sql, (job_id, item_type, description, qty, cost, price))

def get_job_details(job_id):
    job = execute_query("SELECT * FROM gunsmith_jobs WHERE id = ?", (job_id,), fetch=True)
    items = execute_query("SELECT * FROM job_items WHERE job_id = ?", (job_id,), fetch=True)
    return job[0] if job else None, items
