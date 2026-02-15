# FFL Suite

Open Source FFL Management Software.

## Features
- **Inventory Management**: Track acquisitions and dispositions.
- **A&D Bound Book**: Automatic generation of ATF-compliant Bound Book.
- **Form 4473**: Generate partial PDF 4473 forms.
- **Contacts**: Manage customers and vendors.
- **Compliance**: Basic checks for serial number duplication and inventory status.

## Installation

### Running from Source
1. Install Python 3.8+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python ffl_suite/main.py
   ```

### Building the Executable
1. Install dependencies.
2. Run the build script:
   ```bash
   python build_app.py
   ```
3. The executable will be in the `dist/` folder.

## Database
The application uses SQLite (`ffl_data.db`). The database is automatically created in the application directory upon first run.
