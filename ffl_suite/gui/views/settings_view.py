import tkinter as tk
from tkinter import ttk, messagebox
from ffl_suite.logic.settings_manager import get_ffl_info, set_setting

class SettingsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        ttk.Label(self, text="FFL Information", font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(padx=20, pady=10)

        ttk.Label(form_frame, text="Licensee Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="License Number:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.license_entry = ttk.Entry(form_frame, width=40)
        self.license_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Premise Address:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.address_entry = ttk.Entry(form_frame, width=40)
        self.address_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=20)

    def load_settings(self):
        info = get_ffl_info()
        if info['name']: self.name_entry.insert(0, info['name'])
        if info['license_number']: self.license_entry.insert(0, info['license_number'])
        if info['premise_address']: self.address_entry.insert(0, info['premise_address'])

    def save_settings(self):
        set_setting('ffl_name', self.name_entry.get())
        set_setting('ffl_license_number', self.license_entry.get())
        set_setting('ffl_premise_address', self.address_entry.get())
        messagebox.showinfo("Success", "Settings saved successfully.")
