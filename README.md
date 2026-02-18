# FFL Suite (Web Architecture)

A comprehensive, web-based FFL software suite featuring Inventory Management, A&D Bound Book, Digital 4473, NFA E-Forms Helper, and POS.

## Features
- **Web Interface:** Modern, touch-friendly UI using HTML5/Tailwind/Alpine.js.
- **Inventory:** Track firearms with price, cost, and acquisition/disposition details.
- **POS:** Point of Sale system with receipt generation and automatic inventory updates.
- **4473 Wizard:** Digital form with signature capture and PDF generation.
- **NFA Vault:** Dedicated module for NFA items and Trust management.
- **Gunsmithing:** Job tracking board.

## Installation

### Local Desktop (Single EXE)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main_web.py
   ```
   This will launch a native window wrapping the web application.

### Docker (Server)
1. Build and run:
   ```bash
   docker-compose up --build -d
   ```
2. Access at `http://localhost:5000`.

## Building Single EXE
Use PyInstaller to package the application:
```bash
python build_app.py
```
The executable will be in `dist/`.
