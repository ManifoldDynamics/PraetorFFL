from flask import Flask, render_template, jsonify, request
import sys
import threading
import os

# Initialize Flask
template_dir = os.path.join(os.path.dirname(__file__), 'ffl_suite/web/templates')
static_dir = os.path.join(os.path.dirname(__file__), 'ffl_suite/web/static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Ensure DB path is absolute if in docker
if os.environ.get('DOCKER_MODE'):
    # In docker, we might mount /app/data
    pass # DB manager usually defaults to relative, which is fine in /app

# API Routes to access existing logic
from ffl_suite.database.db_manager import init_db, execute_query
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
    results = search_inventory(query)
    # Convert tuples to dicts: id, make, model, serial, type, caliber
    data = []
    if results:
        for r in results:
            data.append({
                'id': r[0], 'make': r[1], 'model': r[2], 'serial': r[3],
                'type': r[4], 'caliber': r[5]
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
        save_draft_4473(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

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
