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
from ffl_suite.database.db_manager import init_db
from ffl_suite.logic.inventory_manager import get_inventory_count, get_total_acquisitions_count, get_total_dispositions_count

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard/stats')
def get_stats():
    return jsonify({
        'inventory': get_inventory_count(),
        'acquisitions': get_total_acquisitions_count(),
        'dispositions': get_total_dispositions_count()
    })

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
