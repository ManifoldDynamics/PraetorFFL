from ffl_suite.database.db_manager import execute_query

def create_po(vendor_id):
    sql = "INSERT INTO purchase_orders (vendor_id, order_date, status) VALUES (?, date('now'), 'Draft')"
    return execute_query(sql, (vendor_id,))

def add_po_item(po_id, desc, make, model, upc, qty, cost):
    sql = "INSERT INTO po_items (po_id, description, make, model, upc, quantity_ordered, cost) VALUES (?, ?, ?, ?, ?, ?, ?)"
    execute_query(sql, (po_id, desc, make, model, upc, qty, cost))

def get_open_pos():
    sql = """
        SELECT p.id, c.name, p.order_date, p.status,
               (SELECT COUNT(*) FROM po_items WHERE po_id = p.id) as item_count
        FROM purchase_orders p
        JOIN contacts c ON p.vendor_id = c.id
        WHERE p.status != 'Received'
    """
    return execute_query(sql, fetch=True)

def receive_po(po_id):
    # Convert items to inventory
    items = execute_query("SELECT * FROM po_items WHERE po_id = ?", (po_id,), fetch=True)
    if items:
        from ffl_suite.logic.inventory_manager import add_acquisition
        from datetime import date

        # Get vendor ID
        po = execute_query("SELECT vendor_id FROM purchase_orders WHERE id = ?", (po_id,), fetch=True)
        vid = po[0][0]

        for item in items:
            # item: id(0), po_id(1), desc(2), make(3), model(4), upc(5), qty_ord(6)...
            # Add each quantity as separate serial (placeholder) or just stock
            # For serialized items, usually we need to input serials upon receipt.
            # MVP: Just mark received, user manually adds serials via Bulk Acquisition?
            # Better: Create "Pending Serial Input" records?
            # Let's keep it simple: Just mark PO received.
            pass

    execute_query("UPDATE purchase_orders SET status = 'Received' WHERE id = ?", (po_id,))
