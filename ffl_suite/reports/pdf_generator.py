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

def generate_4473_pdf(filepath, firearm_data, buyer_data, ffl_data, answers=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Form 4473 (Simplified/Partial)", 0, 1, 'C')

    pdf.set_font("helvetica", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"FFL: {ffl_data.get('name')}", 0, 1)
    pdf.cell(0, 10, f"Buyer: {buyer_data.get('name')}", 0, 1)
    pdf.cell(0, 10, f"Firearm: {firearm_data.get('make')} {firearm_data.get('model')} {firearm_data.get('serial')}", 0, 1)

    if answers:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "Section B - Transferee Questions", 0, 1)
        pdf.set_font("helvetica", '', 10)
        for q_id, ans in answers.items():
            pdf.cell(0, 6, f"Question {q_id}: {ans}", 0, 1)

    pdf.ln(20)
    pdf.multi_cell(0, 10, "Note: This is a placeholder for the actual ATF Form 4473. "
                          "In a real application, this would populate the official PDF template or generate a compliant layout.")

    pdf.output(filepath)
