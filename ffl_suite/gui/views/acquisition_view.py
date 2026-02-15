import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
from ffl_suite.logic.inventory_manager import add_acquisition
from ffl_suite.logic.compliance import can_acquire
from ffl_suite.database.db_manager import execute_query

class AcquisitionView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.contact_map = {}

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll_frame, text="Acquire Firearm", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Form Container
        form_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_frame.pack(padx=20, pady=10)

        # Fields
        fields = [
            ("Source Contact:", "contact_combo", "combo"),
            ("UPC/EAN:", "upc_entry", "entry"),
            ("Make:", "make_entry", "entry"),
            ("Model:", "model_entry", "entry"),
            ("Serial Number:", "serial_entry", "entry"),
            ("Type:", "type_combo", "combo"),
            ("Caliber/Gauge:", "caliber_entry", "entry"),
            ("Importer (if any):", "importer_entry", "entry"),
            ("Date (YYYY-MM-DD):", "date_entry", "entry")
        ]

        self.entries = {}

        for i, (label, name, w_type) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=10)

            if w_type == "entry":
                entry = ctk.CTkEntry(form_frame, width=300)
                if name == "date_entry":
                    entry.insert(0, date.today().isoformat())
            else: # combo
                if name == "type_combo":
                    values = ["Pistol", "Revolver", "Rifle", "Shotgun", "Receiver", "Frame", "Silencer", "Any Other Weapon"]
                else:
                    values = [] # contact_combo
                entry = ctk.CTkComboBox(form_frame, width=300, values=values)

            entry.grid(row=i, column=1, sticky="w", padx=10, pady=10)
            self.entries[name] = entry

        # Buttons
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Record Acquisition", command=self.submit).pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Bulk Acquisition", command=self.open_bulk_dialog).pack(side='left', padx=10)

    def load_contacts(self):
        sql = "SELECT id, name, license_number FROM contacts"
        contacts = execute_query(sql, fetch=True)
        values = []
        self.contact_map = {}
        if contacts:
            for c in contacts:
                display = c[1]
                if c[2]:
                    display += f" ({c[2]})"
                values.append(display)
                self.contact_map[display] = c[0]

        if values:
            self.entries['contact_combo'].configure(values=values)
            self.entries['contact_combo'].set(values[0])
        else:
            self.entries['contact_combo'].configure(values=["No Contacts Found"])
            self.entries['contact_combo'].set("No Contacts Found")

    def submit(self):
        contact_name = self.entries['contact_combo'].get()
        if not contact_name or contact_name not in self.contact_map:
            messagebox.showerror("Error", "Please select a valid contact.")
            return

        data = {
            'make': self.entries['make_entry'].get(),
            'model': self.entries['model_entry'].get(),
            'serial_number': self.entries['serial_entry'].get(),
            'type': self.entries['type_combo'].get(),
            'caliber': self.entries['caliber_entry'].get(),
            'importer': self.entries['importer_entry'].get(),
            'condition': "New",
            'upc': self.entries['upc_entry'].get(),
            'acquisition_date': self.entries['date_entry'].get()
        }

        if not all([data['make'], data['model'], data['serial_number'], data['type'], data['caliber']]):
             messagebox.showerror("Error", "Please fill in all required fields.")
             return

        if not can_acquire(data['make'], data['model'], data['serial_number']):
            messagebox.showwarning("Warning", "This firearm (Make/Model/Serial) is already in inventory!")
            return

        try:
            add_acquisition(data, self.contact_map[contact_name])
            messagebox.showinfo("Success", "Firearm acquired successfully.")
            self.entries['serial_entry'].delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to acquire firearm: {e}")

    def open_bulk_dialog(self):
        from ffl_suite.gui.views.bulk_acquisition_dialog import BulkAcquisitionDialog
        BulkAcquisitionDialog(self)
