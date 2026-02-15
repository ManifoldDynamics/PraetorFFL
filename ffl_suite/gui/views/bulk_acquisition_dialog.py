import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from ffl_suite.logic.inventory_manager import add_acquisition
from ffl_suite.logic.compliance import can_acquire

class BulkAcquisitionDialog(tk.Toplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Bulk Acquisition")
        self.geometry("600x600")

        self.create_form()

    def create_form(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Bulk Acquisition (Same Make/Model)", font=("Arial", 12, "bold")).pack(pady=10)

        # Common Fields
        common_frame = ttk.LabelFrame(main_frame, text="Common Details")
        common_frame.pack(fill='x', pady=5)

        # Source Contact (Re-use parent's logic/map if possible, or simple reload)
        ttk.Label(common_frame, text="Source Contact:").grid(row=0, column=0, sticky='e')
        self.contact_combo = ttk.Combobox(common_frame, width=40, state="readonly")
        self.contact_combo['values'] = self.parent_view.contact_combo['values'] # Reuse
        self.contact_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Use simpler approach for fields than dict mapping to avoid complexity
        ttk.Label(common_frame, text="Make:").grid(row=1, column=0, sticky='e')
        self.make_entry = ttk.Entry(common_frame, width=40)
        self.make_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(common_frame, text="Model:").grid(row=2, column=0, sticky='e')
        self.model_entry = ttk.Entry(common_frame, width=40)
        self.model_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(common_frame, text="Type:").grid(row=3, column=0, sticky='e')
        self.type_combo = ttk.Combobox(common_frame, values=["Pistol", "Revolver", "Rifle", "Shotgun", "Receiver", "Frame", "Silencer", "Any Other Weapon"], state="readonly")
        self.type_combo.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(common_frame, text="Caliber:").grid(row=4, column=0, sticky='e')
        self.caliber_entry = ttk.Entry(common_frame, width=40)
        self.caliber_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(common_frame, text="Importer:").grid(row=5, column=0, sticky='e')
        self.importer_entry = ttk.Entry(common_frame, width=40)
        self.importer_entry.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(common_frame, text="UPC:").grid(row=6, column=0, sticky='e')
        self.upc_entry = ttk.Entry(common_frame, width=40)
        self.upc_entry.grid(row=6, column=1, sticky='w', padx=5, pady=5)

        # Serials Input
        ttk.Label(main_frame, text="Serial Numbers (One per line):").pack(anchor='w', pady=(10,0))
        self.serials_text = tk.Text(main_frame, height=10)
        self.serials_text.pack(fill='both', expand=True, pady=5)

        ttk.Button(main_frame, text="Process Bulk Import", command=self.process_import).pack(pady=10)

    def process_import(self):
        contact_name = self.contact_combo.get()
        if not contact_name:
            messagebox.showerror("Error", "Select a contact.")
            return
        # Safe get from parent map
        contact_id = self.parent_view.contact_map.get(contact_name)

        # Base Data
        base_data = {
            'make': self.make_entry.get(),
            'model': self.model_entry.get(),
            'type': self.type_combo.get(),
            'caliber': self.caliber_entry.get(),
            'importer': self.importer_entry.get(),
            'upc': self.upc_entry.get(),
            'condition': "New",
            'acquisition_date': date.today().isoformat()
        }

        if not all([base_data['make'], base_data['model'], base_data['type'], base_data['caliber']]):
             messagebox.showerror("Error", "Fill in Make, Model, Type, and Caliber.")
             return

        # Parse Serials
        raw_text = self.serials_text.get("1.0", "end")
        serials = []
        for line in raw_text.splitlines():
            s = line.strip()
            if s: serials.append(s)

        if not serials:
            messagebox.showerror("Error", "Enter at least one serial number.")
            return

        success_count = 0
        errors = []

        for serial in serials:
            if not can_acquire(base_data['make'], base_data['model'], serial):
                errors.append(f"Skipped {serial}: Already exists.")
                continue

            item_data = base_data.copy()
            item_data['serial_number'] = serial
            try:
                add_acquisition(item_data, contact_id)
                success_count += 1
            except Exception as e:
                errors.append(f"Error {serial}: {e}")

        msg = f"Imported {success_count} firearms."
        if errors:
            # Show up to 10 errors
            err_msg = "\n".join(errors[:10])
            if len(errors) > 10: err_msg += "\n..."
            messagebox.showwarning("Bulk Import Result", f"{msg}\n\nErrors:\n{err_msg}")
        else:
            messagebox.showinfo("Success", msg)
            self.destroy()
