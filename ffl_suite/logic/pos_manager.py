from ffl_suite.database.db_manager import execute_query
from datetime import datetime

def get_all_products(search_query=None):
    sql = "SELECT * FROM products"
    params = ()
    if search_query:
        sql += " WHERE name LIKE ? OR upc LIKE ?"
        p = f"%{search_query}%"
        params = (p, p)
    return execute_query(sql, params, fetch=True)

def create_product(data):
    sql = "INSERT INTO products (upc, name, description, price, cost, quantity_on_hand, category) VALUES (?, ?, ?, ?, ?, ?, ?)"
    params = (
        data.get('upc'), data['name'], data.get('description'),
        data.get('price', 0), data.get('cost', 0), data.get('quantity_on_hand', 0), data.get('category')
    )
    return execute_query(sql, params)

def process_sale(sale_data):
    """
    Finalizes a sale.
    sale_data: {
        customer_id,
        payment_method,
        items: [ { type: 'product'|'firearm', id: 1, price: 100, qty: 1 } ]
    }
    """
    # 1. Calculate Totals
    subtotal = sum(item['price'] * item['quantity'] for item in sale_data['items'])
    tax_rate = 0.0825 # Example Texas tax, ideally from settings
    tax = subtotal * tax_rate
    total = subtotal + tax

    # 2. Create Sale Record
    sale_sql = """
        INSERT INTO sales_orders (customer_id, sale_date, subtotal, tax, total, payment_method, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Completed')
    """
    sale_id = execute_query(sale_sql, (sale_data.get('customer_id'), datetime.now().isoformat(), subtotal, tax, total, sale_data['payment_method']))

    # 3. Process Items
    for item in sale_data['items']:
        # Record Line Item
        item_sql = """
            INSERT INTO sale_items (sale_id, product_id, firearm_id, description, quantity, price_per_unit)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        pid = item['id'] if item['type'] == 'product' else None
        fid = item['id'] if item['type'] == 'firearm' else None

        # Fetch description if missing
        desc = item.get('description', 'Item')

        execute_query(item_sql, (sale_id, pid, fid, desc, item['quantity'], item['price']))

        # Inventory Deductions
        if item['type'] == 'product':
            execute_query("UPDATE products SET quantity_on_hand = quantity_on_hand - ? WHERE id = ?", (item['quantity'], pid))
        elif item['type'] == 'firearm':
            # Auto-dispose if firearm
            from ffl_suite.logic.inventory_manager import record_disposition
            # Disposition date is today
            record_disposition(fid, sale_data.get('customer_id'), datetime.now().strftime("%Y-%m-%d"))

    # 4. Generate Receipt PDF
    try:
        from ffl_suite.reports.receipt_generator import generate_receipt_pdf
        import os
        # Ensure directory
        rec_dir = os.path.join(os.environ.get('DATA_DIR', '.'), "receipts")
        if not os.path.exists(rec_dir): os.makedirs(rec_dir)
        path = os.path.join(rec_dir, f"receipt_{sale_id}.pdf")

        # Gather full data
        full_sale_data = {
            'id': sale_id, 'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'subtotal': subtotal, 'tax': tax, 'total': total,
            'items': sale_data['items']
        }
        generate_receipt_pdf(path, full_sale_data)

        # Update DB
        execute_query("UPDATE sales_orders SET receipt_path = ? WHERE id = ?", (path, sale_id))
    except Exception as e:
        print(f"Receipt Gen Error: {e}")

    return sale_id
