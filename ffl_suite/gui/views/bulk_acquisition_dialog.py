import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from ffl_suite.logic.inventory_manager import add_acquisition
from ffl_suite.logic.compliance import can_acquire

class BulkAcquisitionDialog(ctk.CTkToplevel):
    def __init__(self, parent_view):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.title("Bulk Acquisition")
        self.geometry("600x700")
        self.attributes("-topmost", True)

        self.create_form()

    def create_form(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Bulk Acquisition (Same Make/Model)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Common Fields
        common_frame = ctk.CTkFrame(main_frame)
        common_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(common_frame, text="Source Contact:").grid(row=0, column=0, sticky='e', padx=10, pady=5)
        self.contact_combo = ctk.CTkComboBox(common_frame, width=300, values=["No Contacts"])
        # Reuse parent values if available
        if hasattr(self.parent_view, 'entries') and 'contact_combo' in self.parent_view.entries:
            self.contact_combo.configure(values=self.parent_view.entries['contact_combo'].cget('values'))
        self.contact_combo.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        fields = [
            ("Make", "make_entry", "entry"),
            ("Model", "model_entry", "entry"),
            ("Type", "type_combo", "combo"),
            ("Caliber", "caliber_entry", "entry"),
            ("Importer", "importer_entry", "entry"),
            ("UPC", "upc_entry", "entry")
        ]

        self.entries = {}
        for i, (label, name, w_type) in enumerate(fields, 1):
            ctk.CTkLabel(common_frame, text=label+":").grid(row=i, column=0, sticky='e', padx=10, pady=5)

            if w_type == "entry":
                entry = ctk.CTkEntry(common_frame, width=300)
            else:
                entry = ctk.CTkComboBox(common_frame, width=300, values=["Pistol", "Revolver", "Rifle", "Shotgun", "Receiver", "Frame", "Silencer", "Any Other Weapon"])

            entry.grid(row=i, column=1, sticky='w', padx=10, pady=5)
            self.entries[name] = entry

        # Serials Input
        ctk.CTkLabel(main_frame, text="Serial Numbers (One per line):").pack(anchor='w', pady=(10,0))
        self.serials_text = ctk.CTkTextbox(main_frame, height=200)
        self.serials_text.pack(fill='both', expand=True, pady=5)

        ctk.CTkButton(main_frame, text="Process Bulk Import", command=self.process_import).pack(pady=10)

    def process_import(self):
        contact_name = self.contact_combo.get()
        if not contact_name:
            messagebox.showerror("Error", "Select a contact.")
            return
        # Safe get from parent map
        contact_id = self.parent_view.contact_map.get(contact_name)

        # Base Data
        base_data = {
            'make': self.entries['make_entry'].get(),
            'model': self.entries['model_entry'].get(),
            'type': self.entries['type_combo'].get(),
            'caliber': self.entries['caliber_entry'].get(),
            'importer': self.entries['importer_entry'].get(),
            'upc': self.entries['upc_entry'].get(),
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
