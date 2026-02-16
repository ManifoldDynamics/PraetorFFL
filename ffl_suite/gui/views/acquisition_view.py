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

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_frame, text="Acquire Firearm", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))

        self.entries = {}

        # 1. Source Information Card
        source_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        source_frame.pack(fill='x', padx=10, pady=10)
        ctk.CTkLabel(source_frame, text="Source Information", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor='w', padx=15, pady=10)

        source_grid = ctk.CTkFrame(source_frame, fg_color="transparent")
        source_grid.pack(fill='x', padx=10, pady=(0, 15))

        # Contact
        ctk.CTkLabel(source_grid, text="Source Contact").grid(row=0, column=0, sticky="w", padx=5)
        self.entries['contact_combo'] = ctk.CTkComboBox(source_grid, width=300, values=[])
        self.entries['contact_combo'].grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Date
        ctk.CTkLabel(source_grid, text="Acquisition Date").grid(row=0, column=1, sticky="w", padx=5)
        self.entries['date_entry'] = ctk.CTkEntry(source_grid, width=200)
        self.entries['date_entry'].insert(0, date.today().isoformat())
        self.entries['date_entry'].grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # 2. Firearm Identity Card
        id_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        id_frame.pack(fill='x', padx=10, pady=10)
        ctk.CTkLabel(id_frame, text="Firearm Identity", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor='w', padx=15, pady=10)

        id_grid = ctk.CTkFrame(id_frame, fg_color="transparent")
        id_grid.pack(fill='x', padx=10, pady=(0, 15))

        # Row 1: UPC, Serial
        ctk.CTkLabel(id_grid, text="UPC/EAN").grid(row=0, column=0, sticky="w", padx=5)
        self.entries['upc_entry'] = ctk.CTkEntry(id_grid)
        self.entries['upc_entry'].grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(id_grid, text="Serial Number").grid(row=0, column=1, sticky="w", padx=5)
        self.entries['serial_entry'] = ctk.CTkEntry(id_grid)
        self.entries['serial_entry'].grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Row 2: Make, Model
        ctk.CTkLabel(id_grid, text="Make/Manufacturer").grid(row=2, column=0, sticky="w", padx=5, pady=(10,0))
        self.entries['make_entry'] = ctk.CTkEntry(id_grid)
        self.entries['make_entry'].grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(id_grid, text="Model").grid(row=2, column=1, sticky="w", padx=5, pady=(10,0))
        self.entries['model_entry'] = ctk.CTkEntry(id_grid)
        self.entries['model_entry'].grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        id_grid.grid_columnconfigure((0, 1), weight=1)

        # 3. Technical Details Card
        tech_frame = ctk.CTkFrame(scroll_frame, corner_radius=10)
        tech_frame.pack(fill='x', padx=10, pady=10)
        ctk.CTkLabel(tech_frame, text="Technical Details", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor='w', padx=15, pady=10)

        tech_grid = ctk.CTkFrame(tech_frame, fg_color="transparent")
        tech_grid.pack(fill='x', padx=10, pady=(0, 15))

        ctk.CTkLabel(tech_grid, text="Type").grid(row=0, column=0, sticky="w", padx=5)
        self.entries['type_combo'] = ctk.CTkComboBox(tech_grid, values=["Pistol", "Revolver", "Rifle", "Shotgun", "Receiver", "Frame", "Silencer", "Any Other Weapon"])
        self.entries['type_combo'].grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(tech_grid, text="Caliber/Gauge").grid(row=0, column=1, sticky="w", padx=5)
        self.entries['caliber_entry'] = ctk.CTkEntry(tech_grid)
        self.entries['caliber_entry'].grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(tech_grid, text="Importer").grid(row=0, column=2, sticky="w", padx=5)
        self.entries['importer_entry'] = ctk.CTkEntry(tech_grid)
        self.entries['importer_entry'].grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        tech_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Buttons
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Record Acquisition", height=40, font=ctk.CTkFont(weight="bold"), command=self.submit).pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Bulk Acquisition", height=40, fg_color="gray", command=self.open_bulk_dialog).pack(side='left', padx=10)

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
