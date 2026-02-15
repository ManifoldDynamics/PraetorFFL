import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from ffl_suite.logic.inventory_manager import add_acquisition
from ffl_suite.database.db_manager import execute_query
from ffl_suite.logic.compliance import can_acquire

class AcquisitionView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Acquire Firearm", font=("Arial", 16, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=10)

        # Row 0: Source Contact
        ttk.Label(form_frame, text="Source Contact:").grid(row=0, column=0, sticky='e')
        self.contact_combo = ttk.Combobox(form_frame, width=40, state="readonly")
        self.contact_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.contact_combo['postcommand'] = self.load_contacts

        # Row 1: Make
        ttk.Label(form_frame, text="Make:").grid(row=1, column=0, sticky='e')
        self.make_entry = ttk.Entry(form_frame, width=40)
        self.make_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # Row 2: Model
        ttk.Label(form_frame, text="Model:").grid(row=2, column=0, sticky='e')
        self.model_entry = ttk.Entry(form_frame, width=40)
        self.model_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Row 3: Serial
        ttk.Label(form_frame, text="Serial Number:").grid(row=3, column=0, sticky='e')
        self.serial_entry = ttk.Entry(form_frame, width=40)
        self.serial_entry.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        # Row 4: Type
        ttk.Label(form_frame, text="Type:").grid(row=4, column=0, sticky='e')
        self.type_combo = ttk.Combobox(form_frame, values=["Pistol", "Revolver", "Rifle", "Shotgun", "Receiver", "Frame", "Silencer", "Any Other Weapon"], state="readonly")
        self.type_combo.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        # Row 5: Caliber
        ttk.Label(form_frame, text="Caliber/Gauge:").grid(row=5, column=0, sticky='e')
        self.caliber_entry = ttk.Entry(form_frame, width=40)
        self.caliber_entry.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        # Row 6: Importer
        ttk.Label(form_frame, text="Importer (if any):").grid(row=6, column=0, sticky='e')
        self.importer_entry = ttk.Entry(form_frame, width=40)
        self.importer_entry.grid(row=6, column=1, sticky='w', padx=5, pady=5)

        # Row 7: Date
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=7, column=0, sticky='e')
        self.date_entry = ttk.Entry(form_frame, width=40)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=7, column=1, sticky='w', padx=5, pady=5)

        ttk.Button(self, text="Record Acquisition", command=self.submit).pack(pady=20)

        self.contact_map = {} # Name -> ID

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
        self.contact_combo['values'] = values

    def submit(self):
        contact_name = self.contact_combo.get()
        if not contact_name or contact_name not in self.contact_map:
            messagebox.showerror("Error", "Please select a valid contact.")
            return

        data = {
            'make': self.make_entry.get(),
            'model': self.model_entry.get(),
            'serial_number': self.serial_entry.get(),
            'type': self.type_combo.get(),
            'caliber': self.caliber_entry.get(),
            'importer': self.importer_entry.get(),
            'condition': "New", # Defaulting for now
            'acquisition_date': self.date_entry.get()
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

            # Clear form
            self.serial_entry.delete(0, 'end')
            # Keep other fields as user might be entering batch
        except Exception as e:
            messagebox.showerror("Error", f"Failed to acquire firearm: {e}")
