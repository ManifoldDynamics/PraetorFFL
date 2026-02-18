from flask import Flask, render_template, jsonify, request
import sys
import threading
import os

# Initialize Flask
template_dir = os.path.join(os.path.dirname(__file__), 'ffl_suite/web/templates')
static_dir = os.path.join(os.path.dirname(__file__), 'ffl_suite/web/static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize DB on startup (for Gunicorn/Docker)
from ffl_suite.database.db_manager import init_db, execute_query, get_resource_path
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"DB Init Warning: {e}")

# API Routes to access existing logic
from ffl_suite.logic.inventory_manager import (
    get_inventory_count, get_total_acquisitions_count, get_total_dispositions_count,
    search_inventory, add_acquisition, record_disposition
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/modules/<path:name>')
def get_module(name):
    return render_template(f'modules/{name}.html')

@app.route('/api/dashboard/stats')
def get_stats():
    return jsonify({
        'inventory': get_inventory_count(),
        'acquisitions': get_total_acquisitions_count(),
        'dispositions': get_total_dispositions_count()
    })

@app.route('/api/inventory')
def api_inventory():
    query = request.args.get('q', '')
    # Need to fetch price/cost too. search_inventory returns SELECT *
    # Schema: id, make, model, serial, type, caliber, importer, condition, upc, price, cost, acq_date...
    # Let's check logic/inventory_manager.py search_inventory
    results = search_inventory(query)
    data = []
    if results:
        for r in results:
            # Safer to map by index if we know schema order, or dict factory.
            # Schema order in create: id, make, model, serial, type, caliber, importer, condition, upc, price, cost...
            # 0:id, 1:make, 2:model, 3:serial, 4:type, 5:caliber, 6:importer, 7:cond, 8:upc, 9:price, 10:cost
            data.append({
                'id': r[0], 'make': r[1], 'model': r[2], 'serial': r[3],
                'type': r[4], 'caliber': r[5], 'upc': r[8], 'price': r[9], 'cost': r[10]
            })
    return jsonify(data)

@app.route('/api/contacts')
def api_contacts():
    # Simple direct query for contacts
    contacts = execute_query("SELECT id, name FROM contacts", fetch=True)
    return jsonify([{'id': c[0], 'name': c[1]} for c in contacts])

@app.route('/api/acquire', methods=['POST'])
def api_acquire():
    data = request.json
    # data: contact_id, make, model...
    try:
        add_acquisition(data, data['contact_id'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/dispose', methods=['POST'])
def api_dispose():
    data = request.json
    try:
        record_disposition(data['firearm_id'], data['contact_id'], data['date'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/4473/submit', methods=['POST'])
def api_submit_4473():
    data = request.json
    try:
        from ffl_suite.logic.transaction_manager import save_draft_4473
        from ffl_suite.reports.pdf_generator import generate_4473_pdf
        from ffl_suite.logic.settings_manager import get_ffl_info

        # Save to DB
        tid = save_draft_4473(data)

        # Generate PDF - Use persistent data dir if in Docker
        pdf_dir = os.path.join(os.environ.get('DATA_DIR', '.'), "forms_4473")
        if not os.path.exists(pdf_dir): os.makedirs(pdf_dir)
        filename = f"4473_{tid}_{data.get('transferee_name')}.pdf".replace(' ', '_')
        filepath = os.path.join(pdf_dir, filename)

        # We need structured data for the generator
        # firearm info might be ID only in 'data', need to fetch details?
        # The wizard sends firearm_id. Let's fetch firearm details.
        from ffl_suite.database.db_manager import execute_query
        firearm_res = execute_query("SELECT make, model, serial_number, type, caliber FROM firearms WHERE id=?", (data.get('firearm_id'),), fetch=True)
        firearm_data = {}
        if firearm_res:
            fr = firearm_res[0]
            firearm_data = {'make': fr[0], 'model': fr[1], 'serial': fr[2], 'type': fr[3], 'caliber': fr[4]}

        buyer_data = {'name': data.get('transferee_name')}
        ffl_data = get_ffl_info()

        generate_4473_pdf(filepath, firearm_data, buyer_data, ffl_data, full_data=data)

        return jsonify({'success': True, 'pdf_url': f'/api/4473/download/{filename}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/4473/download/<filename>')
def api_download_4473(filename):
    from flask import send_from_directory
    directory = os.path.join(os.environ.get('DATA_DIR', '.'), "forms_4473")
    return send_from_directory(directory, filename)

# POS APIs
@app.route('/api/products')
def api_products():
    from ffl_suite.logic.pos_manager import get_all_products
    q = request.args.get('q')
    prods = get_all_products(q)
    # Convert to dict list
    data = [{'id': p[0], 'upc': p[1], 'name': p[2], 'price': p[4], 'stock': p[6]} for p in prods]
    return jsonify(data)

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.json
    try:
        from ffl_suite.logic.pos_manager import process_sale
        sale_id = process_sale(data)
        return jsonify({'success': True, 'sale_id': sale_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- Settings APIs ---
@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    from ffl_suite.logic.settings_manager import get_setting, set_setting

    keys = ['ffl_name', 'ffl_license_number', 'ffl_premise_address', 'tax_rate', 'printer_ip', 'printer_type', 'receipt_footer', 'logo_path']

    if request.method == 'GET':
        data = {k: get_setting(k) for k in keys}
        return jsonify(data)
    else: # POST
        data = request.json
        for k, v in data.items():
            set_setting(k, v)
        return jsonify({'success': True})

@app.route('/api/sales/receipt/<int:sale_id>')
def api_get_receipt(sale_id):
    # Serve the PDF
    from flask import send_file
    from ffl_suite.database.db_manager import execute_query
    res = execute_query("SELECT receipt_path FROM sales_orders WHERE id = ?", (sale_id,), fetch=True)
    if res and res[0][0]:
        # Path stored in DB might be absolute or relative.
        # If relative, we assume it's relative to CWD or DATA_DIR logic
        path = res[0][0]
        if os.path.exists(path):
            return send_file(path)
    return "Receipt not found", 404

# --- Inventory Edit ---
@app.route('/api/inventory/update', methods=['POST'])
def api_inventory_update():
    data = request.json
    try:
        from ffl_suite.database.db_manager import execute_query
        sql = "UPDATE firearms SET make=?, model=?, serial_number=?, type=?, caliber=?, upc=?, price=?, cost=? WHERE id=?"
        execute_query(sql, (data['make'], data['model'], data['serial'], data['type'], data['caliber'], data.get('upc'), data.get('price', 0), data.get('cost', 0), data['id']))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# --- NFA APIs ---
@app.route('/api/nfa/inventory')
def api_nfa_inventory():
    from ffl_suite.database.db_manager import execute_query
    # Filter for NFA types
    sql = "SELECT id, make, model, serial_number, type, caliber FROM firearms WHERE type IN ('Silencer', 'Short-Barreled Rifle', 'Short-Barreled Shotgun', 'Machine Gun', 'Any Other Weapon') AND disposition_date IS NULL"
    rows = execute_query(sql, fetch=True)
    data = [{'id': r[0], 'make': r[1], 'model': r[2], 'serial': r[3], 'type': r[4], 'caliber': r[5]} for r in rows]
    return jsonify(data)

@app.route('/api/nfa/acquire', methods=['POST'])
def api_nfa_acquire():
    data = request.json
    # Same as regular acquisition but enforces NFA type
    try:
        add_acquisition(data, data.get('contact_id')) # contact_id might be null if from Form 2 (Manufacture)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/nfa/entities', methods=['GET', 'POST'])
def api_nfa_entities():
    from ffl_suite.logic.nfa_manager import get_nfa_entities, add_nfa_entity
    if request.method == 'GET':
        ents = get_nfa_entities()
        return jsonify([{'id': e[0], 'name': e[1], 'type': e[2]} for e in ents])
    else:
        try:
            add_nfa_entity(request.json)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/nfa/forms', methods=['POST'])
def api_nfa_forms():
    data = request.json
    try:
        from ffl_suite.logic.nfa_manager import create_nfa_form, get_nfa_form_details
        from ffl_suite.reports.nfa_pdf_generator import generate_form4_helper

        # Create draft
        row_id = create_nfa_form(data['form_type'], data['transferee_entity_id'], data['firearm_id'], data)
        full_data = get_nfa_form_details(row_id)

        # Generate PDF
        pdf_dir = os.path.join(os.environ.get('DATA_DIR', '.'), "forms_nfa")
        if not os.path.exists(pdf_dir): os.makedirs(pdf_dir)
        filename = f"Form4_Helper_{row_id}.pdf"
        filepath = os.path.join(pdf_dir, filename)

        generate_form4_helper(filepath, full_data)

        return jsonify({'success': True, 'pdf_url': f'/api/nfa/download/{filename}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/nfa/download/<filename>')
def api_download_nfa(filename):
    from flask import send_from_directory
    directory = os.path.join(os.environ.get('DATA_DIR', '.'), "forms_nfa")
    return send_from_directory(directory, filename)

# --- Gunsmithing APIs ---
@app.route('/api/gunsmith/jobs', methods=['GET', 'POST', 'DELETE'])
def api_gunsmith_jobs():
    from ffl_suite.logic.gunsmith_manager import get_active_jobs, create_job
    from ffl_suite.database.db_manager import execute_query

    if request.method == 'GET':
        jobs = get_active_jobs()
        # jobs: id, customer, gun, desc, status, date
        return jsonify([{'id': j[0], 'customer': j[1], 'gun': j[2], 'description': j[3], 'status': j[4], 'date': j[5]} for j in jobs])

    elif request.method == 'POST':
        data = request.json
        if 'id' in data: # Update
            execute_query("UPDATE gunsmith_jobs SET status=?, description=?, notes=? WHERE id=?",
                          (data['status'], data['description'], data.get('notes'), data['id']))
            return jsonify({'success': True})
        else: # Create
            try:
                create_job(data['customer_id'], data['firearm_id'], data['description'])
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400

    elif request.method == 'DELETE':
        jid = request.args.get('id')
        execute_query("DELETE FROM gunsmith_jobs WHERE id=?", (jid,))
        return jsonify({'success': True})

# Start logic
def start_server():
    app.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == '__main__':
    # Initialize DB
    init_db()

    if os.environ.get('DOCKER_MODE'):
        print("Starting in Docker Mode (Gunicorn should handle this)...")
        # If run directly in docker without gunicorn:
        app.run(host='0.0.0.0', port=5000)
    else:
        import webview
        # Start Flask in a thread
        t = threading.Thread(target=start_server)
        t.daemon = True
        t.start()

        # Create Native Window
        webview.create_window('FFL Suite', 'http://127.0.0.1:5000', width=1280, height=800, resizable=True)
        webview.start()
