from fpdf import FPDF
from ffl_suite.logic.settings_manager import get_ffl_info

def generate_form4_helper(filepath, data):
    """
    Generates a Helper PDF for filing ATF Form 4 eForms.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "ATF eForms Helper - Form 4 (5320.4)", 0, 1, 'C')

    pdf.set_font("helvetica", 'I', 10)
    pdf.cell(0, 6, f"Control #: {data.get('id')} - Draft", 0, 1, 'C')
    pdf.ln(10)

    # Section 1: Transferor (FFL)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "1. Transferor (FFL)", 0, 1)
    ffl = get_ffl_info()
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"Name: {ffl.get('name')}", 0, 1)
    pdf.cell(0, 6, f"License: {ffl.get('license_number')}", 0, 1)
    pdf.cell(0, 6, f"Address: {ffl.get('premise_address')}", 0, 1)
    pdf.ln(5)

    # Section 2: Transferee (Applicant)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "2. Transferee (Applicant)", 0, 1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"Name: {data.get('entity_name')}", 0, 1)
    pdf.cell(0, 6, f"Type: {data.get('entity_type')}", 0, 1)
    # Address logic depends on entity type, for now MVP just name
    pdf.ln(5)

    # Section 4: Firearm (Item)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "4. Firearm Information", 0, 1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"Manufacturer: {data.get('firearm_make')}", 0, 1)
    pdf.cell(0, 6, f"Model: {data.get('firearm_model')}", 0, 1)
    pdf.cell(0, 6, f"Serial Number: {data.get('firearm_serial')}", 0, 1)
    pdf.cell(0, 6, f"Caliber: {data.get('firearm_cal')}", 0, 1)
    pdf.cell(0, 6, f"Type: {data.get('firearm_type')}", 0, 1)
    pdf.ln(5)

    # Section 12: CLEO
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "12. Chief Law Enforcement Officer (CLEO)", 0, 1)
    pdf.set_font("helvetica", '', 10)
    pdf.cell(0, 6, f"Name: {data.get('cleo_name')}", 0, 1)
    pdf.cell(0, 6, f"Title: {data.get('cleo_title')}", 0, 1)
    pdf.cell(0, 6, f"Agency: {data.get('cleo_agency')}", 0, 1)
    pdf.cell(0, 6, f"Address: {data.get('cleo_address')}", 0, 1)
    pdf.ln(5)

    # Responsible Persons (if Trust/Corp)
    rps = data.get('responsible_persons', [])
    if rps:
        pdf.add_page()
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 10, "Responsible Persons (Form 5320.23 Data)", 0, 1)
        pdf.set_font("helvetica", '', 10)

        for rp in rps:
            # rp tuple: id(0), ent_id(1), first(2), mid(3), last(4), title(5), dob(6), pob_c(7), pob_s(8), pob_cnt(9), ssn(10), upin(11)...
            name = f"{rp[2]} {rp[3] or ''} {rp[4]}".strip()
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, f"Name: {name}   Title: {rp[5]}", 0, 1, fill=True)
            pdf.cell(0, 6, f"DOB: {rp[6]}   POB: {rp[7]}, {rp[8]} {rp[9]}", 0, 1)
            pdf.cell(0, 6, f"SSN: {rp[10]}   UPIN: {rp[11]}", 0, 1)
            pdf.cell(0, 6, f"Photo: {rp[12]}", 0, 1)
            pdf.cell(0, 6, f"Fingerprints: {rp[13]}", 0, 1)
            pdf.ln(4)

    pdf.output(filepath)
