from fpdf import FPDF
from ffl_suite.logic.settings_manager import get_setting

class ReceiptPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        name = get_setting('ffl_name') or "FFL Store"
        self.cell(0, 5, name, 0, 1, 'C')
        self.set_font('helvetica', '', 9)
        addr = get_setting('ffl_premise_address') or ""
        self.cell(0, 5, addr, 0, 1, 'C')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        footer_text = get_setting('receipt_footer') or "Thank you for your business!"
        self.multi_cell(0, 4, footer_text, 0, 'C')

def generate_receipt_pdf(filepath, sale_data, settings_override=None):
    # Determine settings source
    if settings_override:
        def get_cfg(k): return settings_override.get(k)
    else:
        from ffl_suite.logic.settings_manager import get_setting
        get_cfg = get_setting

    # 80mm width thermal paper style
    pdf = FPDF(format=(80, 200)) # Height arbitrary
    pdf.set_margins(5, 5, 5)
    pdf.add_page()

    # --- Header ---
    if get_cfg('receipt_show_logo') and get_cfg('logo_path'):
        # TODO: Handle logo logic safely
        pass

    pdf.set_font('helvetica', 'B', 12)
    name = get_cfg('ffl_name') or "FFL Store"
    pdf.cell(0, 5, name, 0, 1, 'C')

    pdf.set_font('helvetica', '', 9)
    addr = get_cfg('ffl_premise_address') or ""
    pdf.multi_cell(0, 4, addr, 0, 'C')

    header_msg = get_cfg('receipt_header')
    if header_msg:
        pdf.ln(2)
        pdf.set_font('helvetica', 'I', 8)
        pdf.multi_cell(0, 4, header_msg, 0, 'C')

    pdf.ln(4)

    # --- Info ---
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 5, f"Receipt #: {sale_data['id']}", 0, 1)
    pdf.cell(0, 5, f"Date: {sale_data['date']}", 0, 1)
    pdf.ln(2)

    # Items
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(40, 5, "Item", 0, 0)
    pdf.cell(10, 5, "Qty", 0, 0)
    pdf.cell(20, 5, "Price", 0, 1, 'R')
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())

    pdf.set_font('helvetica', '', 8)
    for item in sale_data['items']:
        name = item.get('name') or item.get('description') or "Item"
        qty = item['quantity']
        price = item['price']

        # Multiline name
        y = pdf.get_y()
        pdf.multi_cell(40, 4, name, 0, 'L')
        h = pdf.get_y() - y

        pdf.set_xy(45, y)
        pdf.cell(10, h, str(qty), 0, 0)

        pdf.set_xy(55, y)
        pdf.cell(20, h, f"{price:.2f}", 0, 1, 'R')

    pdf.ln(2)
    pdf.line(5, pdf.get_y(), 75, pdf.get_y())
    pdf.ln(1)

    # Totals
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(50, 5, "Subtotal:", 0, 0, 'R')
    pdf.cell(20, 5, f"{sale_data['subtotal']:.2f}", 0, 1, 'R')

    pdf.cell(50, 5, "Tax:", 0, 0, 'R')
    pdf.cell(20, 5, f"{sale_data['tax']:.2f}", 0, 1, 'R')

    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(50, 6, "Total:", 0, 0, 'R')
    pdf.cell(20, 6, f"{sale_data['total']:.2f}", 0, 1, 'R')

    # --- Footer ---
    pdf.ln(5)
    footer_text = get_cfg('receipt_footer')
    if footer_text:
        pdf.set_font('helvetica', 'I', 8)
        pdf.multi_cell(0, 4, footer_text, 0, 'C')

    pdf.output(filepath)
