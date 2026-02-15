import sys
import os

# Ensure the local package path is in sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Also add the parent directory if running from inside ffl_suite
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ffl_suite.gui.app import App
from ffl_suite.database.db_manager import init_db

def main():
    print("FFL Suite Starting...")
    init_db()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
