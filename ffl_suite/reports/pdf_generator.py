from fpdf import FPDF
from datetime import datetime
from ffl_suite.logic.inventory_manager import get_bound_book
from ffl_suite.logic.settings_manager import get_ffl_info

class BoundBookPDF(FPDF):
    def header(self):
        info = get_ffl_info()
        name = info.get('name', 'FFL')
        license_num = info.get('license_number', 'N/A')
        address = info.get('premise_address', '')

        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Acquisition & Disposition Record', 0, 1, 'C')
        self.set_font('helvetica', '', 10)
        self.cell(0, 5, f"{name} - License: {license_num}", 0, 1, 'C')
        self.cell(0, 5, f"{address}", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_bound_book_pdf(filepath):
    pdf = BoundBookPDF(orientation='L', unit='mm', format='A4') # Landscape for wide table
    pdf.add_page()
    pdf.set_font("helvetica", size=8)

    # Table Header
    cols = [10, 30, 30, 30, 20, 20, 25, 40, 25, 40]
    headers = ['ID', 'Make', 'Model', 'Serial', 'Type', 'Cal.', 'Acq Date', 'From', 'Disp Date', 'To']

    pdf.set_font('helvetica', 'B', 8)
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 7, h, border=1)
    pdf.ln()

    # Data
    pdf.set_font('helvetica', '', 8)
    data = get_bound_book()
    if data:
        for row in data:
            # row: id, make, model, serial, type, caliber, acq_date, source_name, disp_date, dest_name
            values = list(row)
            if values[7] is None: values[7] = "Unknown"
            if values[8] is None: values[8] = ""
            if values[9] is None: values[9] = ""

            pdf.cell(cols[0], 6, str(values[0]), border=1)
            pdf.cell(cols[1], 6, str(values[1])[:18], border=1)
            pdf.cell(cols[2], 6, str(values[2])[:18], border=1)
            pdf.cell(cols[3], 6, str(values[3])[:18], border=1)
            pdf.cell(cols[4], 6, str(values[4])[:12], border=1)
            pdf.cell(cols[5], 6, str(values[5])[:12], border=1)
            pdf.cell(cols[6], 6, str(values[6]), border=1)
            pdf.cell(cols[7], 6, str(values[7])[:22], border=1)
            pdf.cell(cols[8], 6, str(values[8]), border=1)
            pdf.cell(cols[9], 6, str(values[9])[:22], border=1)
            pdf.ln()

    pdf.output(filepath)

def generate_4473_pdf(filepath, firearm_data, buyer_data, ffl_data, full_data=None):
    """
    Generates a PDF for Form 4473 using comprehensive data.
    """
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "ATF Form 4473 - Firearms Transaction Record", 0, 1, 'C')

    # Section A: Firearm
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Section A - Firearm Information", 0, 1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"Make: {firearm_data.get('make')}   Model: {firearm_data.get('model')}", 0, 1)
    pdf.cell(0, 6, f"Serial: {firearm_data.get('serial')}   Type: {firearm_data.get('type')}   Caliber: {firearm_data.get('caliber')}", 0, 1)
    pdf.ln(5)

    # Section B: Transferee
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Section B - Transferee Information", 0, 1)
    pdf.set_font("helvetica", '', 10)

    # Pull from full_data if available (preferred), else fallback to buyer_data
    d = full_data if full_data else buyer_data

    pdf.cell(0, 6, f"Name: {d.get('transferee_name', d.get('name'))}", 0, 1)
    pdf.cell(0, 6, f"Address: {d.get('transferee_address', '')} {d.get('transferee_city', '')} {d.get('transferee_state', '')} {d.get('transferee_zip', '')}", 0, 1)
    pdf.cell(0, 6, f"DOB: {d.get('transferee_dob', '')}   POB: {d.get('transferee_pob', '')}", 0, 1)
    pdf.cell(0, 6, f"Height: {d.get('transferee_height', '')}   Weight: {d.get('transferee_weight', '')}   Sex: {d.get('transferee_sex', '')}", 0, 1)
    pdf.ln(5)

    # Questionnaire
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, "Questionnaire (21.a - 21.m)", 0, 1)
    pdf.set_font("helvetica", '', 9)

    # List of Question keys
    q_keys = [f"q_21{x}" for x in ['a','b','c','d','e','f','g','h','i','j','k','l1','l2','m']]

    # Layout in 2 columns
    col_width = 90
    for i, key in enumerate(q_keys):
        ans = d.get(key, "N/A")
        # simple toggle logic for position
        if i % 2 == 0:
            pdf.cell(col_width, 5, f"{key[2:]}: {ans}", 0, 0)
        else:
            pdf.cell(col_width, 5, f"{key[2:]}: {ans}", 0, 1)
    if len(q_keys) % 2 != 0: pdf.ln()
    pdf.ln(5)

    # Section C: ID & NICS
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Section C - Identification & NICS", 0, 1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"ID Type: {d.get('id_type', '')}   Number: {d.get('id_number', '')}   Exp: {d.get('id_expiration_date', '')}", 0, 1)
    pdf.cell(0, 6, f"NICS NTN: {d.get('nics_ntn', '')}   Status: {d.get('nics_status', '')}   Date: {d.get('nics_date', '')}", 0, 1)
    pdf.ln(5)

    # Certification
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Certification", 0, 1)
    pdf.set_font("helvetica", 'I', 10)
    pdf.multi_cell(0, 5, "I certify that the answers to the above questions are true and correct.")

    pdf.ln(5)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"Transferee Signature: [Digital Signature Recorded]", 0, 1)
    pdf.cell(0, 6, f"Date: {d.get('certification_date', '')}", 0, 1)

    # Render signature points if available
    sig_points = d.get('buyer_signature_svg')
    if sig_points and sig_points != "[]":
        try:
            # Parse string back to list of tuples
            import ast
            points = ast.literal_eval(sig_points)
            if points:
                # Draw small representation
                # Find bounding box to scale? Just plot relative to current Y
                start_x = pdf.get_x() + 20
                start_y = pdf.get_y() + 5
                pdf.set_draw_color(0, 0, 139) # Dark Blue
                # Naive plot: just dots or lines
                # For PDF robustness, we usually create an image or draw lines.
                # FPDF line(x1, y1, x2, y2). Points is just a list of dots from mouse move.
                # Scale down: canvas was 400x150. Let's scale by 0.2
                scale = 0.2
                for i in range(len(points) - 1):
                     p1 = points[i]
                     p2 = points[i+1]
                     # Check for huge jumps (pen lift)? Canvas 'draw' event is drag, so continuous.
                     pdf.line(start_x + p1[0]*scale, start_y + p1[1]*scale,
                              start_x + p2[0]*scale, start_y + p2[1]*scale)
                pdf.set_draw_color(0, 0, 0) # Reset
        except:
            pass

    pdf.output(filepath)
